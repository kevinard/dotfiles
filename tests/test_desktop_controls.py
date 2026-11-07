"""Desktop behavior with fake devices/daemons; never change the running session."""
import configparser
from contextlib import contextmanager, redirect_stdout
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_helpers import load

REPO = Path(__file__).resolve().parents[1]


def load_path(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class DisplayControls(unittest.TestCase):
    def setUp(self):
        self.brightness = load("brightness-control")

    def test_identical_monitors_are_addressed_by_connector_and_bus(self):
        output = """Display 1
   I2C bus: /dev/i2c-5
   DRM connector: card1-DP-1
   Monitor: Identical
Display 2
   I2C bus: /dev/i2c-8
   DRM connector: card1-HDMI-A-1
   Monitor: Identical
"""
        self.assertEqual(self.brightness.ddc_displays(output), {"DP-1": "5", "HDMI-A-1": "8"})

    def test_minimum_is_visible_and_low_brightness_has_fine_steps(self):
        self.assertEqual(self.brightness.target_level(1, 100, "down", 5), 1)
        self.assertEqual(self.brightness.target_level(3, 100, "up", 5), 4)
        self.assertEqual(self.brightness.target_level(99, 100, "up", 5), 100)
        self.assertGreater(self.brightness.target_level(1, 255, "down", 5), 0)

    def test_coarse_backlights_can_be_dimmed_with_normal_and_precise_keys(self):
        for current, maximum in [(8, 15), (2, 10)]:
            for step in (1, 5):
                with self.subTest(current=current, maximum=maximum, step=step):
                    self.assertLess(self.brightness.target_level(current, maximum, "down", step), current)

    def test_adjustments_make_progress_without_crossing_display_bounds(self):
        for maximum in (2, 10, 15, 255, 10000):
            minimum = max(1, (maximum + 99) // 100)
            for current in {minimum, max(minimum, maximum // 2), maximum}:
                for step in (1, 5):
                    with self.subTest(maximum=maximum, current=current, step=step):
                        up = self.brightness.target_level(current, maximum, "up", step)
                        down = self.brightness.target_level(current, maximum, "down", step)
                        self.assertTrue(minimum <= down <= current <= up <= maximum)
                        if current > minimum:
                            self.assertLess(down, current)
                        if current < maximum:
                            self.assertGreater(up, current)

    def test_unknown_external_display_never_changes_laptop_backlight(self):
        responses = [json.dumps({"DP-9": {"current_mode": 0}}), json.dumps({"name": "DP-9"}), ""]
        with tempfile.TemporaryDirectory() as temporary, \
                patch.dict(os.environ, {"XDG_CACHE_HOME": temporary}), \
                patch.object(self.brightness, "command", side_effect=responses), \
                patch.object(self.brightness, "backlight") as laptop:
            with self.assertRaisesRegex(RuntimeError, "No DDC"):
                self.brightness.main(["down"])
            laptop.assert_not_called()

    def test_invalid_ddc_read_never_writes_a_brightness_value(self):
        with patch.object(self.brightness, "command", return_value="VCP 10 ERR") as commands:
            with self.assertRaises(RuntimeError):
                self.brightness.adjust_ddc("5", "down", 5)
            self.assertEqual(commands.call_count, 1)


class AudioControls(unittest.TestCase):
    def test_cycle_moves_application_streams_and_preserves_dsp_routing(self):
        audio = load("audio-control")
        sinks = [{"name": "speakers"}, {"name": "hdmi", "ports": [{"availability": "not available"}]},
                 {"name": "dsp", "properties": {"node.virtual": "true"}}, {"name": "headphones"}]
        streams = [{"index": 1, "properties": {"application.name": "Firefox"}},
                   {"index": 2, "properties": {"application.name": "EasyEffects"}},
                   {"index": 3, "properties": {}}]
        with patch.object(audio, "command", side_effect=[json.dumps(sinks), "speakers", "", json.dumps(streams)]) as commands, \
                patch.object(audio.subprocess, "run") as run:
            audio.cycle_output()
        self.assertIn(["pactl", "set-default-sink", "headphones"], [call.args[0] for call in commands.call_args_list])
        moves = [call.args[0] for call in run.call_args_list if "move-sink-input" in call.args[0]]
        self.assertEqual(moves, [["pactl", "move-sink-input", "1", "headphones"]])


class ScopedCommands(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.log = self.root / "commands.jsonl"
        self.environment = os.environ | {"PATH": str(self.root) + ":/usr/bin:/bin", "COMMAND_LOG": str(self.log)}
        self.environment.pop("CANOPA_SESSION", None)
        self.stub("systemd-run", '''
import os, sys
record("systemd-run")
if os.environ.get("SCOPE_FAIL") == "1":
    sys.exit(1)
if os.environ.get("RECORD_ONLY") == "1":
    sys.exit(0)
argv = sys.argv[sys.argv.index("--") + 1:]
os.execvp(argv[0], argv)
''')
        self.stub("swaylock", '''
import os, sys
record("swaylock")
sys.exit(int(os.environ.get("LOCK_EXIT", "0")))
''')
        self.stub("systemctl", 'record("systemctl")\n')

    def stub(self, name, body):
        executable = self.root / name
        executable.write_text('''#!/usr/bin/env python3
import json, os, sys
def record(name):
    with open(os.environ["COMMAND_LOG"], "a") as log:
        log.write(json.dumps({"program": name, "args": sys.argv[1:]}) + "\\n")
''' + body)
        executable.chmod(0o755)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_scope_failure_falls_back_to_direct_locking(self):
        result = subprocess.run(["/bin/sh", str(REPO / "home/dot_local/bin/executable_desktop-lock")],
                                env=self.environment | {"SCOPE_FAIL": "1"}, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([call["program"] for call in self.calls()], ["systemd-run", "swaylock"])
        self.assertEqual(self.calls()[-1]["args"], ["-f"])

    def test_successful_scoped_lock_does_not_start_a_second_locker(self):
        result = subprocess.run(["/bin/sh", str(REPO / "home/dot_local/bin/executable_desktop-lock")],
                                env=self.environment, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([call["program"] for call in self.calls()], ["systemd-run", "swaylock"])

    def test_power_menu_does_not_suspend_if_both_lock_attempts_fail(self):
        locker = self.root / "desktop-lock"
        shutil.copy2(REPO / "home/dot_local/bin/executable_desktop-lock", locker)
        locker.chmod(0o755)
        result = subprocess.run(["/bin/sh", str(REPO / "home/dot_config/rofi/scripts/executable_powermenu.sh"), "Suspend"],
                                env=self.environment | {"SCOPE_FAIL": "1", "LOCK_EXIT": "7", "ROFI_RETV": "1"},
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertNotIn("systemctl", [call["program"] for call in self.calls()])

    def test_before_sleep_locks_without_contacting_the_user_manager(self):
        service = configparser.ConfigParser(interpolation=None)
        service.read(REPO / "home/dot_config/systemd/user/swayidle.service")
        argv = shlex.split(service["Service"]["ExecStart"])
        handler = argv[argv.index("before-sleep") + 1]
        result = subprocess.run(["/bin/sh", "-c", handler], env=self.environment | {"SCOPE_FAIL": "1"},
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls(), [{"program": "swaylock", "args": ["-f"]}])

    def test_application_arguments_remain_literal(self):
        arguments = ["example-app", "/tmp/project ${HOME} with spaces", "$USER", "$(not-executed)", "semi;colon"]
        result = subprocess.run(["/bin/sh", str(REPO / "home/dot_local/bin/executable_desktop-launch"), *arguments],
                                env=self.environment | {"RECORD_ONLY": "1"}, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        scope = self.calls()[0]["args"]
        separator = scope.index("--")
        self.assertIn("--expand-environment=no", scope[:separator])
        self.assertEqual(scope[separator + 1:], arguments)


class DesktopControls(unittest.TestCase):
    def test_canopa_menu_opens_native_quick_settings(self):
        desktop = load("desktop-control")
        with patch.object(desktop, "config", return_value={"notificationBackend": "canopa"}), \
                patch.object(desktop, "command") as commands, \
                patch.object(desktop.subprocess, "run") as rofi:
            desktop.menu()
        commands.assert_called_once_with(["canopa-shell", "--toggle-panel"])
        rofi.assert_not_called()

    def test_canopa_display_recovery_does_not_start_a_competing_layout_daemon(self):
        desktop = load("desktop-control")
        with patch.object(desktop, "config", return_value={"notificationBackend": "canopa"}), \
                patch.object(desktop, "command", side_effect=['{"eDP-1": {}}', "", "", ""]) as commands:
            desktop.recover_displays()
        self.assertEqual([call.args[0] for call in commands.call_args_list], [
            ["niri", "msg", "--json", "outputs"], ["niri", "msg", "output", "eDP-1", "on"],
            ["niri", "msg", "action", "power-on-monitors"], ["brightness-control", "clear"]])

    def test_canopa_uses_its_pinned_control_socket_and_on_off_responses(self):
        desktop = load("desktop-control")
        with patch.dict(os.environ, {"XDG_RUNTIME_DIR": "/tmp/test-runtime"}), \
                patch.object(desktop, "config", return_value={"notificationBackend": "canopa"}), \
                patch.object(desktop, "command", return_value="on") as commands:
            self.assertTrue(desktop.dnd(True))
        self.assertEqual(commands.call_args.args[0], ["canopa-notify", "ctl", "--socket",
                         "/tmp/test-runtime/canopa-notify/control.sock", "dnd", "on"])

    def test_cancelled_clipboard_selection_never_overwrites_clipboard(self):
        desktop = load("desktop-control")
        with patch.object(desktop, "command", return_value="1\ttext"), \
                patch.object(desktop.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "")) as commands:
            desktop.clipboard()
        self.assertEqual(commands.call_count, 1)

    def test_binary_clipboard_selection_is_copied_without_text_decoding(self):
        desktop = load("desktop-control")
        data = b"\x89PNG\r\n\x00\xff"
        with patch.dict(os.environ, {"ROFI_RETV": "1"}), \
                patch.object(desktop.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, data)) as commands:
            desktop.clipboard_mode("123\t[[ binary data png ]]")
        copy = commands.call_args_list[-1]
        self.assertEqual(copy.args[0], ["wl-copy"])
        self.assertEqual(copy.kwargs["input"], data)


class SnapshotRecovery(unittest.TestCase):
    def setUp(self):
        self.snapshot = load_path("snapshot", REPO / "provision/arch/libexec/dotfiles-snapshot")
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.snapshots = self.root / "snapshots"
        (self.snapshots / "1/snapshot").mkdir(parents=True)
        self.backup = self.snapshots / ".boot/1"
        self.backup.mkdir(parents=True)
        self.uki = self.backup / "arch-linux.efi"
        self.uki.write_bytes(b"old signed kernel image")
        self.manifest = {"version": 1, "snapshot": "1", "sha256": {self.uki.name: self.snapshot.digest(self.uki)}}
        self.write_manifest()

    def write_manifest(self):
        (self.backup / "manifest.json").write_text(json.dumps(self.manifest))

    def test_corrupt_image_is_rejected_before_touching_recovery_esp(self):
        self.uki.write_bytes(b"damaged")
        target = self.root / "esp"
        with self.assertRaisesRegex(RuntimeError, "checksum mismatch"):
            self.snapshot.restore_ukis(self.snapshots, "1", target)
        self.assertFalse(target.exists())

    def test_manifest_cannot_escape_the_boot_backup(self):
        self.manifest["sha256"] = {"../outside.efi": "bad"}
        self.write_manifest()
        with self.assertRaisesRegex(RuntimeError, "filename"):
            self.snapshot.verify(self.snapshots, "1")

    def test_restore_preserves_current_uki_and_copies_verified_backup(self):
        esp = self.root / "esp"
        (esp / "EFI/Linux").mkdir(parents=True)
        current = esp / "EFI/Linux/arch-linux.efi"
        current.write_bytes(b"new signed kernel image")
        with patch.object(self.snapshot, "mounted"), patch.object(self.snapshot.os, "sync"), redirect_stdout(io.StringIO()):
            self.snapshot.restore_ukis(self.snapshots, "1", esp)
        self.assertEqual(current.read_bytes(), b"old signed kernel image")
        saved = list((self.snapshots / ".boot").glob("before-restore-*/arch-linux.efi"))
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].read_bytes(), b"new signed kernel image")

    def test_missing_root_snapshot_is_not_a_valid_boot_restore(self):
        (self.snapshots / "1/snapshot").rmdir()
        with self.assertRaisesRegex(RuntimeError, "Root snapshot"):
            self.snapshot.verify(self.snapshots, "1")

    @contextmanager
    def checkpoint_creation(self, corrupt=False):
        esp = self.root / "esp"
        images = esp / "EFI/Linux"
        images.mkdir(parents=True)
        (images / "arch-linux.efi").write_bytes(b"signed boot image")

        def snapper_command(argv):
            if argv[3] == "create":
                (self.snapshots / "2/snapshot").mkdir(parents=True)
                return "2"
            if argv[3:] == ["cleanup", "number"]:
                return ""
            raise AssertionError(f"Unexpected command: {argv}")

        def delete_snapshot(argv, **kwargs):
            self.assertEqual(argv, ["snapper", "-c", "root", "delete", "2"])
            shutil.rmtree(self.snapshots / "2")
            return subprocess.CompletedProcess(argv, 0)

        def sync():
            if corrupt:
                (self.snapshots / ".boot/2/arch-linux.efi").write_bytes(b"damaged after backup")

        with patch.object(self.snapshot, "mounted"), \
                patch.object(self.snapshot, "command", side_effect=snapper_command) as commands, \
                patch.object(self.snapshot.subprocess, "run", side_effect=delete_snapshot), \
                patch.object(self.snapshot.os, "sync", side_effect=sync), redirect_stdout(io.StringIO()):
            yield esp, commands

    def test_create_produces_a_verified_root_and_boot_pair(self):
        with self.checkpoint_creation() as (esp, _):
            self.snapshot.create(self.snapshots, esp)
        _, files = self.snapshot.verify(self.snapshots, "2")
        self.assertEqual(list(files), ["arch-linux.efi"])
        self.assertEqual((self.snapshots / ".boot/2/arch-linux.efi").read_bytes(), b"signed boot image")

    def test_create_rejects_corruption_and_removes_the_unverified_pair(self):
        with self.checkpoint_creation(corrupt=True) as (esp, commands):
            with self.assertRaisesRegex(RuntimeError, "checksum mismatch"):
                self.snapshot.create(self.snapshots, esp)
        self.assertFalse((self.snapshots / "2").exists())
        self.assertFalse((self.snapshots / ".boot/2").exists())
        self.assertFalse(any(call.args[0][3] == "cleanup" for call in commands.call_args_list))


class RootProvisioning(unittest.TestCase):
    @contextmanager
    def snapshot_installation(self, existing_hook=None):
        provision = load_path("provision_desktop", REPO / "scripts/provision-desktop")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "etc").mkdir()
            (root / "etc/arch-release").touch()
            hook = root / "etc/pacman.d/hooks/00-desktop-snapshot.hook"
            if existing_hook is not None:
                hook.parent.mkdir(parents=True)
                hook.write_bytes(existing_hook)
            state = {"fail_checkpoint": False}
            checkpoints = []

            def isolated_path(value):
                original = Path(value)
                if str(original) == "/" or any(str(original).startswith(prefix) for prefix in ("/etc/", "/usr/", "/var/")):
                    return root / str(original).lstrip("/")
                return original

            def system_command(argv, **kwargs):
                if argv[0] == "/usr/local/libexec/dotfiles-snapshot":
                    checkpoints.append(hook.exists())
                    if state["fail_checkpoint"]:
                        raise subprocess.CalledProcessError(1, argv)
                return subprocess.CompletedProcess(argv, 0)

            with patch.object(provision, "Path", side_effect=isolated_path), \
                    patch.object(provision.os, "geteuid", return_value=0), patch.object(provision.os, "chown"), \
                    patch.object(provision, "check_snapshot_layout"), \
                    patch.object(provision.subprocess, "run", side_effect=system_command), redirect_stdout(io.StringIO()):
                yield provision, hook, state, checkpoints

    def test_package_hook_is_activated_only_after_successful_checkpoint(self):
        with self.snapshot_installation() as (provision, hook, _, checkpoints):
            provision.main(["--apply", "--snapshots"])
            self.assertEqual(checkpoints, [False])
            self.assertIn("AbortOnFail", hook.read_text())

    def test_failed_initial_checkpoint_leaves_no_hook_and_allows_retry(self):
        with self.snapshot_installation() as (provision, hook, state, checkpoints):
            state["fail_checkpoint"] = True
            with self.assertRaises(subprocess.CalledProcessError):
                provision.main(["--apply", "--snapshots"])
            self.assertFalse(hook.exists())
            state["fail_checkpoint"] = False
            provision.main(["--apply", "--snapshots"])
            self.assertEqual(checkpoints, [False, False])
            self.assertIn("AbortOnFail", hook.read_text())

    def test_failed_checkpoint_keeps_a_previously_installed_hook(self):
        original = b"# existing package policy\n"
        with self.snapshot_installation(existing_hook=original) as (provision, hook, state, _):
            state["fail_checkpoint"] = True
            with self.assertRaises(subprocess.CalledProcessError):
                provision.main(["--apply", "--snapshots"])
            self.assertEqual(hook.read_bytes(), original)

    def test_snapper_registration_preserves_other_configs_and_is_idempotent(self):
        provision = load_path("provision_desktop", REPO / "scripts/provision-desktop")
        original = '# local settings\nSNAPPER_CONFIGS="home"\nOTHER="keep me"\n'
        updated = provision.register_root(original)
        self.assertIn('SNAPPER_CONFIGS="home root"', updated)
        self.assertIn('OTHER="keep me"', updated)
        self.assertEqual(provision.register_root(updated), updated)
        self.assertEqual(provision.register_root(provision.register_root("")), provision.register_root(""))
        with self.assertRaises(RuntimeError):
            provision.register_root('SNAPPER_CONFIGS="$CUSTOM"\n')

    def test_preview_never_runs_package_or_service_commands(self):
        provision = load_path("provision_desktop", REPO / "scripts/provision-desktop")
        with patch.object(provision.subprocess, "run") as commands, redirect_stdout(io.StringIO()):
            provision.main(["--snapshots"])
        commands.assert_not_called()


if __name__ == "__main__":
    unittest.main()
