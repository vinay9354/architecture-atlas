"""Probe client for Lab 12: fetch one URL and print the outcome, or idle until stopped.

Used inside the two test-client Pods to check the NetworkPolicy from inside the cluster
(port-forward traffic does not exercise NetworkPolicy):

    python /app/probe.py http://tracking-stub/shipments/AM-1001     # one request, exit 0 or 1
    python /app/probe.py --idle                                     # sleep until SIGTERM

Standard library only.
"""
from __future__ import annotations

import argparse
import signal
import sys
import threading
import urllib.error
import urllib.request


def fetch(url: str, timeout_s: float) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout_s) as resp:
            return True, f"HTTP {resp.status} {resp.read().decode(errors='replace')}"
    except urllib.error.HTTPError as err:
        with err:
            return False, f"HTTP {err.code} {err.read().decode(errors='replace')}"
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        reason = getattr(err, "reason", err)
        return False, f"FAILED {type(reason).__name__}: {reason}"


def idle() -> int:
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda signum, frame: stop.set())
    stop.wait()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch a URL once, or idle until SIGTERM")
    parser.add_argument("url", nargs="?")
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--idle", action="store_true")
    args = parser.parse_args(argv)
    if args.idle:
        return idle()
    if not args.url:
        parser.error("a URL is required unless --idle is given")
    ok, message = fetch(args.url, args.timeout)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
