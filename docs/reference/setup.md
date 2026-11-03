# Detailed installation and device lifecycle reference

Start with [the quick setup](../setup.md). This page is optional background for
boot security, work isolation, service onboarding and device retirement.

This reference covers a new laptop/desktop, reinstall, or retiring a device.
The default Arch installation is UEFI, LUKS2-encrypted Btrfs, normal + LTS UKIs,
niri with Canopa or Waybar, an ordinary login password, and independent hardware
SSH credentials. Enable Secure Boot after testing passphrase boot, then optionally
add TPM2 + PIN with a reviewed measurement policy. Add password + Solo login/sudo
only after testing root-password recovery.

There is no unattended disk formatter. Partitioning, firmware trust enrollment and
PAM activation have explicit checkpoints because mistakes affect data or recovery.
The repeatable post-install configuration is one command; credentials and device
identities remain separate from Git.

```sh
scripts/setup-machine plan
```

## 1. Prepare before wiping or replacing a device

- Make an encrypted off-device backup and restore a sample file. Include projects,
  documents, SSH configuration, browser data and both current password vaults.
- Keep the disk recovery credential, root recovery password, password-manager
  recovery material, token PINs, and any backup encryption credentials accessible
  without the laptop. Store Secure Boot signing-key backups encrypted too.
- Keep the backup Solo physically separate. Both Solos have independent SSH keys;
  confirm both GitHub registrations remain authorized. Do not reset either token
  to provision a new machine.
- Record the machine's purpose, hostname, disk model/serial, GPU/CPU, desired power
  manager, and VPN/backup destinations. Record disk UUIDs only after formatting.
- For employer equipment, agree the OS, personal-token use, service destinations,
  and recovery policy with the employer. Do not import work secrets into personal
  storage as part of bootstrap.

Keep an Arch installation USB and a tested way to enter firmware setup. A stock
Arch ISO may require temporarily disabling Secure Boot; plan recovery before
enrolling firmware keys. [Arch Secure Boot guidance](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot)

## 2. Install the encrypted base OS

Follow [the Arch installation runbook](../arch-install.md) in order. It separates:

1. Live media: network/time, positively identify the target disk, GPT ESP + LUKS2,
   Btrfs subvolumes, mount everything, pacstrap and generated fstab.
2. Interactive chroot: timezone/locale/hostname, user and root recovery passwords,
   wheel sudo, networking, CPU microcode, initramfs, UKIs and boot entries.
3. First boot: test the normal and LTS entries with a disk passphrase before any
   Secure Boot/TPM/PAM changes.

Both home and swap belong inside encryption. The EFI partition is unencrypted;
signed UKIs provide verification, not confidentiality of embedded files. Never
embed passwords, recovery keys or private credentials in a UKI.

Use passphrase disk unlock initially. Full-disk encryption cannot protect secrets
already accessible in an unlocked running session. Lock before suspend; shut down
for travel when the machine may leave your control. Hibernation needs separately
tested encrypted swap/resume configuration.

## 3. Configure the installed system as your normal user

The base install supplies Git, Python, sudo and chezmoi. Clone over HTTPS so initial
setup does not depend on SSH already working:

```sh
git clone https://github.com/kevinard/dotfiles.git \
  "${XDG_DATA_HOME:-$HOME/.local/share}/chezmoi"
cd "${XDG_DATA_HOME:-$HOME/.local/share}/chezmoi"
scripts/setup-machine configure --apply
```

If this checkout already exists, use it; do not clone over it or discard local
changes. Replace the URL if using a different remote. Review the checkout/revision
before executing it. This flow does not pipe downloaded scripts into a shell.

On first use, `./setup` asks for identity, email and name, detects hardware, and
uses the defaults described in the quick guide. Hybrid GPUs need an extra choice.
`./setup --customize` asks every question on first install and opens the config
editor on an existing installation. GPG signing defaults to `no` until a
signing key is available; SSH authentication does not configure Git signing.

| Choice | Personal Arch | Work Arch |
| --- | --- | --- |
| `env` | `home` | `work` |
| Desktop | niri + selected shell | niri + selected shell |
| SSH agent | Managed OpenSSH agent | Managed OpenSSH agent |
| Personal-only packages | Included | Excluded |
| Hardware | Detected; hybrid GPU asks | Detected; hybrid GPU asks |

