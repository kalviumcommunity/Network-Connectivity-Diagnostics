#!/usr/bin/env bash
# Start the CloudNotes lab: CloudNotes server + reverse proxy.
# Standard library Python only. No root, no docker, no pip.
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PY="$(command -v python3 || command -v python)"
if [ -z "$PY" ]; then
  echo "python3 not found. Install Python 3 and retry." >&2
  exit 1
fi

mkdir -p logs

# The servers log to logs/app.log and logs/proxy.log themselves, so we send
# the redundant stdout/stderr to /dev/null to avoid duplicate log lines.
echo "Starting CloudNotes server..."
"$PY" app/cloudnotes_server.py >/dev/null 2>&1 &
echo $! > logs/cloudnotes.pid

echo "Starting reverse proxy..."
"$PY" app/proxy_server.py >/dev/null 2>&1 &
echo $! > logs/proxy.pid

sleep 1
echo
echo "Lab started."
echo "  CloudNotes PID: $(cat logs/cloudnotes.pid)"
echo "  Proxy PID:      $(cat logs/proxy.pid)"
echo
echo "Try:   curl http://localhost:8080/health"
echo "Logs:  logs/app.log  logs/proxy.log"
echo "Stop:  scripts/stop.sh"
