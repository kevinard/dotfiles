# Desktop controls and recovery

Run `./setup` to install the home configuration and desktop dependencies, then log
out and back in. `Super+Space` opens the shared desktop controls menu in either
shell. Canopa opens its native Quick settings panel; the Waybar fallback uses Rofi.
Canopa's launcher also exposes individual tools. No OCR action or Omarchy
software bundle is added.

| Control | Shortcut |
| --- | --- |
| Canopa applications | Super+D |
| Canopa Files | Super+E |
| Canopa Settings | Super+Ctrl+Comma |
| Waybar clipboard history | Super+Ctrl+V |
| Waybar emoji and symbols | Super+Ctrl+E |
| Waybar calculator | Super+Ctrl+Q or Calculator key |
| Audio settings | Super+Ctrl+A |
| Bluetooth | Super+Ctrl+B |
| Displays | Super+Ctrl+D |
| Do Not Disturb | Super+Ctrl+Period |
| Recover laptop display | Super+Ctrl+Shift+P |

In Canopa, open Applications and enter `clip` for clipboard history, `emoji` or
`symbol` for characters, or a calculation. The Calculator key also opens
Applications. Clipboard recording can be enabled in Canopa Settings.

Brightness keys adjust the focused display: laptop backlight or connector-matched
DDC/CI. Shift adjusts all active displays; Alt uses 1% steps. Ordinary steps are
5%, reduced to 1% near minimum, with a visible minimum. Coarse backlights use at
least one hardware step per adjustment. External monitors need
DDC/CI enabled in their own menus and the existing user DDC access configuration.
An unsupported external display never falls back to dimming the laptop. Feedback
banners show the resulting level. `brightness-control clear` invalidates the
topology cache manually.

Volume keys use 5% steps; Alt uses 1%. Shift+Mute cycles available physical outputs
and moves application streams, leaving DSP/EasyEffects routing alone.

Do Not Disturb can be toggled from the desktop menu or its shortcut. The existing
Waybar idle-only inhibitor remains available separately.

The font aliases in `home/dot_config/fontconfig/fonts.conf` map `system-ui` to
Inter and `ui-monospace` to the existing monospace preferences, headed by Atkinson
Hyperlegible Mono. Existing serif, sans-serif and monospace selections are retained.

Niri already handles the internal panel when the lid opens/closes. Canopa Settings
owns its saved monitor/input includes; the Waybar fallback retains Kanshi dock layouts. No competing lid daemon is introduced. The recovery
shortcut enables the internal connector, powers displays on, reloads Kanshi in the Waybar session and
invalidates the DDC cache. It does not rewrite monitor configuration.

## System policy

Root changes are an explicit stage, separate from a home apply:

```sh
./setup system --snapshots              # Preview all root changes
./setup system --apply --snapshots      # Apply after a fresh desktop login
```

Omit `--snapshots` for memory and boot policy alone. This performs a full Arch
package upgrade, installs the named root files with backups under
`/var/backups/dotfiles-desktop`, and enables services for the next boot. Reboot to
activate system policy; it does not reset active swap or force live sysctls.

Memory policy uses zstd zram with logical capacity equal to RAM, priority 100 ahead
of disk swap, swappiness 100, and one-page swap-in reads. Zram allocates RAM as
needed; this is not additional physical memory. Zswap is disabled at boot to
avoid double compression. Dirty-page limits are 64/256 MiB with a 15-second
writeback interval. Existing disk swap remains available for hibernation.

Systemd-oomd targets application scopes under sustained pressure. The compositor,
locker, idle daemon, shell, notifications and related desktop services belong in
`session.slice`; application launches use `app.slice`. Apply home units and start
a fresh session before enabling the policy. After reboot, run `desktop-health`,
`systemd-cgls --user-unit app.slice session.slice`, `oomctl` and `zramctl`. Confirm
actual scope placement, including Canopa-launched applications. One application
may be terminated to preserve responsiveness.

Canopa's lock listener coordinates compositor lock readiness with logind; its
Stasis supervisor owns automatic idle policy. Both use the protected session slice.
The Waybar fallback uses Swayidle and Swaylock. Manual Canopa locking waits for
readiness through the listener; fallback locking uses a protected scope.

