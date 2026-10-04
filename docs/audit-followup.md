# Audit follow-up

Implemented on `codex/dotfiles-audit-fixes`, starting at `ff72702` and preserving
the cleanup already committed there. Numbers correspond to the original audit.

| Finding | Change / remaining deployment check |
| --- | --- |
| 1. Lock and sleep | niri-owned swayidle, blocking swaylock before sleep, resume monitor power, recovery lock binding; test actual suspend/resume. GNOME retains its stock locker. |
| 2. Start pages | Loopback-only servers, graphical-session lifetime, absent work checkout skipped; existing process needs next login/restart. |
| 3. Kitty permissions | Remote control disabled; clipboard reads ask permission. |
| 4. Arch recipe | Non-destructive entry point, explicit live/chroot runbook, generated fstab, consistent Btrfs root flags, corrected TPM flag; VM/recovery test remains. |
| 5. Root policies | Authenticated wheel sudo, removed broad storage grants/root hotplug execution, local-active Blueman rule; root deployment is explicit. |
| 6. Ubuntu desktop | GNOME/PaperWM profile, selected preferences at login, no Sway/SDDM/Waybar/idle-owner installation on GNOME; private PaperWM preferences need capture on laptop. |
| 7. Missing dependencies | Composed niri/shell/CPU/GPU requirements, Canopa config/units and pinned build installer, Telegram/mise/locker requirements. |
| 8. Session migration | niri startup links, graphical lifetime relationships, correct kanshi condition, native launches, daemon reload after each apply. |
| 9. Provisioning failures | Strict scripts, ordered package prerequisites, idempotent reconciliation, no unnecessary paru bootstrap or repeated battery enablement. AUR printer drivers are explicitly optional. |
| 10. Ubuntu bootstrap | Temporary isolated keyring, exact Mozilla fingerprint, supported mise PPA, structured Snap options, checked lazygit external. Ubuntu package resolution needs the laptop/VM. |
| 11. Shell startup | Portable profile, minimal zshenv, login/interactive boundaries, guarded GPG/mise/work integration; retain installed old managers pending migration. |
| 12. Portals | niri-specific GTK chooser override, GNOME screencast backend, no global GDK override; test screencast and chooser on each desktop. |
| 13. Power | Modern optional TLP example, separate native power selection, no generic forced sleep/ASPM/USB/Wi-Fi tuning; root migration and hardware measurements remain explicit. |
| 14. Monitors | kanshi owned by niri, all existing dock profiles retained; verify output identities/coordinates on hardware. |
| 15. Brightness | Serialized user helper, topology-aware bounded cache, distinct DDC display identities; removed privileged user-script hook. |
| 16. Password/clipboard | KeePassXC screen-lock/expired-credential policy, sensitive-copy filter, bounded history, actual Canopa namespace protected; verify password MIME hints/capture behavior. |
| 17. Firefox tuning | Shared intentional preferences; removed resource/GPU experiments, retired geolocation URL and tracking exceptions. Existing prefs.js needs selective resets. |
| 18. Git | Correct quoted theme path, selected flavour, explicit identity, no host-wide work HTTPS rewrite. |
| 19. Launchers | Vendor Chromium/Code entries, forwarded Chromium arguments, Mozilla Firefox MIME ID, explicit editor helper path. |
| 20. Desktop helpers | Direct argv project launches, niri logout, built-in niri screenshots; obsolete Wi-Fi/X11/Hyprland helpers removed. |
| 21. Small helpers | Mixed battery units/charger names and alert state, safe audio mute handling, decoded local file URLs, correct Thunar symlink action. |
| 22. Externals | Checksummed shell snapshots/Yubico/lazygit; one shell update owner; packaged mise; explicit rolling personal nvim exception; no root Papirus download script. |
| 23. Themes | Installed GTK/cursors, light/dark preference, all Bat flavours, shared tmux/niri/rofi palette, selected Delta flavour. |
| 24. Legacy/state | Desktop-aware ignores, narrow removals and startup-link migration; reduced Thunar geometry state. KeePassXC writable config still needs normal diff/merge care. |

Validation includes seven synthetic profiles and focused helper regressions. Niri
and Canopa configuration checks run locally when those tools are available. External
manifests parse offline; actual shell/Yubico/lazygit archives were downloaded to
record/check their hashes and layouts. Mozilla's primary fingerprint was inspected
in a temporary keyring. No system apply, package installation, service restart,
root-policy replacement or Canopa build was performed during implementation.

The offline suite and CI are not substitutes for Ubuntu package-resolution testing,
a disposable Arch install, or lock/sleep/dock/capture checks on the actual machines.
Deployment instructions and selective Firefox/root migrations are in the linked
bootstrap, maintenance and provisioning documents.
