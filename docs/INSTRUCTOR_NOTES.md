# Instructor Notes — Network-Connectivity-Diagnostics

Internal reference for graders and facilitators. **Do not share with students
before submission.**

## Design goals

- 100% local; runs on Linux, macOS, WSL, and GitHub Codespaces.
- Python standard library only (`http.server`, `socketserver`, `socket`,
  `json`, `logging`). No pip, Docker, nginx, root, or firewall changes.
- Three independent failures, one per network layer (DNS → TCP → HTTP).
- Every failure produces a clear, discoverable log line and has exactly one
  primary root cause. No race conditions, no hidden tricks.
- Completable by an average beginner in 30–45 minutes.

## Architecture

```
curl ──► proxy_server.py (8080) ──► cloudnotes_server.py (9000)
                                          └─► resolve weather-api.internal
                                              via app/hosts_mapping.json
```

Both servers log to stdout and to `logs/`. `start.sh` backgrounds both and
records PIDs in `logs/*.pid`.

## The three intentional bugs

| # | File | Broken value | Correct value | Log evidence |
|---|------|--------------|---------------|--------------|
| 1 | `app/hosts_mapping.json` | key `wether-api.internal` (typo) | `weather-api.internal` | `ERROR Unable to resolve weather-api.internal` |
| 2 | `app/config.json` `cloudnotes.host` | `127.0.0.1` | `0.0.0.0` | `WARNING Service listening only on 127.0.0.1` |
| 3 | `app/config.json` `proxy.upstream_port` | `9001` | `9000` | `ERROR Upstream connection refused: 127.0.0.1:9001` |

### Why each is discoverable

1. **DNS** — `dig`/`nslookup`/`host`/`ping` show the name has no public record,
   steering students to the app's own resolver file. The log names the exact
   hostname; the typo is visible by eye in the small JSON file.
2. **TCP** — the boot warning plus `ss`/`netstat`/`lsof` output both point at the
   loopback binding; the config key is obvious.
3. **HTTP** — the proxy log prints the upstream target and the refusal; comparing
   `proxy.upstream_port` to `cloudnotes.port` reveals the mismatch.

## Grading rubric alignment

| Screenshot | Evidence expected |
|------------|-------------------|
| 1 | DNS investigation: `dig`/`nslookup`/`host` + `ERROR Unable to resolve...` |
| 2 | DNS fix: `/weather` returns 200, `INFO Resolved weather-api.internal` |
| 3 | TCP diagnosis (`ss`/`netstat` on 127.0.0.1) and recovery (`0.0.0.0`, /health 200) |
| 4 | Proxy diagnosis (`Upstream connection refused`) and recovery (200 via 8080) |
| 5 | `healthcheck.sh` all PASS + `curl localhost:8080/health` healthy |

## Reset / regrade

`scripts/reset_lab.sh` stops the processes, rewrites both config files back to
the broken values, and restores the seeded sample logs. Use it between students
or for a clean redo.

## Common student mistakes

- Forgetting to restart after editing config (servers cache config at boot).
- Fixing `127.0.0.1` references inside the proxy `upstream_host` (not needed;
  `127.0.0.1:9000` is correct for the proxy → app hop).
- Editing the `_comment` field or adding trailing commas, breaking JSON. Have
  them run `python3 -m json.tool app/config.json` to validate.

## Manual full solution check

```bash
bash scripts/reset_lab.sh
# apply the three fixes
python3 - <<'PY'
import json
c=json.load(open("app/config.json"))
c["cloudnotes"]["host"]="0.0.0.0"
c["proxy"]["upstream_port"]=9000
json.dump(c,open("app/config.json","w"),indent=2); open("app/config.json","a").write("\n")
m=json.load(open("app/hosts_mapping.json"))
m["mappings"]["weather-api.internal"]=m["mappings"].pop("wether-api.internal")
json.dump(m,open("app/hosts_mapping.json","w"),indent=2); open("app/hosts_mapping.json","a").write("\n")
PY
bash scripts/stop.sh && bash scripts/start.sh
bash scripts/healthcheck.sh   # expect all PASS
```
