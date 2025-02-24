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
mkfs.btrfs /dev/mapper/root
mkfs.fat -F32 $bootPartition

# create btrfs subvolumes
mount --mkdir /dev/mapper/root /mnt
btrfs subvolume create /mnt/@
btrfs subvolume create /mnt/@home
btrfs subvolume create /mnt/@snapshots
btrfs subvolume create /mnt/@var_log
btrfs subvolume create /mnt/@swap
umount /mnt

# mount the partitions
mount --mkdir -o noatime,compress=zstd,space_cache=v2,subvol=@ /dev/mapper/root /mnt
mount --mkdir -o noatime,compress=zstd,space_cache=v2,subvol=@home /dev/mapper/root /mnt/home
mount --mkdir -o noatime,compress=zstd,space_cache=v2,subvol=@snapshots /dev/mapper/root /mnt/.snapshots
mount --mkdir -o noatime,compress=zstd,space_cache=v2,subvol=@var_log /dev/mapper/root /mnt/var/log
mount --mkdir -o noatime,subvol=@swap /dev/mapper/root /mnt/swap
mount --mkdir $bootPartition /mnt/efi

# setup swap
btrfs filesystem mkswapfile --size 4g --uuid clear /mnt/swap/swapfile
swapon /mnt/swap/swapfile

# install system
pacstrap -K /mnt base linux linux-firmware iwd efibootmgr sbctl sbsigntools git chezmoi reflector fwupd curl sudo pacman-contrib base-devel btrfs-progs

# generate fstab
# genfstab -U /mnt >> /mnt/etc/fstab

# this needs to be done from outside the arch-chroot
ln -sf ../run/systemd/resolve/stub-resolv.conf /mnt/etc/resolv.conf

arch-chroot /mnt

## download dotfiles

# copy config files
cp -r etc/* /etc/

ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime

hwclock --systohc

locale-gen

echo "$hostname" >/etc/hostname
echo "127.0.1.1        $hostname" >>/etc/hosts

systemctl enable systemd-resolved.service
systemctl enable iwd.service
systemctl enable systemd-networkd.service
systemctl enable systemd-timesyncd.service

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