For both identities on one machine, use separate Linux accounts and run setup as
each account. `env` selects an identity; it does not isolate two identities within
one account. Accounts still share kernel/root. Use a work VM or separate machine
where stronger separation is required. Never copy a machine's complete chezmoi
config onto another machine without reviewing hardware choices.

`configure` initializes missing configuration, displays a diff, and with `--apply`
installs packages, applies files and builds/installs the pinned Canopa package set if selected.
It stops at the first failed stage. Without `--apply`, it initializes choices and
shows the diff only. Existing chezmoi configuration is kept; edit it with
`chezmoi edit-config` to change choices. `--reconfigure` explicitly regenerates the
template using saved data; it can remove custom config sections, so back those up.
`--skip-desktop-build` leaves Canopa installation for `scripts/install-canopa`
and an opted-in scheduler helper for `scripts/install-system76-scheduler-niri`.
The builds need network access and a configured Rust toolchain; do not start that
desktop until all companion binaries are installed.

Use the same command again to resume after a failure. There is no persistent
"completed" flag that would hide a partially installed stage. Reapplying is
convergent, but explicitly invoking configuration can perform another Arch upgrade
and a Canopa build if the recorded revision or installed binaries need updating.
It does not pull the dotfiles repository or discard your changes.

Set Zsh as your login shell if desired:

```sh
chsh -s /usr/bin/zsh
```

First test `canopa-session` from a TTY after logging in again (`niri-session` for Waybar).
For Canopa Greeter, use `./setup login` followed by `./setup login --apply` and reboot;
see [the Canopa guide](../canopa.md). For an optional SDDM
graphical login, the simplest initial greeter uses SDDM's default X11 backend:

```sh
sudo pacman -Syu --needed xorg-server sddm
sudo systemctl enable sddm.service
```

Check `systemctl status display-manager.service` first and keep only one display
manager enabled. Do not install the repository's optional `wayland.conf` for this
X11-greeter path; existing SDDM overrides must agree with the selected backend.
The user session remains Wayland/niri. Changing the greeter to Wayland is a
separate compositor setup, not required for user-session Wayland.

Log out and back in after applying. Unit changes and environment variables must
reach a fresh session. Then run `desktop-health` inside niri and test lock, suspend,
resume, docking, notifications, portals and screen sharing on actual hardware.

## 4. Use either Solo for SSH

For each test, connect only the intended Solo and run:

```sh
scripts/setup-machine ssh
export SSH_AUTH_SOCK="$XDG_RUNTIME_DIR/ssh-agent.socket"
ssh -T git@github.com
```

The helper starts the managed Arch user agent and runs `ssh-add -K` to load
resident credentials. It never generates/replaces an SSH identity, resets the
token, clears other agent identities, or copies private keys into Git. PIN + touch
requirements remain. At the first connection, verify GitHub's published host key
fingerprint before accepting it. [GitHub fingerprints](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)

GitHub's success message comes with exit status 1 because it provides no shell.
If an old `IdentityFile` or `IdentitiesOnly` setting restricts agent selection,
review `ssh -G github.com` and `ssh -vT git@github.com`; don't disable host-key checks.

