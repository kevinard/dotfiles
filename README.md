# Dotfiles

Personal configuration managed with chezmoi. Arch manages the niri/Canopa desktop
and terminal setup. Ubuntu 26.04 work manages terminal and development configuration;
GNOME/PaperWM and other desktop applications remain locally owned.

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
Package installation runs before files; Bat's theme cache rebuilds after them.
Arch also reconciles desktop startup links for the next login. Package installation
may prompt for sudo and upgrades Arch as a complete transaction.

Machine choices are stored in `~/.config/chezmoi/chezmoi.toml` under `[data]`:

| Setting | Arch personal | Ubuntu work |
| --- | --- | --- |
| `env` (identity) | `home` | `work` |
| `themeFlavour`, `themeColor` | Terminal and desktop theme | Terminal theme |
| `desktopShell` | `canopa` or `waybar` | Not used |
| `hasBattery`, `cpuVendor`, `gpuVendor` | Actual hardware | Not used |
| `powerManager` | `tlp`, `native` or `none` | Not managed |

The distribution determines scope: Arch uses niri; Ubuntu has no managed desktop.
There is no compositor choice or GNOME-on-Arch option. Old Ubuntu desktop/hardware
fields are ignored. `env` selects identity and optional work shell integration.
`projectPaths` is a TOML array, e.g. `["/home/me/projects", "/home/me/work projects"]`.
Older `onBattery`, `graphicsStack`, and whitespace-separated `projectsPaths` configs
still render; see the migration guide for explicit new settings.

Shared package requirements, palettes, and pinned dependencies are in
`home/.chezmoidata/`. Template helpers cover only repeated logic: machine defaults,
package composition and graphical unit relationships.
Application files remain beside their target paths. `private_` restricts target
permissions; it does not encrypt Git history. Keep credentials and private keys out
of the source tree.

```sh
scripts/check-dotfiles       # offline rendering and regression checks
chezmoi diff                # preview every deployment
desktop-health              # Arch-only checks inside the installed niri desktop
```

See [Arch installation](docs/arch-install.md), [root configuration](provision/arch/README.md),
[Ubuntu work scope](docs/work-laptop.md), and [maintenance/recovery](docs/maintenance.md).
