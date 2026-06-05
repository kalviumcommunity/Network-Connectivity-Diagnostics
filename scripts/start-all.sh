#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Starting CloudNotes environment..."

# Start the Flask application.
if pgrep -f "python3 .*cloudnotes/app.py" >/dev/null 2>&1; then
  echo "CloudNotes already running."
else
  nohup python3 cloudnotes/app.py > logs/cloudnotes.log 2>&1 &
  echo "Started CloudNotes on 127.0.0.1:5000"
fi

# Start nginx.
if pgrep -f "nginx: master process" >/dev/null 2>&1; then
  echo "nginx already running."
else
  nginx -c "$ROOT_DIR/nginx/nginx.conf"
  echo "Started nginx with configuration from nginx/nginx.conf"
fi

echo "Environment started. Use ./scripts/healthcheck.sh to verify." 
