#!/bin/sh

targetDisk="/dev/sda"
bootPartition="/dev/sda1"
systemPartition="/dev/sda2"
hostname="tower"
username="kevinard"

# partition the disk
fdisk $targetDisk
# wipe any existing partitions, then create 2 partitions: 1G (EFI System) and rest of the disk (Linux root (x86-64))

# make the new partition a LUKS volume
cryptsetup luksFormat $systemPartition
# --cipher aes-xts-plain64 \
# --key-size 512 \
# --hash sha512 \
# --pbkdf argon2id \
# --pbkdf-memory 1048576 \
# --pbkdf-parallel 4 \
# --iter-time 5000 \
# --sector-size 4096

cryptsetup open $systemPartition root

# format the partitions
mkfs.ext4 /dev/mapper/root
mkfs.fat -F32 $bootPartition

# mount the partitions
mount --mkdir /dev/mapper/root /mnt
mount --mkdir $bootPartition /mnt/efi

pacstrap -K /mnt base linux linux-firmware intel-ucode neovim iwd efibootmgr sbctl sbsigntools git chezmoi reflector fwupd less sudo pacman-contrib base-devel nvidia nvidia-utils libva-nvidia-driver intel-media-driver

# this needs to be done from outside the arch-chroot
ln -sf ../run/systemd/resolve/stub-resolv.conf /mnt/etc/resolv.conf

arch-chroot /mnt

## download dotfiles

# copy config files
cp -r boot/* /boot/
cp -r etc/* /etc/

ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime

hwclock --systohc

# uncomment desired locales (en_US.UTF-8 and fr_FR.UTF-8) in /etc/locale.gen then
locale-gen

echo -e "LANG=en_US.UTF-8\nLC_TIME=fr_FR.UTF-8" >/etc/locale.conf

echo "$hostname" >/etc/hostname
echo "127.0.1.1        $hostname" >>/etc/hosts

systemctl enable systemd-resolved.service
systemctl enable iwd.service
systemctl enable systemd-networkd.service
systemctl enable systemd-tymesyncd.service

# setup reflector (update mirrors list)
systemctl enable reflector.timer
systemctl enable paccache.timer

efibootmgr \
  --create \
  --label "Arch Linux" \
  --index 0 \
  --disk $targetDisk \
  --part 1 \
  --loader "\\arch-linux.efi"

efibootmgr \
  --create \
  --label "Arch Linux Fallback" \
  --index 1 \
  --disk $targetDisk \
  --part 1 \
  --loader "\\arch-linux-fallback.efi"

passwd root

# reboot

fwupdmgr refresh
fwupdmgr get-devices
fwupdmgr get-updates
# update firmwares if available (see fwupd doc)

# secure boot should be in setup mode
sbctl status

sbctl create-keys

sbctl enroll-keys -m

sbctl sign -s /efi/arch-linux.efi
sbctl sign -s /efi/arch-linux-fallback.efi

# reboot and enable Secure Boot in bios

# this should now show secure boot enabled and not in setup mode anymore
sbctl status

# store the recovery-key in password manager
systemd-cryptenroll $systemPartition --recovery-key
systemd-cryptenroll $systemPartition --tpm2-device=auto -tpm2-with-pin=yes

groupadd --gid 1000 $username
useradd --create-home --uid 1000 --gid 1000 --groups wheel --shell /bin/bash $username
passwd $username

sed -i "/etc/pacman.conf" \
  -e "s|^#Color|&\nColor\nILoveCandy|" \
  -e "s|^#VerbosePkgLists|&\nVerbosePkgLists|" \
  -e "s|^#ParallelDownloads.*|&\nParallelDownloads = 20|"
