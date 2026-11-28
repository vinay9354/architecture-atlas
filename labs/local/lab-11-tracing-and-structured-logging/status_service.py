#!/usr/bin/env python3
"""Lab 11: "status-service", the downstream service. Standard library only. Teaching code.

Routes
  GET /status/{shipment_id}   current status of a shipment
  GET /eta/{shipment_id}      estimated delivery date

It reads `traceparent`, continues the caller's trace when the header is valid, and writes one JSON
log line per request (see telemetry.py for the fields).

Two faults are planted for you to find from the logs, not from this docstring's details:
  * one route is slow for one group of shipments;
  * one shipment makes one route fail.
(Spoilers are in the lab's solution file.)

Run standalone:
  python3 status_service.py --port 8012 --log logs/status-service.log
"""
import argparse
import json
import random
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import telemetry
import traceparent

SERVICE = "status-service"
ROUTES = [(re.compile(r"^/status/(SHP-[0-9]{4})$"), "/status/{shipment_id}"),
          (re.compile(r"^/eta/(SHP-[0-9]{4})$"), "/eta/{shipment_id}")]
STATUSES = ["label created", "picked up", "in transit", "at depot", "out for delivery", "delivered"]


def build_catalog():
    """50 fictional shipments, SHP-1000 to SHP-1049. No addresses or customer data (NFR-6)."""
    catalog = {}
    for i in range(50):
        carrier = "carrier-c" if i % 10 == 7 else ("carrier-a" if i % 2 == 0 else "carrier-b")
        catalog[f"SHP-{1000 + i}"] = {"carrier": carrier, "status": STATUSES[i % len(STATUSES)],
                                      "seq": 3 + i % 7, "eta": f"2026-12-{1 + i % 5:02d}"}
    return catalog


SHIPMENTS = build_catalog()
SLOW_CARRIER = "carrier-c"     # the ETA for this carrier is "recomputed from full event history"
FAILING_SHIPMENT = "SHP-1013"  # its status read hits a simulated event-store timeout


class StatusServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, addr, log_path, seed=12, slow_ms=120, echo=False):
        super().__init__(addr, Handler)
        self.logger = telemetry.JsonLogger(SERVICE, log_path, echo=echo)
        self.ids = traceparent.IdGenerator(seed)
        self.ids_lock = threading.Lock()
        self.rng = random.Random(seed + 1000)
        self.slow_ms = slow_ms


class Handler(BaseHTTPRequestHandler):
    server: StatusServer

    def log_message(self, *args):  # silence http.server's own access log, we write JSON instead
        pass

    def do_GET(self):  # noqa: N802 (http.server naming)
        started = time.perf_counter()
        span = telemetry.start_span(self.headers.get("traceparent"), self.server.ids, self.server.ids_lock)
        route, shipment_id = "unmatched", None
        for pattern, template in ROUTES:
            m = pattern.match(self.path)
            if m:
                route, shipment_id = template, m.group(1)
        status, body, message = self.respond(route, shipment_id)
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
        shipment = SHIPMENTS.get(shipment_id or "", {})
        extra = {"method": "GET", "shipment_id": shipment_id, "carrier": shipment.get("carrier"),
                 "tp_in": span.tp_in}
        if message:
            extra["message"] = message
        self.server.logger.request(
            level="ERROR" if status >= 500 else ("WARN" if status >= 400 else "INFO"),
            trace_id=span.trace_id, span_id=span.span_id, parent_span_id=span.parent_span_id,
            route=route, status=status, duration_ms=(time.perf_counter() - started) * 1000, **extra)

    def respond(self, route, shipment_id):
        with self.server.ids_lock:
            work_ms = self.server.rng.uniform(1.0, 4.0)   # ordinary lookup time
        time.sleep(work_ms / 1000)
        if route == "unmatched":
            return 404, {"error": "no such route"}, None
        shipment = SHIPMENTS.get(shipment_id)
        if shipment is None:
            return 404, {"error": "unknown shipment"}, None
        if route == "/status/{shipment_id}":
            if shipment_id == FAILING_SHIPMENT:
                time.sleep(0.025)
                return 503, {"error": "status temporarily unavailable"}, "event store read timed out"
            return 200, {"shipment_id": shipment_id, "status": shipment["status"], "seq": shipment["seq"]}, None
        if shipment["carrier"] == SLOW_CARRIER:
            time.sleep(self.server.slow_ms / 1000)   # full event-history replay
        return 200, {"shipment_id": shipment_id, "eta": shipment["eta"]}, None


def make_server(host, port, log_path, **kwargs):
    return StatusServer((host, port), log_path, **kwargs)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8012)
    p.add_argument("--log", default="status-service.log")
    p.add_argument("--seed", type=int, default=12)
    p.add_argument("--slow-ms", type=int, default=120)
    p.add_argument("--echo", action="store_true", help="also print each log line")
    args = p.parse_args(argv)
    server = make_server(args.host, args.port, args.log, seed=args.seed, slow_ms=args.slow_ms, echo=args.echo)
    print(f"status-service on http://{args.host}:{server.server_address[1]}, logging to {args.log}",
          file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
