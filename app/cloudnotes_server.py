#!/usr/bin/env python3
"""
CloudNotes application server (lab edition).

Standard library only. No pip install required.

This server powers the Network-Connectivity-Diagnostics lab. It deliberately
contains networking misconfigurations that students must diagnose and fix:

  Scenario 1 (DNS):  it resolves the weather API hostname through a local
                     mapping file (app/hosts_mapping.json). A broken mapping
                     causes resolution to fail.

  Scenario 2 (TCP):  the listen interface is read from app/config.json. When
                     bound to 127.0.0.1 the service is only reachable from
                     loopback, not from other interfaces.

Endpoints:
  GET /health    -> {"status": "healthy"}
  GET /notes     -> contents of data/notes.json
  GET /weather   -> simulated weather, requires weather-api.internal to resolve
"""

import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(APP_DIR)
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
HOSTS_PATH = os.path.join(APP_DIR, "hosts_mapping.json")
NOTES_PATH = os.path.join(ROOT_DIR, "data", "notes.json")
LOG_PATH = os.path.join(ROOT_DIR, "logs", "app.log")

# ---------------------------------------------------------------------------
# Logging (file + stdout)
# ---------------------------------------------------------------------------
logger = logging.getLogger("cloudnotes")
logger.setLevel(logging.INFO)
_fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
_file = logging.FileHandler(LOG_PATH)
_file.setFormatter(_fmt)
_stream = logging.StreamHandler(sys.stdout)
_stream.setFormatter(_fmt)
logger.addHandler(_file)
logger.addHandler(_stream)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def resolve_internal_host(hostname):
    """Resolve an internal hostname using the local DNS mapping file.

    Returns the mapped IP address, or None if the name cannot be resolved.
    This mimics how an application uses DNS: if the name has no record, the
    lookup fails and the dependent feature breaks.
    """
    try:
        mapping = load_json(HOSTS_PATH).get("mappings", {})
    except (OSError, ValueError) as exc:
        logger.error("Unable to read hosts mapping file: %s", exc)
        return None

    ip = mapping.get(hostname)
    if ip is None:
        logger.error("Unable to resolve %s (no record in hosts_mapping.json)", hostname)
        return None

    logger.info("Resolved %s -> %s", hostname, ip)
    return ip


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------
class CloudNotesHandler(BaseHTTPRequestHandler):
    server_version = "CloudNotes/1.0"

    def _send_json(self, status, payload):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        logger.info("%s - %s", self.address_string(), fmt % args)

    def do_GET(self):
        path = self.path.split("?", 1)[0].rstrip("/")

        if path in ("", "/health"):
            self._send_json(200, {"status": "healthy", "service": "cloudnotes"})
            return

        if path == "/notes":
            try:
                self._send_json(200, load_json(NOTES_PATH))
            except (OSError, ValueError) as exc:
                logger.error("Failed to load notes: %s", exc)
                self._send_json(500, {"error": "could not load notes"})
            return

        if path == "/weather":
            host = self.server.weather_api_host
            ip = resolve_internal_host(host)
            if ip is None:
                self._send_json(
                    502,
                    {"error": "weather upstream unresolved", "host": host},
                )
                return
            self._send_json(
                200,
                {"host": host, "resolved_ip": ip, "temperature_c": 21, "summary": "clear"},
            )
            return

        self._send_json(404, {"error": "not found", "path": self.path})


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
def main():
    cfg = load_json(CONFIG_PATH)["cloudnotes"]
    host = cfg["host"]
    port = int(cfg["port"])
    weather_host = cfg["weather_api_host"]

    logger.info("Starting CloudNotes server")

    # Scenario 1 evidence: probe the weather dependency at boot.
    if resolve_internal_host(weather_host) is None:
        logger.error("Startup dependency check failed for %s", weather_host)

    # Scenario 2 evidence: warn when bound to loopback only.
    if host in ("127.0.0.1", "localhost"):
        logger.warning(
            "Service listening only on 127.0.0.1 - not reachable from other interfaces"
        )

    httpd = ThreadingHTTPServer((host, port), CloudNotesHandler)
    httpd.weather_api_host = weather_host
    logger.info("CloudNotes listening on %s:%s", host, port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("CloudNotes shutting down")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
