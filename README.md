# Dotfiles

Personal configuration managed with chezmoi. The supported machines are Arch with
niri/Canopa and Ubuntu 26.04 with GNOME/PaperWM. Ubuntu can select niri separately
when its official packages are available.

`.chezmoiroot` points to `home/`. Only that tree is home configuration. Documentation,
validation, and root-owned Arch reference files live alongside it and are never
copied into `$HOME` by an apply.

```sh
chezmoi init https://github.com/kevinard/dotfiles.git
chezmoi diff
chezmoi apply
```

Use the actual remote if this checkout has a different repository name. Read
[bootstrap and migration](docs/bootstrap.md) before the first apply of this branch.
Package installation runs before files; session reconciliation runs after them.
The latter changes startup links for the next login and does not replace running
desktop processes. Package installation may prompt for sudo and upgrades Arch as
a complete transaction.

Machine choices are stored in `~/.config/chezmoi/chezmoi.toml` under `[data]`:

| Choice | Arch personal | Ubuntu work now | Ubuntu work later |
| --- | --- | --- | --- |
| `env` (identity) | `home` | `work` | `work` |
| `desktop` | `niri` | `gnome` | `niri` |
| `desktopShell` | `canopa` | `gnome` | `waybar` or `canopa` |
| `powerManager` | `tlp` on laptop | `native` | `native` |

`hasBattery` is a boolean; `cpuVendor` and `gpuVendor` are independent choices.
`projectPaths` is a TOML array, e.g. `["/home/me/projects", "/home/me/work projects"]`.
The distribution comes from chezmoi's OS-release data. Older `env`, `onBattery`,
`graphicsStack`, and whitespace-separated `projectsPaths` configs still render;
see the migration guide for explicit new settings.

Shared package requirements, palettes, and pinned dependencies are in
`home/.chezmoidata/`. Template helpers cover only repeated logic: machine defaults,
package composition, graphical unit relationships, and Firefox preferences.
Application files remain beside their target paths. `private_` restricts target
permissions; it does not encrypt Git history. Keep credentials and private keys out
of the source tree.

```sh
scripts/check-dotfiles       # offline rendering and regression checks
desktop-health              # read-only checks inside the installed desktop
chezmoi diff                # preview every deployment
```

See [Arch installation](docs/arch-install.md), [root configuration](provision/arch/README.md),
[GNOME/PaperWM](docs/gnome.md), and [maintenance/recovery](docs/maintenance.md).
