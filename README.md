# Network-Connectivity-Diagnostics

A self-contained, **local** troubleshooting sandbox for **LU 1.6 – Network
Connectivity Diagnostics**.

> ⚠️ **This is a temporary educational lab, not the real CloudNotes project.**
> Everything runs on your own machine. There are no cloud accounts, no Docker,
> no Kubernetes, no nginx, no root privileges, no firewall changes, and no
> `pip install`. You only need **Python 3** and a terminal.

The lab ships with a deliberately **broken** networking environment. You will
diagnose and fix three independent failures using standard networking tools and
the application logs, then verify recovery end to end.

---

## Repository purpose

CloudNotes is a small note-taking service fronted by a lightweight reverse
proxy. In this lab it has been misconfigured in three ways. Your job is to act
as the on-call engineer: investigate, collect evidence, find the root cause,
apply the fix, and verify.

```
client ──► proxy (8080) ──► CloudNotes (9000) ──► weather-api.internal (local DNS)
```

## Learning objectives

By completing this lab you will practice:

- DNS resolution diagnosis (`dig`, `nslookup`, `host`, `ping`)
- TCP listener / interface-binding diagnosis (`ss`, `netstat`, `lsof`)
- HTTP and reverse-proxy diagnosis (`curl`, logs)
- Structured troubleshooting: **observe → hypothesize → test → fix → verify**

## Requirements

- Python 3.8+ (`python3`)
- A POSIX shell (Linux, macOS, WSL, or GitHub Codespaces)
- `curl` (preinstalled on all of the above)

## Quick start (under 5 minutes)

```bash
# 1. Start the lab (runs in the background)
bash scripts/start.sh

# 2. Confirm it is broken
bash scripts/healthcheck.sh
curl http://localhost:8080/health      # returns 502 until you fix things

# 3. Read the logs for evidence
cat logs/app.log
cat logs/proxy.log

# 4. Fix the three scenarios (see docs/ASSIGNMENT.md)

# 5. Verify recovery
bash scripts/healthcheck.sh
curl http://localhost:8080/health      # -> {"status": "healthy"}

# 6. Stop the lab when done
bash scripts/stop.sh
```

After every config change, restart so the servers reload:

```bash
bash scripts/stop.sh && bash scripts/start.sh
```

To return the lab to its original broken state at any time:

```bash
bash scripts/reset_lab.sh
```

## The three scenarios

| # | Layer | Symptom | Where to look |
|---|-------|---------|---------------|
| 1 | DNS  | `weather-api.internal` will not resolve | `logs/app.log`, `app/hosts_mapping.json` |
| 2 | TCP  | service only reachable on loopback | `logs/app.log`, `ss`/`netstat`/`lsof`, `app/config.json` |
| 3 | HTTP | proxy returns 502, upstream refused | `logs/proxy.log`, `app/config.json` |

Full step-by-step instructions are in **[docs/ASSIGNMENT.md](docs/ASSIGNMENT.md)**.

## Troubleshooting philosophy

1. **Reproduce** the failure with a command (`curl`, `dig`, `ss`).
2. **Read the logs** — every failure prints a clear error or warning.
3. **Form one hypothesis** about the root cause.
4. **Inspect the config** that the logs point to.
5. **Apply the smallest fix**, restart, and **re-verify**.
6. Never change two things at once.

## Verification commands

```bash
dig weather-api.internal +short            # scenario 1 context
curl http://localhost:9000/weather         # scenario 1 result
ss -tlnp | grep 9000                        # scenario 2 (use netstat/lsof if no ss)
curl http://localhost:9000/health           # scenario 2 result
curl http://localhost:8080/health           # scenario 3 / final result
bash scripts/healthcheck.sh                  # all-in-one status
```

Final success looks like:

```json
{
  "status": "healthy"
}
```

## File structure

```
Network-Connectivity-Diagnostics/
├── README.md
├── SUBMISSION.md
├── docs/
│   ├── ASSIGNMENT.md
│   └── INSTRUCTOR_NOTES.md
├── app/
│   ├── cloudnotes_server.py
│   ├── proxy_server.py
│   ├── config.json
│   └── hosts_mapping.json
├── logs/
│   ├── app.log
│   └── proxy.log
├── scripts/
│   ├── start.sh
│   ├── stop.sh
│   ├── healthcheck.sh
│   └── reset_lab.sh
└── data/
    └── notes.json
```

## Reminder

This repository is a **sandbox for learning only**. Delete it when you are done.
It is not production code and is not part of the main CloudNotes application.
