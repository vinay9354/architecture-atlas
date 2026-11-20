#!/usr/bin/env python3
"""Lab 05 Part A: lost updates on a shared counter, and the lock that prevents them.

Standard library only. Several threads each add 1 to a shared counter many times. Each increment
is written as three steps on purpose: read the value, yield, write value + 1. The yield
(time.sleep(0)) invites the interpreter to switch threads between the read and the write, which is
exactly the window in which another thread's increment can be overwritten (a lost update).
Without the yield the race still exists, but under the GIL it shows up rarely and unpredictably.

Two engines:
  threads  Real threads (default). Results vary from run to run; that is what a race looks like.
  sim      A deterministic scheduler that interleaves the same read and write steps of N logical
           threads using random.Random(--seed). Same seed, same interleaving, same result, and it
           prints the first interleaving that lost an update.

Run:  python counter_race.py --mode racy locked
      python counter_race.py --engine sim --mode racy locked --seed 3
"""
import argparse
import json
import random
import sys
import threading
import time
from collections import deque


class Counter:
    def __init__(self):
        self.value = 0


def racy_worker(counter, n, force_yield=True):
    for _ in range(n):
        value = counter.value      # read
        if force_yield:
            time.sleep(0)          # yield: another thread may run here
        counter.value = value + 1  # write: overwrites whatever happened in between


def locked_worker(counter, n, lock):
    for _ in range(n):
        with lock:                 # read, yield, and write happen as one critical section
            value = counter.value
            time.sleep(0)
            counter.value = value + 1


def run_threads(mode, threads, increments, force_yield=True):
    counter, lock = Counter(), threading.Lock()
    if mode == "racy":
        workers = [threading.Thread(target=racy_worker, args=(counter, increments, force_yield))
                   for _ in range(threads)]
    else:
        workers = [threading.Thread(target=locked_worker, args=(counter, increments, lock)) for _ in range(threads)]
    t0 = time.perf_counter()
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    expected = threads * increments
    return {"engine": "threads", "mode": mode, "threads": threads, "expected": expected,
            "final": counter.value, "lost_updates": expected - counter.value,
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1)}


def run_sim(mode, threads, increments, seed):
    """Deterministic interleaving of read and write steps; returns metrics and the first lost update."""
    rng = random.Random(seed)
    counter = 0
    remaining = [increments] * threads
    pending = [None] * threads     # value read and not yet written, per logical thread
    lock_owner = None
    recent = deque(maxlen=6)
    first_loss = None
    steps = 0
    while True:
        runnable = [t for t in range(threads)
                    if pending[t] is not None
                    or (remaining[t] > 0 and (mode == "racy" or lock_owner is None))]
        if not runnable:
            break
        t = rng.choice(runnable)
        steps += 1
        if pending[t] is None:     # step 1: (acquire the lock if any, then) read
            if mode == "locked":
                lock_owner = t
            pending[t] = counter
            recent.append(f"T{t} reads {counter}")
        else:                      # step 2: write read + 1 (then release the lock if any)
            overwritten = counter - pending[t]
            recent.append(f"T{t} writes {pending[t] + 1}" + (f"  <- {overwritten} update(s) lost" if overwritten else ""))
            if overwritten and first_loss is None:
                first_loss = list(recent)
            counter = pending[t] + 1
            pending[t] = None
            remaining[t] -= 1
            if mode == "locked":
                lock_owner = None
    expected = threads * increments
    return {"engine": "sim", "mode": mode, "threads": threads, "expected": expected, "final": counter,
            "lost_updates": expected - counter, "steps": steps, "first_loss": first_loss}


def print_table(rows):
    cols = [("engine", "engine"), ("mode", "mode"), ("threads", "threads"), ("expected", "expected"),
            ("final", "final"), ("lost_updates", "lost")]
    print(" | ".join(f"{h:>10}" for _, h in cols))
    print("-+-".join("-" * 10 for _ in cols))
    for r in rows:
        print(" | ".join(f"{str(r[k]):>10}" for k, _ in cols))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--engine", choices=["threads", "sim"], default="threads")
    ap.add_argument("--mode", nargs="+", choices=["racy", "locked"], default=["racy", "locked"])
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--increments", type=int, default=2000, help="increments per thread")
    ap.add_argument("--no-yield", action="store_true", help="drop the forced yield between read and write")
    ap.add_argument("--seed", type=int, default=3, help="interleaving seed for --engine sim")
    ap.add_argument("--json", help="also write results to this file")
    args = ap.parse_args(argv)
    if args.engine == "sim":
        rows = [run_sim(m, args.threads, args.increments, args.seed) for m in args.mode]
    else:
        rows = [run_threads(m, args.threads, args.increments, not args.no_yield) for m in args.mode]
    print(f"engine={args.engine} threads={args.threads} increments/thread={args.increments}"
          + (f" seed={args.seed}" if args.engine == "sim" else "")
          + (" yield=off" if args.no_yield and args.engine == "threads" else ""))
    print()
    print_table(rows)
    for r in rows:
        if r.get("first_loss"):
            print(f"\nFirst lost update ({r['mode']}), last steps before it:")
            for line in r["first_loss"]:
                print(f"  {line}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
