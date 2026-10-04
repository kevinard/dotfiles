# Bootstrap and migration

This branch does not apply itself. Review its diff before deploying; log out and
back in after an apply. Changing unit files on disk does not update running processes.
In particular, the old start page keeps its old bind address until restarted or
the next graphical login.

For an existing Arch laptop, add these fields to the current `[data]` without
discarding identity/signing settings:

```toml
desktop = "niri"
desktopShell = "canopa"
hasBattery = true
cpuVendor = "intel" # choose the actual CPU; use "none" for a VM/unknown vendor
gpuVendor = "intel" # choose the actual GPU; supports amd/nvidia/none too
powerManager = "tlp"
projectPaths = ["/home/kevinard/projects"]
```

For the work laptop use `desktop="gnome"`, `desktopShell="gnome"`,
`powerManager="native"`, and its actual hardware/project roots. Existing configs
default Ubuntu to GNOME and Arch to niri/Canopa. Legacy CPU selection defaults to
`none`, rather than guessing which microcode or thermal daemon to install.
`chezmoi init` offers validated new choices but asks for newly introduced fields.

Packages are installation requirements, not an instruction to remove every other
installed package. Arch's installer uses `pacman -Syu --needed`, including selected
CPU/GPU groups. Optional Brother AUR drivers remain documented in the package data;
build them explicitly as an ordinary user after reviewing their PKGBUILDs. No AUR
helper is installed merely to install official packages.

Ubuntu uses its signed archive for common tools and gh, Mozilla's repository with
an exact primary-key fingerprint check, and mise's supported Ubuntu 26.04 PPA.
Code and nvim Snap installs
use classic confinement; vendor launchers supply their executable paths. Firefox
and Thunderbird use Mozilla apt packages. Switching an existing Thunderbird Snap
installation may require migrating the old profile; retain a backup of
`~/snap/thunderbird/common/` before uninstalling it. This branch does not uninstall
Snaps. An old manual `/usr/local/bin/lazygit` is also not overwritten. Ubuntu receives
a fixed, checksummed official lazygit release under `~/.local/bin`, ahead of that
old installation in the managed PATH. The supplied release archives target amd64.

For a fresh Canopa installation, apply the package/configuration phase, then run
`scripts/install-canopa` from this checkout before logging into niri. It builds the
recorded Canopa commit with its Cargo.lock in a disposable checkout. A local Canopa
checkout can be supplied as its argument; your development checkout is never changed.
It installs all six companion binaries together and records the revision, without
restarting the desktop. Rustup must have the pinned toolchain specified by that
project. Subsequently, Canopa's own `scripts/update.sh` is an intentional development
workflow; update the recorded revision in this repository after testing it.

On Ubuntu, choosing niri installs `niri` and `xwayland-satellite` from configured apt
repositories. There is no automatic third-party compositor repository. Verify their
candidates before switching; if unavailable, keep the GNOME profile. GNOME uses its
existing display manager; the scripts do not replace GDM with SDDM.
On a fresh Arch installation, choose and explicitly enable a display manager
(for example SDDM), or start `niri-session` from a login TTY.

Niri uses the distribution's `niri-session` integration. Cliphist, kanshi, swayidle,
the chosen shell/notification owner, and the polkit agent are wanted by `niri.service`
and stop with `graphical-session.target`. GNOME retains its own clipboard, notification,
monitor, lock, and portal management. Start pages deliberately follow either graphical
session and serve loopback only. The work page is skipped if its checkout is absent.

The reconciliation script runs after every apply, reloads unit definitions, and removes only known old enablement links. If you previously
enabled a different unit under another target, inspect `systemctl --user list-unit-files`
and remove that extra link yourself. The `.chezmoiremove` list covers only named obsolete
managed files, including the old mise binary so the package installation is used.
It does not remove GNOME extension settings, password databases, SSH keys, or Firefox
profiles. Old external Git metadata may remain beside shell files; oh-my-zsh self
updates are disabled and chezmoi now supplies pinned archive contents.

The previous Dunst mask may remain when switching to the Waybar fallback. Review and
run `systemctl --user unmask dunst.service` if necessary. Keep exactly one notification
daemon. Avoid starting Canopa and Dunst in the same session.

Root policy and hardware overrides are a separate migration; see
[`provision/arch/README.md`](../provision/arch/README.md). The home apply cannot remove
an already installed unsafe udev or polkit rule. Choose exactly one power manager;
remove old TLP enablement on Ubuntu if retaining GNOME's native power manager.

After deployment, run `desktop-health`. Manually test lock after 10 minutes, suspend
and resume, an inhibited presentation, dock unplug/replug, and a portal screencast.
Swayidle waits for `swaylock -f` before sleep; verify this with the actual laptop.
GNOME enables its stock automatic locking rather than launching another locker.
