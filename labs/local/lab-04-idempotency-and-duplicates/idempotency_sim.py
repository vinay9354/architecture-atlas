#!/usr/bin/env python3
"""Lab 04 idempotency simulator: retries over a lossy channel, idempotency keys, and an inbox table.

Standard library only (sqlite3 in memory for the stores), deterministic for the same --seed.

The scenario is a fictional AtlasMart payment capture API. A client captures payment for each order.
Requests always reach the server, but the response is lost with probability --loss-rate, so the
client sees a timeout and retries (up to --max-attempts). The server cannot tell a retry from a new
request unless the client says so.

Modes:
  no-key  Each request creates a charge. A lost response plus a retry charges the order twice.
  key     The client sends one idempotency key per order and reuses it on every retry. The server
          stores the key and its response in the same transaction as the charge; a repeated key gets
          the stored response back (a replay) and no new charge. A UNIQUE constraint does the work.
  inbox   Downstream, a consumer receives PaymentCaptured events with at-least-once delivery
          (an event is redelivered when the consumer crashes after committing but before
          acknowledging). A naive consumer applies every delivery; an inbox consumer records each
          message ID in a table with a primary key, in the same transaction as its side effect, and
          skips IDs it has already seen.

Run:  python idempotency_sim.py --mode no-key key inbox --orders 1000 --loss-rate 0.2
"""
import argparse
import hashlib
import json
import random
import sqlite3
import sys
import uuid

SCHEMA = """
CREATE TABLE charges (
    charge_id    INTEGER PRIMARY KEY,
    order_id     TEXT    NOT NULL,
    amount_cents INTEGER NOT NULL,
    captured_seq INTEGER NOT NULL
);
CREATE TABLE idempotency_keys (
    idem_key     TEXT    PRIMARY KEY,      -- the UNIQUE constraint that makes retries safe
    request_hash TEXT    NOT NULL,
    status_code  INTEGER NOT NULL,
    response     TEXT    NOT NULL
);
"""

CONSUMER_SCHEMA = """
CREATE TABLE order_payments (
    row_id       INTEGER PRIMARY KEY,
    order_id     TEXT    NOT NULL,
    amount_cents INTEGER NOT NULL
);
CREATE TABLE inbox (
    message_id   TEXT    PRIMARY KEY      -- one row per message ever processed
);
"""


def make_uuid(rng):
    return str(uuid.UUID(int=rng.getrandbits(128), version=4))


class PaymentService:
    """The server side. Responses are JSON strings so a replay can be compared byte for byte."""

    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript(SCHEMA)
        self.seq = 0  # stands in for a timestamp; every new charge gets a new value

    def _charge(self, request):
        self.seq += 1
        cur = self.db.execute("INSERT INTO charges (order_id, amount_cents, captured_seq) VALUES (?, ?, ?)",
                              (request["order_id"], request["amount_cents"], self.seq))
        body = {"charge_id": cur.lastrowid, "order_id": request["order_id"],
                "amount_cents": request["amount_cents"], "status": "captured", "captured_seq": self.seq}
        return 201, json.dumps(body, sort_keys=True)

    def capture(self, request, idem_key=None):
        """Return (status_code, response_json, replayed)."""
        if idem_key is None:
            with self.db:  # one transaction
                status, body = self._charge(request)
            return status, body, False
        request_hash = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        with self.db:
            try:
                # Reserve the key first. A second request with the same key fails here, before charging.
                self.db.execute("INSERT INTO idempotency_keys (idem_key, request_hash, status_code, response) "
                                "VALUES (?, ?, 0, '')", (idem_key, request_hash))
            except sqlite3.IntegrityError:
                stored_hash, status, body = self.db.execute(
                    "SELECT request_hash, status_code, response FROM idempotency_keys WHERE idem_key = ?",
                    (idem_key,)).fetchone()
                if stored_hash != request_hash:
                    return 422, json.dumps({"error": "idempotency key reused with a different request"}), False
                return status, body, True
            status, body = self._charge(request)
            self.db.execute("UPDATE idempotency_keys SET status_code = ?, response = ? WHERE idem_key = ?",
                            (status, body, idem_key))
        return status, body, False


def run_api(mode, orders, loss_rate, max_attempts, seed):
    """Capture payment for every order through a channel that loses responses; return metrics."""
    # Separate generators so both modes see the same amounts and the same lost responses.
    amount_rng, loss_rng, key_rng = random.Random(seed), random.Random(seed + 1), random.Random(seed + 2)
    server = PaymentService()
    requests_sent = lost = gave_up = replays = 0
    retried_orders = identical_on_retry = 0
    expected_cents = 0
    for n in range(orders):
        order_id = f"AM-{100000 + n}"
        amount = amount_rng.randrange(1000, 20001)  # 10.00 to 200.00, a labelled lab assumption
        expected_cents += amount
        request = {"order_id": order_id, "amount_cents": amount}
        key = make_uuid(key_rng) if mode == "key" else None
        received = first_body = None
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            requests_sent += 1
            status, body, replayed = server.capture(request, key)  # the request always arrives
            replays += replayed
            if first_body is None:
                first_body = body  # what the server said the first time, seen only by this harness
            if loss_rng.random() < loss_rate:
                lost += 1  # response lost on the way back; the client times out and retries
                continue
            received = body
            break
        if received is None:
            gave_up += 1  # outcome unknown to the client, although the server did charge
        elif attempts > 1:
            retried_orders += 1
            identical_on_retry += received == first_body  # byte-for-byte the response that was lost
    charges, charged_cents = server.db.execute("SELECT COUNT(*), COALESCE(SUM(amount_cents), 0) FROM charges").fetchone()
    double_charged = server.db.execute(
        "SELECT COUNT(*) FROM (SELECT order_id FROM charges GROUP BY order_id HAVING COUNT(*) > 1)").fetchone()[0]
    result = {
        "mode": mode, "orders": orders, "requests": requests_sent, "lost_responses": lost, "gave_up": gave_up,
        "charges": charges, "double_charged_orders": double_charged, "extra_charges": charges - orders,
        "overcharged": round((charged_cents - expected_cents) / 100, 2), "replays": replays,
        "retried_orders": retried_orders, "identical_on_retry": identical_on_retry,
    }
    if mode == "key":
        # A client bug: the same key with a different amount must be refused, not replayed.
        some_key = server.db.execute("SELECT idem_key FROM idempotency_keys LIMIT 1").fetchone()[0]
        status, _, _ = server.capture({"order_id": "AM-100000", "amount_cents": 1}, some_key)
        result["key_reuse_status"] = status
    return result


