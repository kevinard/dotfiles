"""kdbx-tidy on synthetic databases only; never opens a real vault."""
import base64
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import hashlib
import hmac
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]
try:
    import pykeepass
except ImportError:
    pykeepass = None

PASSWORD = "correct horse battery staple"
PSL = "// test list\ncom\nnet\norg\nuk\nco.uk\n*.ck\n!www.ck\ngithub.io\n"


def when(year, month=1, day=1):
    return datetime(year, month, day, tzinfo=timezone.utc)


def encrypt_export(data, password, kdf):
    """Build a password-protected Bitwarden export the way the Bitwarden clients do."""
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import pad
    export = {"encrypted": True, "passwordProtected": True, "salt": "c2FsdHlzYWx0", **kdf}
    tidy = load_tidy()
    enc_key, mac_key = tidy.export_keys(export, password)
    def seal(plain):
        iv = os.urandom(16)
        data = AES.new(enc_key, AES.MODE_CBC, iv).encrypt(pad(plain, 16))
        mac = hmac.new(mac_key, iv + data, hashlib.sha256).digest()
        return "2." + "|".join(base64.b64encode(part).decode() for part in (iv, data, mac))
    export["encKeyValidation_DO_NOT_EDIT"] = seal(b"validation")
    export["data"] = seal(json.dumps(data).encode())
    return export


def load_tidy():
    loader = importlib.machinery.SourceFileLoader(
        "kdbx_tidy", str(REPO / "home/dot_local/bin/executable_kdbx-tidy"))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def login(name, username, password, uris, changed="2024-01-01T00:00:00Z", **extra):
    return {"type": 1, "name": name, "creationDate": "2019-01-01T00:00:00Z",
            "revisionDate": changed, "folderId": extra.pop("folder", None),
            "login": {"username": username, "password": password,
                      "uris": [{"uri": uri} for uri in uris],
                      "passwordRevisionDate": changed, **extra.pop("login", {})}, **extra}


EXPORT = {"encrypted": False, "folders": [{"id": "f1", "name": "Social"}], "items": [
    login("Bank", "carol", "bank-new", ["https://www.bank.com/login"], "2025-06-01T00:00:00Z"),
    login("Mail", "alice", "mail-old", ["https://mail.example.com"], "2020-03-01T00:00:00Z"),
    login("Forum", "dave", "forum-same", ["https://forum.net", "https://forum-mirror.org"],
          login={"totp": "JBSWY3DPEHPK3PXP"}),
    login("New site", "erin", "new-pw", ["new.org", "androidapp://org.new"], folder="f1",
          fields=[{"name": "PIN", "value": "1234", "type": 1}]),
    login("New site again", "erin", "other", ["https://www.new.org"]),
    login("Passkey site", "frank", "pk", ["https://pk.com"],
          login={"fido2Credentials": [{"credentialId": "x"}]}),
    {"type": 2, "name": "Recovery codes", "notes": "abc def", "creationDate": "2021-01-01T00:00:00Z",
     "revisionDate": "2021-01-01T00:00:00Z"},
    {"type": 5, "name": "Old SSH key", "sshKey": {"privateKey": "secret"}},
]}


