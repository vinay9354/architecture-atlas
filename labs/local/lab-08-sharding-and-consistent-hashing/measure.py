#!/usr/bin/env python3
"""Lab 08 measurements: how many keys move when a node joins or leaves, how evenly keys spread, and
why an even spread of keys is not an even spread of load.

Standard library only, deterministic for a given --seed. Three experiments over synthetic shipment IDs:

  A. Movement: fraction of keys whose owner changes going from N to N+1 nodes and from N to N-1,
     for hash-mod-N, the consistent-hash ring, and rendezvous hashing, next to the theory.
  B. Spread: keys per node (max/mean, min/mean, coefficient of variation) for the ring with
     1, 10, 100, 200 virtual nodes, with mod-N and rendezvous as reference rows.
  C. Hot keys: 1% of keys receive 30% of reads; compare the spread of keys with the spread of reads.

Run:  python measure.py --keys 100000 --nodes 10 --seed 8
"""
import argparse
import json
import random
import statistics
import sys
import time
from collections import Counter

import placement


def make_keys(count, seed):
    """Unique synthetic shipment IDs such as SHP-0048213371, drawn from a seeded generator."""
    rng = random.Random(seed)
    seen = set()
    while len(seen) < count:
        seen.add(f"SHP-{rng.randrange(10**10):010d}")
    return sorted(seen)


def moved(before, after):
    """Fraction of keys whose owner differs between two assignments of the same key list."""
    return sum(1 for a, b in zip(before, after) if a != b) / len(before)


def moves_touch_only(before, after, node):
    """True if every moved key moved to `node` (join) or away from `node` (leave): minimal movement."""
    return all(a == node or b == node for a, b in zip(before, after) if a != b)


def spread(owners, nodes):
    """Keys-per-node statistics. Nodes that own nothing still count (with zero keys)."""
    counts = Counter(owners)
    per_node = [counts.get(n, 0) for n in nodes]
    mean = statistics.fmean(per_node)
    return {
        "max_over_mean": round(max(per_node) / mean, 3),
        "min_over_mean": round(min(per_node) / mean, 3),
        "cv": round(statistics.pstdev(per_node) / mean, 3),
    }


def experiment_movement(keys, n, vnodes):
    """Experiment A. Remove the last node for the N-1 case, so every scheme loses the same node."""
    base, grown, shrunk = placement.node_names(n), placement.node_names(n + 1), placement.node_names(n - 1)
    joined, left = grown[-1], base[-1]
    theory = {
        ("mod-N", "add"): n / (n + 1), ("mod-N", "remove"): (n - 1) / n,
        ("ring", "add"): 1 / (n + 1), ("ring", "remove"): 1 / n,
        ("rendezvous", "add"): 1 / (n + 1), ("rendezvous", "remove"): 1 / n,
    }
    rows, cache = [], {}
    for scheme in ("mod-N", "ring", "rendezvous"):
        before = placement.assign(placement.build(scheme, base, vnodes), keys)
        cache[scheme] = before
        for change, nodes, node in (("add", grown, joined), ("remove", shrunk, left)):
            after = placement.assign(placement.build(scheme, nodes, vnodes), keys)
            rows.append({
                "scheme": scheme if scheme != "ring" else f"ring ({vnodes} vnodes)",
                "change": f"{n} -> {len(nodes)}",
                "moved": round(moved(before, after), 4),
                "theory": round(theory[(scheme, change)], 4),
                "only_changed_node": moves_touch_only(before, after, node),
            })
    return rows, cache


def experiment_spread(keys, n, vnode_list, cache):
    """Experiment B. Reuses the mod-N and rendezvous assignments computed in experiment A."""
    nodes = placement.node_names(n)
    rows = [{"scheme": "mod-N", "vnodes": "-", **spread(cache["mod-N"], nodes), "cv_theory": "-"}]
    ring_owners = {}
    for v in vnode_list:
        owners = placement.assign(placement.Ring(nodes, v), keys)
        ring_owners[v] = owners
        # Each node's share of the circle is a sum of v random arcs, so its cv is about 1/sqrt(v).
        rows.append({"scheme": "ring", "vnodes": v, **spread(owners, nodes), "cv_theory": round(v ** -0.5, 3)})
    rows.append({"scheme": "rendezvous", "vnodes": "-", **spread(cache["rendezvous"], nodes), "cv_theory": "-"})
    return rows, ring_owners


def read_weights(n_keys, hot_fraction, hot_share, skew, rng):
    """Share of all reads that each key receives. `skew` = 0 spreads the hot share evenly over the hot
    keys; skew > 0 spreads it Zipf-style (the hottest key gets the most) inside the hot set."""
    hot_count = max(1, round(n_keys * hot_fraction))
    hot = rng.sample(range(n_keys), hot_count)
    weights = [(1.0 - hot_share) / (n_keys - hot_count)] * n_keys
    raw = [1.0 / (rank ** skew) for rank in range(1, hot_count + 1)]
    total = sum(raw)
    for key_index, r in zip(hot, raw):
        weights[key_index] = hot_share * r / total
    return weights


