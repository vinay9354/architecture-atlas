"""Tracking stub: a tiny, dependency-free HTTP service for Lab 12.

It stands in for AtlasMart's Tracking API so the lab can focus on Kubernetes, not on the application.
Standard library only (Python 3.12+). Endpoints:

    GET /healthz             200 {"status": "ok"} while the process can serve at all (liveness)
    GET /readyz              200 {"status": "ready"} after a short warm-up, 503 before it and during
                             shutdown (readiness)
    GET /shipments/{id}      200 with fixed JSON for any well-formed id (letters, digits, hyphen,
                             1-32 characters), 400 for a malformed id
    anything else            404 (405 for methods other than GET)

The response to /shipments/{id} includes which pod and node served it, read from the POD_NAME and
NODE_NAME environment variables (the Deployment sets them with the downward API), so you can see
Kubernetes spreading and replacing replicas.

On SIGTERM the server first reports not-ready, waits a short grace period so the Service stops sending
it new requests, then stops. Run `python tracking_stub.py --help` for options, or `--self-test` to start
the server on an ephemeral 127.0.0.1 port, call every endpoint once, and exit 0 on success.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import signal
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

VERSION = "0.1.0"
SHIPMENT_ID = re.compile(r"^[A-Za-z0-9-]{1,32}$")

# Fixed, obviously fictional data: no personal data and no delivery address (AtlasMart NFR-6).
FIXED_SHIPMENT = {
    "status": "IN_TRANSIT",
    "carrier": "carrier-a",
    "last_scan_at": "2026-11-21T09:00:00Z",
    "estimated_delivery": "2026-11-24",
}


class StubState:
    """Readiness bookkeeping shared by all request threads."""

    def __init__(self, ready_delay_s: float) -> None:
        self.started = time.monotonic()
        self.ready_delay_s = ready_delay_s
        self.shutting_down = threading.Event()

    def is_ready(self) -> bool:
        if self.shutting_down.is_set():
            return False
        return time.monotonic() - self.started >= self.ready_delay_s


def served_by() -> dict:
    return {
        "pod": os.environ.get("POD_NAME", socket.gethostname()),
        "node": os.environ.get("NODE_NAME", "unknown"),
    }


def make_handler(state: StubState, quiet: bool):
    class Handler(BaseHTTPRequestHandler):
        server_version = f"tracking-stub/{VERSION}"
        sys_version = ""

        def _send(self, code: int, body: dict) -> None:
            payload = json.dumps(body, sort_keys=True).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:  # noqa: N802 (name fixed by BaseHTTPRequestHandler)
            path = urlsplit(self.path).path
            if path == "/healthz":
                self._send(200, {"status": "ok"})
            elif path == "/readyz":
                if state.is_ready():
                    self._send(200, {"status": "ready"})
                else:
                    self._send(503, {"status": "not-ready"})
            elif path.startswith("/shipments/"):
                shipment_id = path[len("/shipments/"):]
                if not SHIPMENT_ID.match(shipment_id):
                    self._send(400, {"error": "shipment id must be 1-32 letters, digits, or hyphens"})
                    return
                body = {"shipment_id": shipment_id, **FIXED_SHIPMENT, "served_by": served_by()}
                self._send(200, body)
            else:
                self._send(404, {"error": "not found"})

        def _method_not_allowed(self) -> None:
            self._send(405, {"error": "method not allowed"})

        do_POST = do_PUT = do_DELETE = do_PATCH = _method_not_allowed  # noqa: N815

        def log_message(self, fmt: str, *args) -> None:
            if quiet:
                return
            # One JSON line per request on stderr: easy to read with `kubectl logs`.
            line = {"ts": round(time.time(), 3), "client": self.client_address[0], "msg": fmt % args}
            sys.stderr.write(json.dumps(line) + "\n")

    return Handler


def build_server(host: str, port: int, ready_delay_s: float, quiet: bool = False):
    state = StubState(ready_delay_s)
    server = ThreadingHTTPServer((host, port), make_handler(state, quiet))
    server.daemon_threads = True
    return server, state


def install_sigterm(server, state: StubState, grace_s: float) -> None:
    def stop_later() -> None:
        time.sleep(grace_s)
        server.shutdown()

    def on_sigterm(signum, frame) -> None:
        state.shutting_down.set()  # /readyz now returns 503; the endpoint is removed from the Service
        threading.Thread(target=stop_later, daemon=True).start()

    signal.signal(signal.SIGTERM, on_sigterm)


def self_test() -> int:
    """Start on an ephemeral loopback port, call each endpoint, and report."""
    server, _ = build_server("127.0.0.1", 0, ready_delay_s=0.0, quiet=True)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    expected = {"/healthz": 200, "/readyz": 200, "/shipments/AM-1001": 200, "/shipments/bad%20id": 400,
                "/nope": 404}
    failures = 0
    try:
        for path, want in expected.items():
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=3) as resp:
                    got = resp.status
            except urllib.error.HTTPError as err:
                got = err.code
                err.close()
            print(f"self-test {path:<22} expected {want} got {got}")
            failures += got != want
    finally:
        server.shutdown()
        server.server_close()
    print("self-test passed" if not failures else f"self-test FAILED ({failures})")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lab 12 tracking stub HTTP service")
    parser.add_argument("--host", default="127.0.0.1", help="bind address (the container uses 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--ready-delay", type=float,
                        default=float(os.environ.get("READY_DELAY_SECONDS", "2")),
                        help="seconds before /readyz reports ready (env READY_DELAY_SECONDS)")
    parser.add_argument("--shutdown-grace", type=float, default=2.0,
                        help="seconds between SIGTERM (not-ready) and stopping the listener")
    parser.add_argument("--quiet", action="store_true", help="no access log")
    parser.add_argument("--self-test", action="store_true", help="run a loopback self-test and exit")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    server, state = build_server(args.host, args.port, args.ready_delay, args.quiet)
    install_sigterm(server, state, args.shutdown_grace)
    host, port = server.server_address[:2]
    print(f"tracking-stub {VERSION} listening on {host}:{port} (ready after {args.ready_delay}s)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    print("tracking-stub stopped", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
