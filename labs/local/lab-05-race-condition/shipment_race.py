#!/usr/bin/env python3
"""Lab 05 Part B: a lost update on a database row, fixed with optimistic concurrency or an atomic update.

Standard library only (sqlite3). Two workers, each with its own database connection, apply carrier
scan events to the same shipment row. Every scan must increment scan_count and set last_location.
The database file lives in a temporary directory that is removed when the script exits.

Modes:
  racy        SELECT the row, compute in Python, UPDATE with the computed values. Two separate
              statements with a gap between them: the other worker's write can land in the gap and
              is then overwritten (a lost update).
  optimistic  Same read-then-write, but the UPDATE only applies if the row's version is still the
              one that was read (WHERE version = ?). Zero rows changed means someone else won;
              re-read and retry.
  atomic      One statement does the read-modify-write inside the database
              (SET scan_count = scan_count + 1), so there is no gap to race in.

Results with real threads vary from run to run. --seed only picks the location names; the
interleaving is up to the operating system and the interpreter.

Run:  python shipment_race.py --mode racy optimistic atomic --scans 300
"""
import argparse
import json
import os
import random
import sqlite3
import sys
import tempfile
import threading
import time

SHIPMENT_ID = "SHP-0001"
HUBS = ["Sorting hub A", "Sorting hub B", "Line haul", "Local depot", "Out for delivery"]


def connect(path):
    db = sqlite3.connect(path, timeout=30, isolation_level=None)  # autocommit: one transaction per statement
    db.execute("PRAGMA busy_timeout = 30000")
    return db


def setup(path):
    db = connect(path)
    db.execute("PRAGMA journal_mode = WAL")   # readers do not block the writer
    db.execute("PRAGMA synchronous = OFF")    # lab speed; never do this with data you care about
    db.execute("CREATE TABLE shipments (shipment_id TEXT PRIMARY KEY, last_location TEXT NOT NULL, "
               "scan_count INTEGER NOT NULL, version INTEGER NOT NULL)")
    db.execute("INSERT INTO shipments VALUES (?, 'Label created', 0, 0)", (SHIPMENT_ID,))
    db.close()


def apply_scan_racy(db, location, stats):
    count, = db.execute("SELECT scan_count FROM shipments WHERE shipment_id = ?", (SHIPMENT_ID,)).fetchone()
    time.sleep(0)  # the gap between read and write, made a little wider on purpose
    db.execute("UPDATE shipments SET scan_count = ?, last_location = ? WHERE shipment_id = ?",
               (count + 1, location, SHIPMENT_ID))


def apply_scan_optimistic(db, location, stats):
    while True:
        count, version = db.execute("SELECT scan_count, version FROM shipments WHERE shipment_id = ?",
                                    (SHIPMENT_ID,)).fetchone()
        time.sleep(0)
        cur = db.execute("UPDATE shipments SET scan_count = ?, last_location = ?, version = version + 1 "
                         "WHERE shipment_id = ? AND version = ?", (count + 1, location, SHIPMENT_ID, version))
        if cur.rowcount == 1:
            return
        stats["conflicts"] += 1  # someone else changed the row since we read it: re-read and retry


def apply_scan_atomic(db, location, stats):
    db.execute("UPDATE shipments SET scan_count = scan_count + 1, last_location = ?, version = version + 1 "
               "WHERE shipment_id = ?", (location, SHIPMENT_ID))


APPLY = {"racy": apply_scan_racy, "optimistic": apply_scan_optimistic, "atomic": apply_scan_atomic}


def worker(path, mode, locations, stats, start):
    db = connect(path)
    try:
        start.wait()
        for loc in locations:
            APPLY[mode](db, loc, stats)
    finally:
        db.close()


def run_mode(mode, workers=2, scans=300, seed=5, directory=None):
    """Run one mode in a fresh database; returns metrics. The database is deleted afterwards."""
    rng = random.Random(seed)
    with tempfile.TemporaryDirectory(prefix="lab05-", dir=directory) as tmp:
        path = os.path.join(tmp, "shipments.db")
        setup(path)
        stats = [{"conflicts": 0} for _ in range(workers)]
        start = threading.Barrier(workers)
        threads = [threading.Thread(target=worker,
                                    args=(path, mode, [rng.choice(HUBS) for _ in range(scans)], stats[i], start))
                   for i in range(workers)]
        t0 = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.perf_counter() - t0
        db = connect(path)
        count, version = db.execute("SELECT scan_count, version FROM shipments WHERE shipment_id = ?",
                                    (SHIPMENT_ID,)).fetchone()
        db.close()
    expected = workers * scans
    return {"mode": mode, "workers": workers, "expected": expected, "scan_count": count,
            "lost_updates": expected - count, "conflicts_retried": sum(s["conflicts"] for s in stats),
            "version": version, "elapsed_ms": round(elapsed * 1000, 1)}


def print_table(rows):
    cols = [("mode", "mode"), ("workers", "workers"), ("expected", "expected"), ("scan_count", "scan_count"),
            ("lost_updates", "lost"), ("conflicts_retried", "retries"), ("elapsed_ms", "elapsed ms")]
    print(" | ".join(f"{h:>10}" for _, h in cols))
    print("-+-".join("-" * 10 for _ in cols))
    for r in rows:
        print(" | ".join(f"{str(r[k]):>10}" for k, _ in cols))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", nargs="+", choices=list(APPLY), default=list(APPLY))
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--scans", type=int, default=300, help="scan events per worker")
    ap.add_argument("--seed", type=int, default=5, help="picks location names only")
    ap.add_argument("--json", help="also write results to this file")
    args = ap.parse_args(argv)
    print(f"workers={args.workers} scans/worker={args.scans} sqlite={sqlite3.sqlite_version} seed={args.seed}")
    print()
    rows = [run_mode(m, args.workers, args.scans, args.seed) for m in args.mode]
    print_table(rows)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
