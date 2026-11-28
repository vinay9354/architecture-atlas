"""Lab 16: an in-process event bus with topics, at-least-once delivery, and seeded misbehaviour.

The bus keeps one append-only log per topic (so a subscription can be replayed) and one pending
list per subscription. `deliver_one()` hands one pending event to one subscriber. Two faults can be
switched on, both driven by one seeded random generator so runs are reproducible:

* duplicate_rate: after a handler succeeds, its acknowledgment is "lost" and the event is put back
  at the end of that subscription's pending list, so it is delivered again later (at-least-once).
* reorder_rate: instead of the oldest pending event, a slightly newer one is delivered first.

A handler that raises is retried (the event goes back to the end of the list) until max_attempts,
then it is moved to the subscription's dead-letter list.

Events are dictionaries shaped like a CloudEvents 1.0 JSON event: specversion, id, source, type,
subject, datacontenttype, and data. `make_event()` builds one; `check_event()` validates one.
"""
import random

REQUIRED_ATTRIBUTES = ("specversion", "id", "source", "type")


def make_event(source, event_id, event_type, subject, data):
    """Return a CloudEvents-shaped event. Consumers deduplicate on (source, id)."""
    return {
        "specversion": "1.0",
        "id": event_id,
        "source": source,
        "type": event_type,
        "subject": subject,
        "datacontenttype": "application/json",
        "data": dict(data, schema_version=1),
    }


def check_event(event):
    """Raise ValueError if a required attribute is missing or empty."""
    for name in REQUIRED_ATTRIBUTES:
        if not event.get(name):
            raise ValueError(f"event is missing required attribute {name!r}")
    if event["specversion"] != "1.0":
        raise ValueError(f"unsupported specversion {event['specversion']!r}")


class Subscription:
    def __init__(self, topic, name, handler, types=None):
        self.topic, self.name, self.handler = topic, name, handler
        self.types = set(types) if types else None   # filter: None means every event on the topic
        self.pending = []          # list of [event, attempts]
        self.dead_letters = []


class EventBus:
    def __init__(self, seed=16, duplicate_rate=0.0, reorder_rate=0.0, max_attempts=5):
        self.rng = random.Random(seed)
        self.duplicate_rate, self.reorder_rate, self.max_attempts = duplicate_rate, reorder_rate, max_attempts
        self.logs = {}             # topic -> list of events, in publish order
        self.subscriptions = []
        self.delivery_log = []     # (step, subscriber, topic, type, id, subject, outcome)
        self.stats = {"published": 0, "deliveries": 0, "duplicates_injected": 0, "reorders_injected": 0,
                      "handler_errors": 0, "dead_lettered": 0}

    def subscribe(self, topic, name, handler, types=None):
        """Subscribe `handler` to `topic`; `types` (optional) filters by event type at the bus."""
        sub = Subscription(topic, name, handler, types)
        self.subscriptions.append(sub)
        self.logs.setdefault(topic, [])
        return sub

    def publish(self, topic, event):
        check_event(event)
        self.logs.setdefault(topic, []).append(event)
        self.stats["published"] += 1
        for sub in self.subscriptions:
            if sub.topic == topic and (sub.types is None or event["type"] in sub.types):
                sub.pending.append([event, 0])

    def replay(self, topic, name):
        """Re-deliver every event ever published on `topic` to the named subscription."""
        for sub in self.subscriptions:
            if sub.topic == topic and sub.name == name:
                events = [e for e in self.logs[topic] if sub.types is None or e["type"] in sub.types]
                sub.pending.extend([event, 0] for event in events)
                return len(events)
        raise KeyError(f"no subscription {name!r} on topic {topic!r}")

    def pending_count(self):
        return sum(len(s.pending) for s in self.subscriptions)

    def deliver_one(self):
        """Deliver one pending event to one subscriber. Return False when nothing is pending."""
        ready = [s for s in self.subscriptions if s.pending]
        if not ready:
            return False
        sub = self.rng.choice(ready)
        index = 0
        if len(sub.pending) > 1 and self.rng.random() < self.reorder_rate:
            index = self.rng.randrange(1, min(len(sub.pending), 4))
            self.stats["reorders_injected"] += 1
        item = sub.pending.pop(index)
        event = item[0]
        item[1] += 1
        self.stats["deliveries"] += 1
        step = self.stats["deliveries"]
        try:
            outcome = sub.handler(event) or "applied"
        except Exception as exc:  # noqa: BLE001 - any handler failure means "not acknowledged"
            self.stats["handler_errors"] += 1
            if item[1] >= self.max_attempts:
                sub.dead_letters.append(event)
                self.stats["dead_lettered"] += 1
                outcome = f"dead-lettered ({exc})"
            else:
                sub.pending.append(item)
                outcome = f"failed, will retry ({exc})"
        else:
            if self.rng.random() < self.duplicate_rate:
                sub.pending.append([event, item[1]])     # the ack was lost: redeliver later
                self.stats["duplicates_injected"] += 1
        self.delivery_log.append((step, sub.name, sub.topic, event["type"], event["id"],
                                  event.get("subject"), outcome))
        return True
