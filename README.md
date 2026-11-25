# Dotfiles

Arch: niri desktop and development tools for home and work identities.

## Install

On an installed OS with Git, Python 3 and chezmoi available, install the matching
`canopa`, `canopa-compositor` and `canopa-login` packages for the default profile.
See [Canopa setup](docs/canopa.md). Then run as your normal user:

```sh
git clone https://github.com/kevinard/dotfiles.git "${XDG_DATA_HOME:-$HOME/.local/share}/chezmoi"
cd "${XDG_DATA_HOME:-$HOME/.local/share}/chezmoi"
./setup
```

Answer home/work, email and name. Hardware is detected; the defaults are Canopa,
mocha/lavender, and no GPG signing. A hybrid GPU may need one extra choice.
On a machine without a display manager, setup enables Canopa Greeter for the
next boot. Reboot and sign in to **Canopa**. If you already have a display manager,
log out and choose **Canopa** there. Use `./setup login --apply` to switch an
existing login screen to Canopa Greeter.

## Everyday use

```sh
./setup --preview     # See changes first
./setup              # Apply configuration and install/update dotfiles packages
./setup ssh          # Save the connected Solo's SSH keys (Arch)
chezmoi edit-config  # Change saved preferences
```

To update this checkout first, run `git pull --ff-only`. `./setup --customize`
asks every question on first install, or opens your saved configuration afterward.

## Only when needed

- [New disk / OS installation](docs/arch-install.md)
- [Solo keys for login and sudo](docs/hardware-auth.md)
- [Existing-install migration](docs/bootstrap.md)
- [Recovery and maintenance](docs/maintenance.md)
- [Full Canopa desktop and migration](docs/canopa.md)
- [Desktop controls, memory policy and snapshots](docs/desktop.md)
- [Opt-in process priorities for niri](docs/desktop.md#optional-process-scheduler)

`./setup --help` lists the commands. [Quick setup notes](docs/setup.md) cover the
first desktop login; [detailed reference](docs/reference/setup.md) is optional.
Disk formatting, Secure Boot and PAM activation are explicit steps. Credentials
and token mappings stay outside Git.