def delivery_log(events, redelivery_rate, rng):
    """At-least-once delivery: each delivery is redelivered later with probability redelivery_rate."""
    pending = list(events)
    log = []
    while pending:
        ev = pending.pop(0)
        log.append(ev)
        if rng.random() < redelivery_rate:  # consumer committed but crashed before the ack
            pending.insert(rng.randrange(len(pending) + 1), ev)
    return log


def consume(log, use_inbox):
    db = sqlite3.connect(":memory:")
    db.executescript(CONSUMER_SCHEMA)
    applied = dropped = 0
    for ev in log:
        with db:  # side effect and inbox row commit together, or not at all
            if use_inbox:
                try:
                    db.execute("INSERT INTO inbox (message_id) VALUES (?)", (ev["message_id"],))
                except sqlite3.IntegrityError:
                    dropped += 1
                    continue
            db.execute("INSERT INTO order_payments (order_id, amount_cents) VALUES (?, ?)",
                       (ev["order_id"], ev["amount_cents"]))
            applied += 1
    total = db.execute("SELECT COALESCE(SUM(amount_cents), 0) FROM order_payments").fetchone()[0]
    doubled = db.execute(
        "SELECT COUNT(*) FROM (SELECT order_id FROM order_payments GROUP BY order_id HAVING COUNT(*) > 1)").fetchone()[0]
    return applied, dropped, doubled, total


def run_inbox(orders, redelivery_rate, seed):
    rng = random.Random(seed + 3)
    events = []
    for n in range(orders):
        events.append({"message_id": make_uuid(rng), "type": "PaymentCaptured",
                       "order_id": f"AM-{100000 + n}", "amount_cents": rng.randrange(1000, 20001)})
    log = delivery_log(events, redelivery_rate, rng)
    expected = sum(e["amount_cents"] for e in events)
    rows = []
    for name, use_inbox in (("naive", False), ("inbox", True)):
        applied, dropped, doubled, total = consume(log, use_inbox)
        rows.append({"consumer": name, "events": len(events), "deliveries": len(log), "applied": applied,
                     "dropped_duplicates": dropped, "double_applied_orders": doubled,
                     "ledger_total": round(total / 100, 2), "expected_total": round(expected / 100, 2)})
    return rows


def print_table(rows, cols):
    print(" | ".join(f"{h:>12}" for _, h in cols))
    print("-+-".join("-" * 12 for _ in cols))
    for r in rows:
        print(" | ".join(f"{str(r[k]):>12}" for k, _ in cols))


API_COLS = [("mode", "mode"), ("requests", "requests"), ("lost_responses", "lost resp"), ("gave_up", "gave up"),
            ("charges", "charges"), ("double_charged_orders", "double chgd"), ("overcharged", "overcharged"),
            ("replays", "replays"), ("retried_orders", "retried ok"), ("identical_on_retry", "identical")]
INBOX_COLS = [("consumer", "consumer"), ("events", "events"), ("deliveries", "deliveries"), ("applied", "applied"),
              ("dropped_duplicates", "dup dropped"), ("double_applied_orders", "double appl"),
              ("ledger_total", "ledger total"), ("expected_total", "expected")]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", nargs="+", choices=["no-key", "key", "inbox"], default=["no-key", "key", "inbox"])
    ap.add_argument("--orders", type=int, default=1000)
    ap.add_argument("--loss-rate", type=float, default=0.2, help="chance that one response is lost")
    ap.add_argument("--max-attempts", type=int, default=4, help="client attempts per order, including the first")
    ap.add_argument("--redelivery-rate", type=float, default=0.1, help="chance that one delivery is redelivered")
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--json", help="also write results to this file")
    args = ap.parse_args(argv)
    print(f"orders={args.orders} loss_rate={args.loss_rate} max_attempts={args.max_attempts} "
          f"redelivery_rate={args.redelivery_rate} seed={args.seed}")
    out = {}
    api_rows = [run_api(m, args.orders, args.loss_rate, args.max_attempts, args.seed)
                for m in args.mode if m != "inbox"]
    if api_rows:
        print("\nPayment capture API (client retries on timeout)")
        print_table(api_rows, API_COLS)
        for r in api_rows:
            if "key_reuse_status" in r:
                print(f"\nsame key, different amount -> HTTP {r['key_reuse_status']} (refused, not replayed)")
        out["api"] = api_rows
    if "inbox" in args.mode:
        inbox_rows = run_inbox(args.orders, args.redelivery_rate, args.seed)
        print("\nPaymentCaptured consumer (at-least-once delivery)")
        print_table(inbox_rows, INBOX_COLS)
        out["consumer"] = inbox_rows
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
