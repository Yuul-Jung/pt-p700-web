#!/usr/bin/env bash
set -euo pipefail
# Ubuntu installer for Brother PT-P700 print bridge.
# Requires sudo for system packages, installed driver, and USB access rules.
sudo apt update
sudo apt install -y git cmake gettext libgd-dev libusb-1.0-0-dev python3-venv python3-pip
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
git clone --depth 1 https://git.familie-radermacher.ch/linux/ptouch-print.git "$WORKDIR/ptouch-print"
cd "$WORKDIR/ptouch-print"
./compile.sh
test -f build/ptouch-print
sudo install -m 0755 build/ptouch-print /usr/local/bin/ptouch-print
if [[ -f udev/20-usb-ptouch-permissions.rules ]]; then
  sudo install -m 0644 udev/20-usb-ptouch-permissions.rules /etc/udev/rules.d/20-usb-ptouch-permissions.rules
  sudo udevadm control --reload-rules
  sudo udevadm trigger --subsystem-match=usb
fi
cd - >/dev/null
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
echo 'Installation completed. Reconnect USB, check PLite light OFF, then run:'
echo '  lsusb | grep -i brother'
echo '  ptouch-print --info'
echo '  .venv/bin/python bridge.py'
