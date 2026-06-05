#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Resetting assignment environment to broken state..."

# Restore application code and proxy configuration from git if available.
if [ -d .git ]; then
  git checkout -- cloudnotes/app.py nginx/cloudnotes.conf scripts/reset-environment.sh 2>/dev/null || true
fi

# Restore broken DNS resolver configuration.
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run with sudo to write /etc/resolv.conf and manage nginx." >&2
  exit 1
fi
cp dns/broken-resolv.conf /etc/resolv.conf
chmod 644 /etc/resolv.conf

echo "Broken DNS configuration restored to /etc/resolv.conf"

echo "Restarting services..."
./scripts/stop-all.sh
./scripts/start-all.sh

echo "Reset complete."
