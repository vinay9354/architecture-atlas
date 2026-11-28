#!/usr/bin/env python3
"""Lab 07: a tiny in-process simulation of a partitioned key-value / document store.

It is NOT a database and says nothing about any product's speed. It models the rules that shape
NoSQL data design:

- Every item has a partition key (pk) and a sort key (sk). A stable hash of the pk picks one of N
  partitions. Inside a partition, the items of one pk (an "item collection") are kept sorted by sk.
- get(pk, sk) reads one item from one partition. query(pk, prefix) reads a contiguous sk range of
  one pk. scan() reads every item in every partition: the only way to answer a question the keys
  were not designed for.
- A global secondary index is another partitioned table keyed by different attributes. Its updates
  are queued and applied by propagate(), so a read of the index right after a base write can miss
  it (eventual consistency). sync=True applies them immediately (used by the load simulation).
- An optional per-partition write budget (writes per simulated second) rejects writes beyond it,
  which is how a hot partition shows up as throttling.

The meter counts requests, items read, items written, and distinct partitions touched.
"""
import bisect
import zlib
from collections import defaultdict, deque


def stable_hash(text):
    """CRC-32 of the UTF-8 bytes: the same in every process (Python's hash() is randomized)."""
    return zlib.crc32(text.encode("utf-8"))


class Meter:
    def __init__(self):
        self.reset()

    def reset(self):
        self.requests = self.items_read = self.items_written = 0
        self.partitions = set()

    def snapshot(self):
        return {"requests": self.requests, "items_read": self.items_read,
                "items_written": self.items_written, "partitions_touched": len(self.partitions)}


class Table:
    def __init__(self, name, partitions=16, budget=None):
        self.name = name
        self.parts = [dict() for _ in range(partitions)]   # pk -> ([sk, ...] sorted, [item, ...])
        self.indexes = []
        self.meter = Meter()
        self.budget = budget                                  # writes per partition per second
        self.offered = defaultdict(int)                       # (partition, second) -> writes attempted
        self.accepted = defaultdict(int)                      # (partition, second) -> writes accepted
        self.throttled = 0

    def partition_of(self, pk):
        return stable_hash(pk) % len(self.parts)

    def _admit(self, part, second):
        if second is None:
            return True
        self.offered[(part, second)] += 1
        if self.budget is not None and self.accepted[(part, second)] >= self.budget:
            self.throttled += 1
            return False
        self.accepted[(part, second)] += 1
        return True

    # ---- writes -------------------------------------------------------------------------------
    def put(self, pk, sk, item, second=None):
        """Insert or replace one item. Returns False if the partition's budget rejected it."""
        part = self.partition_of(pk)
        if not self._admit(part, second):
            return False
        self.meter.requests += 1
        self.meter.items_written += 1
        self.meter.partitions.add(part)
        sks, items = self.parts[part].setdefault(pk, ([], []))
        i = bisect.bisect_left(sks, sk)
        old = None
        if i < len(sks) and sks[i] == sk:
            old, items[i] = items[i], item
        else:
            sks.insert(i, sk)
            items.insert(i, item)
        for index in self.indexes:
            index.on_base_write(old, item, second)
        return True

    def delete(self, pk, sk):
        part = self.partition_of(pk)
        sks, items = self.parts[part].get(pk, ([], []))
        i = bisect.bisect_left(sks, sk)
        if i < len(sks) and sks[i] == sk:
            del sks[i]
            del items[i]

    # ---- reads --------------------------------------------------------------------------------
    def get(self, pk, sk):
        part = self.partition_of(pk)
        self.meter.requests += 1
        self.meter.partitions.add(part)
        sks, items = self.parts[part].get(pk, ([], []))
        i = bisect.bisect_left(sks, sk)
        if i < len(sks) and sks[i] == sk:
            self.meter.items_read += 1
            return items[i]
        return None

    def query(self, pk, prefix="", limit=None, newest_first=False):
        """Items of one pk whose sk starts with prefix, in sk order (or reverse). Reads only those."""
        part = self.partition_of(pk)
        self.meter.requests += 1
        self.meter.partitions.add(part)
        sks, items = self.parts[part].get(pk, ([], []))
        lo = bisect.bisect_left(sks, prefix)
        hi = bisect.bisect_left(sks, prefix + "￿")
        chosen = items[lo:hi]
        if newest_first:
            chosen = chosen[::-1]
        if limit is not None:
            chosen = chosen[:limit]
        self.meter.items_read += len(chosen)
        return list(chosen)

    def scan(self, predicate=None):
        """Read every item in every partition; return those matching predicate."""
        found = []
        for part, collections in enumerate(self.parts):
            self.meter.requests += 1
            self.meter.partitions.add(part)
            for _, items in collections.values():
                self.meter.items_read += len(items)
                found.extend(it for it in items if predicate is None or predicate(it))
        return found

    # ---- shape --------------------------------------------------------------------------------
    def item_count(self):
        return sum(len(items) for coll in self.parts for _, items in coll.values())

    def partition_item_counts(self):
        return [sum(len(items) for _, items in coll.values()) for coll in self.parts]

    def add_global_index(self, name, keyfn, partitions=16, budget=None, sync=False):
        index = GlobalIndex(name, keyfn, partitions, budget, sync)
        self.indexes.append(index)
        return index

    def load_stats(self, seconds):
        """Per-partition offered write rate: hottest, mean, and hot ratio (hottest / mean)."""
        per_part = defaultdict(int)
        for (part, _), n in self.offered.items():
            per_part[part] += n
        total = sum(per_part.values())
        hottest = max(per_part.values(), default=0) / seconds
        mean = total / (len(self.parts) * seconds)
        return {"hottest_per_s": hottest, "mean_per_s": mean,
                "hot_ratio": hottest / mean if mean else 0.0, "throttled": self.throttled}


class GlobalIndex(Table):
    """A secondary index partitioned by its own key. keyfn(item) -> (pk, sk) or None (not indexed)."""

    def __init__(self, name, keyfn, partitions=16, budget=None, sync=False):
        super().__init__(name, partitions, budget)
        self.keyfn, self.sync = keyfn, sync
        self.pending = deque()

    def on_base_write(self, old, new, second):
        if self.sync:
            self._apply(old, new, second)
        else:
            self.pending.append((old, new, second))

    def _apply(self, old, new, second):
        if old is not None and self.keyfn(old) is not None:
            self.delete(*self.keyfn(old))
        target = self.keyfn(new)
        if target is not None:
            self.put(target[0], target[1], dict(new), second)

    def propagate(self):
        """Apply queued index updates (what the store does asynchronously). Returns how many."""
        n = len(self.pending)
        while self.pending:
            self._apply(*self.pending.popleft())
        return n

    def backfill(self, base):
        """Build the index from existing data: one full scan of the base table."""
        for item in base.scan():
            target = self.keyfn(item)
            if target is not None:
                self.put(target[0], target[1], dict(item))
