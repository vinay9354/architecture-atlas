"""Lab 02: a simulated system of record (the Tracking Event Store's `shipments` table).

Nothing sleeps. Every read adds its simulated cost to a counter (`busy_ms`), and every write bumps the
row's version and records when that version was committed, so the cache layer can tell exactly how
stale a cached copy is.
"""

STATUSES = ["label_created", "picked_up", "in_transit", "at_hub", "out_for_delivery", "delivered"]


class SimulatedDatabase:
    def __init__(self, n_keys, read_ms=20.0):
        self.read_ms = read_ms
        self.calls = 0
        self.busy_ms = 0.0
        self.writes = 0
        # Per key: current version (starts at 1) and the commit time of every version.
        self._version = [1] * n_keys
        self._committed_at = [[0.0, 0.0] for _ in range(n_keys)]   # index = version; slot 0 unused

    def status(self, key, version=None):
        v = self._version[key] if version is None else version
        return STATUSES[min(v - 1, len(STATUSES) - 1)]

    def version(self, key):
        return self._version[key]

    def committed_at(self, key, version):
        return self._committed_at[key][version]

    def read(self, key, now):
        """One query. Returns (status, version) as of `now`; the caller adds `read_ms` of latency."""
        self.calls += 1
        self.busy_ms += self.read_ms
        v = self._version[key]
        return self.status(key, v), v

    def write(self, key, now):
        """A carrier scan changes the shipment's status: a new version, committed at `now`."""
        self.writes += 1
        self._version[key] += 1
        self._committed_at[key].append(now)
        return self._version[key]
