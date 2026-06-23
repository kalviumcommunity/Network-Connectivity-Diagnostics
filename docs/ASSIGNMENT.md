# Assignment – LU 1.6 Network Connectivity Diagnostics

**Estimated time:** 30–45 minutes.

You are the on-call engineer for CloudNotes. The service is down. Three
independent misconfigurations are breaking connectivity at three different
layers. Fix them in order. Each fix moves you one layer closer to a working
end-to-end request through the proxy.

> Workflow for every scenario: **observe → read logs → hypothesize → inspect
> config → fix → restart → verify.**
> After any change to `app/config.json` or `app/hosts_mapping.json`, restart:
> `bash scripts/stop.sh && bash scripts/start.sh`

## Setup

```bash
bash scripts/start.sh
bash scripts/healthcheck.sh
```

You should see failures. Good — that is the starting point.

---

## Scenario 1 — DNS resolution failure

**Symptom:** CloudNotes cannot reach `weather-api.internal`. The `/weather`
endpoint returns `502`.

### Investigate (capture Screenshot 1)

```bash
cat logs/app.log
curl http://localhost:9000/weather
dig weather-api.internal +short
nslookup weather-api.internal
host weather-api.internal
ping -c1 weather-api.internal
cat app/hosts_mapping.json
```

The application log shows:

```
ERROR Unable to resolve weather-api.internal (no record in hosts_mapping.json)
```

`dig`/`nslookup`/`host`/`ping` confirm the name has **no public DNS record** —
it is an *internal* hostname that CloudNotes resolves through its own mapping
file, `app/hosts_mapping.json`. Look closely at the keys in that file.

### Root cause

The mapping file has a **misspelled** hostname: `wether-api.internal` instead of
`weather-api.internal`. CloudNotes asks for `weather-api.internal`, finds no
matching record, and fails.

### Fix

Edit `app/hosts_mapping.json` so the correct hostname is mapped:

```json
"mappings": {
  "weather-api.internal": "127.0.0.1",
  "notes-db.internal": "127.0.0.1"
}
```

### Verify (capture Screenshot 2)

```bash
bash scripts/stop.sh && bash scripts/start.sh
curl http://localhost:9000/weather
grep "Resolved weather-api.internal" logs/app.log
```

Expected: HTTP 200 with `resolved_ip`, and a log line
`INFO Resolved weather-api.internal -> 127.0.0.1`.

---

## Scenario 2 — TCP connectivity failure

**Symptom:** CloudNotes is bound to loopback only, so it is not reachable on the
machine's other interfaces (and the proxy in front of it is fragile).

### Investigate (capture Screenshot 3a)

```bash
grep -i listening logs/app.log
ss -tlnp | grep 9000          # Linux
netstat -an | grep 9000       # macOS / fallback
lsof -iTCP:9000 -sTCP:LISTEN  # macOS / Linux
```

The application log shows:

```
WARNING Service listening only on 127.0.0.1 - not reachable from other interfaces
```

`ss`/`netstat`/`lsof` confirm the socket is bound to `127.0.0.1:9000` rather than
`0.0.0.0:9000`.

### Root cause

`app/config.json` sets `cloudnotes.host` to `127.0.0.1`. The service must bind
to `0.0.0.0` to accept connections on all interfaces.

### Fix

Edit `app/config.json`:

```json
"cloudnotes": {
  "host": "0.0.0.0",
  "port": 9000,
  "weather_api_host": "weather-api.internal"
}
```

### Verify (capture Screenshot 3b)

```bash
bash scripts/stop.sh && bash scripts/start.sh
ss -tlnp | grep 9000          # now shows 0.0.0.0:9000
curl http://localhost:9000/health
```

Expected: socket bound to `0.0.0.0:9000`, and `curl` returns
`{"status": "healthy", "service": "cloudnotes"}`. The loopback warning is gone
from `logs/app.log`.

---

## Scenario 3 — HTTP / reverse proxy failure

**Symptom:** Requests through the proxy on `8080` return `502 Bad Gateway`.

### Investigate (capture Screenshot 4a)

```bash
curl -i http://localhost:8080/health
cat logs/proxy.log
cat app/config.json
```

The proxy log shows:

```
INFO  Forwarding /health -> 127.0.0.1:9001
ERROR Upstream connection refused: 127.0.0.1:9001
```

CloudNotes listens on `9000`, but the proxy forwards to `9001`.

### Root cause

`app/config.json` sets `proxy.upstream_port` to `9001`, which does not match
`cloudnotes.port` (`9000`). The proxy points at a port where nothing is
listening.

### Fix

Edit `app/config.json`:

```json
"proxy": {
  "host": "0.0.0.0",
  "port": 8080,
  "upstream_host": "127.0.0.1",
  "upstream_port": 9000
}
```

### Verify (capture Screenshot 4b)

```bash
bash scripts/stop.sh && bash scripts/start.sh
curl -i http://localhost:8080/health
grep "Relayed" logs/proxy.log
```

Expected: HTTP 200 through the proxy.

---

## Final verification (capture Screenshot 5)

```bash
bash scripts/healthcheck.sh
curl http://localhost:8080/health
```

All checks should report `PASS`, and the final command returns:

```json
{
  "status": "healthy"
}
```

You have now diagnosed and repaired failures at the DNS, TCP, and HTTP layers.

See **[../SUBMISSION.md](../SUBMISSION.md)** for what to submit.
