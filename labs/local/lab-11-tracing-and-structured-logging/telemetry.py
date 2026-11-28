"""Lab 11: shared telemetry helpers for both services. Standard library only.

* `JsonLogger` writes exactly one JSON object per line (JSON Lines) to the service's log file.
* `start_span` reads the incoming `traceparent`, continues the trace if the header is valid, and
  starts a new trace if it is missing or invalid (the W3C "restart").

Field contract of every request log line (the collector relies on it):
    timestamp       UTC, ISO 8601 with microseconds, the moment the line was written (request end)
    level           INFO, WARN, or ERROR
    service         tracking-api or status-service
    trace_id        32 hex characters, shared by every span of one request across services
    span_id         16 hex characters, this service's unit of work for this request
    parent_span_id  the caller's span id, or null for a root span
    route           the route TEMPLATE (/track/{shipment_id}), never the raw path, so that it stays
                    low-cardinality and can be grouped
    status          HTTP status code returned
    duration_ms     time from request received to response written, milliseconds
Extra fields: method, shipment_id, carrier, tp_in (what happened to the incoming traceparent),
message. No customer data is logged: shipment ids are not personal data, and addresses are never
stored (AtlasMart NFR-6).
"""
import json
import threading
from datetime import datetime, timezone

import traceparent

FIELD_ORDER = ("timestamp", "level", "service", "trace_id", "span_id", "parent_span_id",
               "route", "status", "duration_ms")


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class JsonLogger:
    def __init__(self, service, path, echo=False):
        self.service = service
        self.path = path
        self.echo = echo
        self._lock = threading.Lock()
        # Truncate on start: ids are seeded, so a rerun must not mix with old lines.
        with open(path, "w", encoding="utf-8"):
            pass

    def request(self, *, level, trace_id, span_id, parent_span_id, route, status, duration_ms, **extra):
        record = {"timestamp": utc_now_iso(), "level": level, "service": self.service,
                  "trace_id": trace_id, "span_id": span_id, "parent_span_id": parent_span_id,
                  "route": route, "status": status, "duration_ms": round(duration_ms, 2)}
        record.update(extra)
        line = json.dumps(record, separators=(",", ":"))
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
            if self.echo:
                print(line, flush=True)
        return record


class Span:
    """The ids for one service's handling of one request."""

    def __init__(self, trace_id, span_id, parent_span_id, sampled, tp_in):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.sampled = sampled
        self.tp_in = tp_in

    def outgoing_traceparent(self):
        """Header for a call made while handling this request: same trace, this span as parent."""
        return traceparent.format_traceparent(self.trace_id, self.span_id, self.sampled)


def start_span(header_value, ids, ids_lock):
    ctx, reason = traceparent.parse(header_value)
    with ids_lock:
        span_id = ids.span_id()
        new_trace = None if ctx else ids.trace_id()
    if ctx:
        return Span(ctx.trace_id, span_id, ctx.parent_id, ctx.sampled, "valid")
    tp_in = "none" if reason == "missing" else f"invalid: {reason}"
    return Span(new_trace, span_id, None, True, tp_in)
