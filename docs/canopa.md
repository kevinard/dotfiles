# Canopa desktop

`desktopShell = "canopa"` now selects the complete Canopa session. Run `./setup`
from an ordinary-user TTY for initial migration or a desktop upgrade, then select
**Canopa** in the login manager. An ordinary TTY can also run `canopa-session`.
An already-installed revision is checked without rebuilding. Waybar remains
available through `desktopShell = "waybar"` and the ordinary Niri login entry.

The installation includes Shell, Notify, Files, Settings, the Wi-Fi/audio/media
providers, wallpaper, lockscreen, the logind lock listener, idle supervisor,
polkit dialogs, GnuPG pinentry, the appearance portal and the optional greeter.
Canopa's compatible Niri lives at `/usr/lib/canopa/niri`; `/usr/bin/niri` and its
ordinary login entry remain available. System packages own the executables,
services, launcher entries, file-manager activation, portal registration and
`/etc/pam.d/canopa-lock`. That lock policy includes Arch's existing `system-auth`;
it does not enroll a token or change login/sudo authentication.

## Session and controls

The shell uses Canopa's spine layout, native icons and quick settings, with the
chosen Catppuccin accent and Inter typography. Super+D opens applications,
Super+Space opens Quick settings, Super+E opens Files, and Super+Ctrl+Comma opens
Settings. Super+Alt+L locks. Existing navigation, clipboard, calculator,
brightness and audio shortcuts remain. Quick settings includes the wallpaper
picker, Files, Settings, keep-awake, media, sound, Wi-Fi, notification center and
session controls. Logout, reboot and shutdown require a menu confirmation.
Directories open in Canopa Files. Bluetooth still opens Blueman; clipboard,
emoji and calculator tools retain their existing shortcuts.

The packaged target starts its companions after compositor readiness. A compositor
wrapper reads the managed `.profile` and imports the desktop environment into
D-Bus/systemd, including helper paths and the managed SSH agent socket. A dotfiles
drop-in adds clipboard watchers, battery alerts when applicable, and the optional
scheduler. Desktop daemons use `session.slice`; Canopa launches applications through
Niri into application scopes. Native polkit and pinentry windows float and are
excluded from captures. Exactly one shell, notification daemon, polkit agent and
idle controller should run in a session.

Canopa uses its own `~/.config/canopa/niri.kdl`, including the established Niri
layout, animations, bindings, rules and startup applications. Settings owns
`niri-input.kdl` and `niri-displays.kdl`; extra device options live in
`niri-custom.kdl`. These three files and `stasis.rune` are initialized only when
missing, so subsequent applies retain Settings edits. Canopa does not run Kanshi:
use Settings to save display layouts. The Waybar session retains Kanshi, Swayidle,
Thunar's daemon and Hyprpolkitagent.

The shared `config.kdl` is a managed dotfile. Personalization changes made in
Settings are live, but review/import them into the source before the next apply
with `chezmoi merge ~/.config/canopa/config.kdl`. Keep runtime wallpaper assignments
in their native state file rather than adding that state to Git. Put wallpaper
images in `~/Pictures/Wallpapers`, then choose them in Quick settings or Settings.
The initial wallpaper is a solid theme background.

Stasis is pinned to the Canopa-tested 1.7.0 commit. The initial policy locks after
five minutes on AC, powers displays off one minute later, and suspends ten minutes
later. Battery waits are two minutes, 30 seconds and five minutes. These waits are
sequential. Change them in Settings. The Quick settings keep-awake control uses
this same backend. Do not enable an additional `stasis.service`. The lock listener
coordinates external logind sleep requests and waits for compositor lock readiness.

GnuPG's existing agent configuration is backed up and only its `pinentry-program`
setting is replaced with `~/.local/bin/desktop-pinentry`. The wrapper uses native
Canopa dialogs on Wayland and curses on a TTY. After the next graphical login:

