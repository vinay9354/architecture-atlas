#!/usr/bin/env python3
"""Lab 11: one-command run. Starts status-service and tracking-api in this process on free ports of
127.0.0.1, runs the load script against tracking-api, stops both, and leaves the two log files.

  python3 run_lab.py                      propagation on, logs in ./logs
  python3 run_lab.py --no-propagate --out logs-broken
"""
import argparse
import os
import sys
import threading

import load
import status_service
import tracking_api


def start(server):
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://{server.server_address[0]}:{server.server_address[1]}"


def run(out_dir, requests, seed=11, propagate=True, slow_ms=120, stdout=sys.stdout):
    os.makedirs(out_dir, exist_ok=True)
    status_log = os.path.join(out_dir, "status-service.log")
    api_log = os.path.join(out_dir, "tracking-api.log")
    status = status_service.make_server("127.0.0.1", 0, status_log, seed=seed + 1, slow_ms=slow_ms)
    status_url = start(status)
    api = tracking_api.make_server("127.0.0.1", 0, status_url, api_log, seed=seed, propagate=propagate)
    api_url = start(api)
    print(f"status-service {status_url}   tracking-api {api_url}   "
          f"propagation {'on' if propagate else 'OFF'}", file=stdout)
    try:
        summary = load.run(api_url, requests, seed, out=stdout)
    finally:
        for server in (api, status):
            server.shutdown()
            server.server_close()
    print(f"logs: {api_log} {status_log}", file=stdout)
    return {"summary": summary, "logs": [api_log, status_log]}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--out", default="logs")
    p.add_argument("--requests", type=int, default=200)
    p.add_argument("--seed", type=int, default=11)
    p.add_argument("--slow-ms", type=int, default=120)
    p.add_argument("--no-propagate", action="store_true")
    args = p.parse_args(argv)
    run(args.out, args.requests, args.seed, not args.no_propagate, args.slow_ms)
    return 0


if __name__ == "__main__":
    sys.exit(main())
