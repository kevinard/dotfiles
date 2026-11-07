"""Check stage boundaries without applying dotfiles, touching tokens or using sudo."""
from contextlib import redirect_stdout, redirect_stderr
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
import tomllib
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]


class MachineSetup(unittest.TestCase):
    def setUp(self):
        loader = importlib.machinery.SourceFileLoader("setup_machine", str(REPO / "scripts/setup-machine"))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.setup = importlib.util.module_from_spec(spec)
        loader.exec_module(self.setup)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.config = Path(self.temporary.name) / "chezmoi.toml"
        self.args = SimpleNamespace(config=self.config, apply=False, reconfigure=False,
                                    skip_desktop_build=False, customize=False)

    def test_preview_initializes_missing_config_but_never_applies(self):
        with patch.object(self.setup.shutil, "which", return_value="/usr/bin/chezmoi"), \
                patch.object(self.setup, "run") as commands, redirect_stdout(io.StringIO()):
            self.setup.configure(self.args, "arch")
        self.assertEqual(len(commands.call_args_list), 2)
        self.assertIn("init", commands.call_args_list[0].args[0])
        self.assertEqual(commands.call_args_list[1].args[0][-1], "diff")
        for call in commands.call_args_list:
            self.assertIn(str(REPO), call.args[0])
            self.assertIn(str(self.config), call.args[0])

    def test_existing_configuration_is_not_regenerated(self):
        self.config.write_text("[data]\n")
        with patch.object(self.setup.shutil, "which", return_value="/usr/bin/chezmoi"), \
                patch.object(self.setup, "run") as commands, redirect_stdout(io.StringIO()):
            self.setup.configure(self.args, "arch")
        self.assertEqual(len(commands.call_args_list), 1)
        self.assertEqual(commands.call_args.args[0][-1], "diff")

    def test_customize_preserves_existing_config_and_offers_editor(self):
        original = '[data]\nenv="work"\n\n[git]\nautoCommit=false\n'
        self.config.write_text(original)
        self.args.customize = True
        with patch.object(self.setup.shutil, "which", return_value="/usr/bin/chezmoi"), \
                patch.object(self.setup, "default_init_options") as defaults, \
                patch.object(self.setup, "run") as commands, redirect_stdout(io.StringIO()):
            self.setup.configure(self.args, "arch")
        self.assertEqual(commands.call_args_list[0].args[0][-1], "edit-config")
        self.assertEqual(self.config.read_text(), original)
        defaults.assert_not_called()

    def test_first_customize_asks_all_questions(self):
        self.args.customize = True
        with patch.object(self.setup.shutil, "which", return_value="/usr/bin/chezmoi"), \
                patch.object(self.setup, "default_init_options") as defaults, \
                patch.object(self.setup, "run") as commands, redirect_stdout(io.StringIO()):
            self.setup.configure(self.args, "arch")
        self.assertEqual(commands.call_args_list[0].args[0][-2:], ["init", "--prompt"])
        defaults.assert_not_called()

    def test_hardware_detection_and_hybrid_gpu_choice(self):
        root = Path(self.temporary.name)
        cpuinfo = root / "cpuinfo"
        cpuinfo.write_text("vendor_id : GenuineIntel\n")
        battery = root / "class/power_supply/BAT0/type"
        battery.parent.mkdir(parents=True)
        battery.write_text("Battery\n")
        gpu = root / "class/drm/card0/device/vendor"
        gpu.parent.mkdir(parents=True)
        gpu.write_text("0x8086\n")
        self.assertEqual(self.setup.hardware_defaults(root, cpuinfo), (True, "intel", "intel"))
        second = root / "class/drm/card1/device/vendor"
        second.parent.mkdir(parents=True)
        second.write_text("0x10de\n")
        self.assertEqual(self.setup.hardware_defaults(root, cpuinfo), (True, "intel", None))
        with patch.object(self.setup, "hardware_defaults", return_value=(True, "intel", None)), \
                redirect_stdout(io.StringIO()):
            options = self.setup.default_init_options("arch")
        self.assertFalse(any(option.startswith("GPU vendor") for option in options))

    def test_missing_hardware_information_uses_generic_packages(self):
        root = Path(self.temporary.name)
        self.assertEqual(self.setup.hardware_defaults(root, root / "missing"), (False, "none", "none"))

    def test_failed_apply_stops_before_desktop_build(self):
        self.config.write_text("[data]\n")
        self.args.apply = True
        data = subprocess.CompletedProcess([], 0, stdout='{"processScheduler":true}')
        with patch.object(self.setup.shutil, "which", return_value="/usr/bin/chezmoi"), \
                patch.object(self.setup, "run", side_effect=[None, data, subprocess.CalledProcessError(1, ["chezmoi", "apply"])]) as commands, \
                redirect_stdout(io.StringIO()), self.assertRaises(subprocess.CalledProcessError):
            self.setup.configure(self.args, "arch")
        self.assertEqual([call.args[0][-1] for call in commands.call_args_list], ["diff", "--format=json", "apply"])

    def test_setup_reuses_installed_canopa_without_an_installer(self):
        self.config.write_text("[data]\n")
        self.args.apply = True
        data = subprocess.CompletedProcess([], 0, stdout="{}")
        output = io.StringIO()
        with patch.object(self.setup.shutil, "which", side_effect=lambda program: program), \
                patch.object(self.setup, "run", return_value=data) as commands, redirect_stdout(output):
            self.setup.configure(self.args, "arch")
        self.assertIn("Using the installed Canopa desktop", output.getvalue())
        self.assertEqual([call.args[0][-1] for call in commands.call_args_list], ["diff", "--format=json", "apply"])

    def test_missing_canopa_stops_before_apply_unless_explicitly_skipped(self):
        self.config.write_text("[data]\n")
        self.args.apply = True
        data = subprocess.CompletedProcess([], 0, stdout='{"desktopShell":"canopa"}')
        with patch.object(self.setup.shutil, "which", side_effect={"chezmoi": "/usr/bin/chezmoi"}.get), \
                patch.object(self.setup, "run", return_value=data) as commands, redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "install the Canopa desktop and compositor"):
                self.setup.configure(self.args, "arch")
            self.assertEqual([call.args[0][-1] for call in commands.call_args_list], ["diff", "--format=json"])
            commands.reset_mock()
            self.args.skip_desktop_build = True
            self.setup.configure(self.args, "arch")
            self.assertEqual([call.args[0][-1] for call in commands.call_args_list], ["diff", "--format=json", "apply"])

    def test_scheduler_helper_build_follows_apply_only_when_selected(self):
        self.config.write_text("[data]\n")
        self.args.apply = True
        for enabled in (False, True):
            for skip in (False, True):
                self.args.skip_desktop_build = skip
                data = subprocess.CompletedProcess([], 0, stdout=json.dumps({
                    "desktopShell": "waybar", "processScheduler": enabled}))
                with self.subTest(enabled=enabled, skip=skip), \
                        patch.object(self.setup.shutil, "which", return_value="/usr/bin/chezmoi"), \
                        patch.object(self.setup, "run", return_value=data) as commands, \
                        redirect_stdout(io.StringIO()):
                    self.setup.configure(self.args, "arch")
                builds = [call.args[0] for call in commands.call_args_list
                          if call.args[0] == [REPO / "scripts/install-system76-scheduler-niri"]]
                self.assertEqual(bool(builds), enabled and not skip)

    def test_installed_scheduler_helper_does_not_need_network_or_compiler(self):
        root = Path(self.temporary.name)
        state = root / "state/system76-scheduler-niri"
        state.mkdir(parents=True)
        installer = REPO / "scripts/install-system76-scheduler-niri"
        revision = next(line.split("=", 1)[1] for line in installer.read_text().splitlines()
                        if line.startswith("revision="))
        (state / "dotfiles-installed-revision").write_text(revision + "\n")
        binary = root / ".local/bin/system76-scheduler-niri"
        binary.parent.mkdir(parents=True)
        binary.write_text("#!/bin/sh\nexit 0\n")
        binary.chmod(0o755)
        environment = {"HOME": str(root), "XDG_STATE_HOME": str(root / "state"), "PATH": "/nonexistent"}
        result = subprocess.run(["/bin/bash", str(installer)], env=environment,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("no rebuild needed", result.stdout)
        binary.unlink()
        incomplete = subprocess.run(["/bin/bash", str(installer)], env=environment,
                                    text=True, capture_output=True)
        self.assertNotEqual(incomplete.returncode, 0)
        self.assertNotIn("no rebuild needed", incomplete.stdout)

    def test_ssh_uses_managed_socket_without_clearing_agent(self):
        with patch.dict(os.environ, {"XDG_RUNTIME_DIR": self.temporary.name,
                                    "SSH_AUTH_SOCK": "/some/forwarded-agent"}), \
                patch.object(self.setup.shutil, "which", return_value="/usr/bin/tool"), \
                patch.object(self.setup, "run") as commands, redirect_stdout(io.StringIO()):
            self.setup.load_ssh_token()
        self.assertEqual([call.args[0] for call in commands.call_args_list], [
            ["systemctl", "--user", "start", "ssh-agent.service"],
            ["ssh-add", "-K"], ["ssh-add", "-l"]])
        for call in commands.call_args_list[1:]:
            self.assertEqual(call.kwargs["env"]["SSH_AUTH_SOCK"],
                             str(Path(self.temporary.name) / "ssh-agent.socket"))

    def test_unsupported_distribution_rejected(self):
        for stage in ("configure", "ssh", "auth", "check"):
            with self.subTest(stage=stage), \
                    patch.object(self.setup.os, "geteuid", return_value=1000), \
                    patch.object(self.setup.platform, "freedesktop_os_release", return_value={"ID": "unsupported"}), \
                    patch.object(self.setup, "run") as commands, \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(self.setup.main([stage]), 1)
                commands.assert_not_called()

    def test_plan_does_not_run_commands(self):
        with patch.object(self.setup, "run") as commands, redirect_stdout(io.StringIO()):
            self.assertEqual(self.setup.main(["plan"]), 0)
            commands.assert_not_called()

    def test_real_fresh_init_respects_repository_home_subdirectory(self):
        root = Path(self.temporary.name)
        source = root / "checkout"
        shutil.copytree(REPO / "home", source / "home",
                        ignore=shutil.ignore_patterns(".chezmoiexternals", "__pycache__", "*.pyc"))
        (source / ".chezmoiroot").write_text("home\n")
        subprocess.run(["git", "init", "--quiet", str(source)], check=True)
        destination = root / "destination"
        destination.mkdir()
        fixture = json.loads((REPO / "tests/profiles/arch-work.json").read_text())
        fixture["chezmoi"]["homeDir"] = str(destination)
        override = root / "fixture.json"
        override.write_text(json.dumps(fixture))
        with patch.object(self.setup, "REPO", source):
            command = self.setup.chezmoi_command(self.config)
        command += ["--destination", str(destination), "--override-data-file", str(override),
                    "--cache", str(root / "cache"), "--persistent-state", str(root / "state")]
        with patch.object(self.setup, "hardware_defaults", return_value=(True, "intel", "intel")), \
                redirect_stdout(io.StringIO()):
            prompts = ["init"] + self.setup.default_init_options("arch")
        prompts += ["--promptChoice", "Identity=work"]
        for question, answer in {"Email address": "work@example.test",
                                 "Full name": "Work Test"}.items():
            prompts += ["--promptString", question + "=" + answer]
        result = subprocess.run(command + prompts, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(self.config.exists())
        saved = tomllib.loads(self.config.read_text())["data"]
        self.assertEqual(saved["desktopShell"], "canopa")
        self.assertEqual(saved["powerManager"], "tlp")
        self.assertEqual(saved["gpgsign"], "no")
        rendered = subprocess.run(command + ["dump", "--format=json"], check=True,
                                  text=True, capture_output=True)
        targets = json.loads(rendered.stdout)
        self.assertIn(".profile", targets)
        self.assertNotIn("home/.profile", targets)
        self.assertFalse(any(target.startswith("scripts/") for target in targets))

    def test_short_entry_point_forwards_actions_from_any_directory(self):
        root = Path(self.temporary.name)
        entry = root / "checkout/setup"
        entry.parent.mkdir()
        shutil.copy2(REPO / "setup", entry)
        backend = entry.parent / "scripts/setup-machine"
        backend.parent.mkdir()
        backend.write_text("#!/usr/bin/env python3\nimport json, sys\nprint(json.dumps(sys.argv[1:]))\n")
        backend.chmod(0o755)
        for arguments, expected in (([], ["configure", "--apply"]),
                                    (["--preview"], ["configure"]),
                                    (["--customize"], ["configure", "--apply", "--customize"]),
                                    (["ssh"], ["ssh"]), (["auth"], ["auth"]),
                                    (["scheduler", "--apply"], ["scheduler", "--apply"]),
                                    (["login", "--apply"], ["login", "--apply"])):
            with self.subTest(arguments=arguments):
                result = subprocess.run([str(entry)] + arguments, cwd=root,
                                        text=True, capture_output=True, check=True)
                self.assertEqual(json.loads(result.stdout), expected)

    def test_system_stage_preview_and_apply_have_distinct_privilege_boundaries(self):
        for apply in (False, True):
            with self.subTest(apply=apply), patch.object(self.setup.os, "geteuid", return_value=1000), \
                    patch.object(self.setup.platform, "freedesktop_os_release", return_value={"ID": "arch"}), \
                    patch.object(self.setup, "run") as commands:
                args = ["system", "--snapshots"] + (["--apply"] if apply else [])
                self.assertEqual(self.setup.main(args), 0)
            expected = [REPO / "scripts/provision-desktop", "--snapshots"]
            if apply:
                expected = ["sudo", REPO / "scripts/provision-desktop", "--apply", "--snapshots"]
            commands.assert_called_once_with(expected)

    def test_scheduler_uses_saved_opt_in_and_separate_root_stage(self):
        self.config.write_text("[data]\n")
        for enabled in (False, True):
            for apply in (False, True):
                self.args.apply = apply
                data = subprocess.CompletedProcess([], 0, stdout=json.dumps({"processScheduler": enabled}))
                with self.subTest(enabled=enabled, apply=apply), \
                        patch.object(self.setup, "run", return_value=data) as commands:
                    self.setup.configure_scheduler(self.args)
                expected = [REPO / "scripts/provision-desktop", "--scheduler", "enable" if enabled else "disable"]
                if apply:
                    expected = ["sudo", *expected, "--apply"]
                self.assertEqual(commands.call_args_list[1].args[0], expected)
                self.assertEqual(len(commands.call_args_list), 3 if apply and not enabled else 2)

    def test_scheduler_rejects_non_boolean_before_root_commands(self):
        self.config.write_text("[data]\n")
        data = subprocess.CompletedProcess([], 0, stdout='{"processScheduler":"false"}')
        with patch.object(self.setup, "run", return_value=data) as commands, self.assertRaisesRegex(RuntimeError, "boolean"):
            self.setup.configure_scheduler(self.args)
        self.assertEqual(commands.call_count, 1)


if __name__ == "__main__":
    unittest.main()