```sh
gpgconf --reload gpg-agent
gpg-connect-agent updatestartuptty /bye
```

The managed OpenSSH agent remains independent of GnuPG and token enrollment.

## Builds and migration

`scripts/install-canopa` builds commit
`887ec8ae8e19087e965e5c18b49016398edec8fe` and Stasis commit
`d84e75e22cc00329712fb1caa83445d2f12ce921`. Clean temporary clones exclude changes
in development checkouts. Both application builds use their Cargo.lock; the
Canopa package recipe also verifies the pinned Niri/Smithay sources and patch.
Build dependencies come from the composed Arch package list, with Rust 1.95.0
required by the recorded Canopa toolchain. Build jobs default to one.

The installer creates checksummed Arch source packages, builds without root, and
uses `sudo pacman -U --needed` only after all packages and configuration validation
succeed. Each Canopa revision gets a timestamped package release so pacman does not
mistake a new development commit for an already-installed version. Build caches
and package artifacts remain under `~/.cache/dotfiles/canopa/` (or XDG_CACHE_HOME).
To inspect/build without installing or migrating:

```sh
scripts/install-canopa --build-only
# Optional local sources; still build only the pinned committed revisions:
scripts/install-canopa ~/Projects/canopa --stasis-source /path/to/stasis --build-only
```

After successful package installation, previous local Canopa unit overrides are
saved in `units-*` backups so the packaged units can load. Then colliding `~/.local/bin/canopa*`
executables are moved into unique `companions-*` backups under
`~/.local/state/canopa/`; unrelated tools are retained. GnuPG backups are alongside
those directories. A failed build or package transaction never retires local
executables. Configuration changes from the preceding chezmoi apply remain on
failure; rerun setup from the TTY after resolving the failed stage. No build
restarts the desktop. Installation refuses to replace an active Canopa Shell.

## Login screen

The `canopa-login` package supplies a dedicated unprivileged greeter account,
Cage integration, administrator-owned presentation and a greetd example.
Installation alone does not select greetd. Use:

```sh
./setup login
./setup login --apply
```

The apply step validates `/etc/canopa/greeter.kdl`, backs up the previous greetd
configuration and display-manager link under `/var/backups/dotfiles-canopa-login/`,
disables the previous manager's boot enablement and enables greetd for the next boot. It leaves the running display manager and
session alone. Reboot to activate it. Greetd retains its distribution PAM policy;
only its frontend changes. Edit `/etc/canopa/greeter.kdl` as administrator for
login-screen appearance. No personal files or credentials are installed there.

To restore an earlier manager, use a TTY, restore the saved greetd config if
needed, disable greetd, and enable the manager recorded in
`previous-display-manager` with `systemctl enable --force NAME.service`. Reboot.
If no manager was previously configured, leave greetd disabled and use TTY login.

## Validation and recovery

Run `desktop-health` inside Canopa, inspect
`journalctl --user -u canopa-compositor -u canopa-shell -u canopa-lock`, and run
`canopa config check` and `canopa-settings check`. Test multi-monitor lock/unlock,
external `loginctl lock-session`, suspend/resume, dock hotplug, authorization,
a GnuPG prompt, file opening and portal screencasting on the actual machine.

For a session configuration failure, preserve the affected include and restore
it from the source or a known working copy. `canopa-settings init-session` recreates
missing preference files without replacing existing ones. The ordinary Niri
session and TTY remain recovery routes. A crashed locker does not unlock a session.
For package rollback, retain/install the previous matching Canopa desktop and
compositor packages with `pacman -U`; restore compatible state/configuration from
backups as necessary. Selecting Waybar in chezmoi and reapplying selects the fallback
services for the next ordinary Niri login; it does not uninstall Canopa packages or
undo the separately selected login manager.

The offline dotfiles suite validates rendered profiles and migration boundaries.
It does not install packages, change display managers, authenticate host users,
or establish physical suspend/VT behavior.
