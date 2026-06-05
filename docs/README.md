# Network Connectivity Diagnostics

This repository is a hands-on troubleshooting lab for CloudNotes, a small Flask application behind an nginx reverse proxy.

## Objectives

- Diagnose a DNS resolution failure.
- Identify a TCP reachability issue caused by loopback-only binding.
- Fix an HTTP reverse proxy misconfiguration.

## Scenario Summary

The lab is intentionally broken in three independent ways:

1. `dns/broken-resolv.conf` points `api.weather.example` to a non-existent resolver.
2. `cloudnotes/config.py` binds Flask to `127.0.0.1` only, preventing remote clients from reaching the service.
3. `nginx/cloudnotes.conf` proxies traffic to the wrong backend port `9000`, causing `502 Bad Gateway`.

## Files of interest

- `cloudnotes/app.py` — Flask entrypoint.
- `cloudnotes/config.py` — runtime host and weather API configuration.
- `nginx/cloudnotes.conf` — reverse proxy upstream.
- `dns/broken-resolv.conf` — broken resolver configuration.
- `scripts/reset-environment.sh` — resets the broken assignment state.
- `docs/student-guide.md` — student troubleshooting instructions.

## Instructor notes

Use this lab when teaching troubleshooting methodology:

- Observe
- Gather evidence
- Identify layer
- Form hypothesis
- Fix root cause
- Verify

The lab supports evidence gathering with `dig`, `ping`, `traceroute`, `ss`, `iptables`, `curl`, and `tail`.
