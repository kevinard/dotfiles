#!/bin/sh
set -eu
if command -v bat >/dev/null; then
    bat cache --build
elif command -v batcat >/dev/null; then
    batcat cache --build
fi
