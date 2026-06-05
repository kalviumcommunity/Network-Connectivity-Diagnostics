# Network Connectivity Diagnostics

A hands-on troubleshooting repository for CloudNotes, a Flask application exposed through nginx with three independent networking faults.

## Lab design

The repository includes three realistic, layer-separated failures:

1. DNS resolution is broken by a bad nameserver in `/etc/resolv.conf`.
2. The Flask service binds only to `127.0.0.1`, causing TCP reachability failure for remote clients.
3. nginx proxies to the wrong backend port, producing `502 Bad Gateway`.

## Repository structure

- `cloudnotes/` — Flask application source code and dependencies.
- `dns/` — broken resolver configuration and troubleshooting notes.
- `nginx/` — reverse proxy configuration.
- `scripts/` — start, stop, reset, and health check scripts.
- `logs/` — sample logs with observable failure evidence.
- `docs/` — instructor and student materials.
- `.github/` — repository metadata.

## Setup

1. Install Python dependencies:

```bash
python3 -m pip install -r cloudnotes/requirements.txt
```

2. Reset the environment to the broken state:

```bash
sudo ./scripts/reset-environment.sh
```

3. Use the student guide:

```bash
less docs/student-guide.md
```

## Completion criteria

- `dig api.weather.example` resolves successfully after fixing DNS.
- Flask listens on `0.0.0.0:5000`.
- `curl http://localhost/` returns `HTTP/1.1 200 OK` after fixing nginx.
- All failures are diagnosed through observable evidence in logs and network tools.
