#!/usr/bin/env python3
"""Lab 11: a tiny "collector" that reads both services' JSON log files. Standard library only.

  python3 collect.py traces  logs/*.log [--slowest 5]     how many traces, connected or not, errors
  python3 collect.py tree    logs/*.log --trace <id>      one trace as a tree of spans
  python3 collect.py tree    logs/*.log --slowest         the slowest trace as a tree
  python3 collect.py latency logs/*.log [--by carrier]    per-route percentiles (nearest rank)

A span's start is computed as its log timestamp (written at the end of the request) minus its
duration. Both services run on one machine, so their clocks agree; across machines, clock skew
would shift children relative to parents, which is why real tracers record start times explicitly.
"""
import argparse
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone


def load_spans(paths):
    spans, bad = [], 0
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    end = datetime.strptime(rec["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    end = end.replace(tzinfo=timezone.utc).timestamp()
                    rec["_start"] = end - rec["duration_ms"] / 1000
                    spans.append(rec)
                except (ValueError, KeyError):
                    bad += 1
    return spans, bad


def by_trace(spans):
    traces = defaultdict(list)
    for s in spans:
        traces[s["trace_id"]].append(s)
    return traces


def roots_of(trace_spans):
    ids = {s["span_id"] for s in trace_spans}
    return [s for s in trace_spans if s["parent_span_id"] is None or s["parent_span_id"] not in ids]


def trace_duration(trace_spans):
    start = min(s["_start"] for s in trace_spans)
    end = max(s["_start"] + s["duration_ms"] / 1000 for s in trace_spans)
    return (end - start) * 1000


def percentile(sorted_values, p):
    """Nearest-rank percentile: the smallest value with at least p% of values at or below it."""
    rank = max(1, math.ceil(p / 100 * len(sorted_values)))
    return sorted_values[rank - 1]


def describe(s):
    extra = " ".join(f"{k}={s[k]}" for k in ("shipment_id", "carrier") if s.get(k))
    msg = f'  "{s["message"]}"' if s.get("message") else ""
    return (f'{s["service"]:<15}{s.get("method", "GET")} {s["route"]:<23}{s["status"]}  '
            f'{s["duration_ms"]:8.2f} ms  span={s["span_id"]}  {extra}{msg}')


def render_tree(trace_spans, out):
    t0 = min(s["_start"] for s in trace_spans)
    children = defaultdict(list)
    for s in trace_spans:
        children[s["parent_span_id"]].append(s)
    services = sorted({s["service"] for s in trace_spans})
    print(f'trace {trace_spans[0]["trace_id"]}: {len(trace_spans)} spans, {len(services)} '
          f'service(s) {services}, {trace_duration(trace_spans):.2f} ms', file=out)

    def walk(span, prefix, is_last, depth):
        branch = "" if depth == 0 else ("`-- " if is_last else "|-- ")
        offset = (span["_start"] - t0) * 1000
        print(f"{prefix}{branch}[+{offset:7.2f} ms] {describe(span)}", file=out)
        kids = sorted(children.get(span["span_id"], []), key=lambda k: k["_start"])
        for i, kid in enumerate(kids):
            ext = "" if depth == 0 else ("    " if is_last else "|   ")
            walk(kid, prefix + ext, i == len(kids) - 1, depth + 1)

    for root in sorted(roots_of(trace_spans), key=lambda r: r["_start"]):
        if root["parent_span_id"] is not None:
            print(f'(parent {root["parent_span_id"]} is not in these logs: a caller that does not log, '
                  f'or a lost span)', file=out)
        walk(root, "", True, 0)


def cmd_traces(spans, args, out):
    traces = by_trace(spans)
    per_service = defaultdict(int)
    for s in spans:
        per_service[s["service"]] += 1
    multi = [t for t in traces.values() if len({s["service"] for s in t}) > 1]
    roots = [s for s in spans if s["parent_span_id"] is None]
    ids = {s["span_id"] for s in spans}
    dangling = [s for s in spans if s["parent_span_id"] is not None and s["parent_span_id"] not in ids]
    print(f"spans: {len(spans)} {dict(sorted(per_service.items()))}", file=out)
    print(f"traces: {len(traces)}   spanning more than one service: {len(multi)}   "
          f"single-service: {len(traces) - len(multi)}", file=out)
    print(f"root spans (no parent): {len(roots)}   spans whose parent is not in the logs: {len(dangling)}",
          file=out)
    errors = [t for t in traces.values() if any(s["status"] >= 500 for s in t)]
    print(f"traces with an error (any span status >= 500): {len(errors)} (first 10 shown)", file=out)
    for t in sorted(errors, key=lambda t: min(s["_start"] for s in t))[:10]:
        worst = max(t, key=lambda s: (s["status"], s["_start"]))
        print(f"  {t[0]['trace_id']}  {describe(worst)}", file=out)
    print(f"slowest {args.slowest} traces (first to last span):", file=out)
    for t in sorted(traces.values(), key=trace_duration, reverse=True)[:args.slowest]:
        root = sorted(roots_of(t), key=lambda r: r["_start"])[0]
        print(f"  {t[0]['trace_id']}  {trace_duration(t):8.2f} ms  {len(t)} spans  "
              f"root: {root['service']} {root['route']} {root.get('shipment_id')}", file=out)
    return 0


def cmd_tree(spans, args, out):
    traces = by_trace(spans)
    if args.slowest_tree:
        trace_id = max(traces, key=lambda k: trace_duration(traces[k]))
    else:
        trace_id = args.trace
    if trace_id not in traces:
        print(f"trace {trace_id} not found in {len(traces)} traces", file=out)
        return 1
    render_tree(traces[trace_id], out)
    return 0


def cmd_latency(spans, args, out):
    groups = defaultdict(list)
    for s in spans:
        key = (s["service"], s["route"]) + ((str(s.get(args.by)),) if args.by else ())
        groups[key].append(s)
    head = f"{'service':<15}{'route':<23}" + (f"{args.by:<11}" if args.by else "")
    print(f"{head}{'count':>6}{'5xx':>5}{'p50':>9}{'p95':>9}{'p99':>9}{'max':>9}   (ms, nearest rank)",
          file=out)
    for key in sorted(groups):
        vals = sorted(s["duration_ms"] for s in groups[key])
        errs = sum(1 for s in groups[key] if s["status"] >= 500)
        label = f"{key[0]:<15}{key[1]:<23}" + (f"{key[2]:<11}" if args.by else "")
        print(f"{label}{len(vals):>6}{errs:>5}" + "".join(f"{percentile(vals, p):>9.2f}" for p in (50, 95, 99))
              + f"{vals[-1]:>9.2f}", file=out)
    return 0


def main(argv=None, out=sys.stdout):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("traces")
    t.add_argument("logs", nargs="+")
    t.add_argument("--slowest", type=int, default=5)
    tr = sub.add_parser("tree")
    tr.add_argument("logs", nargs="+")
    g = tr.add_mutually_exclusive_group(required=True)
    g.add_argument("--trace")
    g.add_argument("--slowest", dest="slowest_tree", action="store_true")
    la = sub.add_parser("latency")
    la.add_argument("logs", nargs="+")
    la.add_argument("--by", help="also group by this log field, for example carrier")
    args = p.parse_args(argv)
    spans, bad = load_spans(args.logs)
    if bad:
        print(f"skipped {bad} line(s) that were not valid JSON log records", file=out)
    return {"traces": cmd_traces, "tree": cmd_tree, "latency": cmd_latency}[args.cmd](spans, args, out)


if __name__ == "__main__":
    sys.exit(main())
