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
| Clipboard history | Super+Ctrl+V |
| Emoji and symbols | Super+Ctrl+E |
| Calculator | Super+Ctrl+Q or Calculator key |
| Audio settings | Super+Ctrl+A |
| Bluetooth | Super+Ctrl+B |
| Displays | Super+Ctrl+D |
| Do Not Disturb | Super+Ctrl+Period |
| Recover laptop display | Super+Ctrl+Shift+P |

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
