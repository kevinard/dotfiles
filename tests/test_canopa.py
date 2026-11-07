"""Exercise Canopa migration and install boundaries without changing the host."""
from contextlib import redirect_stdout
import importlib.machinery
import importlib.util
import io
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]


def load(name):
    loader = importlib.machinery.SourceFileLoader(name.replace('-', '_'), str(REPO / 'scripts' / name))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class CanopaInstall(unittest.TestCase):
    def setUp(self):
        self.installer = load('install-canopa')
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.state = self.root / 'state'
        self.state.mkdir()

    def test_pinentry_migration_preserves_options_and_backs_up_previous_config(self):
        gnupg = self.root / 'gnupg'
        gnupg.mkdir()
        config = gnupg / 'gpg-agent.conf'
        original = '# My agent\ndefault-cache-ttl 300\npinentry-program /old/pinentry\nenable-ssh-support\n'
        config.write_text(original)
        with redirect_stdout(io.StringIO()):
            self.installer.configure_pinentry(self.state, gnupg, Path('/home/test/desktop-pinentry'))
            self.installer.configure_pinentry(self.state, gnupg, Path('/home/test/desktop-pinentry'))
        self.assertEqual(config.read_text(), '# My agent\ndefault-cache-ttl 300\nenable-ssh-support\npinentry-program /home/test/desktop-pinentry\n')
        backups = list(self.state.glob('gnupg-*/gpg-agent.conf'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), original)
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)

    def test_pinentry_refuses_symlink_without_modifying_target(self):
        target = self.root / 'agent'
        target.write_text('keep me\n')
        gnupg = self.root / 'gnupg'
        gnupg.mkdir()
        (gnupg / 'gpg-agent.conf').symlink_to(target)
        with self.assertRaisesRegex(RuntimeError, 'non-regular'):
            self.installer.configure_pinentry(self.state, gnupg, Path('/pinentry'))
        self.assertEqual(target.read_text(), 'keep me\n')

    def test_local_binary_migration_retains_unrelated_tools_and_original_symlink(self):
        local = self.root / 'bin'
        local.mkdir()
        (local / 'canopa').write_text('old binary')
        (local / 'canopa-shell').symlink_to('/missing/development-binary')
        (local / 'my-tool').write_text('keep')
        with redirect_stdout(io.StringIO()):
            self.installer.retire_companions(self.state, local)
            self.installer.retire_companions(self.state, local)
        backups = list(self.state.glob('companions-*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / 'canopa').read_text(), 'old binary')
        self.assertEqual(os.readlink(backups[0] / 'canopa-shell'), '/missing/development-binary')
        self.assertEqual((local / 'my-tool').read_text(), 'keep')
        self.assertFalse((local / 'canopa').exists())

    def test_complete_packages_skip_compiler_but_missing_binary_or_changed_package_does_not(self):
        system = self.root / 'usr'
        for name in (*self.installer.PROGRAMS, 'stasis', '../lib/canopa/niri'):
            binary = system / 'bin' / name
            binary.parent.mkdir(parents=True, exist_ok=True)
            binary.write_text('test binary')
            binary.chmod(0o755)
        versions = 'canopa 0.1.0-1\ncanopa-compositor 0.1.0-1\ncanopa-login 0.1.0-1\nstasis 1.7.0-1'
        (self.state / 'dotfiles-installed-packages').write_text(
            self.installer.REVISION + '\n' + self.installer.STASIS_REVISION + '\n' + versions + '\n')
        with patch.object(self.installer, 'package_versions', return_value=versions), \
                patch.object(self.installer, 'run') as commands:
            self.assertTrue(self.installer.installed(self.state, self.root / 'config.kdl', system))
            commands.assert_called_once_with([system / 'bin/canopa', 'config', 'check', '--file', self.root / 'config.kdl'])
            (system / 'bin/canopa-polkit').unlink()
            self.assertFalse(self.installer.installed(self.state, self.root / 'config.kdl', system))
        with patch.object(self.installer, 'package_versions', return_value='changed'):
            (system / 'bin/canopa-polkit').write_text('restored binary')
            (system / 'bin/canopa-polkit').chmod(0o755)
            self.assertFalse(self.installer.installed(self.state, self.root / 'config.kdl', system))

    def test_build_only_and_failed_build_never_install_or_migrate(self):
        config = self.root / 'config/canopa/config.kdl'
        config.parent.mkdir(parents=True)
        config.write_text('schema-version 1\n')
        environment = {'XDG_CONFIG_HOME': str(self.root / 'config'),
                       'XDG_STATE_HOME': str(self.root / 'state'),
                       'XDG_CACHE_HOME': str(self.root / 'cache')}
        for failed in (False, True):
            with self.subTest(failed=failed), patch.dict(os.environ, environment), \
                    patch.object(self.installer.os, 'geteuid', return_value=1000), \
                    patch.object(self.installer.platform, 'freedesktop_os_release', return_value={'ID': 'arch'}), \
                    patch.object(self.installer.platform, 'machine', return_value='x86_64'), \
                    patch.object(self.installer, 'build_canopa', side_effect=RuntimeError('failed') if failed else None,
                                 return_value=([self.root / 'canopa.pkg'], '1.95.0')), \
                    patch.object(self.installer, 'build_stasis', return_value=[self.root / 'stasis.pkg']), \
                    patch.object(self.installer, 'run') as commands, \
                    patch.object(self.installer, 'retire_companions') as retire, \
                    patch.object(self.installer, 'configure_pinentry') as pinentry, redirect_stdout(io.StringIO()):
                if failed:
                    with self.assertRaisesRegex(RuntimeError, 'failed'):
                        self.installer.main(['--build-only'])
                else:
                    self.installer.main(['--build-only'])
                commands.assert_not_called()
                retire.assert_not_called()
                pinentry.assert_not_called()
        self.assertFalse((self.state / 'canopa/dotfiles-installed-packages').exists())

    def test_install_failure_or_active_desktop_preserves_local_binaries_and_unit_overrides(self):
        for mode in ('active', 'transaction-fails', 'success'):
            with self.subTest(mode=mode):
                root = self.root / mode
                config = root / 'config/canopa/config.kdl'
                config.parent.mkdir(parents=True)
                config.write_text('schema-version 1\n')
                binary = root / '.local/bin/canopa'
                binary.parent.mkdir(parents=True)
                binary.write_text('previous binary')
                unit = root / 'config/systemd/user/canopa-shell.service'
                unit.parent.mkdir(parents=True)
                unit.write_text('previous unit')
                environment = {'XDG_CONFIG_HOME': str(root / 'config'), 'GNUPGHOME': str(root / 'gnupg'),
                               'XDG_STATE_HOME': str(root / 'state'), 'XDG_CACHE_HOME': str(root / 'cache')}

                def execute(argv, **kwargs):
                    if argv[0] == 'sudo' and mode == 'transaction-fails':
                        raise subprocess.CalledProcessError(1, argv)
                    return subprocess.CompletedProcess(argv, 0)

                with patch.dict(os.environ, environment), \
                        patch.object(self.installer.Path, 'home', return_value=root), \
                        patch.object(self.installer.os, 'geteuid', return_value=1000), \
                        patch.object(self.installer.platform, 'freedesktop_os_release', return_value={'ID': 'arch'}), \
                        patch.object(self.installer.platform, 'machine', return_value='x86_64'), \
                        patch.object(self.installer, 'installed', return_value=False), \
                        patch.object(self.installer, 'build_canopa', return_value=([root / 'canopa.pkg'], '1.95.0')), \
                        patch.object(self.installer, 'build_stasis', return_value=[root / 'stasis.pkg']), \
                        patch.object(self.installer, 'package_versions', return_value='installed packages'), \
                        patch.object(self.installer.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0 if mode == 'active' else 3)), \
                        patch.object(self.installer, 'run', side_effect=execute) as commands, redirect_stdout(io.StringIO()):
                    if mode == 'success':
                        self.installer.main([])
                    else:
                        with self.assertRaises((RuntimeError, subprocess.CalledProcessError)):
                            self.installer.main([])
                state = root / 'state/canopa'
                if mode == 'success':
                    self.assertFalse(binary.exists())
                    self.assertFalse(unit.exists())
                    self.assertEqual(next(state.glob('companions-*/canopa')).read_text(), 'previous binary')
                    self.assertEqual(next(state.glob('units-*/canopa-shell.service')).read_text(), 'previous unit')
                    self.assertTrue((state / 'dotfiles-installed-packages').exists())
                    self.assertEqual(commands.call_args_list[-1].args[0], ['systemctl', '--user', 'daemon-reload'])
                else:
                    self.assertEqual(binary.read_text(), 'previous binary')
                    self.assertEqual(unit.read_text(), 'previous unit')
                    self.assertFalse((state / 'dotfiles-installed-packages').exists())
                    self.assertFalse((root / 'gnupg').exists())


class CanopaLogin(unittest.TestCase):
    def test_preview_does_not_write_configuration_or_select_a_display_manager(self):
        provision = load('provision-canopa-login')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, destination = root / 'packaged.toml', root / 'greetd.toml'
            source.write_text('new login\n')
            destination.write_text('existing login\n')
            with patch.object(provision, 'SOURCE', source), patch.object(provision, 'DESTINATION', destination), \
                    patch.object(provision.subprocess, 'run') as commands, \
                    patch.object(provision.shutil, 'copyfile') as copy, redirect_stdout(io.StringIO()):
                provision.main([])
            commands.assert_not_called()
            copy.assert_not_called()
            self.assertEqual(destination.read_text(), 'existing login\n')

    def test_apply_validates_first_backs_up_manager_and_does_not_restart_it(self):
        provision = load('provision-canopa-login')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, destination = root / 'packaged.toml', root / 'greetd.toml'
            source.write_text('new login\n')
            destination.write_text('existing login\n')
            manager = root / 'etc/systemd/system/display-manager.service'
            manager.parent.mkdir(parents=True)
            manager.symlink_to('/usr/lib/systemd/system/sddm.service')
            (root / 'etc/arch-release').touch()

            def isolated_path(value):
                return root / str(value).lstrip('/') if str(value).startswith(('/etc/', '/var/')) else Path(value)

            with patch.object(provision, 'SOURCE', source), patch.object(provision, 'DESTINATION', destination), \
                    patch.object(provision, 'Path', side_effect=isolated_path), \
                    patch.object(provision.os, 'geteuid', return_value=0), \
                    patch.object(provision.subprocess, 'run') as commands, redirect_stdout(io.StringIO()):
                provision.main(['--apply'])
            self.assertEqual(destination.read_text(), 'new login\n')
            backups = list((root / 'var/backups/dotfiles-canopa-login').iterdir())
            self.assertEqual((backups[0] / 'config.toml').read_text(), 'existing login\n')
            self.assertEqual((backups[0] / 'previous-display-manager').read_text(), '/usr/lib/systemd/system/sddm.service\n')
            self.assertEqual([call.args[0] for call in commands.call_args_list], [
                ['/usr/bin/canopa-greeter', '--canopa-config', '/etc/canopa/greeter.kdl', 'check-config'],
                ['systemctl', 'disable', 'sddm.service'],
                ['systemctl', 'enable', '--force', 'greetd.service']])


class CanopaPreferences(unittest.TestCase):
    def test_reapply_preserves_settings_owned_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, destination = root / 'source', root / 'home'
            destination.mkdir()
            shutil.copytree(REPO / 'home/dot_config/canopa', source)
            shutil.copytree(REPO / 'home/.chezmoitemplates', source / '.chezmoitemplates')
            shutil.copytree(REPO / 'home/.chezmoidata', source / '.chezmoidata')
            names = ('config.kdl', 'niri.kdl', 'niri-input.kdl', 'niri-displays.kdl', 'niri-custom.kdl', 'stasis.rune')
            for name in names:
                (destination / name).write_text('custom Settings preference\n')
            config = root / 'config.json'
            config.write_text('{"data":{"themeFlavour":"mocha","themeColor":"lavender"}}')
            command = ['chezmoi', '--source', str(source), '--destination', str(destination),
                       '--config', str(config), '--cache', str(root / 'cache'),
                       '--persistent-state', str(root / 'state'), 'apply']
            subprocess.run(command, check=True, capture_output=True, text=True)
            for name in names:
                self.assertEqual((destination / name).read_text(), 'custom Settings preference\n')

    def test_login_environment_reaches_activation_and_the_compositor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / 'home with spaces'
            home.mkdir()
            binary_dir = root / 'bin'
            binary_dir.mkdir()
            (home / '.profile').write_text('export PATH="$HOME/.local/bin:$PATH"\nexport SSH_AUTH_SOCK="$HOME/managed-agent.socket"\n')
            activation = binary_dir / 'dbus-update-activation-environment'
            activation.write_text('#!/bin/sh\nprintf "%s\\n" "$PATH" "$SSH_AUTH_SOCK" "$@" > "$HOME/activation"\n')
            activation.chmod(0o755)
            app = binary_dir / 'compositor'
            app.write_text('#!/bin/sh\nprintf "%s\\n" "$PATH" "$SSH_AUTH_SOCK" "$@"\n')
            app.chmod(0o755)
            environment = os.environ | {'HOME': str(home), 'PATH': str(binary_dir) + ':/usr/bin:/bin'}
            result = subprocess.run(['/bin/sh', str(REPO / 'home/dot_local/bin/executable_desktop-session'),
                                     str(app), 'literal $(no-command) argument'], env=environment,
                                    text=True, capture_output=True, check=True)
            self.assertTrue(result.stdout.startswith(str(home / '.local/bin') + ':'))
            self.assertIn(str(home / 'managed-agent.socket'), result.stdout)
            self.assertIn('literal $(no-command) argument', result.stdout)
            self.assertIn('--systemd\nPATH\n', (home / 'activation').read_text())


if __name__ == '__main__':
    unittest.main()
