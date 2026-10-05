# Audit follow-up

Implemented on `codex/dotfiles-audit-fixes`, starting at `ff72702` and preserving
the cleanup already committed there. The scope was then narrowed: Arch owns niri,
Ubuntu work owns terminal/development settings only. Numbers correspond to the original audit.

| Finding | Change / remaining deployment check |
| --- | --- |
| 1. Lock and sleep | niri-owned swayidle, blocking swaylock before sleep, resume monitor power, recovery lock binding; test actual suspend/resume. GNOME retains its stock locker. |
| 2. Start pages | Arch loopback-only server with graphical-session lifetime; work server no longer managed; existing process needs next login/restart. |
| 3. Kitty permissions | Remote control disabled; clipboard reads ask permission. |
| 4. Arch recipe | Non-destructive entry point, explicit live/chroot runbook, generated fstab, consistent Btrfs root flags, corrected TPM flag; VM/recovery test remains. |
| 5. Root policies | Authenticated wheel sudo, removed broad storage grants/root hotplug execution, local-active Blueman rule; root deployment is explicit. |
| 6. Ubuntu desktop | Terminal-only work profile. GNOME/PaperWM, apps, hardware and power are locally owned; no desktop services or preferences deployed on Ubuntu. |
| 7. Missing dependencies | Composed niri/shell/CPU/GPU requirements, Canopa config/units and pinned build installer, Telegram/mise/locker requirements. |
| 8. Session migration | niri startup links, graphical lifetime relationships, correct kanshi condition, native launches, daemon reload after each apply. |
| 9. Provisioning failures | Strict scripts, ordered package prerequisites, idempotent reconciliation, no unnecessary paru bootstrap or repeated battery enablement. AUR printer drivers are explicitly optional. |
| 10. Ubuntu bootstrap | Terminal apt packages, supported mise PPA and checked lazygit external; removed desktop packages, Snap setup and Mozilla repository installation. Ubuntu package resolution needs the laptop/VM. |
| 11. Shell startup | Portable profile, minimal zshenv, login/interactive boundaries, guarded GPG/mise/work integration; retain installed old managers pending migration. |
| 12. Portals | niri-specific GTK chooser override, GNOME screencast backend, no global GDK override; test screencast and chooser on Arch; work portals are unmanaged. |
| 13. Power | Modern optional TLP example, separate native power selection, no generic forced sleep/ASPM/USB/Wi-Fi tuning; root migration and hardware measurements remain explicit. |
| 14. Monitors | kanshi owned by niri, all existing dock profiles retained; verify output identities/coordinates on hardware. |
| 15. Brightness | Serialized user helper, topology-aware bounded cache, distinct DDC display identities; removed privileged user-script hook. |
| 16. Password/clipboard | KeePassXC screen-lock/expired-credential policy, sensitive-copy filter, bounded history, actual Canopa namespace protected; verify password MIME hints/capture behavior. |
| 17. Firefox tuning | Arch personal preferences; work profiles no longer managed; removed resource/GPU experiments, retired geolocation URL and tracking exceptions. Existing prefs.js needs selective resets. |
| 18. Git | Correct quoted theme path, selected flavour, explicit identity, no host-wide work HTTPS rewrite. |
| 19. Launchers | Removed manual Chromium/Code entries and obsolete work wrappers; Arch uses vendor launchers and an explicit editor helper path. Work MIME defaults are unmanaged. |
| 20. Desktop helpers | Direct argv project launches, niri logout, built-in niri screenshots; obsolete Wi-Fi/X11/Hyprland helpers removed. |
| 21. Small helpers | Mixed battery units/charger names and alert state, safe audio mute handling, decoded local file URLs, correct Thunar symlink action. |
| 22. Externals | Checksummed shell snapshots/lazygit; work Yubico install unmanaged; one shell update owner; packaged mise; explicit rolling personal nvim exception; no root Papirus download script. |
| 23. Themes | Installed GTK/cursors, light/dark preference, all Bat flavours, shared tmux/niri/rofi palette, selected Delta flavour. |
| 24. Legacy/state | Desktop-aware ignores, narrow removals and startup-link migration; reduced Thunar geometry state. KeePassXC writable config still needs normal diff/merge care. |

Validation includes six synthetic profiles and focused helper regressions. The work
profile is checked against its complete allowed target set, including stale Ubuntu
desktop fields; fresh Ubuntu init produces no desktop/hardware fields. Niri and
Canopa checks run locally when available. External manifests parse offline; retained
shell/lazygit archives were downloaded to check hashes and layouts. No system apply,
package install, service restart, root-policy replacement or Canopa build was performed.

The offline suite and CI are not substitutes for Ubuntu package-resolution testing,
a disposable Arch install, or lock/sleep/dock/capture checks on the actual machines.
Deployment instructions and selective Firefox/root migrations are in the linked
bootstrap, maintenance and provisioning documents.
