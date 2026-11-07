# Arch installation runbook

Start with [quick setup](setup.md) for the post-install steps. The optional
[device lifecycle reference](reference/setup.md) covers preparation and retirement.
This document covers the OS/boot phase only. The working baseline uses a LUKS
passphrase; TPM unlock is a separate, policy-dependent extension.

The former `arch-install.sh` mixed live-system and chroot operations. It now only
points to the setup guides. These are manual stages; do not paste them into a single unattended
script. Follow the current [Arch installation guide](https://wiki.archlinux.org/title/Installation_guide)
for live-media/network setup and disk partitioning. Verify the disk by model, serial
and size before any formatting. Test this layout in a disposable VM first.

## Live system: partition and mount

Choose a GPT EFI system partition (at least 1 GiB) and a Linux LUKS2 partition.
Format the ESP as FAT32, initialize/open LUKS as `root`, and create Btrfs on
`/dev/mapper/root`. Those destructive operations are deliberately manual, against
the partitions you have identified. Keep a passphrase/recovery method independent
of TPM unlock.

After opening and formatting the intended volume:

```sh
set -eu
mount --mkdir /dev/mapper/root /mnt
for subvolume in @ @home @snapshots @var_log @swap; do
    btrfs subvolume create "/mnt/$subvolume"
done
umount /mnt
mount --mkdir -o noatime,compress=zstd,subvol=@ /dev/mapper/root /mnt
mount --mkdir -o noatime,compress=zstd,subvol=@home /dev/mapper/root /mnt/home
mount --mkdir -o noatime,compress=zstd,subvol=@snapshots /dev/mapper/root /mnt/.snapshots
mount --mkdir -o noatime,compress=zstd,subvol=@var_log /dev/mapper/root /mnt/var/log
mount --mkdir -o noatime,subvol=@swap /dev/mapper/root /mnt/swap
```

Mount your verified ESP at `/mnt/efi`, using its actual partition path. If desired,
create a Btrfs swapfile inside `@swap` with `btrfs filesystem mkswapfile`; select a
size for your RAM/workload. Hibernation additionally needs supported resume parameters
and a tested Btrfs resume offset; a small swapfile alone does not configure hibernation.

```sh
pacstrap -K /mnt base linux linux-lts linux-firmware btrfs-progs mkinitcpio \
    iwd systemd-resolvconf efibootmgr systemd-ukify plymouth git chezmoi \
    curl sudo python openssh base-devel reflector pacman-contrib fwupd sbctl sbsigntools
genfstab -U /mnt > /mnt/etc/fstab
cat /mnt/etc/fstab
findmnt -R /mnt
```

Confirm every mounted subvolume and the ESP appear in fstab. Never copy a generic
fstab over this file. Install the matching CPU microcode package before generating
initramfs. Decide whether this machine uses iwd/networkd or another network manager.

Now enter the chroot **interactively**:

```sh
arch-chroot /mnt
```

## Inside the chroot: configure the installed system

Run this stage only at the chroot prompt. Obtain this repository inside the installed
system. Review root files individually under `provision/arch/etc`; do not copy the
entire directory. Set timezone, locales, hostname, root/user passwords and wheel
membership according to the Arch guide. Validate the wheel sudoers candidate with
`visudo` before installation.

For a typical new machine, install the appropriate `intel-ucode` or `amd-ucode`
package, set `/etc/hostname`, configure `/etc/locale.gen` and run `locale-gen`.
Set `/etc/localtime` (for example Europe/Paris), run `hwclock --systohc`, and set
console keymap in `/etc/vconsole.conf` if needed before generating UKIs. Create
the normal account with a home and wheel membership, set its password, and set a
separate root recovery password. These values belong to this machine.

Validate `provision/arch/etc/sudoers.d/local` with `visudo -cf`, then install it as
`/etc/sudoers.d/local`, root-owned mode 0440. Do not enable passwordless sudo.

For the iwd + networkd option, review/install the generic `20-wired.network` and
`25-wireless.network` references, not the host-specific `.link` file. Let networkd
manage addresses; do not also enable iwd's built-in IP configuration or another
network manager. Enable `iwd`, `systemd-networkd`, `systemd-resolved` and
`systemd-timesyncd`. Point `/etc/resolv.conf` at
`/run/systemd/resolve/stub-resolv.conf`. Join Wi-Fi with `iwctl` after boot and
check `resolvectl query github.com` and clock synchronization before bootstrap.
Leave optional DNSSEC/DoT overrides uninstalled until the upstream DNS path is
tested; a browser working does not prove system DNS works.

Use the installed system's current mkinitcpio defaults as the base. For encrypted
root use systemd-based hooks, including `sd-encrypt` before `filesystems`; the
reference primary/fallback configurations illustrate this. Keep automatic GPU
discovery unless a measured hardware issue requires an override. Install the
primary/LTS preset files explicitly if adopting the UKI paths in this repository.

Generate `/etc/kernel/cmdline` using the **UUID of the LUKS container**, not the
filesystem UUID. Substitute the verified UUID manually:

```text
rd.luks.name=YOUR-LUKS-UUID=root root=/dev/mapper/root rootflags=subvol=@ rw
```

Add only desired boot options. The explicit `rootflags=subvol=@` agrees with the
mounted root and generated fstab. Do not copy the former `root=gpt-auto` recipe
without understanding its partition-discovery requirements. Build both UKIs:

```sh
mkdir -p /efi/EFI/Linux
mkinitcpio -P
ls -l /efi/EFI/Linux
```

Create firmware boot entries with `efibootmgr` for the verified disk and ESP index,
pointing to `\EFI\Linux\arch-linux.efi` and
`\EFI\Linux\arch-linux-lts-fallback.efi`. Confirm both paths exist. The fallback
uses the same tested kernel command line and encryption/root layout.

Enable the network/time/mirror/cache services that match your chosen setup. If using
iwd + networkd, install only the relevant reviewed `.network` files; the checked-in
MAC/link example is host-specific. Install Canopa from its packages for the default
profile. The dotfiles package phase installs Niri, Swayidle and Swaylock for the
Waybar profile.

Exit the chroot, unmount, and reboot. **No configuration commands follow
`arch-chroot` in an executable parent script.** First verify passphrase boot and the
LTS boot path before adding Secure Boot or TPM enrollment.

## After a successful boot: Secure Boot and TPM

Follow the current Secure Boot/UKI instructions and `sbctl` documentation. Enroll
keys only with a tested firmware recovery path. Signing must cover both UKIs and
be repeated after generation; check the package hooks on your installation rather
than assuming one-time signatures are sufficient.

Use `sbctl status` to inspect firmware state. In firmware Setup Mode, create and
enroll your own keys following the current sbctl guidance. Decide explicitly
whether Microsoft/vendor certificates must be retained for option ROMs or other
operating systems; do not erase firmware trust material blindly. Register both
UKIs for signing with `sbctl sign --save`, using their actual paths. Check `sbctl
verify`, rebuild with `mkinitcpio -P`, and verify again to test the installed signing
hooks before enabling Secure Boot in firmware. Reboot and confirm enabled state
and both boot entries. See [UKI guidance](https://wiki.archlinux.org/title/Unified_kernel_image)
and [sbctl](https://man.archlinux.org/man/sbctl.8.en).

Enroll a LUKS recovery key and store it off-device before relying on TPM. Keep
passphrase boot until an explicit TPM2 + PIN policy is configured for the full
Secure Boot/UKI design. A bare enrollment command with default PCR selection is
not a complete policy. Follow [current TPM guidance](https://wiki.archlinux.org/title/Trusted_Platform_Module)
and the installed `systemd-cryptenroll` manual for signed PCR/boot-phase policy and
volume binding. Configure matching initramfs unlock options and rebuild both UKIs.
Test unlock, recovery-key boot, the fallback kernel, a kernel upgrade and restore
from live media before declaring that extension complete. The setup helper does
not enroll TPM or firmware trust automatically.
