"""Enrollment failures must not publish incomplete or overwrite working mappings."""
from contextlib import ExitStack, redirect_stdout, redirect_stderr
import importlib.machinery
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]


class LoginEnrollment(unittest.TestCase):
    def setUp(self):
        loader = importlib.machinery.SourceFileLoader(
            "enroll_login_keys", str(REPO / "scripts/enroll-login-keys"))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.helper = importlib.util.module_from_spec(spec)
        loader.exec_module(self.helper)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.output = Path(self.temporary.name) / "state/u2f_mappings"
        self.first = "test-user:primary-handle,public-key,es256,+presence\n"
        self.second = "test-user:backup-handle,public-key-2,es256,+presence\n"

    def invoke(self, results, output=None):
        with ExitStack() as stack:
            stack.enter_context(patch.object(self.helper.os, "geteuid", return_value=1000))
            stack.enter_context(patch.object(self.helper.pwd, "getpwuid",
                                            return_value=SimpleNamespace(pw_name="test-user")))
            stack.enter_context(patch.object(self.helper.sys.stdin, "isatty", return_value=True))
            stack.enter_context(patch.object(self.helper.shutil, "which", return_value="/usr/bin/pamu2fcfg"))
            stack.enter_context(patch("builtins.input", return_value=""))
            commands = stack.enter_context(patch.object(self.helper.subprocess, "run", side_effect=results))
            stack.enter_context(redirect_stdout(io.StringIO()))
            stack.enter_context(redirect_stderr(io.StringIO()))
            status = self.helper.main(["--output", str(output or self.output)])
            return status, commands

    def result(self, output):
        return subprocess.CompletedProcess(["pamu2fcfg"], 0, output)

    def test_both_registrations_are_one_private_mapping(self):
        status, commands = self.invoke([self.result(self.first), self.result(self.second)])
        self.assertEqual(status, 0)
        self.assertEqual(self.output.read_text(),
                         "test-user:primary-handle,public-key,es256,+presence:"
                         "backup-handle,public-key-2,es256,+presence\n")
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o600)
        for call in commands.call_args_list:
            self.assertEqual(call.args[0], ["pamu2fcfg", "-u", "test-user",
                                           "-o", "pam://kevinard-linux",
                                           "-i", "pam://kevinard-linux"])

    def test_failed_backup_leaves_no_mapping(self):
        status, _ = self.invoke([self.result(self.first),
                                subprocess.CalledProcessError(1, ["pamu2fcfg"])])
        self.assertEqual(status, 1)
        self.assertFalse(self.output.exists())

    def test_malformed_or_wrong_user_registration_leaves_no_mapping(self):
        for invalid in ("", "root:handle,key,es256,+presence", self.first + self.second,
                        "test-user:handle,key", "test-user:a,key,es256,:b,key,es256,"):
            with self.subTest(output=invalid):
                status, _ = self.invoke([self.result(invalid)])
                self.assertEqual(status, 1)
                self.assertFalse(self.output.exists())

    def test_existing_file_is_preserved_without_enrollment(self):
        self.output.parent.mkdir()
        self.output.write_text("existing registrations\n")
        with self.assertRaises(SystemExit):
            self.invoke([])
        self.assertEqual(self.output.read_text(), "existing registrations\n")

    def test_duplicate_handles_are_rejected(self):
        status, _ = self.invoke([self.result(self.first), self.result(self.first)])
        self.assertEqual(status, 1)
        self.assertFalse(self.output.exists())

    def test_symlink_cannot_replace_another_file(self):
        target = Path(self.temporary.name) / "existing"
        target.write_text("preserve me")
        self.output.parent.mkdir()
        self.output.symlink_to(target)
        with self.assertRaises(FileExistsError):
            self.helper.write_mapping(self.output, "test-user", [
                self.helper.registration(self.first, "test-user"),
                self.helper.registration(self.second, "test-user")])
        self.assertEqual(target.read_text(), "preserve me")

    def test_repository_output_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.invoke([], REPO / "u2f_mappings")


if __name__ == "__main__":
    unittest.main()
