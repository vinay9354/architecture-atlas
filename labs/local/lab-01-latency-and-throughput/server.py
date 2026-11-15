#!/usr/bin/env python3
"""Lab 01 target service: a tiny HTTP server with a configurable service time and worker limit.

Standard library only. Each request to /status/<id> "works" for --service-ms milliseconds
(plus optional jitter) and returns a small JSON document. --max-workers limits how many requests
are served at once; requests beyond that wait for a free worker, which is what makes latency rise
with load. Simplifications: the work is a sleep, not CPU; there is no database; no TLS.

Run:  python server.py --port 8080 --service-ms 20 --max-workers 8
"""
import argparse
import json
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Config:
    service_s = 0.020
    jitter_s = 0.0
    workers = threading.BoundedSemaphore(8)
    rng = random.Random(1)
    rng_lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # keep-alive so the load generator reuses connections

    def do_GET(self):  # noqa: N802 (http.server naming)
        if self.path == "/health":
            self._reply(200, {"status": "ok"})
            return
        if not self.path.startswith("/status/"):
            self._reply(404, {"error": "not found"})
            return
        order_id = self.path[len("/status/"):]
        with Config.workers:  # wait for a free worker, then "work"
            with Config.rng_lock:
                jitter = Config.rng.uniform(0, Config.jitter_s) if Config.jitter_s else 0.0
            time.sleep(Config.service_s + jitter)
        self._reply(200, {"order_id": order_id, "status": "in_transit", "served_at": time.time()})

    def _reply(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # noqa: A002 - silence per-request logging
        return


def make_server(host, port, service_ms, jitter_ms, max_workers):
    Config.service_s = service_ms / 1000.0
    Config.jitter_s = jitter_ms / 1000.0
    Config.workers = threading.BoundedSemaphore(max_workers)
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    return server


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--service-ms", type=float, default=20.0, help="simulated work per request")
    ap.add_argument("--jitter-ms", type=float, default=0.0, help="uniform random extra time, 0..jitter")
    ap.add_argument("--max-workers", type=int, default=8, help="requests served concurrently")
    args = ap.parse_args()
    server = make_server(args.host, args.port, args.service_ms, args.jitter_ms, args.max_workers)
    print(f"serving on http://{args.host}:{args.port}  service={args.service_ms} ms "
          f"jitter={args.jitter_ms} ms workers={args.max_workers}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
