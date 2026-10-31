# Bootstrap and migration

For a fresh machine, follow [installation and device setup](setup.md) and run
`./setup` after the base OS is installed. This page covers migration of existing
configurations. Arch now uses the managed SSH
agent for both `home` and `work` identities.

Review the branch diff before deploying. On Arch, log out and back in after an
apply: changing unit files does not update running processes. In particular, an
old start page keeps its old bind address until restarted or the next login.

For an existing Arch laptop, add these fields to the current `[data]` without
discarding identity/signing settings:

```toml
desktopShell = "canopa"
hasBattery = true
cpuVendor = "intel" # choose the actual CPU; use "none" for a VM/unknown vendor
gpuVendor = "intel" # choose the actual GPU; supports amd/nvidia/none too
powerManager = "tlp"
projectPaths = ["/home/kevinard/projects"]
```

Arch uses niri; `desktopShell` selects Canopa or the Waybar fallback. Legacy CPU
selection defaults to `none`, rather than guessing microcode or thermal daemons.
`chezmoi init` offers validated choices for new hardware fields on Arch only.
The former `desktop` field is no longer used on Arch.

Packages are installation requirements, not an instruction to remove every other
installed package. Arch's installer uses `pacman -Syu --needed`, including selected
CPU/GPU groups. Optional Brother AUR drivers remain documented in the package data;
build them explicitly as an ordinary user after reviewing their PKGBUILDs. No AUR
helper is installed merely to install official packages.

For a fresh Canopa installation on Arch, apply the package/configuration phase,
then run `scripts/install-canopa` from this checkout before logging into niri. It
builds the recorded Canopa commit with Cargo.lock in a disposable checkout. A local
checkout can be supplied as its argument; your development checkout is never changed.
It installs all six companion binaries and records the revision, without restarting
the desktop. An already installed revision is checked rather than rebuilt unless
you supply a local checkout. Rustup must have the pinned toolchain specified by
that project.
Canopa's own `scripts/update.sh` remains an intentional development workflow; update
the recorded revision in this repository after testing it.

On a fresh Arch installation, choose and explicitly enable a display manager
(for example SDDM), or start `niri-session` from a login TTY. Niri uses the distribution's
session integration. Cliphist, kanshi, swayidle, the chosen shell/notification owner
and the polkit agent are wanted by `niri.service` and stop with `graphical-session.target`.
The personal start page also follows that session and serves loopback only.

Arch's reconciliation script runs after every apply, reloads unit definitions, and
removes only known old enablement links. If a different target owns an extra link,
inspect `systemctl --user list-unit-files` and remove it explicitly. The
`.chezmoiremove` list removes named obsolete files on Arch and the old mise binary
on Arch so the package installation is used. It does not remove
password databases, SSH keys or Firefox profiles. Old external Git metadata may
remain beside shell files; oh-my-zsh self updates are disabled and chezmoi supplies
pinned archive contents.

A previous Dunst mask may remain when switching to Waybar. Review and run
`systemctl --user unmask dunst.service` if necessary. Keep exactly one notification
daemon; avoid starting Canopa and Dunst in the same session.

Root policy and hardware overrides are a separate Arch migration; see
[`provision/arch/README.md`](../provision/arch/README.md). The home apply cannot remove
an already installed unsafe udev or polkit rule. Choose exactly one power manager.

Optional Solo authentication is a separate enrollment and root-policy step; see
[hardware authentication](hardware-auth.md). Keep mapping files and recovery
credentials outside the repository. Test both tokens and root-password recovery
before enabling the policy on a new machine.

After Arch deployment, run `desktop-health`. Manually test lock after ten minutes,
suspend/resume, an inhibited presentation, dock unplug/replug and a portal screencast.
Swayidle waits for `swaylock -f` before sleep; verify this on the actual laptop.
