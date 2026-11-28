"""Lab 02: seeded workloads of AtlasMart tracking reads and carrier scans.

* Tracking reads arrive as a Poisson process (random gaps, a fixed average rate). Which shipment is
  read follows a Zipf-like popularity curve: the shipment of rank k is read in proportion to
  1 / k**s. With s = 1, a few hundred shipments get a large share of all reads and most shipments are
  read rarely, the skew a notification campaign or sale day produces.
* Carrier scans (status changes) arrive as a Poisson process and pick a shipment uniformly: carriers
  scan parcels whether or not anyone is watching them.

All randomness comes from one `random.Random(seed)`, so a seed always gives the same event list.
"""
import bisect
import itertools
import random

READ, WRITE = "read", "write"


class Zipf:
    """Sample ranks 0..n-1 with probability proportional to 1 / (rank + 1) ** s."""

    def __init__(self, n, s, rng):
        self.rng = rng
        weights = [1.0 / (k ** s) for k in range(1, n + 1)]
        self.cum = list(itertools.accumulate(weights))
        self.total = self.cum[-1]

    def share_of_top(self, k):
        """Fraction of all reads that go to the k most popular keys."""
        return self.cum[k - 1] / self.total

    def sample(self):
        return bisect.bisect_left(self.cum, self.rng.random() * self.total)


def poisson_times(rate, duration_s, rng, start=0.0):
    t = start
    while True:
        t += rng.expovariate(rate)
        if t >= duration_s:
            return
        yield t


def tracking_workload(n_keys=50_000, zipf_s=1.0, read_rate=210.0, write_rate=70.0,
                      duration_s=600.0, seed=2):
    """Return a time-ordered list of (t, kind, key) for reads and writes."""
    rng = random.Random(seed)
    zipf = Zipf(n_keys, zipf_s, rng)
    events = [(t, READ, zipf.sample()) for t in poisson_times(read_rate, duration_s, rng)]
    events += [(t, WRITE, rng.randrange(n_keys)) for t in poisson_times(write_rate, duration_s, rng)]
    events.sort(key=lambda e: (e[0], e[1]))
    return events


def hot_key_workload(read_rate=150.0, duration_s=300.0, seed=2):
    """One viral shipment (key 0) read `read_rate` times a second; no writes."""
    rng = random.Random(seed)
    return [(t, READ, 0) for t in poisson_times(read_rate, duration_s, rng)]


def campaign_workload(customers=2_000, mean_gap_s=5.0, duration_s=300.0, seed=2):
    """A notification sends `customers` people to their own tracking page within the first second;
    each page then refreshes every `mean_gap_s` seconds on average while open. Customer i reads key i."""
    rng = random.Random(seed)
    events = []
    for key in range(customers):
        t = rng.random()                       # first visit inside the first second
        while t < duration_s:
            events.append((t, READ, key))
            t += rng.expovariate(1.0 / mean_gap_s)
    events.sort(key=lambda e: (e[0], e[2]))
    return events


if __name__ == "__main__":
    z = Zipf(50_000, 1.0, random.Random(2))
    for k in (10, 100, 1_000, 5_000, 20_000):
        print(f"top {k:>6,} of 50,000 shipments receive {z.share_of_top(k):6.1%} of reads")
    ev = tracking_workload(duration_s=60)
    reads = sum(1 for e in ev if e[1] == READ)
    print(f"60 s at 210 reads/s and 70 scans/s: {reads:,} reads, {len(ev) - reads:,} scans")
