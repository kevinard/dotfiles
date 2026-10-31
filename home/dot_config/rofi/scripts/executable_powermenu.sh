#!/bin/sh
set -eu
if [ "${ROFI_RETV:-0}" = 1 ]; then
    case "$*" in
        *Lock) desktop-lock ;;
        *Suspend) desktop-lock && systemctl suspend ;;
        *Hibernate) desktop-lock && systemctl hibernate ;;
        *Logout) niri msg action quit ;;
        *Reboot) systemctl reboot ;;
        *Shutdown) systemctl poweroff ;;
    esac
else
    printf '%s\n' '  Lock' '  Suspend' '  Hibernate' '  Logout' '  Reboot' '  Shutdown'
fi
