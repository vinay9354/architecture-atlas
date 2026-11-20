#!/usr/bin/env python3
"""Lab 03 queue simulator: visibility timeouts, competing consumers, retries, and a dead-letter queue.

Standard library only. Time is simulated by a discrete-event loop (no real sleeps), so a run that
covers minutes of queue time finishes in milliseconds and is identical for the same --seed.

The model, loosely shaped like a managed at-least-once queue:
- All messages are published at t=0 (a backlog, for example a carrier uploading a batch of scans).
- An idle consumer receives one visible message, chosen at random (best-effort order, like a standard
  queue). Receiving hides it for --visibility-timeout seconds and increments its receive count.
- On success the consumer deletes the message. If processing outlives the visibility timeout, the
  message reappears and another consumer can receive it too, so the handler runs twice (a duplicate).
- On failure the consumer makes the message visible again after an exponential backoff delay, with no
  jitter or with full jitter.
- A message whose receive count has reached --max-receives is moved to the dead-letter queue (DLQ)
  the next time it would be delivered.
- Failures come from a dependency outage during the first --outage-s seconds, a random transient
  failure rate, and --poison messages that fail on every attempt.
- "retry peak" is the largest number of retried messages that become visible again within one
  simulated second: a direct measure of how synchronized the retries are.

Run:  python queue_sim.py --jitter none full
      python queue_sim.py --max-receives 1 5
      python queue_sim.py --consumers 1 4
"""
import argparse
import heapq
import itertools
import json
import math
import random
import sys
from dataclasses import asdict, dataclass, replace


@dataclass
class Config:
    messages: int = 300
    consumers: int = 4
    failure_rate: float = 0.05     # chance that one attempt fails for a transient reason
    outage_s: float = 2.0          # dependency fails every call during [0, outage_s)
    poison: int = 1                # messages that fail on every attempt
    process_s: float = 0.1         # mean successful processing time (uniform 0.5x to 1.5x)
    fail_s: float = 0.01           # a failed attempt fails fast
    slow_rate: float = 0.01        # chance that a successful attempt outlives the visibility timeout
    visibility_timeout_s: float = 5.0
    max_receives: int = 5
    base_backoff_s: float = 1.0
    max_backoff_s: float = 60.0
    jitter: str = "full"           # "none" or "full"
    seed: int = 7


@dataclass
class Message:
    msg_id: int
    poison: bool
    visible_at: float = 0.0
    receive_count: int = 0
    deleted: bool = False
    dead_lettered: bool = False
    successes: int = 0
    done_at: float = -1.0


def percentile(sorted_values, p):
    """Nearest-rank percentile on an ascending list; p in 0..100."""
    if not sorted_values:
        return float("nan")
    k = max(0, min(len(sorted_values) - 1, math.ceil(p / 100.0 * len(sorted_values)) - 1))
    return sorted_values[k]


def backoff_delay(retry_number, base_s, cap_s, jitter, rng):
    """Delay before retry number 1, 2, 3, ...: base x 2^(n-1), capped; full jitter draws 0..that."""
    ceiling = min(cap_s, base_s * 2 ** (retry_number - 1))
    if jitter == "none":
        return ceiling
    if jitter == "full":
        return rng.uniform(0.0, ceiling)
    raise ValueError(f"unknown jitter mode {jitter!r}")


