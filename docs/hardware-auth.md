# Solo login and sudo on Arch

This adds Linux password + touch of either Solo. Root keeps its separate password
for recovery. SSH PIN requirements are unchanged. Run commands from this checkout.

## 1. Keep a recovery shell open

Set a separate root password, test it with `su -`, then exit that test shell.
Keep root and disk-encryption recovery credentials off-device.

```sh
sudo passwd root
su -
```

Open a dedicated root shell and leave it open throughout testing:

```sh
sudo -i
pam_backup_dir="/root/pam-before-solo-$(date +%Y%m%d-%H%M%S)"
install -d -m 0700 "$pam_backup_dir"
cp -a /etc/pam.d/sudo /etc/pam.d/login /etc/pam.d/sddm "$pam_backup_dir/"
printf '%s\n' "$pam_backup_dir"
```

Record that backup path. Existing token setup or a different display manager?
Use the [reference](reference/hardware-auth.md) before changing it.

## 2. Enroll and install

In your **regular-user terminal**, connect each Solo when prompted:

```sh
./setup auth
sudo install -o root -g root -m 0600 \
  "${XDG_STATE_HOME:-$HOME/.local/state}/dotfiles/u2f_mappings" /etc/u2f_mappings
sudo install -o root -g root -m 0644 \
  provision/arch/etc/pam.d/solo-auth /etc/pam.d/solo-auth
```

This first-install command replaces `/etc/u2f_mappings`; preserve existing users'
registrations instead if the file already exists. No token reset is needed.

## 3. Enable sudo, then test

Run `sudoedit /etc/pam.d/sudo`. Insert this **before existing `auth` lines**, keeping
the original contents:

```pam
auth include solo-auth
```

In another regular terminal, run `sudo -k` followed by `sudo -v` for each test:

- Primary alone and backup alone: touch + correct password must succeed.
- No token, or incorrect password: must fail. Avoid repeated wrong-password tests.

`NOPASSWD` sudoers rules bypass this check. Normal sudo timestamp caching remains.

## 4. Enable login, then test recovery

Run `sudoedit /etc/pam.d/sddm /etc/pam.d/login` and insert the same line before their
existing `auth` lines. Disable SDDM autologin if configured.

On a spare TTY (Ctrl+Alt+F3), test login with each token, denial with neither, and
root login with its password and no token. Test SDDM while keeping a root recovery
shell on a TTY. Only close that shell after every test passes.

This does not enable tokens for screen unlock, polkit or disk unlock.

## If something goes wrong

From the root shell, restore the saved files:

```sh
cp -a "$pam_backup_dir/sudo" /etc/pam.d/sudo
cp -a "$pam_backup_dir/login" /etc/pam.d/login
cp -a "$pam_backup_dir/sddm" /etc/pam.d/sddm
```

If both tokens are lost later, log in as root on a TTY and remove the
`auth include solo-auth` lines. If the OS is inaccessible, use installation media
and your disk recovery credential. [Details and token replacement](reference/hardware-auth.md).