The networkd wait-online drop-in keeps the existing `--any` policy and adds
`--timeout=10`. When offline, that wait fails after ten seconds instead of waiting
for the default two minutes. It is installed by `./setup system --apply` and takes
effect at the next boot; no network manager is replaced or wait service masked.
This bounds the networkd wait, not the whole boot. Services that need a particular
network must still handle that dependency. See the
[wait-online manual](https://www.freedesktop.org/software/systemd/man/latest/systemd-networkd-wait-online.service.html).

TLP, portal selection and hardware power workarounds retain their existing
policies. File-watch/open-file limits require an observed problem before changing
them; the root stage does not change these limits.

## Optional process scheduler

System76 Scheduler is off by default. To opt in, set `processScheduler = true`
under `[data]` in `chezmoi edit-config`, then run:

```sh
./setup                       # Install the package and build the Rust helper
./setup scheduler             # Preview scheduler policy only
./setup scheduler --apply     # Back up root configuration and enable the daemon
```

Reboot, then run `desktop-health` inside niri. This stage is independent of
`./setup system`: it does not install memory, boot or snapshot policy. It performs
a full Arch package upgrade and installs `/etc/system76-scheduler/config.kdl` and
`/etc/system76-scheduler/process-scheduler/pop_os.kdl`, with replaced files backed
up under `/var/backups/dotfiles-scheduler`. Review any additional local scheduler
rules before enabling; they are still loaded. The root daemon applies to the
whole machine, including other users. No helper runs as root.

The policy adjusts process priorities only; legacy CFS latency tuning and
execsnoop/BPF monitoring are disabled. TLP retains power management. Niri,
Xwayland Satellite, the Canopa shell/providers/notifications and the Waybar
fallback use nice -3. Focused applications use nice 0, background applications
nice 4, language servers such as `rust-analyzer` and `clangd` nice 0, and named
compilers/build tools nice 5. These use normal `SCHED_OTHER` scheduling and
best-effort I/O; development tools never use `SCHED_IDLE` or idle I/O.
Explicit wrapper choices (`nice`, `ionice`, `chrt`, `gamemoderun`, etc.) are exempt.

The patched [Rust helper fork](https://github.com/kevinard/system76-scheduler-niri)
handles the initial window snapshot, new/changed/closed windows and focus changes.
Missing window information or PID clears the previous application's preference.
It uses one blocking event loop; stream or D-Bus errors exit with failure so
systemd can restart it. Its lifetime follows the Niri graphical session. If only
the scheduler daemon restarts while focus stays unchanged, resend the selection
with `systemctl --user restart system76-scheduler-niri.service`.
`scripts/install-system76-scheduler-niri` builds commit
`f2fa09c8ae9fd8d8851015699d5cd44957c2b167` with Cargo.lock and the configured
Rust toolchain, then installs the binary atomically in `~/.local/bin`. Repeated
setup skips an already installed revision. An optional local-checkout argument
avoids downloading the fork, while still building that same pinned commit.
It replaces the earlier Python helper at that path. `--skip-desktop-build` leaves
the helper build for an explicit installer run. The IPC API is pinned to Niri
26.04; review that dependency and run the fork's tests when updating Niri.

Inspect `journalctl --user -u system76-scheduler-niri.service -b` and
`journalctl -u com.system76.Scheduler.service -b`. While switching between a browser
and editor during the same parallel build, check `ps -eo pid,ni,cls,comm` and
`ionice -p PID` for representative processes. Compare input/animation smoothness,
editor assistance, audio and build duration with the scheduler disabled. Terminal
multiplexers, shared browser processes and containers can have process trees that
do not map cleanly to a single focused window; verify the workloads you use.

To opt out, set `processScheduler = false`, run `./setup`, then
`./setup scheduler` and `./setup scheduler --apply`. The latter stops/disables
the system daemon and stops the user helper; packages and configuration files are
kept. Reboot to reset inherited process priorities and the kernel autogroup
setting. A home apply alone removes the managed session enablement link; it does
not stop a running helper or disable root policy.

## Snapshots and UKI recovery

The snapshot option requires Btrfs root, a separately mounted Btrfs `/.snapshots`
on the same filesystem, and a FAT ESP at `/efi` with UKIs in `/efi/EFI/Linux`.
This matches the installation runbook. Existing custom Snapper policy or snap-pac
hooks require reconciliation before provisioning; they are not overwritten.

The package hook creates a single root snapshot before package install, upgrade or
removal. It copies corresponding UKIs to `/.snapshots/.boot/NUMBER`, records
SHA-256 checksums, then keeps five numbered root snapshots. Home is excluded.
The hook aborts the package transaction if a paired checkpoint cannot be created.
An unavailable ESP therefore needs mounting before updating. The initial package
upgrade that installs this feature occurs before its hook is installed.
The installer creates and verifies an initial paired checkpoint before activating
the hook. Failed initial setup leaves a new hook inactive so it can be retried;
an already installed hook is retained until its replacement is ready.

```sh
sudo /usr/local/libexec/dotfiles-snapshot list
sudo /usr/local/libexec/dotfiles-snapshot verify NUMBER
```

These are recovery checkpoints, not independent backups. They do not add a boot
menu or change firmware entries. Test this offline recovery on a disposable
installation before relying on it:

1. Boot live media, open the existing LUKS container, and mount the Btrfs top level
   (`subvolid=5`) at a recovery mountpoint. Identify the actual root and snapshot
   subvolumes. The documented layout uses `@` and `@snapshots`.
2. Select a paired snapshot. Create a **writable snapshot** of
   `@snapshots/NUMBER/snapshot` under a new name at the top level. Preserve the
   current `@` under another name, then rename the new writable snapshot to `@`.
   Keep the preserved root until recovery is verified; do not delete it.
3. Mount restored `@` at `/mnt/root`, its `@snapshots` at
   `/mnt/root/.snapshots`, and the verified ESP at `/mnt/root/efi`.
4. Restore matching, already-signed UKIs using the helper from the restored root
   (or this checkout):

   ```sh
   python3 /mnt/root/usr/local/libexec/dotfiles-snapshot restore-uki NUMBER \
       --snapshots /mnt/root/.snapshots --esp /mnt/root/efi
   ```

   All checksums are verified before writing an image. Current images are kept
   under `.boot/before-restore-*`, and replacements use temporary files on the
   ESP. The helper never replaces the root subvolume itself.
5. Confirm expected UKI paths, restored kernel modules, fstab/subvolume settings
   and firmware entries before unmounting and rebooting. Home/application data
   remain at newer versions; account for application data migrations. Verify both
   normal and LTS boots before retiring the preserved root.

See [Canopa session setup and recovery](canopa.md) for native desktop components.

After deployment, check focused/external brightness, headphone switching during
playback, offline boot timing, suspend locking and dock hotplug.
The offline suite tests routing and failure handling; it does not exercise
physical monitors, real memory exhaustion or boot recovery.
