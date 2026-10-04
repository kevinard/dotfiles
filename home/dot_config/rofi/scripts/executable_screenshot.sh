#!/bin/sh
set -eu
selection=$(printf '%s\n' Region Screen Window | rofi -dmenu -p Screenshot)
case "$selection" in
    Region) niri msg action screenshot ;;
    Screen) niri msg action screenshot-screen ;;
    Window) niri msg action screenshot-window ;;
esac
