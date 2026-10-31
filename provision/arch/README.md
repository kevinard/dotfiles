# Root-owned Arch reference configuration

The [device lifecycle reference](../../docs/reference/setup.md) coordinates the OS runbook,
post-install helper, hardware credentials, recovery tests and device retirement.

These files are outside chezmoi's home source root. They are examples for explicit
provisioning, not a tree to copy wholesale into `/etc`. Review each file against the
machine. The installation runbook describes the boot-related subset; networking,
DNS, display manager, printer and font policies are independent choices.

Generated `fstab`, hostnames, MAC addresses, LUKS UUIDs and boot entries belong to
the machine. No generic fstab is checked in. `mkinitcpio.conf` defaults to automatic
GPU discovery. `hardware/` retains optional Intel/NVIDIA examples; choose the actual
driver package and kernel first. An override needs a measured symptom and a retest
procedure before deployment. The old generic GPU blacklist has been removed.

The sudoers example now requires authentication for all wheel commands. Validate
an installed candidate with `visudo -cf PATH` before replacing the live policy.
The `pam.d/solo-auth` reference adds either enrolled Solo as a second factor, with
root-password recovery. Follow [hardware authentication](../../docs/hardware-auth.md)
to enroll both tokens outside Git and test recovery before explicitly activating
it in individual services. No home apply edits PAM or deploys enrollment mappings.
The custom udisks/storage-group rule was removed: use the distribution's active-seat
policy. The Blueman exception checks active/local status as well as wheel membership.
DDC access uses `uaccess`; no root process invokes a program under a user's home.

The power example targets TLP 1.10 or newer, with automatic AC/battery profiles. It
is an alternative to power-profiles-daemon. Suspend state and PCIe/USB/Wi-Fi power
workarounds are left to kernel/TLP defaults rather than forced across machines.
Review `tlp-stat -c` and measure sleep drain, resume, docks and wireless stability.
The retained networking/link and sysctl examples are optional host policies too.

For machines provisioned by the old recipe, these live files may still exist even
though their source was removed:

```text
/etc/polkit-1/rules.d/50-udisks.rules
/etc/udev/rules.d/99-monitor-hotplug.rules
/etc/udev/rules.d/pci_pm.rules
/etc/udev/rules.d/81-wifi-powersave.rules
/etc/udev/rules.d/50-usb_power_save.rules
/etc/systemd/sleep.conf.d/freeze.conf
/etc/modprobe.d/iwlwifi.conf
```

Compare their contents with the old Git revision, back them up, and remove only
copies of those obsolete rules. Reload udev rules/polkit as appropriate and reboot
for kernel/module/suspend changes. Also review the old sudoers NOPASSWD line,
rfkill masks, `nowatchdog`, ASPM and USB kernel arguments, and storage membership.
No home apply performs this root migration automatically.
