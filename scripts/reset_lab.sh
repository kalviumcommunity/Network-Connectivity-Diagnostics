#!/usr/bin/env bash
# Reset the lab to its original broken state.
# Restores the three intentional misconfigurations and clears live logs.
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Stop anything still running.
bash scripts/stop.sh >/dev/null 2>&1 || true

PY="$(command -v python3 || command -v python)"

echo "Restoring broken config.json (bind=127.0.0.1, upstream_port=9001)..."
"$PY" - <<'PY'
import json
p="app/config.json"
c=json.load(open(p))
c["cloudnotes"]["host"]="127.0.0.1"
c["cloudnotes"]["weather_api_host"]="weather-api.internal"
c["proxy"]["upstream_port"]=9001
json.dump(c,open(p,"w"),indent=2)
open(p,"a").write("\n")
PY

echo "Restoring broken hosts_mapping.json (weather host misspelled)..."
"$PY" - <<'PY'
import json
p="app/hosts_mapping.json"
data={
  "_comment":"Local DNS mapping table used by the CloudNotes internal resolver. CloudNotes looks up internal hostnames here instead of using public DNS. If a hostname is missing or misspelled, resolution fails.",
  "mappings":{"wether-api.internal":"127.0.0.1","notes-db.internal":"127.0.0.1"}
}
json.dump(data,open(p,"w"),indent=2)
open(p,"a").write("\n")
PY

echo "Resetting live logs to the seeded broken-state samples..."
cp logs/app.sample.log logs/app.log 2>/dev/null || : > logs/app.log
cp logs/proxy.sample.log logs/proxy.log 2>/dev/null || : > logs/proxy.log
rm -f logs/*.pid

echo "Lab reset to broken state. Run scripts/start.sh to begin."
