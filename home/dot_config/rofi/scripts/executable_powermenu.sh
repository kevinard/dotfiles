#!/bin/zsh

if [ "$ROFI_RETV" = 1 ]; then
  case $@ in
  *Lock)
    loginctl lock-session
    ;;
  *Suspend)
    loginctl lock-session && systemctl suspend
    ;;
  *Hibernate)
    loginctl lock-session && systemctl hibernate
    ;;
  *Logout)
    if [[ "$DESKTOP_SESSION" == 'hyprland' ]]; then
      # hyprctl dispatch exit 0
      loginctl terminate-session "$XDG_SESSION_ID"
    elif [[ "$DESKTOP_SESSION" == 'sway' ]]; then
      swaymsg exit
    fi
    ;;
  *Reboot)
    systemctl reboot
    ;;
  *Shutdown)
    systemctl poweroff
    ;;
  esac
  exit 0
fi

echo -e "  Lock\n  Suspend\n  Hibernate\n  Logout\n  Reboot\n  Shutdown"
