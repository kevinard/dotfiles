# Install Arch on an encrypted Btrfs disk

This installs Arch on one x86-64 UEFI disk with LUKS2, Btrfs, iwd + systemd-networkd, and two
unified kernel images (UKIs), one for `linux` and one for `linux-lts`. On the XPS 13 9315,
use the Intel microcode package. The commands use Bash. Run the live USB, chroot, and installed-system
sections at their respective prompts.

**This layout replaces the partition table on the selected drive.** Back up anything you need
from it first. For a machine that keeps Windows, use a dual-boot layout and save the BitLocker
recovery key before changing firmware settings. If CPS will manage the root from the start, read
the [CPS layout notes](#if-cps-will-manage-the-root) before creating subvolumes.

## 1. Make and boot the live USB

On an existing Linux machine, open Bash and download the ISO into a fresh directory.

```bash
mkdir -p ~/arch-usb
cd ~/arch-usb
mirror=https://geo.mirror.pkgbuild.com/iso/latest
curl -fLO "$mirror/archlinux-x86_64.iso" &&
    curl -fLO "$mirror/sha256sums.txt" &&
    awk '$2 == "archlinux-x86_64.iso"' sha256sums.txt | sha256sum --check -
```

Check for `archlinux-x86_64.iso: OK`. Verify the release signature with GnuPG and compare the signing key fingerprint with the one published by Arch. [Arch download page](https://archlinux.org/download/)

```bash
curl -fLO "$mirror/archlinux-x86_64.iso.sig" &&
    gpg --auto-key-locate clear,wkd --locate-external-key pierre@archlinux.org &&
    gpg --verify archlinux-x86_64.iso.sig archlinux-x86_64.iso
```

Unmount any mounted partitions on the USB stick. Enter the USB **whole-disk** path, such as
`/dev/sdb`. This overwrites the stick.

```bash
lsblk -d -o PATH,SIZE,MODEL,SERIAL,TRAN,TYPE
read -r -p 'USB whole-disk path: ' usb
lsblk -o PATH,SIZE,MODEL,SERIAL,TRAN,TYPE,MOUNTPOINTS "$usb"
```

Once you have checked the model, size, and mounts, write the image.

```bash
test "$(lsblk -dnro TYPE "$usb")" = disk &&
    sudo dd if=archlinux-x86_64.iso of="$usb" bs=4M status=progress conv=fsync
```

On the XPS, **F2** opens firmware setup and **F12** opens the boot menu. Temporarily disable
Secure Boot to start the official Arch USB, then select its UEFI entry. At the live prompt, run
`bash`. In the Bash shell, set the console layout you want for the disk passphrase and check for
64-bit UEFI mode.

```bash
keymap=us                         # use fr for a French AZERTY console
loadkeys "$keymap"
cat /sys/firmware/efi/fw_platform_size  # should print 64
ip -brief link
```

On wired Ethernet, the live image configures DHCP automatically. For Wi-Fi, get the device name
from `iwctl device list` and run the station commands. `connect` prompts for the network
password when needed.

```bash
iwctl device list
read -r -p 'Wi-Fi device (for example wlan0): ' wifi
read -r -p 'Wi-Fi network name: ' ssid
iwctl station "$wifi" scan
iwctl station "$wifi" get-networks
iwctl station "$wifi" connect "$ssid"
```

```bash
timedatectl set-ntp true
timedatectl status                 # wait for System clock synchronized: yes
resolvectl query archlinux.org
```

## 2. Partition and mount the internal disk from the live USB

Identify the internal SSD by model, serial, and size. The XPS typically exposes it as
`/dev/nvme0n1`. Keep the installer USB on a separate device.

```bash
lsblk -d -o PATH,SIZE,MODEL,SERIAL,TRAN,TYPE
read -r -p 'Internal SSD whole-disk path: ' disk
lsblk -o PATH,SIZE,MODEL,SERIAL,TYPE,FSTYPE,MOUNTPOINTS "$disk"
```

After checking the disk, create a 4 GiB ESP and give the rest to the encrypted root. The larger
ESP leaves room for boot images if the disk is later reprovisioned for CPS. Start with an
unmounted target disk and an unused `/mnt`.

```bash
test "$(lsblk -dnro TYPE "$disk")" = disk &&
    sfdisk --wipe always --wipe-partitions always "$disk" <<'PARTITIONS'
label: gpt
size=4GiB, type=uefi, name=ARCH-EFI
type=linux, name=ARCH-LUKS
PARTITIONS
udevadm settle
esp=$(lsblk -lnpo PATH,PARTLABEL "$disk" | awk '$2 == "ARCH-EFI" {print $1}')
luks=$(lsblk -lnpo PATH,PARTLABEL "$disk" | awk '$2 == "ARCH-LUKS" {print $1}')
lsblk -o PATH,SIZE,TYPE,PARTLABEL,FSTYPE "$disk"
printf 'ESP: %s\nLUKS: %s\n' "$esp" "$luks"
```

Check that both paths point to the new partitions on the selected disk. Format the ESP and
create the encrypted Btrfs filesystem. Use a disk passphrase you can enter with the chosen
console layout.

```bash
test -b "$esp" && test -b "$luks" &&
    mkfs.fat -F 32 -n ARCH_EFI "$esp" &&
    cryptsetup luksFormat --type luks2 "$luks" &&
    cryptsetup open "$luks" root &&
    mkfs.btrfs -L arch-root /dev/mapper/root
```

Create and mount the subvolumes. `@snapshots` and `@var_log` are for this Arch host's snapshot
layout. The `@swap` subvolume keeps any disk swapfile outside root snapshots.

```bash
mount -o subvolid=5 /dev/mapper/root /mnt
for subvolume in @ @home @snapshots @var_log @swap; do
    btrfs subvolume create "/mnt/$subvolume"
done
umount /mnt

mount -o noatime,compress=zstd,subvol=@ /dev/mapper/root /mnt
mount --mkdir -o noatime,subvol=@home /dev/mapper/root /mnt/home
mount --mkdir -o noatime,subvol=@snapshots /dev/mapper/root /mnt/.snapshots
mount --mkdir -o noatime,subvol=@var_log /dev/mapper/root /mnt/var/log
mount --mkdir -o noatime,subvol=@swap /dev/mapper/root /mnt/swap
mount --mkdir -o umask=0077 "$esp" /mnt/efi
findmnt -R /mnt
```

## 3. Install the base system from the live USB

Use `intel-ucode` on the XPS or `amd-ucode` on an AMD machine. `sof-firmware` supplies firmware
for Intel SOF audio. Install microcode with the base packages so it is available for the first
UKI builds.

```bash
cpu_ucode=intel-ucode
pacstrap -K /mnt base linux linux-lts linux-firmware "$cpu_ucode" sof-firmware \
    btrfs-progs cryptsetup dosfstools mkinitcpio systemd-ukify efibootmgr \
    iwd plymouth git chezmoi curl sudo python openssh base-devel \
    reflector pacman-contrib fwupd sbctl sbsigntools &&
    genfstab -U /mnt > /mnt/etc/fstab &&
    cat /mnt/etc/fstab
```

Check the `/`, `/home`, `/.snapshots`, `/var/log`, `/swap`, and `/efi` lines against `findmnt -R
/mnt`. The Btrfs mounts share one filesystem UUID. The EFI line has its own FAT UUID. For a
fresh 4 GiB swapfile, run the optional block below once. Leave it out if using only zram.
Hibernation needs separate resume configuration and testing.

```bash
btrfs filesystem mkswapfile --size 4G /mnt/swap/swapfile &&
    printf '/swap/swapfile none swap defaults 0 0\n' >> /mnt/etc/fstab
```

If you want to transfer local dotfiles commits, create a bundle from your existing
checkout before booting the live USB. Copy it to storage you can access from the
installer.

```bash
git bundle create ~/dotfiles.bundle codex/dotfiles-audit-fixes
```

From the live USB, copy the bundle to the installed filesystem. Use `/var/tmp`
because `arch-chroot` mounts a temporary filesystem over `/tmp`.

```bash
read -r -p 'Path to the dotfiles bundle: ' bundle
install -Dm0644 "$bundle" /mnt/var/tmp/dotfiles.bundle
```

Enter the installed system. `arch-chroot` starts a new shell with the four
exported values. Continue at the chroot prompt with the next section.

```bash
export disk esp luks keymap
arch-chroot /mnt /bin/bash
```

## 4. Configure the system inside the chroot

Set the machine and account names. The example timezone is Europe/Paris. Set a root recovery
password and a separate login password for the normal account.

```bash
hostname=xps9315
username=kevinard
timezone=Europe/Paris
ln -sf "/usr/share/zoneinfo/$timezone" /etc/localtime
hwclock --systohc
printf '%s\n' "$hostname" > /etc/hostname
printf '127.0.1.1\t%s\n' "$hostname" >> /etc/hosts
printf 'KEYMAP=%s\n' "$keymap" > /etc/vconsole.conf
passwd
useradd --create-home --user-group --groups wheel --shell /bin/bash "$username"
passwd "$username"
```

Clone the dotfiles into the normal user's chezmoi source directory. The setup
script and provisioning files are on `codex/dotfiles-audit-fixes`. If you copied
a bundle, set `repo_url=/var/tmp/dotfiles.bundle` in the block below. The last
command restores the GitHub remote for a bundle clone.

```bash
repo_url=https://github.com/kevinard/dotfiles.git
branch=codex/dotfiles-audit-fixes
repo="/home/$username/.local/share/chezmoi"
runuser -u "$username" -- git clone --branch "$branch" "$repo_url" "$repo"
if [[ "$repo_url" = /var/tmp/dotfiles.bundle ]]; then
    runuser -u "$username" -- git -C "$repo" remote set-url origin https://github.com/kevinard/dotfiles.git
fi
```

Apply the repo's English UI and French regional formats, wheel sudo policy, and generic network
profiles. iwd handles Wi-Fi association and networkd handles IP addresses. Leave iwd's built-in
IP configuration disabled with this setup.

```bash
sed -i -e 's/^#en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/' \
    -e 's/^#fr_FR.UTF-8 UTF-8$/fr_FR.UTF-8 UTF-8/' /etc/locale.gen
install -m 0644 "$repo/provision/arch/etc/locale.conf" /etc/locale.conf
locale-gen
visudo -cf "$repo/provision/arch/etc/sudoers.d/local" &&
    install -Dm0440 "$repo/provision/arch/etc/sudoers.d/local" /etc/sudoers.d/local &&
    visudo -c

install -Dm0644 "$repo/provision/arch/etc/systemd/network/20-wired.network" \
    /etc/systemd/network/20-wired.network
install -Dm0644 "$repo/provision/arch/etc/systemd/network/25-wireless.network" \
    /etc/systemd/network/25-wireless.network
systemctl enable iwd.service systemd-networkd.service systemd-resolved.service \
    systemd-timesyncd.service
systemctl enable paccache.timer
```

For automatic mirror selection, review the included countries and protocol before enabling
Reflector. The live image's copied mirror list is enough to start.

```bash
cat "$repo/provision/arch/etc/xdg/reflector/reflector.conf"
install -Dm0644 "$repo/provision/arch/etc/xdg/reflector/reflector.conf" \
    /etc/xdg/reflector/reflector.conf
systemctl enable reflector.timer
```

## 5. Build and register both UKIs inside the chroot

Install the repo's mkinitcpio configs and presets. Both use `sd-encrypt` and boot `@`.
The primary UKI uses the Plymouth hook and embeds `quiet splash` from
`/etc/kernel/cmdline-linux`. The LTS fallback uses `/etc/kernel/cmdline` with
`plymouth.enable=0` for a text unlock prompt and skips hardware autodetection to
include a wider set of drivers. `cryptsetup luksUUID` reads the UUID of the
**LUKS container** for `rd.luks.name=`.

```bash
install -m 0644 "$repo/provision/arch/etc/mkinitcpio.conf" /etc/mkinitcpio.conf
install -m 0644 "$repo/provision/arch/etc/mkinitcpio-fallback.conf" /etc/mkinitcpio-fallback.conf
install -m 0644 "$repo/provision/arch/etc/mkinitcpio.d/"{linux,linux-lts}.preset /etc/mkinitcpio.d/

mountpoint -q /efi &&
    luks_uuid=$(cryptsetup luksUUID "$luks") &&
    boot_args=$(printf 'rd.luks.name=%s=root root=/dev/mapper/root rootfstype=btrfs rootflags=subvol=@ rw' \
        "$luks_uuid") &&
    printf '%s plymouth.enable=0\n' "$boot_args" > /etc/kernel/cmdline &&
    printf '%s quiet splash\n' "$boot_args" > /etc/kernel/cmdline-linux &&
    mkdir -p /efi/EFI/Linux &&
    mkinitcpio -P &&
    ls -lh /efi/EFI/Linux/
```

Check that `mkinitcpio -P` succeeded and both files exist. Add direct UEFI entries, creating the
LTS entry first and the primary one last so the primary goes to the front of the boot order.

```bash
esp_part=$(lsblk -dno PARTN "$esp")
test -s /efi/EFI/Linux/arch-linux-lts-fallback.efi &&
    test -s /efi/EFI/Linux/arch-linux.efi &&
    efibootmgr --create --disk "$disk" --part "$esp_part" \
        --label 'Arch Linux LTS Fallback' --loader '\EFI\Linux\arch-linux-lts-fallback.efi' &&
    efibootmgr --create --disk "$disk" --part "$esp_part" \
        --label 'Arch Linux' --loader '\EFI\Linux\arch-linux.efi'
efibootmgr -v
```

Confirm both entries are present. Run `exit` to leave the chroot.

For an existing installation with these two UKIs, keep its current unlock and root
arguments when updating the command-line files. Use the primary and fallback hook
lists above, install the updated presets, and rebuild both images with
`sudo mkinitcpio -p linux -p linux-lts`. For Secure Boot, verify the rebuilt images
using the checks in step 7.

## 6. Return to the live USB, then boot the installed system

At the live prompt, make the resolver symlink now that `arch-chroot` has released its temporary
resolver mount. Unmount the target, close LUKS, and reboot. Remove the installer USB when the
system restarts.

```bash
ln -sfn /run/systemd/resolve/stub-resolv.conf /mnt/etc/resolv.conf
sync
umount -R /mnt && cryptsetup close root && reboot
```

Unlock at the Plymouth passphrase prompt and log in as your normal user. Join Wi-Fi
again with the `iwctl` commands from step 1. Check the booted kernel, network, mounts,
and sudo access.

```bash
uname -r
findmnt /
findmnt /efi
resolvectl query github.com
timedatectl status
sudo -v
sudo efibootmgr -v
```

Boot **Arch Linux LTS Fallback** once from the firmware boot menu. Unlock at the
text prompt, log in, and confirm `uname -r` shows the LTS kernel. Then reboot back
into the primary entry. You can also select the fallback for one boot with its
four-digit ID from `efibootmgr -v`.

```bash
read -r -p 'Boot number for Arch Linux LTS Fallback: ' lts_entry
sudo efibootmgr --bootnext "$lts_entry" && sudo reboot
```

Once both entries work, install the matching Canopa packages if using the default desktop, then
apply the dotfiles from the checkout created in step 4.
[Canopa packages](canopa.md) · [Desktop login and accounts](setup.md)

```bash
cd "${XDG_DATA_HOME:-$HOME/.local/share}/chezmoi"
./setup --preview
./setup
```

## 7. Finish boot protection from the installed system

Check for firmware updates before enrolling your own keys or setting a TPM policy. If an update
is offered, apply it while on AC power and recheck both boot entries after the reboot.

```bash
fwupdmgr refresh
fwupdmgr get-devices
fwupdmgr get-updates
# If you choose an update, run: fwupdmgr update DEVICE-ID
```

### Secure Boot with automatic UKI signing

Create the signing keys while Secure Boot is still disabled. Point `ukify` at the `sbctl` db key
so both UKIs are automatically signed on each `mkinitcpio` rebuild, including the package hooks
after a kernel update. On an existing system, merge these settings into its `uki.conf`.

```bash
sudo sbctl status
sudo sbctl create-keys
sudo tee /etc/kernel/uki.conf >/dev/null <<'UKI'
[UKI]
SecureBootPrivateKey=/var/lib/sbctl/keys/db/db.key
SecureBootCertificate=/var/lib/sbctl/keys/db/db.pem
UKI
sudo mkinitcpio -P && sudo sbctl verify \
    /efi/EFI/Linux/arch-linux.efi /efi/EFI/Linux/arch-linux-lts-fallback.efi
```

Check that `sbctl verify` reports both UKIs as signed. Back up `/var/lib/sbctl` to encrypted
storage and verify how to restore factory keys in the firmware. On the XPS 9315, open
**Boot Configuration → Expert Key Management** in firmware. Use its key-management controls
to enter **Setup Mode**, then boot back to Arch and confirm it with `sbctl status`.

The enrollment command includes Microsoft and built-in firmware certificates. Review the
certificates your firmware and any other OS need before enrolling. If `sbctl` refuses
enrollment, resolve its reported reason before enabling Secure Boot. [Dell firmware options](https://www.dell.com/support/manuals/en-us/xps-13-9315-laptop/xps-13-9315-service-manual/system-setup-options?guid=guid-238088b4-fceb-4320-9fe4-3170d7892d99&lang=en-us) · [sbctl enrollment options](https://man.archlinux.org/man/sbctl.8.en)

```bash
sudo sbctl status
sudo sbctl enroll-keys --microsoft --firmware-builtin
sudo sbctl list-enrolled-keys
```

Enable Secure Boot in firmware, then passphrase-boot both entries again. If boot fails, use the
firmware's Secure Boot settings and your working USB to recover.

```bash
sudo sbctl status
sudo sbctl verify /efi/EFI/Linux/arch-linux.efi /efi/EFI/Linux/arch-linux-lts-fallback.efi
```

### LUKS recovery key and optional TPM unlock

Add an independent recovery key. Save the displayed key somewhere accessible off the laptop.
Test it using `cryptsetup` or by entering it at the next boot prompt. Keep the original
passphrase slot.

```bash
lsblk -o PATH,PARTLABEL,FSTYPE,UUID
read -r -p 'UUID of the ARCH-LUKS container: ' luks_uuid
luks="/dev/disk/by-uuid/$luks_uuid"
sudo systemd-cryptenroll --recovery-key "$luks"
sudo cryptsetup open --test-passphrase "$luks"
```

The passphrase and recovery key are enough to finish the install. For the optional TPM2 + PIN
setup, use an explicit PCR policy and test both UKIs and a kernel update before relying on it.
[Boot protection reference](reference/setup.md#5-finish-boot-protection)

## Optional desktop system policy and snapshots

After your first desktop login and any Secure Boot setup, you can enable the
repo's zram policy and paired Btrfs and UKI snapshots. Review the system changes
before applying them. [Snapshot and recovery details](desktop.md#snapshots-and-uki-recovery)

```bash
cd "${XDG_DATA_HOME:-$HOME/.local/share}/chezmoi"
./setup system --snapshots
./setup system --apply --snapshots
```

## If CPS will manage the root

The steps above provision a pacman-managed Arch root. A CPS-managed image uses the same two-partition disk layout with different mount and boot rules. Use a shared `@var` at `/var`, mount Btrfs ID 5 read-write at `/cps`, and create `/cps/@environments` beside the initial root. Keep selectors off the `/` line in `fstab` so CPS can select the boot root per environment. CPS owns the boot entries and root rollback in that setup. [CPS Btrfs guide](https://github.com/kevinard/cps/blob/main/docs/setups/btrfs.md)
