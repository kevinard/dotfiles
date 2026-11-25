# Quick setup

Already have Arch installed? Start at step 1. For a new disk, use the
[Arch OS installer runbook](arch-install.md) first; it installs the prerequisites.

## 1. Install your configuration

Install the matching `canopa`, `canopa-compositor` and `canopa-login` packages
for the default Canopa profile with its graphical login. See [Canopa setup](canopa.md).

From this checkout, as your normal user:

```sh
./setup
```

It asks for home/work, email and name, then installs dotfiles packages and
applies configuration. CPU, GPU and battery are detected; hybrid GPUs get an
extra choice. Defaults are Canopa, mocha/lavender, TLP on laptops and no GPG signing.

Use `./setup --preview` to inspect changes first, or `./setup --customize` to choose
everything on first install (it opens the config editor on an existing machine).
Existing machine settings are kept.
Change preferences later with `chezmoi edit-config`, then run `./setup` again.

## 2. Start a fresh session

If setup enabled Canopa Greeter, reboot and sign in to **Canopa**. On a machine
with an existing display manager, log out and select **Canopa** there. The Canopa
session starts the compositor and shell. Run `desktop-health` inside Canopa to
check its services. Waybar users select the ordinary Niri session or run
`niri-session` from a TTY. To use Zsh as your login shell, run `chsh -s /usr/bin/zsh`.

Preview the configuration before switching an existing display manager to Canopa Greeter.

```sh
./setup login             # Preview greetd configuration
./setup login --apply     # Back up the old configuration; select greetd for next boot
```

Reboot afterward. From a TTY, `canopa-session` is available for recovery.
See [the full Canopa guide](canopa.md) for migration, upgrades and rollback.

## 3. Connect your accounts

For SSH on Arch, plug in one Solo and run `./setup ssh`, then repeat with the other.
It saves the tokens' resident keys in `~/.ssh` (PIN once per machine); afterwards
each connection needs only a touch. Test with `ssh -T git@github.com`.

Sign into your password manager and VPN, restore your files, and connect your
backup destination. These accounts and secrets are never copied into Git.
Test a backup restore before retiring the old device.

Optional hardware login/sudo: [short activation guide](hardware-auth.md).
For boot security, offline-access checks and device retirement, see the
[detailed reference](reference/setup.md). Routine use needs only the README.
