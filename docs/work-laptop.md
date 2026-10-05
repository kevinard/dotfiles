# Ubuntu work laptop

Ubuntu 26.04 receives terminal and development configuration: Zsh, Git/Delta,
Kitty, tmux, Bat, Neovim, CLI helpers, GPG settings and terminal fonts. Its package
list is under `packages.ubuntu.common`. Neovim comes from Ubuntu's archive;
mise uses its supported PPA; lazygit is a checksummed user-level external.

The laptop owns its GNOME/PaperWM desktop, applications and power policy. Chezmoi
does not configure its browser profiles, GTK, MIME defaults, wallpapers, user
directories, launchers, portals, notifications or graphical user services. Work
identity and the optional Scalingo shell integration remain shared shell settings.
There are no desktop/hardware prompts on Ubuntu. Old `desktop`, `desktopShell`,
`hasBattery`, `cpuVendor`, `gpuVendor` and `powerManager` data are ignored there.

Ignoring a previously managed file leaves it on disk. If the old work dotfiles were
applied, inspect their changes and restore chosen GNOME/browser settings manually.
Inspect `systemctl --user list-unit-files` for the old startpage/startpage-work,
kanshi, cliphist, Waybar, Thunar and battery units; disable/stop only repository-owned
units you no longer use. Old startpage processes can still listen on the old address
until stopped. Review old TLP enablement separately. Keep backups of profiles and
credentials rather than deleting application data to reset settings.

Existing Chromium, Code, Firefox, Thunderbird and Yubico installations remain
locally owned. Check `command -v nvim` after deployment if a previous Neovim Snap
is still installed; review that migration separately. Installing the managed apt
package does not uninstall other applications or their data.

Switching to niri later can keep all terminal configuration unchanged. Add Ubuntu
desktop support when the compositor and required packages are available and the
actual desired desktop setup is known.
