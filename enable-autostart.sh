#!/usr/bin/env bash
set -euo pipefail
# Run from the checked-out pt-p700-web folder, as the desktop user.
cd "$(dirname "$(realpath "$0")")"
if [[ ! -f ".venv/bin/python" || ! -f "bridge.py" ]]; then
  echo "Install project dependencies first: bash install-ubuntu.sh" >&2
  exit 1
fi
mkdir -p "$HOME/.config/systemd/user"
service="$HOME/.config/systemd/user/pt-p700-bridge.service"
cat > "$service" <<EOF
[Unit]
Description=PT-P700 local web print bridge
After=default.target

[Service]
Type=simple
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/.venv/bin/python $(pwd)/bridge.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now pt-p700-bridge.service
systemctl --user --no-pager --full status pt-p700-bridge.service || true
echo "Bridge will start automatically when you sign into this Ubuntu account."
