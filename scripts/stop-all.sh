#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Stopping CloudNotes environment..."

if pgrep -f "python3 .*cloudnotes/app.py" >/dev/null 2>&1; then
  pkill -f "python3 .*cloudnotes/app.py"
  echo "Stopped Flask app."
fi

if pgrep -f "nginx: master process" >/dev/null 2>&1; then
  nginx -s stop -c "$ROOT_DIR/nginx/nginx.conf" || true
  echo "Stopped nginx."
fi

echo "Stop complete."
