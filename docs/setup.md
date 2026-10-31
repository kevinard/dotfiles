# Quick setup

Already have Arch installed? Start at step 1. For a new disk, use the
[Arch OS installer runbook](arch-install.md) first; it installs the prerequisites.

## 1. Install your configuration

From this checkout, as your normal user:

```sh
./setup
```

It asks for home/work, email and name, then installs packages, applies dotfiles
and builds Canopa on Arch. CPU, GPU and battery are detected; hybrid GPUs get an
extra choice. Defaults: Canopa, mocha/lavender, TLP on laptops, no GPG signing.

Use `./setup --preview` to inspect changes first, or `./setup --customize` to choose
everything on first install (it opens the config editor on an existing machine).
Existing machine settings are kept.
Change preferences later with `chezmoi edit-config`, then run `./setup` again.

## 2. Start a fresh session

If you want Zsh as your login shell, run `chsh -s /usr/bin/zsh`. Log out and back in.
On Arch, start `niri-session` from a TTY, or select niri in your existing greeter.
Run `desktop-health` inside niri to check the desktop services.

For a fresh installation without a greeter, SDDM with its default X11 greeter is
one option; the user session still runs on Wayland:

```sh
sudo pacman -Syu --needed xorg-server sddm
sudo systemctl enable sddm.service
```

Keep only one display manager. Do not install the optional SDDM `wayland.conf`
reference when using that default greeter path.

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
