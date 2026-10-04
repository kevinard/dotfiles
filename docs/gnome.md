# GNOME and PaperWM

The Ubuntu profile keeps stock GNOME's notifications, monitors, portals, power
profiles and locking. At graphical login the managed preferences set the selected
light/dark style, font, US AltGr international layout, Caps-to-Escape, both-Shifts
Caps Lock, and a ten-minute idle lock. These are deliberate settings, not a full
dconf database import.

Install PaperWM using the version offered for your GNOME Shell on
[GNOME Extensions](https://extensions.gnome.org/extension/6099/paperwm/).
Then log out/in and enable it:

```sh
gnome-extensions enable paperwm@paperwm.github.com
```

The [upstream installation instructions](https://github.com/paperwm/PaperWM#installation)
also describe source installation when necessary. Do not track the installed extension
tree as dotfiles or disable GNOME's extension version validation.

The work laptop was unavailable during implementation. Its private PaperWM preferences
cannot be inferred from the Arch machine. To capture them for review, run this on the
work laptop:

```sh
dconf dump /org/gnome/shell/extensions/paperwm/
```

Keep only deliberate layout/shortcut keys in a small settings file, inspect it for
host-specific values, and restore them with the extension's installed schema. Do not
blindly import all of `/org/gnome/` or replace `enabled-extensions`, which would remove
unrelated extensions. The default PaperWM shortcut set remains owned by PaperWM.

When official niri packages are available, change `desktop` and `desktopShell` in
chezmoi's local config, review `chezmoi diff`, apply, and select the niri session at
login. Work identity, project roots, and Ubuntu's NetworkManager remain independent
of that choice. Recheck Canopa's NetworkManager backend if selecting Canopa instead
of Waybar.
