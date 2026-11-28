"""Lab 16: four services, each with its own SQLite database, an outbox, and a processed-event table.

The saga is choreographed: nobody is in charge; each service reacts to the previous step's event.

  Orders     place_order        -> order.placed            (topic "orders")
  Inventory  order.placed       -> inventory.reserved      (topic "inventory")
  Payments   inventory.reserved -> payment.authorized | payment.failed   (topic "payments")
  Shipping   payment.authorized -> shipment.created        (topic "shipping")
  Inventory  payment.failed     -> inventory.released      (compensation: put the stock back)
  Orders     inventory.reserved, payment.*, shipment.created -> order status

Every handler runs inside ONE local transaction that (1) records the event in processed_events,
(2) changes the service's own tables, and (3) inserts any outgoing event into the outbox. An
OutboxRelay later publishes outbox rows to the bus. Set idempotent=False to drop step (1) and see
what at-least-once delivery does to a naive consumer.
"""
import json
import sqlite3

from lab16_bus import make_event

COMMON_SCHEMA = """
CREATE TABLE IF NOT EXISTS outbox (
    seq        INTEGER PRIMARY KEY,
    event_id   TEXT NOT NULL UNIQUE,
    topic      TEXT NOT NULL,
    event      TEXT NOT NULL,
    published  INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS processed_events (
    source     TEXT NOT NULL,
    event_id   TEXT NOT NULL,
    PRIMARY KEY (source, event_id)
);
"""

# Order status precedence: a status change is applied only if it moves the order forwards.
RANK = {"PENDING": 0, "RESERVED": 1, "PAID": 2, "SHIPPED": 3, "CANCELLED": 3}
DECLINING_METHOD = "test-card-declined"


class SimulatedCrash(Exception):
    """Raised where a real process would have died."""


class Service:
    name = "service"
    prefix = "svc"
    schema = ""

    def __init__(self, path, idempotent=True):
        self.db = sqlite3.connect(path)
        self.db.executescript(COMMON_SCHEMA + self.schema)
        self.source = f"/atlasmart/{self.name}"
        self.idempotent = idempotent
        self.stats = {"applied": 0, "duplicates_skipped": 0, "stale_ignored": 0, "unknown_order": 0}

    # -- producer side ---------------------------------------------------------------------------
    def emit(self, topic, event_type, subject, data):
        """Insert an outgoing event into the outbox. Call only inside an open transaction."""
        (n,) = self.db.execute("SELECT COALESCE(MAX(seq), 0) + 1 FROM outbox").fetchone()
        event = make_event(self.source, f"{self.prefix}-{n:04d}", event_type, subject, data)
        self.db.execute("INSERT INTO outbox (seq, event_id, topic, event) VALUES (?, ?, ?, ?)",
                        (n, event["id"], topic, json.dumps(event, sort_keys=True)))
        return event

    # -- consumer side ---------------------------------------------------------------------------
    def handle(self, event):
        """Bus entry point: one transaction for dedupe record + state change + outbox rows."""
        handler = getattr(self, "on_" + event["type"].split(".", 1)[1].replace(".", "_"), None)
        if handler is None:
            return "ignored (not interested)"
        with self.db:
            if self.idempotent:
                try:
                    self.db.execute("INSERT INTO processed_events (source, event_id) VALUES (?, ?)",
                                    (event["source"], event["id"]))
                except sqlite3.IntegrityError:
                    self.stats["duplicates_skipped"] += 1
                    return "duplicate skipped"
            outcome = handler(event) or "applied"
        key = {"applied": "applied", "stale ignored": "stale_ignored",
               "unknown order": "unknown_order"}.get(outcome, "applied")
        self.stats[key] += 1
        return outcome

    def count(self, sql, *args):
        return self.db.execute(sql, args).fetchone()[0]

    def unpublished(self):
        return self.count("SELECT COUNT(*) FROM outbox WHERE published = 0")


