# Quick setup

Already have Arch installed? Start at step 1. For a new disk, use the
[Arch OS installer runbook](arch-install.md) first; it installs the prerequisites.

## 1. Install your configuration

From this checkout, as your normal user:

```sh
./setup
```

It asks for home/work, email and name, then installs packages, applies dotfiles
and builds/installs the full Canopa desktop and compatible compositor as Arch
packages. CPU, GPU and battery are detected; hybrid GPUs get an extra choice. Defaults: Canopa, mocha/lavender, TLP on laptops, no GPG signing.

Use `./setup --preview` to inspect changes first, or `./setup --customize` to choose
everything on first install (it opens the config editor on an existing machine).
Existing machine settings are kept.
Change preferences later with `chezmoi edit-config`, then run `./setup` again.

## 2. Start a fresh session

If you want Zsh as your login shell, run `chsh -s /usr/bin/zsh`. Log out and back in.
Select **Canopa** in your existing greeter, or run `canopa-session` from a TTY.
Run `desktop-health` inside Canopa to check its services. Waybar users select the
ordinary Niri session or run `niri-session` instead.

For the Canopa login screen:

```sh
./setup login             # Preview greetd configuration
./setup login --apply     # Back up the old configuration; select greetd for next boot
```

Reboot afterward. The current desktop and display manager keep running until then.
See [the full Canopa guide](canopa.md) for migration, upgrades and rollback.

## 3. Connect your accounts

For SSH on Arch, plug in either Solo and run `./setup ssh`, then test
`ssh -T git@github.com`. Your login session uses the managed SSH agent; if running
before logging in again, follow the helper's environment instruction.

Sign into your password manager and VPN, restore your files, and connect your
backup destination. These accounts and secrets are never copied into Git.
Test a backup restore before retiring the old device.

Optional hardware login/sudo: [short activation guide](hardware-auth.md).
For boot security, offline-access checks and device retirement, see the
[detailed reference](reference/setup.md). Routine use needs only the README.