def load_spread(owners, weights, nodes):
    keys_per_node, reads_per_node = Counter(owners), Counter()
    for owner, w in zip(owners, weights):
        reads_per_node[owner] += w
    k = [keys_per_node.get(n, 0) for n in nodes]
    r = [reads_per_node.get(n, 0.0) for n in nodes]
    return {
        "keys_max_over_mean": round(max(k) / statistics.fmean(k), 3),
        "reads_max_over_mean": round(max(r) / statistics.fmean(r), 3),
        "busiest_node_read_pct": round(100 * max(r), 3),
        "top_key_read_pct": round(100 * max(weights), 3),
    }


def experiment_hot(ring_owners, n, hot_fraction, hot_share, zipf_s, seed):
    """Experiment C on the ring with the most virtual nodes (the best key spread we measured)."""
    nodes = placement.node_names(n)
    n_keys = len(ring_owners)
    scenarios = [
        ("no hot keys", read_weights(n_keys, 0.0, 0.0, 0.0, random.Random(seed))),
        (f"{hot_fraction:.0%} keys get {hot_share:.0%} reads, even", read_weights(
            n_keys, hot_fraction, hot_share, 0.0, random.Random(seed))),
        (f"{hot_fraction:.0%} keys get {hot_share:.0%} reads, zipf {zipf_s}", read_weights(
            n_keys, hot_fraction, hot_share, zipf_s, random.Random(seed))),
    ]
    return [{"scenario": name, **load_spread(ring_owners, w, nodes)} for name, w in scenarios]


def cell(value, decimals):
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def print_table(rows, cols, head, decimals=3, width=12):
    widths = [max(width, len(h)) for h in head]
    widths[0] = max(widths[0], *(len(str(r[cols[0]])) for r in rows))
    print(" | ".join(f"{h:>{w}}" for h, w in zip(head, widths)))
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(" | ".join(f"{cell(r[c], decimals):>{w}}" for c, w in zip(cols, widths)))


def run(keys_count=100_000, n=10, vnodes=100, vnode_list=(1, 10, 100, 200), hot_fraction=0.01,
        hot_share=0.30, zipf_s=1.0, seed=8):
    keys = make_keys(keys_count, seed)
    movement, cache = experiment_movement(keys, n, vnodes)
    spread_rows, ring_owners = experiment_spread(keys, n, vnode_list, cache)
    hot_rows = experiment_hot(ring_owners[max(vnode_list)], n, hot_fraction, hot_share, zipf_s, seed)
    return {"keys": keys_count, "nodes": n, "seed": seed, "movement": movement, "spread": spread_rows,
            "hot_keys": hot_rows, "hot_ring_vnodes": max(vnode_list)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keys", type=int, default=100_000, help="number of synthetic shipment IDs")
    ap.add_argument("--nodes", type=int, default=10, help="starting node count N")
    ap.add_argument("--vnodes", type=int, default=100, help="virtual nodes per node for experiment A")
    ap.add_argument("--vnode-list", type=int, nargs="+", default=[1, 10, 100, 200],
                    help="virtual-node counts for experiment B")
    ap.add_argument("--hot-fraction", type=float, default=0.01, help="fraction of keys that are hot")
    ap.add_argument("--hot-share", type=float, default=0.30, help="fraction of reads the hot keys receive")
    ap.add_argument("--zipf", type=float, default=1.0, help="skew inside the hot set for the last row")
    ap.add_argument("--seed", type=int, default=8)
    ap.add_argument("--json", help="also write results to this file")
    args = ap.parse_args()
    if args.nodes < 2:
        ap.error("--nodes must be at least 2 (the N-1 case needs a node left)")

    t0 = time.perf_counter()
    res = run(args.keys, args.nodes, args.vnodes, args.vnode_list, args.hot_fraction, args.hot_share,
              args.zipf, args.seed)
    n = args.nodes
    print(f"{args.keys} keys, N = {n} nodes, seed {args.seed}\n")
    print(f"A. Keys moved when the cluster changes (theory: mod-N moves N/(N+1) = {n / (n + 1):.4f} on a join "
          f"and (N-1)/N = {(n - 1) / n:.4f} on a leave;\n   ring and rendezvous move 1/(N+1) = {1 / (n + 1):.4f} "
          f"on a join and 1/N = {1 / n:.4f} on a leave)")
    print_table(res["movement"], ["scheme", "change", "moved", "theory", "only_changed_node"],
                ["scheme", "nodes", "moved", "theory", "minimal moves"], decimals=4)
    print("\nB. Keys per node (1.0 is perfectly even; cv = standard deviation / mean)")
    print_table(res["spread"], ["scheme", "vnodes", "max_over_mean", "min_over_mean", "cv", "cv_theory"],
                ["scheme", "vnodes", "max/mean", "min/mean", "cv", "~1/sqrt(vnodes)"])
    print(f"\nC. Keys versus reads per node (ring, {res['hot_ring_vnodes']} vnodes; "
          f"mean node read share = {100 / n:.2f}%)")
    print_table(res["hot_keys"], ["scenario", "keys_max_over_mean", "reads_max_over_mean",
                                  "busiest_node_read_pct", "top_key_read_pct"],
                ["scenario", "keys max/mean", "reads max/mean", "busiest node %", "top key %"])
    print(f"\nfinished in {time.perf_counter() - t0:.1f} s")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
