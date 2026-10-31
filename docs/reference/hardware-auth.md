# Hardware authentication reference

For first-time setup, use [the short activation guide](../hardware-auth.md).

The primary Solo and the converted, locked backup Solo are alternative second
factors for the same Linux account. This policy requires the Linux password plus
a token touch for `sudo`, SDDM password login, and console login. Root keeps its
separate password authentication for emergency console recovery. SSH retains its
independent PIN + touch credentials; PAM enrollment does not replace them.

Arch's package phase installs `pam-u2f` and `libfido2`. Enrollment and activation
are explicit: `chezmoi apply` never enrolls a token, installs root policy, sets a
root password, or edits live PAM files. Ubuntu work authentication remains locally
owned. Run these commands from this repository on the installed Arch system.

References: [pam-u2f configuration and multiple authenticators](https://developers.yubico.com/pam-u2f/),
[pamu2fcfg options](https://developers.yubico.com/pam-u2f/Manuals/pamu2fcfg.1.html).

## Prepare recovery

Keep the tokens' PINs and a strong, separate root password in off-device recovery
records. Root is exempt from the token check, but not its existing password check.
Someone with that password and access to the running system can bypass the tokens.
This policy does not enable SSH root login.

Set the root password and test `su -` from a regular terminal, then exit that shell:

```sh
sudo passwd root
su -
```

Keep a LUKS recovery key/passphrase and an Arch installation USB separately too.
Root's password cannot unlock the encrypted disk. A disk unlocked only by lost
tokens would make the PAM recovery route inaccessible.

Open a dedicated root shell and keep it open until all tests pass:

```sh
sudo -i
```

In that root shell, back up the existing service files:

```sh
pam_backup_dir="/root/pam-before-solo-$(date +%Y%m%d-%H%M%S)"
install -d -m 0700 "$pam_backup_dir"
cp -a /etc/pam.d/sudo /etc/pam.d/login /etc/pam.d/sddm "$pam_backup_dir/"
printf 'PAM recovery directory: %s\n' "$pam_backup_dir"
```

Record that path. If pam-u2f is already enabled, inspect and preserve its policy
and `/etc/u2f_mappings` too; do not overwrite existing enrollment as a first install.

## Enroll both Solos

From a regular-user terminal:

```sh
sudo pacman -Syu --needed pam-u2f libfido2
scripts/enroll-login-keys
```

Connect only the token requested at each prompt. The helper stages one mapping
line with both registrations in
`${XDG_STATE_HOME:-$HOME/.local/state}/dotfiles/u2f_mappings`, with mode 0600. It
does not set/reset PINs, modify SSH credentials, use resident slots, or activate
PAM. Failed/malformed registrations are rejected and existing files are never
overwritten. Use `--output /an/external/path/u2f_mappings.new` to stage a replacement.

Enrollment and policy use the fixed origin `pam://kevinard-linux`, avoiding
hostname-dependent failures. If changing it, change helper and policy together
and enroll fresh credentials. Mapping files contain usernames, public keys and
credential handles; keep them outside Git and in encrypted backups. On a new
machine, enroll both tokens again or restore the matching mapping for the same
user/origin. Do not reset tokens during onboarding.

For a first install, confirm `/etc/u2f_mappings` does not already contain other
users, then install the staged mapping and reviewed policy:

```sh
sudo install -o root -g root -m 0600 \
  "${XDG_STATE_HOME:-$HOME/.local/state}/dotfiles/u2f_mappings" /etc/u2f_mappings
sudo install -o root -g root -m 0644 \
  provision/arch/etc/pam.d/solo-auth /etc/pam.d/solo-auth
```

Use the actual path if you passed `--output`. For additional users, merge their
complete mapping line into the root-owned file instead of replacing it. Every
non-root user of the protected services needs enrollment. Do not add `nouserok`,
`alwaysok`, or password-only fallback for normal users.

The policy skips the token check only for root. The calling service's existing
authentication stack still checks the password. Keep the mapping root-owned so
normal users cannot replace their second factor by editing it. PAM uses Linux
password + touch, without an additional token PIN prompt; SSH still requires its PIN.

## Activate sudo first

Review local PAM changes and sudoers first. `NOPASSWD` rules bypass PAM
authentication, including this second factor. In the regular-user terminal:

```sh
sudoedit /etc/pam.d/sudo
```

Insert this before its existing `auth` lines; keep all original lines:

```pam
auth include solo-auth
```

Do not add it globally to `system-auth` or `system-login`. Keeping it in selected
services preserves the recovery scope. Putting it first prevents later sufficient
password modules from skipping the required check. No daemon restart is needed.

From another regular terminal, run this before each test to avoid sudo's cache:

```sh
sudo -k
sudo -v
```

Test primary alone, backup alone, neither connected, and an incorrect Linux
password with a token connected. Only the first two should succeed. Avoid repeated
incorrect passwords because Arch's faillock policy still applies. Normal sudo
timestamp caching remains enabled: touch is needed when sudo authenticates.

## Activate login

After sudo passes, add the same include before existing `auth` lines in:

```sh
sudoedit /etc/pam.d/sddm /etc/pam.d/login
```

Disable automatic login if configured: `sddm-autologin` is a different PAM service
and does not run this policy. Inspect `/etc/sddm.conf` and `/etc/sddm.conf.d/`.
This does not configure swaylock, hyprlock, polkit, SSH login or LUKS; each has
separate policy. Review the actual PAM service if using another display manager.

Keep the desktop session and dedicated root shell open. On a spare TTY (usually
Ctrl+Alt+F3), test normal-user login with each token, and failure without either.
Test root login with its password and no token, then log root out. Verify SDDM
using a second graphical session or a controlled login test while retaining the
root recovery shell on a TTY. Only close it after all intended services and the
recovery route pass. Root-password recovery must work before relying on this policy.

## Rollback and lost-token recovery

If testing fails, restore from the root shell you kept open:

```sh
cp -a "$pam_backup_dir/sudo" /etc/pam.d/sudo
cp -a "$pam_backup_dir/login" /etc/pam.d/login
cp -a "$pam_backup_dir/sddm" /etc/pam.d/sddm
```

In another root session, set `pam_backup_dir` to the recorded path first. Restore
only affected files if other edits occurred since the backup. No reboot is needed.
Unused policy/mapping files can stay in place until diagnosis is complete.

If both tokens are lost, log in as root on a console using the recovery password.
Remove `auth include solo-auth` from affected service files, or restore backups.
Enroll replacements and repeat the tests before enforcing the policy again.
If one token is lost, remove its credential entry from the mapping when replacing
it; an old registration still authorizes that token. Revoke its SSH public keys
and website registrations separately too.

If PAM or the OS is inaccessible, boot Arch installation media, unlock LUKS with
the independent recovery credential, mount the correct root subvolume, and repair
PAM under that mounted root. See [the installation layout](../arch-install.md). Test
this recovery route before relying on hardware authentication.

## Maintenance

Ordinary applies do not overwrite enrollment or PAM state. Keep actual mappings,
PINs, private SSH reference files and recovery credentials out of the source tree.
Review package `.pacnew` files rather than replaying whole distribution-owned PAM
files from Git. The shared root policy is the only PAM reference file managed here.
