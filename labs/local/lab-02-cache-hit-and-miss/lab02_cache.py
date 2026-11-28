"""Lab 02: a bounded in-memory cache with least-recently-used (LRU) eviction and per-entry TTL.

Standard library only. Time is passed in by the caller (simulated seconds), so nothing sleeps and
every run with the same inputs gives the same result.

Expiry is lazy, as in most real caches: an expired entry stays in memory, still using a slot, until
someone reads it (then it is removed and the read is a miss) or LRU eviction pushes it out.
"""
from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class Entry:
    value: str          # the cached shipment status
    version: int        # the database version the value was read at
    expires_at: float   # simulated seconds


class LRUCache:
    """A fixed number of slots; a full cache evicts the entry read least recently."""

    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be at least 1 entry")
        self.capacity = capacity
        self._data = OrderedDict()   # key -> Entry, least recently used first
        self.evictions = 0
        self.expirations = 0

    def __len__(self):
        return len(self._data)

    def get(self, key, now):
        """Return the live entry for key, or None. Reading an entry makes it most recently used."""
        entry = self._data.get(key)
        if entry is None:
            return None
        if now >= entry.expires_at:
            del self._data[key]
            self.expirations += 1
            return None
        self._data.move_to_end(key)
        return entry

    def set(self, key, value, version, ttl_s, now):
        """Store a copy; evict the least recently used entry if the cache is full."""
        if key in self._data:
            self._data.move_to_end(key)
        elif len(self._data) >= self.capacity:
            self._data.popitem(last=False)
            self.evictions += 1
        self._data[key] = Entry(value, version, now + ttl_s)

    def delete(self, key):
        """Invalidate one key (delete-on-write). Returns True if something was removed."""
        return self._data.pop(key, None) is not None

    def keys_lru_first(self):
        return list(self._data)


if __name__ == "__main__":
    c = LRUCache(capacity=2)
    c.set("SHP-1", "in_transit", 1, ttl_s=30, now=0)
    c.set("SHP-2", "in_transit", 1, ttl_s=30, now=0)
    c.get("SHP-1", now=1)                       # SHP-1 becomes most recently used
    c.set("SHP-3", "in_transit", 1, ttl_s=30, now=2)
    print("after inserting SHP-3 into a full 2-slot cache:", c.keys_lru_first(), "evictions", c.evictions)
    print("SHP-1 at t=29.9 s:", c.get("SHP-1", now=29.9) is not None)
    print("SHP-1 at t=30.0 s:", c.get("SHP-1", now=30.0) is not None, "expirations", c.expirations)
