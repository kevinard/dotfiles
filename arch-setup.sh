#!/bin/sh

# copy config files
cp -r boot/* /boot/
cp -r etc/* /etc/

# during installation, create a separate /boot partition to host the EFI
# install systemd-boot bootloader
bootctl install
systemctl enable systemd-boot-update.service

# setup mkinitcpio (build kernel image)
ROOT_UUID=$(blkid | grep ext4 | cut -d' ' -f2)
sed s/ROOT_UUID/"${ROOT_UUID}"/g /etc/kernel/cmdline
sed s/ROOT_UUID/"${ROOT_UUID}"/g /etc/kernel/fallback_cmdline
mkinitcpio -p linux

# setup networking
systemctl enable systemd-resolved.service
ln -sf ../run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
systemctl enable systemd-networkd.service
WLAN_INTERFACE=$(networkctl | grep wlan | cut -d' ' -f4)
ln -sf /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant-"$WLAN_INTERFACE".conf
systemctl enable wpa_supplicant@"$WLAN_INTERFACE".service

# setup tymesyncd (NTP)
systemctl enable systemd-tymesyncd.service
timedatectl set-ntp true

# setup reflector (update mirrors list)
systemctl enable reflector.timer
