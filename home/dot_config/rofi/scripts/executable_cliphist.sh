#!/bin/sh
# Script mode shares the clipboard picker logic; no shared /tmp preview directory.
set -eu
exec desktop-control clipboard-mode "$@"
