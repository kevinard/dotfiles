#!/bin/sh

# exit immediately if bitwarden is already in $PATH
type bw >/dev/null 2>&1 && exit

case "$(hostnamectl | grep Operating | cut -d':' -f2 | cut -d' ' -f2)" in
Arch)
	sudo pacman -S --needed bitwarden-cli
	;;
Ubuntu)
	sudo apt install build-essential
	npm install -g @bitwarden/cli
	;;
*)
	echo "unsupported OS"
	exit 1
	;;
esac
