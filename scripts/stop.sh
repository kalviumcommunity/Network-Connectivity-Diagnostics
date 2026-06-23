#!/usr/bin/env bash
# Stop the CloudNotes lab processes started by start.sh.
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

stop_pid() {
  local name="$1" file="$2"
  if [ -f "$file" ]; then
    local pid
    pid="$(cat "$file")"
    if kill "$pid" 2>/dev/null; then
      echo "Stopped $name (PID $pid)"
    else
      echo "$name (PID $pid) not running"
    fi
    rm -f "$file"
  else
    echo "No PID file for $name"
  fi
}

stop_pid "CloudNotes" logs/cloudnotes.pid
stop_pid "Proxy" logs/proxy.pid
echo "Done."