def simulate(cfg):
    """Run one configuration and return a dict of results."""
    outcome_rng = random.Random(cfg.seed)        # failures and processing times
    jitter_rng = random.Random(cfg.seed + 1000)  # backoff jitter, kept separate on purpose
    poison_ids = set(outcome_rng.sample(range(cfg.messages), min(cfg.poison, cfg.messages)))
    msgs = [Message(i, i in poison_ids) for i in range(cfg.messages)]
    seq = itertools.count()
    order_rng = random.Random(cfg.seed + 2000)   # which visible message a consumer gets
    ready = [(0.0, next(seq), m.msg_id) for m in msgs]  # (visible_at, tie-break, id); stale entries skipped
    heapq.heapify(ready)
    visible = []                                 # (msg_id, visible_at) entries whose time has come
    finishes = []                                # (time, tie-break, consumer, msg_id, receipt, ok)
    idle = list(range(cfg.consumers))            # kept sorted so the lowest-numbered consumer goes first
    now = 0.0
    last_settled = 0.0
    dlq = []
    receives = failures = retried = duplicates = 0
    retry_visible_at = []                        # when each retried message becomes visible again

    def dispatch():
        nonlocal receives, last_settled
        while ready and ready[0][0] <= now:
            vis, _, mid = heapq.heappop(ready)
            visible.append((mid, vis))
        while idle and visible:
            # Standard queues give best-effort order: take a random visible message.
            i = order_rng.randrange(len(visible))
            visible[i], visible[-1] = visible[-1], visible[i]
            mid, vis = visible.pop()
            m = msgs[mid]
            if m.deleted or m.dead_lettered or vis != m.visible_at:
                continue  # stale heap entry
            if m.receive_count >= cfg.max_receives:
                m.dead_lettered = True  # redrive policy: too many receives, park it in the DLQ
                dlq.append(mid)
                last_settled = now
                continue
            m.receive_count += 1
            receives += 1
            m.visible_at = now + cfg.visibility_timeout_s  # invisible while this consumer holds it
            heapq.heappush(ready, (m.visible_at, next(seq), mid))
            consumer = idle.pop(0)
            if m.poison or now < cfg.outage_s or outcome_rng.random() < cfg.failure_rate:
                ok, duration = False, cfg.fail_s
            else:
                ok = True
                duration = cfg.process_s * outcome_rng.uniform(0.5, 1.5)
                if outcome_rng.random() < cfg.slow_rate:
                    duration = cfg.visibility_timeout_s * outcome_rng.uniform(1.2, 2.0)
            heapq.heappush(finishes, (now + duration, next(seq), consumer, mid, m.receive_count, ok))

    while True:
        dispatch()
        candidates = []
        if finishes:
            candidates.append(finishes[0][0])
        if ready:
            candidates.append(ready[0][0])
        if not candidates:
            break
        now = max(now, min(candidates))
        while finishes and finishes[0][0] <= now:
            t, _, consumer, mid, receipt, ok = heapq.heappop(finishes)
            idle.append(consumer)
            idle.sort()
            m = msgs[mid]
            if ok:
                m.successes += 1
                if m.successes == 1:
                    m.done_at = t
                    last_settled = max(last_settled, t)
                else:
                    duplicates += 1  # the handler's side effect ran again
                m.deleted = True
            else:
                failures += 1
                # Only the current holder may reschedule; an expired lease has nothing left to change.
                if not (m.deleted or m.dead_lettered) and m.receive_count == receipt:
                    delay = backoff_delay(receipt, cfg.base_backoff_s, cfg.max_backoff_s, cfg.jitter, jitter_rng)
                    m.visible_at = t + delay
                    heapq.heappush(ready, (m.visible_at, next(seq), mid))
                    retried += 1
                    retry_visible_at.append(m.visible_at)

    done = sorted(m.done_at for m in msgs if m.successes > 0)
    buckets = {}
    for t in retry_visible_at:
        b = int(t)  # one-second slots
        buckets[b] = buckets.get(b, 0) + 1
    return {
        "consumers": cfg.consumers,
        "jitter": cfg.jitter,
        "max_receives": cfg.max_receives,
        "visibility_s": cfg.visibility_timeout_s,
        "published": cfg.messages,
        "processed": len(done),
        "receives": receives,
        "failures": failures,
        "retried": retried,
        "dead_lettered": len(dlq),
        "dlq_healthy": sum(1 for mid in dlq if not msgs[mid].poison),
        "dlq_poison": sum(1 for mid in dlq if msgs[mid].poison),
        "duplicates": duplicates,
        "p50_s": round(percentile(done, 50), 2),
        "p99_s": round(percentile(done, 99), 2),
        "drain_s": round(last_settled, 2),
        "retry_peak": max(buckets.values(), default=0),
    }


COLUMNS = [
    ("consumers", "consumers"), ("jitter", "jitter"), ("max_receives", "max rcv"), ("visibility_s", "vis s"),
    ("processed", "processed"), ("retried", "retried"), ("dead_lettered", "DLQ"), ("dlq_healthy", "DLQ ok msg"),
    ("duplicates", "duplicates"), ("p50_s", "p50 s"), ("p99_s", "p99 s"), ("drain_s", "drain s"),
    ("retry_peak", "retry peak"),
]


def print_table(rows):
    print(" | ".join(f"{h:>10}" for _, h in COLUMNS))
    print("-+-".join("-" * 10 for _ in COLUMNS))
    for r in rows:
        print(" | ".join(f"{str(r[k]):>10}" for k, _ in COLUMNS))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    d = Config()
    ap.add_argument("--messages", type=int, default=d.messages)
    ap.add_argument("--consumers", type=int, nargs="+", default=[d.consumers])
    ap.add_argument("--jitter", choices=["none", "full"], nargs="+", default=[d.jitter])
    ap.add_argument("--max-receives", type=int, nargs="+", default=[d.max_receives])
    ap.add_argument("--visibility-timeout", type=float, nargs="+", default=[d.visibility_timeout_s],
                    help="seconds a received message stays hidden")
    ap.add_argument("--failure-rate", type=float, default=d.failure_rate)
    ap.add_argument("--outage-s", type=float, default=d.outage_s)
    ap.add_argument("--poison", type=int, default=d.poison)
    ap.add_argument("--process-ms", type=float, default=d.process_s * 1000)
    ap.add_argument("--slow-rate", type=float, default=d.slow_rate)
    ap.add_argument("--base-backoff", type=float, default=d.base_backoff_s, help="seconds")
    ap.add_argument("--max-backoff", type=float, default=d.max_backoff_s, help="seconds")
    ap.add_argument("--seed", type=int, default=d.seed)
    ap.add_argument("--json", help="also write results to this file")
    args = ap.parse_args(argv)
    base = replace(d, messages=args.messages, failure_rate=args.failure_rate, outage_s=args.outage_s,
                   poison=args.poison, process_s=args.process_ms / 1000, slow_rate=args.slow_rate,
                   base_backoff_s=args.base_backoff, max_backoff_s=args.max_backoff, seed=args.seed)
    print(f"messages={base.messages} outage={base.outage_s}s failure_rate={base.failure_rate} "
          f"poison={base.poison} process={args.process_ms:g}ms slow_rate={base.slow_rate} "
          f"backoff={base.base_backoff_s}s..{base.max_backoff_s}s seed={base.seed}")
    print()
    rows = []
    for c, j, mr, vt in itertools.product(args.consumers, args.jitter, args.max_receives, args.visibility_timeout):
        rows.append(simulate(replace(base, consumers=c, jitter=j, max_receives=mr, visibility_timeout_s=vt)))
    print_table(rows)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"config": asdict(base), "rows": rows}, f, indent=2)
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
