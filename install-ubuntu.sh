#!/usr/bin/env bash
set -euo pipefail
# Ubuntu installer for Brother PT-P700 print bridge.
# Requires sudo for system packages, installed driver, and USB access rules.
cd "$(dirname "$(realpath "$0")")"
PROJECT_DIR="$(pwd)"
sudo apt update
sudo apt install -y git cmake gettext libgd-dev libusb-1.0-0-dev python3-venv python3-pip
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
git clone https://git.familie-radermacher.ch/linux/ptouch-print.git "$WORKDIR/ptouch-print"
cd "$WORKDIR/ptouch-print"
./compile.sh
test -f build/ptouch-print
sudo install -m 0755 build/ptouch-print /usr/local/bin/ptouch-print
# Allow active desktop session to access the exact PT-P700 USB device.
printf '%s\n' 'SUBSYSTEM=="usb", ATTR{idVendor}=="04f9", ATTR{idProduct}=="2061", TAG+="uaccess"' \
  | sudo tee /etc/udev/rules.d/70-brother-pt-p700.rules >/dev/null
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=usb
cd "$PROJECT_DIR"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
echo 'Installation completed. Reconnect USB, check PLite light OFF, then run:'
echo '  lsusb | grep -i brother'
echo '  ptouch-print --info'
echo '  bash enable-autostart.sh  # once, to run bridge at login'