Repeat loading when a new agent session starts or when switching to the backup.
Loading an identity does not remove its hardware requirement. For persistent local
reference files, use `ssh-keygen -K` in an empty private directory and deliberately
select the desired credential in SSH config; those filenames may differ from the
custom filenames on the old laptop. [OpenSSH resident-key loading](https://man.openbsd.org/ssh-add.1)

Authorize both public keys on every required SSH destination. A new laptop using
the same token needs no new server-side token registration. Your SSH agent is
shared by applications in your user session; avoid agent forwarding by default.

## 5. Finish boot protection

Follow the post-boot stage in [the installation runbook](../arch-install.md). Sign and
verify both UKIs, enroll Secure Boot keys only with firmware recovery available,
then confirm signing still happens after rebuilding the images. A one-time signed
image is not a complete update workflow. Keep signing keys out of dotfiles.

TPM2 + PIN is optional after that baseline works. Its measurement policy must
verify the intended boot/unlock design and allow planned kernel updates; do not
copy a PCR7-only enrollment command and assume it pins your exact UKI. Signed PCR
policies and volume binding require coordinated initramfs/UKI configuration.
Record and test the chosen policy, fallback boot, recovery-key boot and an upgrade
before relying on it. Until that is done, retain passphrase unlock as the working
default. [Current Arch TPM guidance](https://wiki.archlinux.org/title/Trusted_Platform_Module)

## 6. Add hardware login and sudo

```sh
scripts/setup-machine auth
```

This only stages both PAM registrations. Follow [hardware authentication](../hardware-auth.md)
to back up existing PAM files, install root-owned mappings/policy, activate sudo
first, test each Solo and no-token failure, then activate login and test root
recovery. Keep a root shell open until all checks pass. This is separate from SSH,
disk encryption and the screen locker. Do not enroll/enable root policy just to
make a configuration apply succeed.

## 7. Connect services and restore data

- Pick one authoritative password manager after the mobile/browser trial. Psono
  remains a candidate, not an automatically selected migration. Preserve both
  existing vaults; reconcile conflicts in a candidate vault before cutover.
- Install its official Firefox extension, configure your server URL, authenticate
  interactively, and enable iOS AutoFill on the phone. Test account registration
  with redirects, password changes, multiple accounts, offline cold-start and
  AutoFill with the server unreachable. Do not sync session tokens or whole
  browser profiles between simultaneously used devices as credential bootstrap.
- Enroll a distinct VPN identity per device so a laptop can be revoked independently
  of a portable SSH token. Keep initial password-manager access/recovery possible
  without a circular dependency on that same inaccessible VPN or vault.
- Restore documents/projects and set up the chosen encrypted backup destination.
  Nextcloud's presence in the package list does not configure accounts or backups.
  Test an off-device file restore. Snapshots are rollback tools, not backups.
- Keep client authentication, VPN private keys, vault exports, backup credentials
  and recovery material outside Git. A root-owned service can still depend on a
  separately supplied credential file; don't hardcode it into provisioning.

These providers/destinations have not been chosen in this repository. The flow
does not deploy a password server, migrate live vaults, or claim that installing a
client has backed up your data.

## 8. Acceptance and daily operation

```sh
scripts/setup-machine check
desktop-health
```

`check` is a read-only inventory with DNS queries and boot/disk/service output,
not a pass/fail security audit. It does not prove that disk encryption, Secure
Boot signatures, recovery or backups are correct. Verify these final checkpoints:

- Normal/LTS boot, signed-UKI update cycle, disk recovery and root-console recovery.
- Primary/backup SSH, both PAM tokens, denial without tokens, and sudo cache behavior.
- Screen locks before suspend, successful resume, and measured sleep battery drain.
- Password-manager offline retrieval and tested registration/password-change saves.
- A file restored from encrypted off-device backup and accessible recovery records.

For dotfile maintenance, review/pull the repository, inspect `chezmoi diff`, then
apply. Review Arch news before full upgrades, keep the LTS fallback, and review
`.pacnew` changes. Re-test boot/recovery after changes to encryption, firmware,
PAM or signing. [Maintenance details](../maintenance.md)

## Retire, lose, or replace a device

For a planned replacement, bring the new machine through this flow and verify
access/restore before wiping the old one. Then revoke its VPN identity, application
tokens and sessions where supported, remove it from sync/backup device inventories,
and securely erase storage using a method appropriate to that drive.

If a laptop is lost without either Solo, your hardware SSH private credentials
remain with the tokens, but browser sessions, cached vault data and other local
secrets still need attention. Revoke the lost device's sessions and VPN identity.
Portable SSH identities cannot distinguish laptops: revoking a token's public key
disables that token everywhere it was authorized, not just on one laptop.

If a Solo is lost, revoke its SSH public keys, website registrations and PAM
registrations on every affected machine; keep the other Solo active. Enroll a new
spare and repeat tests. If both are lost, use the separate root and disk recovery
routes. Keep an off-device inventory of which credentials/devices were enrolled.