@unittest.skipIf(pykeepass is None, "python-pykeepass is not installed")
class KdbxTidy(unittest.TestCase):
    def setUp(self):
        self.tidy = load_tidy()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        psl = self.root / "psl.dat"
        psl.write_text(PSL)
        self.suffixes = self.tidy.Suffixes(psl)
        self.database = self.root / "vault.kdbx"
        kp = pykeepass.create_database(str(self.database), password=PASSWORD)
        def add(title, username, password, url, created=when(2022)):
            entry = kp.add_entry(kp.root_group, title, username, password, url=url)
            entry.ctime = entry.mtime = created
            return entry
        add("Mail", "alice", "mail-current", "accounts.example.com/login", when(2023))
        add("Shop", "bob", "shop", "https://shop.co.uk")
        add("Wifi", "", "wifi", None)
        add("Bank", "carol", "bank-old", "https://bank.com", when(2023))
        add("Forum", "dave", "forum-same", "https://forum.net")
        kp.trash_entry(add("Deleted", "zed", "gone", "https://sub.deleted.com"))
        kp.save()

    def open(self, path=None):
        return pykeepass.PyKeePass(str(path or self.database), password=PASSWORD)

    def plan(self, kp, items=None):
        return self.tidy.build_plan(kp, items, self.suffixes)

    def test_public_suffixes(self):
        base = self.suffixes.base_domain
        self.assertEqual(base("a.b.example.com"), "example.com")
        self.assertEqual(base("shop.co.uk"), "shop.co.uk")
        self.assertEqual(base("user.github.io"), "user.github.io")
        self.assertEqual(base("a.b.ck"), "a.b.ck")
        self.assertEqual(base("www.ck"), "www.ck")
        self.assertEqual(base("co.uk"), None)
        self.assertEqual(base("192.168.1.1"), "192.168.1.1")
        self.assertIsNone(self.tidy.web_host("androidapp://com.example"))
        self.assertIsNone(self.tidy.web_host("My bank"))

    def test_report_lists_url_fixes_without_touching_the_file(self):
        before = self.database.read_bytes()
        plan = self.plan(self.open())
        changes = {(c.section.split(",")[0], c.what) for c in plan.changes}
        self.assertEqual(changes, {("Add https:// to scheme-less URLs", "Mail"),
                                   ("Add the base domain", "Mail")})
        self.assertIn(("No URL: never offered by browser or iOS autofill", "Wifi", ""), plan.reviews)
        self.assertNotIn("Deleted", str(plan.changes) + str(plan.reviews))
        self.assertEqual(self.database.read_bytes(), before)

    def test_bitwarden_merge_plan(self):
        items = [self.tidy.Item.from_export(raw, {"f1": "Social"}) for raw in EXPORT["items"]]
        plan = self.plan(self.open(), items)
        sections = {(c.section.split(":")[0], c.what) for c in plan.changes}
        self.assertIn(("Different password, Bitwarden's is newer", "Bank"), sections)
        self.assertIn(("Different password, KeePass's is newer", "Mail"), sections)
        self.assertIn(("Add sites known only to Bitwarden", "Forum"), sections)
        self.assertIn(("Add TOTP known only to Bitwarden", "Forum"), sections)
        added = sorted(c.what for c in plan.changes if c.section.startswith("Only in Bitwarden"))
        self.assertEqual(added, ["New site (erin)", "Passkey site (frank)", "Recovery codes"])
        reviews = {(section.split(" (")[0], what) for section, what, _ in plan.reviews}
        self.assertIn(("Duplicate inside the Bitwarden export", "New site again (erin)"), reviews)
        self.assertIn(("Bitwarden passkeys", "Passkey site (frank)"), reviews)
        self.assertIn(("Bitwarden SSH keys", "Old SSH key"), reviews)

    def test_apply_writes_new_file_and_keeps_every_password(self):
        items = [self.tidy.Item.from_export(raw, {"f1": "Social"}) for raw in EXPORT["items"]]
        kp = self.open()
        self.tidy.apply_plan(self.plan(kp, items), now=when(2026, 11, 11))
        output = self.root / "tidy.kdbx"
        kp.save(filename=str(output))
        result = self.open(output)
        find = lambda title: result.find_entries(title=title, first=True)
        mail, bank, forum = find("Mail"), find("Bank"), find("Forum")
        self.assertEqual(mail.url, "https://accounts.example.com/login")
        self.assertEqual(mail.get_custom_property("KP2A_URL"), "https://example.com")
        self.assertEqual(mail.password, "mail-current")
        self.assertEqual([h.password for h in mail.history], ["mail-old"])
        self.assertEqual(bank.password, "bank-new")
        self.assertEqual([h.password for h in bank.history], ["bank-old"])
        self.assertEqual(forum.get_custom_property("KP2A_URL"), "https://forum-mirror.org")
        self.assertTrue(forum.otp.startswith("otpauth://totp/Forum?secret=JBSWY3DPEHPK3PXP"))
        self.assertEqual(mail.mtime, when(2026, 11, 11))
        new = find("New site")
        self.assertEqual(new.path, ["Imported from Bitwarden", "Social", "New site"])
        self.assertEqual(new.url, "https://new.org")
        self.assertEqual(new.get_custom_property("PIN"), "1234")
        self.assertTrue(new.is_custom_property_protected("PIN"))
        self.assertEqual(find("Recovery codes").notes, "abc def")
        self.assertIsNone(find("Old SSH key"))
        self.assertEqual(self.open().find_entries(title="Bank", first=True).password, "bank-old")

    def test_password_protected_exports(self):
        for kdf in ({"kdfType": 0, "kdfIterations": 1000},
                    {"kdfType": 1, "kdfIterations": 2, "kdfMemory": 16, "kdfParallelism": 1}):
            with self.subTest(kdf=kdf["kdfType"]):
                path = self.root / f"export-{kdf['kdfType']}.json"
                path.write_text(json.dumps(encrypt_export(EXPORT, "export-pw", kdf)))
                items = self.tidy.load_bitwarden(path, ask=lambda _: "export-pw")
                self.assertEqual([item.title for item in items][:2], ["Bank", "Mail"])
                with self.assertRaisesRegex(ValueError, "wrong Bitwarden export password"):
                    self.tidy.load_bitwarden(path, ask=lambda _: "nope")
        restricted = self.root / "restricted.json"
        restricted.write_text(json.dumps({"encrypted": True, "data": "x"}))
        with self.assertRaisesRegex(ValueError, "account-restricted"):
            self.tidy.load_bitwarden(restricted)

    def test_command_line_never_overwrites_and_output_merges_in_keepassxc(self):
        export = self.root / "export.json"
        export.write_text(json.dumps(EXPORT))
        output = self.root / "tidy.kdbx"
        with patch.object(self.tidy.getpass, "getpass", return_value=PASSWORD), \
                patch.object(self.tidy, "PSL_PATH", self.root / "psl.dat"), \
                redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()):
            self.assertEqual(self.tidy.main(["report", str(self.database),
                                             "--bitwarden", str(export)]), 0)
            self.assertFalse(output.exists())
            self.assertEqual(self.tidy.main(["apply", str(self.database), str(output),
                                             "--bitwarden", str(export)]), 0)
            with self.assertRaises(SystemExit):
                self.tidy.main(["apply", str(self.database), str(output)])
        self.assertIn("Different password, Bitwarden's is newer", out.getvalue())
        self.assertNotIn("bank-new", out.getvalue())
        self.assertNotIn("mail-current", out.getvalue())
        if not shutil.which("keepassxc-cli"):
            self.skipTest("keepassxc-cli is not installed")
        merged = self.root / "merged.kdbx"
        shutil.copy(self.database, merged)
        subprocess.run(["keepassxc-cli", "merge", "-q", "--same-credentials", str(merged), str(output)],
                       input=PASSWORD + "\n", text=True, check=True, capture_output=True)
        result = self.open(merged)
        self.assertEqual(result.find_entries(title="Bank", first=True).password, "bank-new")
        self.assertEqual(result.find_entries(title="Mail", first=True)
                         .get_custom_property("KP2A_URL"), "https://example.com")
        self.assertIsNotNone(result.find_entries(title="Recovery codes", first=True))


if __name__ == "__main__":
    unittest.main()
