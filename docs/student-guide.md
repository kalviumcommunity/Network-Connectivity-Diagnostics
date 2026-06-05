# Student Guide: Network Connectivity Diagnostics

## Goal

Fix all three faults and verify end-to-end access to the CloudNotes app through nginx.

## Fault 1 — DNS Resolution Failure

Evidence:

- `curl http://api.weather.example` fails.
- `dig api.weather.example` returns no answer or SERVFAIL.
- `cat /etc/resolv.conf` shows a broken nameserver.

Investigation commands:

```bash
sudo cat /etc/resolv.conf
dig api.weather.example
nslookup api.weather.example
```

Expected root cause:

- `/etc/resolv.conf` points to `10.255.255.1`, a dead resolver.

Fix:

- Replace `/etc/resolv.conf` with a valid resolver, for example:

```bash
sudo cp dns/broken-resolv.conf /etc/resolv.conf
# then edit /etc/resolv.conf to use a valid nameserver, e.g. 1.1.1.1
```

Verification:

```bash
dig api.weather.example
```

should return `status: NOERROR` and a valid A record.

## Fault 2 — TCP Reachability Failure

Evidence:

- The application is running locally on `127.0.0.1:5000`.
- Remote access fails, but local `curl http://127.0.0.1:5000/health` succeeds.
- `ss -tlnp` or `netstat -tlnp` shows Flask listening only on `127.0.0.1:5000`.
- `iptables -L -n` does not show a permissive `ACCEPT` rule for port 5000.

Investigation commands:

```bash
ping localhost
traceroute 127.0.0.1
ss -tlnp | grep 5000
sudo iptables -L -n | grep 5000
```

Expected root cause:

- `cloudnotes/config.py` binds Flask to `127.0.0.1` instead of `0.0.0.0`.

Fix:

- Change `FLASK_HOST = "0.0.0.0"` in `cloudnotes/config.py`.
- Restart the app.

Verification:

```bash
curl http://127.0.0.1:5000/health
```

returns success.

## Fault 3 — HTTP Reverse Proxy Failure

Evidence:

- Direct backend access works, but `curl -v http://localhost/` returns `502 Bad Gateway`.
- `tail -f logs/nginx-error.log` shows `connect() failed` and `upstream connection refused`.

Investigation commands:

```bash
curl -v http://localhost/
tail -n 20 logs/nginx-error.log
```

Expected root cause:

- `nginx/cloudnotes.conf` points `proxy_pass` to `http://127.0.0.1:9000;` while CloudNotes listens on `5000`.

Fix:

- Update `nginx/cloudnotes.conf` to use `server 127.0.0.1:5000;`.
- Reload nginx.

Verification:

```bash
curl -v http://localhost/
```

returns `HTTP/1.1 200 OK`.

## Final verification

After fixing all faults, verify end-to-end:

```bash
curl http://localhost/health
curl http://localhost/weather
```

## Validation checklist

- [ ] `dig api.weather.example` resolves successfully.
- [ ] Local backend health is `healthy`.
- [ ] Flask listens on `0.0.0.0:5000`.
- [ ] nginx reverse proxy returns `200 OK`.
- [ ] Logs contain evidence of the original failure modes.

## Notes

This lab is designed to enforce layered troubleshooting:

- DNS
- Routing/TCP
- HTTP/reverse proxy

Do not bypass the failure modes by disabling services or changing the test endpoints.
