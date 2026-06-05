#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Checking CloudNotes health..."
if curl -sS --fail http://127.0.0.1/health | grep -q 'healthy'; then
  echo "Local backend is healthy."
else
  echo "Backend healthcheck failed." >&2
  exit 1
fi

if curl -sS --fail http://localhost/ >/dev/null 2>&1; then
  echo "nginx reverse proxy is responding."
else
  echo "nginx reverse proxy failed." >&2
  exit 1
fi
