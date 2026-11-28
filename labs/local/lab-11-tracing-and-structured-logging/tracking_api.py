#!/usr/bin/env python3
"""Lab 11: "tracking-api", the front service. Standard library only. Teaching code.

Route
  GET /track/{shipment_id}   calls status-service twice (/status, then /eta) and combines the answers

For every request it reads an incoming `traceparent` (continuing the trace if valid, restarting it
if missing or invalid), creates its own span, sends `traceparent: 00-<trace_id>-<its span id>-<flags>`
on each outgoing call so status-service's spans become its children, and writes one JSON log line.

--no-propagate removes the outgoing header: status-service then starts a new trace for every call,
and each request falls apart into disconnected traces.

Run standalone (start status-service first):
  python3 tracking_api.py --port 8011 --status-url http://127.0.0.1:8012 --log logs/tracking-api.log
"""
import argparse
import json
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import telemetry
import traceparent

SERVICE = "tracking-api"
TRACK_RE = re.compile(r"^/track/(SHP-[0-9]{4})$")
ROUTE = "/track/{shipment_id}"
DOWNSTREAM_TIMEOUT_S = 2.0


class TrackingServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, addr, status_url, log_path, seed=11, propagate=True, echo=False):
        super().__init__(addr, Handler)
        self.status_url = status_url.rstrip("/")
        self.logger = telemetry.JsonLogger(SERVICE, log_path, echo=echo)
        self.ids = traceparent.IdGenerator(seed)
        self.ids_lock = threading.Lock()
        self.propagate = propagate


def call(url, span, propagate):
    """GET url as part of `span`; return (status, parsed JSON body or None)."""
    headers = {"Accept": "application/json"}
    if propagate:
        headers["traceparent"] = span.outgoing_traceparent()
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=DOWNSTREAM_TIMEOUT_S) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        e.close()
        return e.code, None
    except (urllib.error.URLError, TimeoutError):
        return 599, None   # 599: no response at all (connection refused or timeout), lab convention


class Handler(BaseHTTPRequestHandler):
    server: TrackingServer

    def log_message(self, *args):
        pass

    def do_GET(self):  # noqa: N802 (http.server naming)
        started = time.perf_counter()
        span = telemetry.start_span(self.headers.get("traceparent"), self.server.ids, self.server.ids_lock)
        m = TRACK_RE.match(self.path)
        shipment_id = m.group(1) if m else None
        status, body, message = self.respond(span, shipment_id)
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
        extra = {"method": "GET", "shipment_id": shipment_id, "tp_in": span.tp_in}
        if message:
            extra["message"] = message
        self.server.logger.request(
            level="ERROR" if status >= 500 else ("WARN" if status >= 400 else "INFO"),
            trace_id=span.trace_id, span_id=span.span_id, parent_span_id=span.parent_span_id,
            route=ROUTE if m else "unmatched", status=status,
            duration_ms=(time.perf_counter() - started) * 1000, **extra)

    def respond(self, span, shipment_id):
        if shipment_id is None:
            return 404, {"error": "no such route"}, None
        base, prop = self.server.status_url, self.server.propagate
        s_status, s_body = call(f"{base}/status/{shipment_id}", span, prop)
        if s_status == 404:
            return 404, {"error": "unknown shipment"}, None
        if s_status != 200:
            return 502, {"error": "tracking temporarily unavailable"}, f"status-service /status returned {s_status}"
        e_status, e_body = call(f"{base}/eta/{shipment_id}", span, prop)
        eta = e_body["eta"] if e_status == 200 else None   # degrade: show status without an ETA
        message = None if e_status == 200 else f"status-service /eta returned {e_status}, ETA omitted"
        return 200, {"shipment_id": shipment_id, "status": s_body["status"], "eta": eta}, message


def make_server(host, port, status_url, log_path, **kwargs):
    return TrackingServer((host, port), status_url, log_path, **kwargs)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8011)
    p.add_argument("--status-url", default="http://127.0.0.1:8012")
    p.add_argument("--log", default="tracking-api.log")
    p.add_argument("--seed", type=int, default=11)
    p.add_argument("--no-propagate", action="store_true", help="do not send traceparent downstream")
    p.add_argument("--echo", action="store_true", help="also print each log line")
    args = p.parse_args(argv)
    server = make_server(args.host, args.port, args.status_url, args.log, seed=args.seed,
                         propagate=not args.no_propagate, echo=args.echo)
    print(f"tracking-api on http://{args.host}:{server.server_address[1]} -> {args.status_url}, "
          f"propagation {'on' if server.propagate else 'OFF'}, logging to {args.log}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
