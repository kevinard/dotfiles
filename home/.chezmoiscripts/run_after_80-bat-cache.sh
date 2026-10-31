#!/bin/sh
set -eu
if command -v bat >/dev/null; then
    bat cache --build
fi
