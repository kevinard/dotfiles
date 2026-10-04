# Arch installation runbook

The former `arch-install.sh` mixed live-system and chroot operations. It now only
points here. These are manual stages; do not paste them into a single unattended
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
    curl sudo base-devel reflector pacman-contrib fwupd sbctl sbsigntools
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
MAC/link example is host-specific. The dotfiles package phase later declares desktop
dependencies, including niri, swayidle and swaylock.

Exit the chroot, unmount, and reboot. **No configuration commands follow
`arch-chroot` in an executable parent script.** First verify passphrase boot and the
LTS boot path before adding Secure Boot or TPM enrollment.

## After a successful boot: Secure Boot and TPM

Follow the current Secure Boot/UKI instructions and `sbctl` documentation. Enroll
keys only with a tested firmware recovery path. Signing must cover both UKIs and
be repeated after generation; check the package hooks on your installation rather
than assuming one-time signatures are sufficient.

Enroll a recovery key and store it off-device before relying on TPM. After verifying
the actual system partition, the corrected TPM command is:

```sh
systemd-cryptenroll /dev/YOUR-LUKS-PARTITION --tpm2-device=auto --tpm2-with-pin=yes
```

Select and document an appropriate PCR policy for your Secure Boot/UKI design;
consult the installed `systemd-cryptenroll` manual. Rebuild the UKIs if their embedded
unlock configuration changes. Test unlock, recovery-key boot, the fallback kernel,
and a restore from live media before declaring the installation complete.