class OrdersService(Service):
    name, prefix = "orders", "ord"
    schema = """
    CREATE TABLE IF NOT EXISTS orders (
        order_id       TEXT PRIMARY KEY,
        sku            TEXT NOT NULL,
        qty            INTEGER NOT NULL,
        amount_cents   INTEGER NOT NULL,
        payment_method TEXT NOT NULL,
        status         TEXT NOT NULL
    );
    """

    def place_order(self, order_id, sku, qty, amount_cents, payment_method):
        """The business change and its event commit together, or not at all."""
        with self.db:
            self.db.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?, 'PENDING')",
                            (order_id, sku, qty, amount_cents, payment_method))
            self.emit("orders", "atlasmart.order.placed", order_id,
                      {"order_id": order_id, "sku": sku, "qty": qty, "amount_cents": amount_cents,
                       "payment_method": payment_method})

    def place_order_dual_write(self, bus, order_id, sku, qty, amount_cents, payment_method, fault=None):
        """The naive alternative: commit to the database and publish to the bus as two separate writes.

        fault="crash-after-commit": the order commits, the process dies before publishing.
        fault="rollback-after-publish": the event is published, then the transaction fails.
        """
        self.dual_writes = getattr(self, "dual_writes", 0) + 1
        event = make_event(self.source, f"ord-dw-{self.dual_writes:04d}", "atlasmart.order.placed", order_id,
                           {"order_id": order_id, "sku": sku, "qty": qty, "amount_cents": amount_cents,
                            "payment_method": payment_method})
        if fault == "rollback-after-publish":
            try:
                with self.db:
                    self.db.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?, 'PENDING')",
                                    (order_id, sku, qty, amount_cents, payment_method))
                    bus.publish("orders", event)
                    raise SimulatedCrash("database commit failed after publishing")
            except SimulatedCrash:
                return "published, then rolled back"
        with self.db:
            self.db.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?, 'PENDING')",
                            (order_id, sku, qty, amount_cents, payment_method))
        if fault == "crash-after-commit":
            return "committed, crashed before publishing"
        bus.publish("orders", event)
        return "committed and published"

    def _advance(self, order_id, status):
        row = self.db.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        if row is None:
            return "unknown order"
        if RANK[status] <= RANK[row[0]]:
            return "stale ignored"      # an older event arrived after a newer one
        self.db.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
        return "applied"

    def on_inventory_reserved(self, event):
        return self._advance(event["subject"], "RESERVED")

    def on_payment_authorized(self, event):
        return self._advance(event["subject"], "PAID")

    def on_payment_failed(self, event):
        return self._advance(event["subject"], "CANCELLED")

    def on_shipment_created(self, event):
        return self._advance(event["subject"], "SHIPPED")

    def by_status(self):
        return dict(self.db.execute("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status"))


class InventoryService(Service):
    name, prefix = "inventory", "inv"
    schema = """
    CREATE TABLE IF NOT EXISTS stock (sku TEXT PRIMARY KEY, on_hand INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS reservations (
        reservation_id INTEGER PRIMARY KEY,
        order_id       TEXT NOT NULL,
        sku            TEXT NOT NULL,
        qty            INTEGER NOT NULL,
        status         TEXT NOT NULL
    );
    """

    def load_stock(self, levels):
        with self.db:
            self.db.executemany("INSERT INTO stock VALUES (?, ?)", sorted(levels.items()))

    def on_order_placed(self, event):
        d = event["data"]
        self.db.execute("UPDATE stock SET on_hand = on_hand - ? WHERE sku = ?", (d["qty"], d["sku"]))
        self.db.execute("INSERT INTO reservations (order_id, sku, qty, status) VALUES (?, ?, ?, 'RESERVED')",
                        (d["order_id"], d["sku"], d["qty"]))
        # Event-carried state: Payments gets what it needs without calling Orders.
        self.emit("inventory", "atlasmart.inventory.reserved", d["order_id"],
                  {k: d[k] for k in ("order_id", "sku", "qty", "amount_cents", "payment_method")})

    def on_payment_failed(self, event):
        """Compensation: release the reservation and put the stock back."""
        order_id = event["subject"]
        for sku, qty in self.db.execute(
                "SELECT sku, qty FROM reservations WHERE order_id = ?", (order_id,)).fetchall():
            self.db.execute("UPDATE stock SET on_hand = on_hand + ? WHERE sku = ?", (qty, sku))
        self.db.execute("UPDATE reservations SET status = 'RELEASED' WHERE order_id = ?", (order_id,))
        self.emit("inventory", "atlasmart.inventory.released", order_id, {"order_id": order_id})

    def stock(self):
        return dict(self.db.execute("SELECT sku, on_hand FROM stock ORDER BY sku"))


