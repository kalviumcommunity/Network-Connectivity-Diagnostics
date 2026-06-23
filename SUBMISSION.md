# Submission Guide — LU 1.6 Network Connectivity Diagnostics

Submit a single document (PDF or Markdown) containing the five screenshots
below plus short captions. Total effort: 30–45 minutes.

## What to capture

| # | Screenshot | Command(s) that produce the evidence |
|---|------------|--------------------------------------|
| 1 | **DNS investigation** | `cat logs/app.log`, `dig weather-api.internal +short`, `nslookup weather-api.internal`, `cat app/hosts_mapping.json` |
| 2 | **DNS fix verification** | `curl http://localhost:9000/weather` returning 200, `grep "Resolved weather-api.internal" logs/app.log` |
| 3 | **TCP diagnosis + recovery** | before: `ss -tlnp \| grep 9000` showing `127.0.0.1`; after fix + restart: `0.0.0.0:9000` and `curl http://localhost:9000/health` |
| 4 | **HTTP proxy diagnosis + recovery** | before: `cat logs/proxy.log` showing `Upstream connection refused`; after fix + restart: `curl -i http://localhost:8080/health` returning 200 |
| 5 | **Final operational verification** | `bash scripts/healthcheck.sh` (all PASS) and `curl http://localhost:8080/health` |

## For each scenario, write 2–3 sentences

- **Symptom:** what failed and how you reproduced it.
- **Evidence:** the log line or command output that revealed it.
- **Root cause:** the exact file and value that was wrong.
- **Fix + verification:** what you changed and the command proving recovery.

## Final expected output

```bash
curl http://localhost:8080/health
```

```json
{
  "status": "healthy"
}
```

## Checklist before you submit

- [ ] All five screenshots included and labeled.
- [ ] Each scenario has symptom / evidence / root cause / fix / verification.
- [ ] `scripts/healthcheck.sh` shows every check `PASS`.
- [ ] `curl http://localhost:8080/health` returns `{"status": "healthy"}`.
- [ ] You can explain *why* each fix works, not just *what* you changed.

## Tips

- Restart after every config change: `bash scripts/stop.sh && bash scripts/start.sh`.
- Validate JSON edits: `python3 -m json.tool app/config.json`.
- To start over from the broken state: `bash scripts/reset_lab.sh`.
