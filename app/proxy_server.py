#!/usr/bin/env python3
"""
Lightweight reverse proxy for CloudNotes (lab edition).

Standard library only. No nginx, apache, or docker required.

This proxy listens on proxy.host:proxy.port (default 0.0.0.0:8080) and forwards
every request to the upstream CloudNotes server defined in app/config.json.

Scenario 3 (HTTP / proxy): the upstream port in config.json is intentionally
wrong (9001) while CloudNotes actually listens on 9000. Every forwarded request
therefore fails with "connection refused" until the upstream is corrected.
"""

import json
import logging
import os
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(APP_DIR)
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
LOG_PATH = os.path.join(ROOT_DIR, "logs", "proxy.log")

logger = logging.getLogger("proxy")
logger.setLevel(logging.INFO)
_fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
_file = logging.FileHandler(LOG_PATH)
_file.setFormatter(_fmt)
_stream = logging.StreamHandler(sys.stdout)
_stream.setFormatter(_fmt)
logger.addHandler(_file)
logger.addHandler(_stream)


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


class ProxyHandler(BaseHTTPRequestHandler):
    server_version = "CloudNotesProxy/1.0"

    def log_message(self, fmt, *args):
        logger.info("%s - %s", self.address_string(), fmt % args)

    def _bad_gateway(self, reason):
        body = json.dumps({"error": "bad gateway", "reason": reason}).encode("utf-8")
        self.send_response(502)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        up_host = self.server.upstream_host
        up_port = self.server.upstream_port

        raw_request = (
            f"GET {self.path} HTTP/1.0\r\n"
            f"Host: {up_host}:{up_port}\r\n"
            "Connection: close\r\n\r\n"
        ).encode("utf-8")

        logger.info("Forwarding %s -> %s:%s", self.path, up_host, up_port)

        try:
            with socket.create_connection((up_host, up_port), timeout=5) as sock:
                sock.sendall(raw_request)
                chunks = []
                while True:
                    data = sock.recv(4096)
                    if not data:
                        break
                    chunks.append(data)
            response = b"".join(chunks)
        except ConnectionRefusedError:
            logger.error("Upstream connection refused: %s:%s", up_host, up_port)
            self._bad_gateway(f"upstream connection refused at {up_host}:{up_port}")
            return
        except (socket.timeout, OSError) as exc:
            logger.error("Upstream error %s:%s - %s", up_host, up_port, exc)
            self._bad_gateway(str(exc))
            return

        # Relay the raw upstream response (status line + headers + body) verbatim.
        self.wfile.write(response)
        logger.info("Relayed %d bytes from upstream", len(response))


def main():
    cfg = load_config()["proxy"]
    host = cfg["host"]
    port = int(cfg["port"])

    logger.info("Starting CloudNotes proxy")
    httpd = ThreadingHTTPServer((host, port), ProxyHandler)
    httpd.upstream_host = cfg["upstream_host"]
    httpd.upstream_port = int(cfg["upstream_port"])
    logger.info(
        "Proxy listening on %s:%s -> upstream %s:%s",
        host,
        port,
        httpd.upstream_host,
        httpd.upstream_port,
    )

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Proxy shutting down")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
