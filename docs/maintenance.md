# Maintenance and recovery

`scripts/check-dotfiles` renders synthetic profiles without downloading externals,
installing packages, applying files, enabling units, or contacting secret providers.
It validates generated formats, exercises portable shell startup and helper behavior,
and enforces the complete terminal-only Ubuntu target set. If available, niri and
Canopa also validate their configurations. CI reports missing optional validators;
a passing render does not prove packages exist on Ubuntu or that suspend works on
the hardware.

At a dependency update, change one recorded revision/version and checksum together.
The shell archives are pinned to the checkouts installed when this branch was made;
oh-my-zsh self updates are disabled. Lazygit on Ubuntu uses its official 0.65.1
archive, checked against the release checksum manifest. Yubico and other work desktop
applications are installed and updated outside this repository.
Mise follows its supported signed package source, rather than a frozen
2024 binary. The personal nvim repository is the deliberate rolling exception:
retain its Git checkout, review its changes, and commit your own editor changes there.
Mise activates once per interactive zsh; its shims are also available to GUI launches.
Existing Volta/rbenv/tfenv paths are retained when their directories exist. Migrate
their selected tool versions explicitly before removing those directories.

Bat's four vendored themes come from `catppuccin/bat` commit
`6810349b28055dce54076712fc05fc68da4b8ec0`. Font assets remain vendored. GTK uses
installed Adwaita on Arch and the desktop's dark-style preference; Catppuccin remains
selected for terminal, shell, Git, bat, tmux and niri. No downloaded script modifies
root icon directories. Custom cursors were replaced by distribution-provided cursors
to remove an unchecked latest-release dependency.

The following desktop policies apply only to Arch. Cliphist retains 500 items and
skips selections marked sensitive by wl-clipboard.
This relies on the producer supplying that marker: manually verify KeePassXC copies
never enter `cliphist list`. Clear old history with `cliphist wipe` if necessary;
apply does not erase existing history. KeePassXC locks its database with the session
and declines expired browser credentials. Niri hides the password database from
captures and Canopa/Dunst banners from screencasts. Verify the chosen capture tool
actually honors compositor capture restrictions.

Firefox's speculative graphics/cache settings and tracking skip lists were removed
from user.js. Removing a user.js entry does not reset an existing prefs.js value.
On each existing profile, reset the removed `media.memory_*`, `media.cache_*`,
`gfx.*`, `layers.gpu-process.enabled`, `widget.dmabuf.force-enabled`,
`urlclassifier.*skipURLs`/`trackingSkipURLs` and `geo.provider.network.url` overrides
that came from the old user.js in `about:config`. Reset only deliberate old entries,
not every preference under those prefixes. Keep the old source revision as a checklist.
Check `about:support` for actual video decoding and compositing before adding new tuning.

Thunar's mutable window geometry is no longer replayed. KeePassXC still writes its
own preference file: close it before reviewing/applying changes and use
`chezmoi diff`/`chezmoi merge` for intentional local preferences. Do not re-add runtime
state indiscriminately. App configuration is separate from backups of its data.

Keep encrypted independent backups of documents, project work, Firefox profiles,
the password database and recovery information. Store a LUKS recovery key and header
backup off the encrypted disk; test recovery before relying on TPM unlock. Keep at
least one copy outside the laptop. Btrfs snapshots and a bootable LTS kernel help
rollback but do not survive disk failure. Choose a backup tool/destination explicitly,
test a small restore regularly, and check SMART health and periodic Btrfs scrub.
Firmware and Secure Boot changes require a tested recovery boot path.
