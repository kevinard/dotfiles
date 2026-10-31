#!/bin/sh
# Live-media/chroot/root commands must not run together in an unattended script.
printf '%s\n' 'Start with docs/setup.md for quick setup.' \
  'OS installation: docs/arch-install.md.' \
  'After first boot, as your user: ./setup.' \
  'This entry point performs no installation or disk changes.'