class PaymentsService(Service):
    name, prefix = "payments", "pay"
    schema = """
    CREATE TABLE IF NOT EXISTS payments (
        payment_id   INTEGER PRIMARY KEY,
        order_id     TEXT NOT NULL,
        amount_cents INTEGER NOT NULL,
        status       TEXT NOT NULL
    );
    """

    def on_inventory_reserved(self, event):
        d = event["data"]
        status = "DECLINED" if d["payment_method"] == DECLINING_METHOD else "AUTHORIZED"
        cur = self.db.execute("INSERT INTO payments (order_id, amount_cents, status) VALUES (?, ?, ?)",
                              (d["order_id"], d["amount_cents"], status))
        if status == "AUTHORIZED":
            self.emit("payments", "atlasmart.payment.authorized", d["order_id"],
                      {"order_id": d["order_id"], "payment_id": cur.lastrowid, "amount_cents": d["amount_cents"]})
        else:
            self.emit("payments", "atlasmart.payment.failed", d["order_id"],
                      {"order_id": d["order_id"], "reason": "card declined (test)"})


class ShippingService(Service):
    name, prefix = "shipping", "shp"
    schema = """
    CREATE TABLE IF NOT EXISTS shipments (
        shipment_id INTEGER PRIMARY KEY,
        order_id    TEXT NOT NULL,
        status      TEXT NOT NULL
    );
    """

    def on_payment_authorized(self, event):
        cur = self.db.execute("INSERT INTO shipments (order_id, status) VALUES (?, 'CREATED')", (event["subject"],))
        self.emit("shipping", "atlasmart.shipment.created", event["subject"],
                  {"order_id": event["subject"], "shipment_id": cur.lastrowid})


class OutboxRelay:
    """Polls one service's outbox in commit order and publishes each row, at least once.

    crash_before_publish / crash_after_publish: sets of event ids at which the relay dies once
    (before calling publish, or after publish but before marking the row as published).
    """

    def __init__(self, service, bus, crash_before_publish=(), crash_after_publish=()):
        self.service, self.bus = service, bus
        self.crash_before, self.crash_after = set(crash_before_publish), set(crash_after_publish)
        self.crashes = []

    def run_once(self, batch=50):
        rows = self.service.db.execute(
            "SELECT seq, event_id, topic, event FROM outbox WHERE published = 0 ORDER BY seq LIMIT ?",
            (batch,)).fetchall()
        for seq, event_id, topic, payload in rows:
            if event_id in self.crash_before:
                self.crash_before.discard(event_id)
                self.crashes.append(f"{self.service.name} relay crashed before publishing {event_id} "
                                    f"({self.service.unpublished()} outbox rows unpublished)")
                raise SimulatedCrash(self.crashes[-1])
            self.bus.publish(topic, json.loads(payload))
            if event_id in self.crash_after:
                self.crash_after.discard(event_id)
                self.crashes.append(f"{self.service.name} relay crashed after publishing {event_id}, "
                                    "before marking it published")
                raise SimulatedCrash(self.crashes[-1])
            with self.service.db:
                self.service.db.execute("UPDATE outbox SET published = 1 WHERE seq = ?", (seq,))
        return len(rows)
