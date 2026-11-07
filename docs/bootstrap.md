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
processScheduler = false # Optional; see desktop.md for activation and rollback
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

The Canopa profile uses the existing packaged desktop and compatible compositor.
The packages provide applications, lockscreen PAM policy, session entry and
portal registration. See [Canopa setup](canopa.md) for reusing a build and
reviewing older user portal overrides. Native Settings owns display, input and
idle preferences. Kanshi, Swayidle, Thunar and Hyprpolkitagent belong to the
Waybar profile.

When `processScheduler = true`, setup also builds the recorded Rust helper from
the [scheduler fork](https://github.com/kevinard/system76-scheduler-niri), using
`scripts/install-system76-scheduler-niri`. Its installer follows the same temporary
checkout and revision-marker pattern, and never changes your development checkout.
See [scheduler activation and rollback](desktop.md#optional-process-scheduler).

Select **Canopa** in an existing login manager, or run `canopa-session` from a
TTY. The packaged Canopa target starts its companions after compositor readiness.
The dotfiles add optional battery alerts and the opted-in scheduler. The ordinary
Niri/Waybar session retains its clipboard watchers and `niri.service` integration.
The personal start page follows the graphical session and serves loopback only.

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

After Arch deployment, run `desktop-health`. Manually test the configured idle lock,
suspend/resume, an inhibited presentation, dock unplug/replug and a portal screencast.
Canopa waits for compositor lock readiness before sleep; the Waybar fallback
uses Swayidle with `swaylock -f`. Verify both on the actual laptop.
