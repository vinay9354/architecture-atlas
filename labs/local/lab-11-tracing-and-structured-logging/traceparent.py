#!/usr/bin/env python3
"""Lab 11: W3C Trace Context `traceparent` parsing and generation, written by hand.

Standard library only. Teaching code, not a replacement for an OpenTelemetry propagator.

Format (W3C Trace Context Level 1, version 00), 55 characters, lowercase hex, dash separated:

    00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
    |  |                                |                |
    |  trace-id: 16 bytes, 32 hex       parent-id: 8     trace-flags: 8 bits, bit 0 = sampled
    version: 1 byte, 2 hex              bytes, 16 hex

Validation rules implemented (from the specification's traceparent section and processing model):
  * the version is two lowercase hex characters followed by a dash; version ff is invalid;
  * version 00 is exactly 55 characters: trace-id, parent-id, and trace-flags, nothing more;
  * a higher (future) version is parsed with the 00 layout if it is at least 55 characters and
    character 56 is either the end of the value or a dash; anything after that is ignored;
  * trace-id is 32 and parent-id 16 lowercase hex characters, and neither may be all zeros;
  * trace-flags is 2 lowercase hex characters; only the sampled bit (0x01) is understood, and the
    other bits are never copied to outgoing headers.
A receiver that finds the header missing or invalid ignores it and starts a new trace ("restart").

Identifiers come from random.Random(seed) so that lab runs are reproducible. Real tracers must use
a good random source: the specification prefers random trace-ids, and predictable ids leak
information and make collisions likelier.
"""
import random
from dataclasses import dataclass

VERSION = "00"
FLAG_SAMPLED = 0x01
_HEX = frozenset("0123456789abcdef")
_LEN_V00 = 55


@dataclass(frozen=True)
class TraceContext:
    trace_id: str
    parent_id: str
    sampled: bool


def _lower_hex(text, length):
    return len(text) == length and all(c in _HEX for c in text)


def parse(value):
    """Return (TraceContext or None, reason). The reason is "valid" or why the header was ignored."""
    if value is None or value.strip() == "":
        return None, "missing"
    value = value.strip()   # HTTP servers strip surrounding whitespace from field values
    version = value[:2]
    if not (_lower_hex(version, 2) and value[2:3] == "-"):
        return None, "bad version"
    if version == "ff":
        return None, "version ff is forbidden"
    if version == VERSION and len(value) != _LEN_V00:
        return None, f"version 00 must be 55 characters, got {len(value)}"
    if version != VERSION and (len(value) < _LEN_V00 or (len(value) > _LEN_V00 and value[_LEN_V00] != "-")):
        return None, "future version with an unparseable 00 prefix"
    trace_id, parent_id, flags = value[3:35], value[36:52], value[53:55]
    if value[35:36] != "-" or value[52:53] != "-":
        return None, "misplaced dash"
    if not _lower_hex(trace_id, 32):
        return None, "trace-id is not 32 lowercase hex characters"
    if trace_id == "0" * 32:
        return None, "trace-id is all zeros"
    if not _lower_hex(parent_id, 16):
        return None, "parent-id is not 16 lowercase hex characters"
    if parent_id == "0" * 16:
        return None, "parent-id is all zeros"
    if not _lower_hex(flags, 2):
        return None, "trace-flags is not 2 lowercase hex characters"
    return TraceContext(trace_id, parent_id, bool(int(flags, 16) & FLAG_SAMPLED)), "valid"


def format_traceparent(trace_id, span_id, sampled=True):
    """Build a version 00 header. Unknown flag bits are always sent as zero."""
    if not (_lower_hex(trace_id, 32) and trace_id != "0" * 32):
        raise ValueError("invalid trace-id")
    if not (_lower_hex(span_id, 16) and span_id != "0" * 16):
        raise ValueError("invalid span-id")
    return f"{VERSION}-{trace_id}-{span_id}-{FLAG_SAMPLED if sampled else 0:02x}"


class IdGenerator:
    """Seeded, thread-unsafe on its own: callers hold a lock (the services do)."""

    def __init__(self, seed):
        self._rng = random.Random(seed)

    def _nonzero(self, bits):
        while True:
            n = self._rng.getrandbits(bits)
            if n:
                return f"{n:0{bits // 4}x}"

    def trace_id(self):
        return self._nonzero(128)

    def span_id(self):
        return self._nonzero(64)


if __name__ == "__main__":
    examples = [
        "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
        "00-4BF92F3577B34DA6A3CE929D0E0E4736-00F067AA0BA902B7-01",
        "00-00000000000000000000000000000000-00f067aa0ba902b7-01",
        "ff-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
        "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01-extra",
        "01-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-09-future-field",
    ]
    for header in examples:
        ctx, reason = parse(header)
        print(f"{header:<70} {reason}" + (f" (sampled={ctx.sampled})" if ctx else ""))
