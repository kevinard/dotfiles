#!/bin/zsh

if [ "$ROFI_RETV" = 1 ]; then
  case $@ in
  "lock")
    loginctl lock-session
    ;;
  "suspend")
    loginctl lock-session && systemctl suspend
    ;;
  "logout")
    if [[ "$DESKTOP_SESSION" == 'hyprland' ]]; then
      # hyprctl dispatch exit 0
      loginctl terminate-session "$XDG_SESSION_ID"
    elif [[ "$DESKTOP_SESSION" == 'sway' ]]; then
      swaymsg exit
    fi
    ;;
  "reboot")
    systemctl reboot
    ;;
  "shutdown")
    systemctl poweroff
    ;;
  esac
  exit 0
fi

echo_option() {
  echo "$1\0display\x1f$2"
}

echo_option "lock" ""
echo_option "suspend" "󰏦"
echo_option "logout" "󰍃"
echo_option "reboot" "⟲"
echo_option "shutdown" ""
