import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parents[1]
BIN = REPO / "home/dot_local/bin"


def load(name):
    path = BIN / ("executable_" + name)
    loader = importlib.machinery.SourceFileLoader(name.replace("-", "_"), str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class EditorURLs(unittest.TestCase):
    def setUp(self):
        self.editor = load("open-in-editor.tmpl")

    def test_percent_escapes_and_locations(self):
        self.assertEqual(self.editor.parse_url("file-line-column:///tmp/file%20with%20spaces.txt:7:12"),
                         ("/tmp/file with spaces.txt", 7, 12))
        self.assertEqual(self.editor.parse_url("file:///tmp/file%3A42"), ("/tmp/file:42", None, None))
        self.assertEqual(self.editor.parse_url("file://localhost/tmp/name:part.txt:8"),
                         ("/tmp/name:part.txt", 8, None))

    def test_rejects_remote_urls_and_invalid_locations(self):
        for url in ("https://example.test/a", "file://remote/a", "file:///tmp/a:0", "file:///tmp/%00"):
            with self.assertRaises(ValueError):
                self.editor.parse_url(url)


class Batteries(unittest.TestCase):
    def setUp(self):
        self.battery = load("check-low-battery")

    def device(self, root, name, **values):
        path = root / name
        path.mkdir()
        for field, value in values.items():
            (path / field).write_text(str(value))

    def test_mixed_charge_and_energy_and_nonstandard_charger_name(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.device(root, "BAT0", type="Battery", status="Discharging", energy_full=40_000_000, energy_now=4_000_000)
            self.device(root, "CMB1", type="Battery", status="Discharging", charge_full=2_000_000,
                        charge_now=1_000_000, voltage_min_design=10_000_000)
            self.assertEqual(self.battery.battery_status(root), (23, True))
            self.device(root, "USB_C", type="USB", online=1)
            self.assertEqual(self.battery.battery_status(root), (23, False))

    def test_alerts_once_at_each_threshold_then_resets_on_charge(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"XDG_STATE_HOME": temp}), \
                patch.object(self.battery, "subprocess") as commands, \
                patch.object(self.battery, "battery_status", side_effect=[(14, True), (13, True), (4, True), (30, False), (12, True)]):
            for _ in range(5):
                self.battery.main()
            self.assertEqual(commands.run.call_count, 3)


class Brightness(unittest.TestCase):
    def test_identical_models_remain_distinct(self):
        brightness = load("brightness-control")
        output = "Display 1\n Model: Identical\nDisplay 2\n Model: Identical\nInvalid display\n"
        self.assertEqual(brightness.displays(output), ["1", "2"])

    def test_connector_changes_invalidate_fingerprint(self):
        brightness = load("brightness-control")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            connector = root / "card1-DP-1"
            connector.mkdir()
            status = connector / "status"
            status.write_text("connected")
            before = brightness.topology(root)
            status.write_text("disconnected")
            self.assertNotEqual(before, brightness.topology(root))


class Notifications(unittest.TestCase):
    def test_sensitive_clipboard_never_calls_cliphist(self):
        result = subprocess.run(["/bin/sh", str(BIN / "executable_clipboard-store")],
                                env={"CLIPBOARD_STATE": "sensitive", "PATH": "/nonexistent"},
                                input="password", text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unmuted_volume_and_argument_forwarding(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "log"
            (root / "wpctl").write_text('#!/bin/sh\nprintf "Volume: 0.42\\n"\n')
            (root / "notify-send").write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$TEST_LOG"\n')
            for command in ("wpctl", "notify-send"):
                (root / command).chmod(0o755)
            environment = os.environ | {"PATH": str(root) + ":/usr/bin:/bin", "TEST_LOG": str(log)}
            result = subprocess.run(["sh", str(BIN / "executable_notify-progress"), "audio"],
                                    input="42", env=environment, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("audio-volume-medium", log.read_text())

    def test_symlink_names_with_spaces(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "a directory"
            source.mkdir()
            subprocess.run(["python3", str(BIN / "executable_make-symlink"), str(source)], check=True)
            link = source.with_name("a directory (symlink)")
            self.assertEqual(link.resolve(), source)
            # Repeating the action must fail instead of overwriting something.
            result = subprocess.run(["python3", str(BIN / "executable_make-symlink"), str(source)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)


class ProjectLauncher(unittest.TestCase):
    def test_space_and_shell_metacharacters_are_passed_as_one_argument(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project with spaces; echo unwanted"
            project.mkdir()
            config = root / "chezmoi.json"
            config.write_text(json.dumps({"data": {"projectPaths": [str(root)]}}))
            rendered = subprocess.run(["chezmoi", "--config", str(config), "--source", str(REPO / "home"),
                                       "execute-template", "--file", str(REPO / "home/dot_config/rofi/scripts/executable_projects.py.tmpl")],
                                      text=True, capture_output=True, check=True).stdout
            script = root / "projects.py"
            script.write_text(rendered)
            loader = importlib.machinery.SourceFileLoader("projects", str(script))
            spec = importlib.util.spec_from_loader(loader.name, loader)
            module = importlib.util.module_from_spec(spec)
            loader.exec_module(module)
            with patch.dict(os.environ, {"ROFI_RETV": "1"}), patch.object(module.sys, "argv", ["projects.py", str(project)]), \
                    patch.object(module.subprocess, "Popen") as launch:
                module.main()
            self.assertEqual(launch.call_args.args[0], ["kitty", "--directory", str(project), "nvim"])
            self.assertNotIn("shell", launch.call_args.kwargs)


if __name__ == "__main__":
    unittest.main()
