#!/usr/bin/env bash
# Health check for the CloudNotes lab.
# Probes each layer so students see exactly which scenario is still broken.
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PY="$(command -v python3 || command -v python)"
PASS="PASS"; FAIL="FAIL"
rc=0

line() { printf '%-45s %s\n' "$1" "$2"; }

echo "=== CloudNotes lab health check ==="

# Scenario 1: DNS mapping for the weather host
WEATHER_HOST="$("$PY" - <<'PY'
import json
print(json.load(open("app/config.json"))["cloudnotes"]["weather_api_host"])
PY
)"
if "$PY" - "$WEATHER_HOST" <<'PY' >/dev/null 2>&1
import json,sys
m=json.load(open("app/hosts_mapping.json"))["mappings"]
sys.exit(0 if sys.argv[1] in m else 1)
PY
then line "Scenario 1 DNS ($WEATHER_HOST mapped)" "$PASS"
else line "Scenario 1 DNS ($WEATHER_HOST mapped)" "$FAIL"; rc=1
fi

# Scenario 2: CloudNotes bound to a non-loopback interface
BIND_HOST="$("$PY" - <<'PY'
import json
print(json.load(open("app/config.json"))["cloudnotes"]["host"])
PY
)"
if [ "$BIND_HOST" = "127.0.0.1" ] || [ "$BIND_HOST" = "localhost" ]; then
  line "Scenario 2 TCP (bind=$BIND_HOST)" "$FAIL"; rc=1
else
  line "Scenario 2 TCP (bind=$BIND_HOST)" "$PASS"
fi

# Scenario 3: proxy upstream matches CloudNotes port + end-to-end 200
MATCH="$("$PY" - <<'PY'
import json
c=json.load(open("app/config.json"))
print("ok" if c["proxy"]["upstream_port"]==c["cloudnotes"]["port"] else "bad")
PY
)"
if [ "$MATCH" = "ok" ]; then
  line "Scenario 3 proxy upstream port match" "$PASS"
else
  line "Scenario 3 proxy upstream port match" "$FAIL"; rc=1
fi

# End-to-end check through the proxy
CODE="$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/health 2>/dev/null || echo 000)"
if [ "$CODE" = "200" ]; then
  line "End-to-end curl localhost:8080/health" "$PASS ($CODE)"
else
  line "End-to-end curl localhost:8080/health" "$FAIL ($CODE)"; rc=1
fi

echo "==================================="
if [ "$rc" -eq 0 ]; then
  echo "All checks passed. Lab is healthy."
else
  echo "Some checks failed. Read the logs and fix the config."
fi
exit "$rc"
