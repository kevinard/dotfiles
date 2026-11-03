"""Check optional scheduler root-stage boundaries without changing the desktop."""
from contextlib import redirect_stdout
import importlib.machinery
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[1]


class SchedulerProvisioning(unittest.TestCase):
    def setUp(self):
        loader = importlib.machinery.SourceFileLoader("scheduler_provision", str(REPO / "scripts/provision-desktop"))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.provision = importlib.util.module_from_spec(spec)
        loader.exec_module(self.provision)

    def test_preview_has_no_package_service_or_filesystem_mutations(self):
        for mode in ("enable", "disable"):
            with self.subTest(mode=mode), patch.object(self.provision.subprocess, "run") as commands, \
                    patch.object(self.provision, "install") as install, redirect_stdout(io.StringIO()):
                self.provision.main(["--scheduler", mode])
                commands.assert_not_called()
                install.assert_not_called()

    def test_scheduler_stage_does_not_mix_with_snapshots(self):
        with redirect_stdout(io.StringIO()), patch("sys.stderr", new=io.StringIO()), self.assertRaises(SystemExit):
            self.provision.main(["--scheduler", "enable", "--snapshots"])

    def test_enable_backs_up_rules_and_enables_for_boot_without_touching_other_policy(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "etc/arch-release").parent.mkdir()
            (root / "etc/arch-release").touch()
            config = root / "etc/system76-scheduler/config.kdl"
            config.parent.mkdir()
            config.write_text("original policy\n")

            def isolated_path(value):
                value = Path(value)
                if str(value) == "/" or str(value).startswith(("/etc/", "/usr/", "/var/")):
                    return root / str(value).lstrip("/")
                return value

            with patch.object(self.provision, "Path", side_effect=isolated_path), \
                    patch.object(self.provision.os, "geteuid", return_value=0), \
                    patch.object(self.provision.os, "chown"), \
                    patch.object(self.provision.subprocess, "run") as commands, redirect_stdout(io.StringIO()):
                self.provision.main(["--scheduler", "enable", "--apply"])
                self.provision.main(["--scheduler", "enable", "--apply"])
            self.assertEqual(config.read_bytes(), (self.provision.SOURCE / self.provision.SCHEDULER_FILES[0]).read_bytes())
            backups = list((root / "var/backups/dotfiles-scheduler").rglob("config.kdl"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "original policy\n")
            self.assertFalse((root / "etc/sysctl.d").exists())
            invocations = [call.args[0] for call in commands.call_args_list]
            self.assertEqual(invocations, [["pacman", "-Syu", "--needed", "system76-scheduler"],
                                          ["systemctl", "enable", "com.system76.Scheduler.service"]] * 2)

    def test_disable_stops_daemon_without_removing_package_or_configuration(self):
        with patch.object(self.provision.os, "geteuid", return_value=0), \
                patch.object(self.provision.Path, "exists", return_value=True), \
                patch.object(self.provision.subprocess, "run") as commands, \
                patch.object(self.provision, "install") as install, redirect_stdout(io.StringIO()):
            self.provision.main(["--scheduler", "disable", "--apply"])
        commands.assert_called_once_with(["systemctl", "disable", "--now", "com.system76.Scheduler.service"], check=True)
        install.assert_not_called()


if __name__ == "__main__":
    unittest.main()
