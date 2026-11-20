#!/usr/bin/env python3
"""Lab 08 placement schemes: hash-mod-N, a consistent-hash ring with virtual nodes, and rendezvous hashing.

Standard library only. Every scheme answers one question, "which node owns this key?", using a stable
hash (MD5 truncated to 64 bits). Python's built-in hash() is deliberately NOT used: it is randomized
per process for strings, so two processes (or two runs) would disagree about where a key lives.

MD5 is used here only as a fast, well-mixed, stable function, not for security.

Import it from measure.py, or try it interactively:

    >>> from placement import ModN, Ring, Rendezvous
    >>> ring = Ring(["node-0", "node-1", "node-2"], vnodes=100)
    >>> ring.node_for("SHP-0000000042")
"""
import bisect
import hashlib


def stable_hash(text):
    """64-bit integer from the first 8 bytes of MD5(text). Same input, same output, in every process."""
    return int.from_bytes(hashlib.md5(text.encode("utf-8")).digest()[:8], "big")


class ModN:
    """Hash-mod-N: owner = nodes[hash(key) % N]. Simple and even, but N is baked into every placement."""

    name = "mod-N"

    def __init__(self, nodes):
        self.nodes = list(nodes)

    def node_for(self, key):
        return self.nodes[stable_hash(key) % len(self.nodes)]


class Ring:
    """Consistent-hash ring. Each node is placed at `vnodes` points on a 64-bit circle; a key belongs to
    the first point clockwise from the key's hash (wrapping around at the top)."""

    name = "ring"

    def __init__(self, nodes, vnodes=100):
        self.vnodes = vnodes
        points = []
        for node in nodes:
            for v in range(vnodes):
                points.append((stable_hash(f"{node}#vn{v}"), node))
        points.sort()
        self._hashes = [h for h, _ in points]   # sorted positions on the circle
        self._owners = [n for _, n in points]   # owner of each position

    def node_for(self, key):
        i = bisect.bisect_right(self._hashes, stable_hash(key))
        return self._owners[i % len(self._owners)]   # past the last point: wrap to the first


class Rendezvous:
    """Rendezvous (highest random weight) hashing: every node gets a score for the key, and the highest
    score wins. Removing a node only moves the keys it won; adding one only steals keys it now wins."""

    name = "rendezvous"

    def __init__(self, nodes):
        # Pre-hash each node name once; per key we only extend a copy of that state.
        self._seeds = [(node, hashlib.md5(f"{node}|".encode("utf-8"))) for node in nodes]

    def node_for(self, key):
        data = key.encode("utf-8")
        best_node, best_score = None, -1
        for node, seed in self._seeds:
            h = seed.copy()
            h.update(data)
            score = int.from_bytes(h.digest()[:8], "big")
            if score > best_score:
                best_node, best_score = node, score
        return best_node


def node_names(n):
    return [f"node-{i}" for i in range(n)]


def build(scheme, nodes, vnodes=100):
    """Factory used by measure.py and the smoke test."""
    if scheme == "mod-N":
        return ModN(nodes)
    if scheme == "ring":
        return Ring(nodes, vnodes)
    if scheme == "rendezvous":
        return Rendezvous(nodes)
    raise ValueError(f"unknown scheme {scheme!r}")


def assign(placer, keys):
    """List of owners, one per key, in key order."""
    return [placer.node_for(k) for k in keys]
