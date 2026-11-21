"""Smoke test for Lab 10 (REST API auth and validation): the toy API rejects every bad request it should."""
import contextlib
import importlib
import io
import json
import py_compile
import re
import sys
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-10-rest-api-auth-and-validation"


def load(name):
    if str(LAB) not in sys.path:
        sys.path.insert(0, str(LAB))  # the lab modules import each other by name
    return importlib.import_module(name)


class Lab10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jwt = load("toy_jwt")
        cls.val = load("validation")
        cls.api = load("tracking_api")
        cls.demo = load("client_demo")

    def setUp(self):
        self.key = self.jwt.new_key()
        self.issuer = self.jwt.ToyIssuer(self.key, kid="k1")
        self.verifier = self.jwt.Verifier({"k1": self.key})

    def reason(self, token):
        with self.assertRaises(self.jwt.TokenError) as ctx:
            self.verifier.verify(token)
        return ctx.exception.reason

    def test_sources_compile_and_no_committed_key(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)
        src = (LAB / "toy_jwt.py").read_text()
        self.assertIn("hmac.compare_digest", src)
        self.assertIn("secrets.token_bytes", src)

    def test_verifier_accepts_a_good_token(self):
        claims = self.verifier.verify(self.issuer.issue("customer-a1"))
        self.assertEqual(claims["sub"], "customer-a1")
        self.assertEqual(claims["aud"], "tracking-api")
        self.assertLessEqual(claims["exp"] - claims["iat"], 300)

    def test_verifier_rejection_reasons(self):
        now = time.time()
        self.assertEqual(self.reason("not-a-token"), "malformed")
        self.assertEqual(self.reason(self.demo.forge_alg_none(self.issuer)), "alg_not_allowed")
        self.assertEqual(self.reason(self.demo.tamper_subject(self.issuer)), "bad_signature")
        other = self.jwt.ToyIssuer(self.jwt.new_key(), kid="k1")
        self.assertEqual(self.reason(other.issue("customer-a1")), "bad_signature")
        self.assertEqual(self.reason(self.jwt.ToyIssuer(self.key, kid="k9").issue("customer-a1")), "unknown_kid")
        self.assertEqual(self.reason(self.issuer.issue("customer-a1", ttl_s=300, now=now - 600)), "expired")
        self.assertEqual(self.reason(self.issuer.issue("customer-a1", audience="loyalty-api")), "wrong_audience")
        self.assertEqual(self.reason(self.issuer.issue("customer-a1", now=now + 3600)), "issued_in_future")
        wrong_iss = self.jwt.ToyIssuer(self.key, kid="k1", issuer="https://evil.example")
        self.assertEqual(self.reason(wrong_iss.issue("customer-a1")), "wrong_issuer")

    def test_key_rotation_with_two_kids(self):
        new_key = self.jwt.new_key()
        both = self.jwt.Verifier({"k1": self.key, "k2": new_key})
        self.assertEqual(both.verify(self.issuer.issue("customer-a1"))["sub"], "customer-a1")
        self.assertEqual(both.verify(self.jwt.ToyIssuer(new_key, kid="k2").issue("customer-a1"))["sub"], "customer-a1")

    def test_validator_rules(self):
        v = self.val.validate_preferences
        self.assertEqual(v({"delivery_window": "morning"}), [])
        self.assertEqual(v(dict(self.demo.VALID_PREFS)), [])
        pointers = {e["pointer"] for e in v(dict(self.demo.INVALID_PREFS))}
        self.assertEqual(pointers, {"/address", "/delivery_window", "/instructions", "/notify_by"})
        self.assertEqual(v({})[0]["pointer"], "/delivery_window")  # required
        self.assertTrue(v({"delivery_window": True}))               # wrong type
        self.assertTrue(v({"delivery_window": "any", "notify_by": "push"}))  # not an array
        self.assertTrue(v({"delivery_window": "any", "instructions": "a\u0007b"}))  # control character
        self.assertTrue(v(["delivery_window"]))                      # not an object
        with self.assertRaises(self.val.MalformedJson):
            self.val.parse_json(b'{"delivery_window": "any", "delivery_window": "evening"}')
        with self.assertRaises(self.val.MalformedJson):
            self.val.parse_json(b'{"delivery_window": NaN}')

    def test_api_end_to_end_status_codes(self):
        server = self.api.make_server("127.0.0.1", 0, self.verifier)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        host, port = server.server_address[:2]
        try:
            results = self.demo.run_cases(host, port, server, self.issuer)
        finally:
            server.shutdown()
            server.server_close()
        by_case = {r["case"]: r for r in results}
        for r in results:
            self.assertEqual(r["status"], r["expected"], r["case"])
        expected = {
            "no token": 401, "tampered payload (sub changed)": 401, "signed with another key": 401,
            "expired (issued 10 min ago, ttl 5 min)": 401, "wrong audience (loyalty-api)": 401,
            'alg "none", no signature': 401, "own shipment": 200, "someone else's shipment": 404,
            "write without the write scope": 403, "malformed JSON": 400,
            "invalid fields (enum, length, duplicate, address)": 422, "body over 2048 bytes": 413,
            "valid preferences": 200,
        }
        for name, status in expected.items():
            self.assertEqual(by_case[name]["status"], status, name)
        # Every rejected token looks the same to the client; the reason stays server-side.
        bad = [by_case[n]["body"] for n in expected if expected[n] == 401 and n != "no token"]
        self.assertTrue(all(b == {**bad[0], "instance": b["instance"]} for b in bad))
        self.assertIn('error="invalid_token"', by_case["expired (issued 10 min ago, ttl 5 min)"]["headers"]["WWW-Authenticate"])
        # Someone else's shipment is indistinguishable from a missing one (BOLA probing).
        other, missing = by_case["someone else's shipment"]["body"], by_case["shipment that does not exist"]["body"]
        self.assertEqual({**other, "instance": ""}, {**missing, "instance": ""})
        self.assertEqual(by_case["someone else's shipment"]["reason"], "not_owner")
        # Problem details and no address stored (NFR-6).
        invalid = by_case["invalid fields (enum, length, duplicate, address)"]
        self.assertEqual(invalid["headers"]["Content-Type"], "application/problem+json")
        self.assertIn("/address", {e["pointer"] for e in invalid["body"]["errors"]})
        self.assertNotIn("address", json.dumps(server.preferences))
        self.assertNotIn("SHP-1002", server.preferences)

    def test_demo_cli_reports_all_cases(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.demo.main([])
        self.assertEqual(code, 0)
        self.assertIn("15/15 cases returned the expected status.", out.getvalue())
        self.assertIsNone(re.search(r"[0-9a-f]{64}", out.getvalue()))  # the key is never printed


if __name__ == "__main__":
    unittest.main()
