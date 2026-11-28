"""Smoke test for Lab 11 (tracing and structured logging): traceparent rules, propagation, broken propagation."""
import contextlib
import importlib
import io
import json
import py_compile
import re
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-11-tracing-and-structured-logging"
TP_RE = re.compile(r"^00-[0-9a-f]{32}-[0-9a-f]{16}-0[01]$")
FIELDS = ["timestamp", "level", "service", "trace_id", "span_id", "parent_span_id", "route", "status",
          "duration_ms"]


def load(name):
    """Import a lab module by name, making sure it comes from THIS lab's folder.

    Several labs reuse module names (for example tracking_api.py in Labs 10 and 11). When the whole
    suite runs in one process, a module cached by another lab's test would otherwise be reused here.
    """
    lab = str(LAB)
    if lab in sys.path:
        sys.path.remove(lab)
    sys.path.insert(0, lab)  # the lab modules import each other by name
    cached = sys.modules.get(name)
    if cached is not None and not str(getattr(cached, "__file__", "")).startswith(lab):
        for mod_name, mod in list(sys.modules.items()):
            mod_file = str(getattr(mod, "__file__", "") or "")
            if mod_file.startswith(str(LAB.parent)) and not mod_file.startswith(lab):
                del sys.modules[mod_name]
    return importlib.import_module(name)


def serve(server):
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{server.server_address[1]}"


def stop(*servers):
    for s in servers:
        s.shutdown()
        s.server_close()


