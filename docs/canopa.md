# Canopa desktop

`desktopShell = "canopa"` uses the installed Canopa desktop and compositor.
If `canopa`, `canopa-session` and `/usr/lib/canopa/niri` are already installed,
run `./setup --preview` and then `./setup` to apply the dotfiles. Select
**Canopa** in the login manager or run `canopa-session` from a TTY. Set
`desktopShell = "waybar"` for the ordinary Niri/Waybar session.

If you already built Arch packages, install the matching `canopa` and
`canopa-compositor` package files together with `sudo pacman -U`. Include the
matching `canopa-login` or `canopa-oo7` packages if you use them. For new builds,
follow `docs/installation.md` in your Canopa checkout. Package updates use the
same process. Keep the previous matching packages for rollback.

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
Settings. Super+Alt+L locks. Navigation, brightness and audio shortcuts are in
the shared Niri bindings. Quick settings includes the wallpaper
picker, Files, Settings, keep-awake, media, sound, Wi-Fi, notification center and
session controls. Logout, reboot and shutdown require a menu confirmation.
Directories open in Canopa Files. Bluetooth opens Blueman. The Applications
launcher supports `clip`, `emoji`, `symbol` and calculations. If your
`Applications` menu still uses `source "installed-apps"`, change that line to
`source "launcher"` in `~/.config/canopa/config.kdl` to enable those features.

The packaged target starts its companions after compositor readiness. A compositor
wrapper reads the managed `.profile` and imports the desktop environment into
D-Bus/systemd, including helper paths and the managed SSH agent socket. A dotfiles
drop-in adds battery alerts when applicable and the optional
scheduler. Desktop daemons use `session.slice`; Canopa launches applications through
Niri into application scopes. Native polkit and pinentry windows float and are
excluded from captures. Exactly one shell, notification daemon, polkit agent and
idle controller should run in a session.

Setup seeds `config.kdl`, `niri.kdl`, the display, input and custom includes, and
`stasis.rune` only when they are missing. Settings owns the saved display and
input preferences. The dotfiles' initial `niri.kdl` includes the shared Niri
layout, animations, bindings, rules and startup applications. Additional device
options belong in `niri-custom.kdl`. The Waybar profile uses Kanshi, Swayidle,
Thunar and Hyprpolkitagent.

Stasis is optional. See `docs/idle.md` in the Canopa checkout if you want automatic
idle locking and suspend. The initial policy locks after
five minutes on AC, powers displays off one minute later, and suspends ten minutes
later. Battery waits are two minutes, 30 seconds and five minutes. These waits are
sequential. Change them in Settings. Canopa starts its own Stasis supervisor.
Manual locking is available with or without Stasis.

The Canopa profile leaves GnuPG and Secret Service selection to your existing
configuration. To choose Canopa pinentry, set `pinentry-program` to the absolute
path of `~/.local/bin/desktop-pinentry` in your GnuPG agent configuration. The
wrapper uses Canopa on Wayland and curses on a TTY. After editing:

```sh
gpgconf --reload gpg-agent
gpg-connect-agent updatestartuptty /bye
```

The managed OpenSSH agent remains independent of GnuPG and token enrollment.

## Existing portal overrides

Canopa's packages provide portal routing, including the optional oo7 Secret portal.
A legacy `~/.config/xdg-desktop-portal/canopa-portals.conf` still takes precedence
if it exists. Review it and move it aside to use the installed routing. Keep a
backup of any custom choices and log out of all sessions for the account so the
portal restarts with the new routing.

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