def read_log(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


class CaptureHandler(BaseHTTPRequestHandler):
    """A stand-in downstream that records the traceparent header it receives."""
    seen = []

    def log_message(self, *args):
        pass

    def do_GET(self):  # noqa: N802
        CaptureHandler.seen.append(self.headers.get("traceparent"))
        body = json.dumps({"status": "in transit", "eta": "2026-12-01"}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class Lab11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tp = load("traceparent")
        cls.status = load("status_service")
        cls.api = load("tracking_api")
        cls.load = load("load")
        cls.collect = load("collect")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_pair(self, propagate, shipments, header=None):
        """Start both services on ephemeral ports, send one request per shipment, return both logs."""
        st_log, api_log = self.dir / f"st-{propagate}.log", self.dir / f"api-{propagate}.log"
        st = self.status.make_server("127.0.0.1", 0, str(st_log), seed=12, slow_ms=40)
        api = self.api.make_server("127.0.0.1", 0, serve(st), str(api_log), seed=11, propagate=propagate)
        url = serve(api)
        try:
            codes = [self.load.send(url, s, header if i == 0 else None)[0] for i, s in enumerate(shipments)]
        finally:
            stop(api, st)
        return codes, read_log(api_log), read_log(st_log), [str(api_log), str(st_log)]

    def test_sources_compile(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_traceparent_rules_from_the_spec(self):
        parse = self.tp.parse
        ctx, why = parse("00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01")
        self.assertEqual((why, ctx.trace_id, ctx.parent_id, ctx.sampled),
                         ("valid", "4bf92f3577b34da6a3ce929d0e0e4736", "00f067aa0ba902b7", True))
        self.assertFalse(parse("00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-00")[0].sampled)
        self.assertTrue(parse("00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-09")[0].sampled)
        invalid = {
            None: "missing",
            "00-4BF92F3577B34DA6A3CE929D0E0E4736-00f067aa0ba902b7-01": "trace-id is not",
            "00-00000000000000000000000000000000-00f067aa0ba902b7-01": "trace-id is all zeros",
            "00-4bf92f3577b34da6a3ce929d0e0e4736-0000000000000000-01": "parent-id is all zeros",
            "ff-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01": "version ff",
            "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01-x": "version 00 must be 55",
            "0x-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01": "bad version",
            "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-0g": "trace-flags",
            "01-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01x": "future version",
            "00_4bf92f3577b34da6a3ce929d0e0e4736_00f067aa0ba902b7_01": "bad version",
        }
        for header, reason in invalid.items():
            ctx, why = parse(header)
            self.assertIsNone(ctx, header)
            self.assertIn(reason, why, header)
        # A higher version is parsed with the 00 layout; fields after the flags are ignored.
        ctx, why = parse("01-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01-future")
        self.assertEqual((why, ctx.parent_id), ("valid", "00f067aa0ba902b7"))
        ids = self.tp.IdGenerator(1)
        header = self.tp.format_traceparent(ids.trace_id(), ids.span_id(), True)
        self.assertRegex(header, TP_RE)
        self.assertEqual(len(header), 55)
        with self.assertRaises(ValueError):
            self.tp.format_traceparent("0" * 32, "00f067aa0ba902b7")

    def test_outgoing_header_on_the_wire(self):
        CaptureHandler.seen = []
        fake = ThreadingHTTPServer(("127.0.0.1", 0), CaptureHandler)
        log = self.dir / "api-capture.log"
        api = self.api.make_server("127.0.0.1", 0, serve(fake), str(log), seed=11)
        try:
            self.assertEqual(self.load.send(serve(api), "SHP-1001")[0], 200)
        finally:
            stop(api, fake)
        (span,) = read_log(log)
        self.assertEqual(len(CaptureHandler.seen), 2)          # /status and /eta
        for header in CaptureHandler.seen:
            self.assertRegex(header, TP_RE)
            _, trace_id, parent_id, _ = header.split("-")
            self.assertEqual((trace_id, parent_id), (span["trace_id"], span["span_id"]))

    def test_propagation_links_both_services(self):
        client = self.tp.IdGenerator(99)
        c_trace, c_span = client.trace_id(), client.span_id()
        header = self.tp.format_traceparent(c_trace, c_span)
        shipments = ["SHP-1000", "SHP-1001", "SHP-1007", "SHP-1013", "SHP-1002"]
        codes, api_spans, st_spans, logs = self.run_pair(True, shipments, header)
        self.assertEqual(codes, [200, 200, 200, 502, 200])
        for rec in api_spans + st_spans:
            self.assertEqual(list(rec)[:len(FIELDS)], FIELDS)   # one JSON object per line, fixed order
            self.assertRegex(rec["trace_id"], r"^[0-9a-f]{32}$")
            self.assertRegex(rec["span_id"], r"^[0-9a-f]{16}$")
            self.assertTrue(rec["timestamp"].endswith("Z"))
        # The client's trace was continued: same trace id, the client's span is the parent.
        self.assertEqual((api_spans[0]["trace_id"], api_spans[0]["parent_span_id"], api_spans[0]["tp_in"]),
                         (c_trace, c_span, "valid"))
        self.assertTrue(all(s["parent_span_id"] is None for s in api_spans[1:]))
        for parent in api_spans:
            children = [s for s in st_spans if s["trace_id"] == parent["trace_id"]]
            self.assertEqual(len(children), 1 if parent["status"] == 502 else 2)
            for child in children:
                self.assertEqual(child["parent_span_id"], parent["span_id"])
                self.assertEqual(child["tp_in"], "valid")
        self.assertEqual(len({s["span_id"] for s in api_spans + st_spans}), len(api_spans + st_spans))
        # The planted faults are visible from the logs alone.
        err = [s for s in st_spans if s["status"] >= 500]
        self.assertEqual([(s["shipment_id"], s["route"], s["level"]) for s in err],
                         [("SHP-1013", "/status/{shipment_id}", "ERROR")])
        slow = [s for s in st_spans if s["route"] == "/eta/{shipment_id}" and s["carrier"] == "carrier-c"]
        self.assertGreaterEqual(slow[0]["duration_ms"], 40)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(self.collect.main(["tree", *logs, "--slowest"], out=out), 0)
        tree = out.getvalue()
        self.assertIn("3 spans, 2 service(s)", tree)
        self.assertIn("`-- ", tree)
        self.assertIn("carrier=carrier-c", tree)
        out = io.StringIO()
        self.collect.main(["traces", *logs], out=out)
        self.assertIn("traces: 5   spanning more than one service: 5   single-service: 0", out.getvalue())

    def test_invalid_incoming_header_restarts_the_trace(self):
        for label, header in self.load.probe_headers(10)[1:]:
            _, api_spans, st_spans, _ = self.run_pair(True, ["SHP-1000"], header)
            self.assertTrue(api_spans[0]["tp_in"].startswith("invalid: "), label)
            self.assertIsNone(api_spans[0]["parent_span_id"], label)
            self.assertNotIn(api_spans[0]["trace_id"], header.lower(), label)
            self.assertEqual({s["trace_id"] for s in st_spans}, {api_spans[0]["trace_id"]}, label)

    def test_without_propagation_each_request_falls_apart(self):
        shipments = ["SHP-1000", "SHP-1007", "SHP-1013"]
        _, api_spans, st_spans, logs = self.run_pair(False, shipments)
        self.assertEqual(len(st_spans), 5)
        api_traces = {s["trace_id"] for s in api_spans}
        for s in st_spans:
            self.assertIsNone(s["parent_span_id"])
            self.assertEqual(s["tp_in"], "none")
            self.assertNotIn(s["trace_id"], api_traces)
        out = io.StringIO()
        self.collect.main(["traces", *logs], out=out)
        self.assertIn("traces: 8   spanning more than one service: 0   single-service: 8", out.getvalue())


if __name__ == "__main__":
    unittest.main()
