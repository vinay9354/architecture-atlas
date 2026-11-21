#!/usr/bin/env python3
"""Lab 10: run every attack and mistake the toy tracking API must handle, and print what it did.

Standard library only. By default this script generates a fresh signing key, starts the tracking API
on 127.0.0.1 with an ephemeral port in a background thread, runs the cases, and shuts it down. Nothing
is written to disk and the key is never printed.

Each case shows the status the client saw and the reason the server wrote to its own audit log. The
client never sees the reason: every bad token gets the same 401 body.

Run:  python3 client_demo.py            (table)
      python3 client_demo.py --verbose  (also prints each response body)
"""
import argparse
import http.client
import json
import sys
import threading
import time
from dataclasses import dataclass

import toy_jwt
import tracking_api

OWNER = "customer-a1"        # owns SHP-1001 and SHP-1003
OTHER_SHIPMENT = "SHP-1002"  # owned by customer-b2
READ = "tracking:read"
WRITE = "tracking:read tracking:preferences:write"

VALID_PREFS = {"delivery_window": "evening", "safe_place": "porch",
               "instructions": "Ring twice, parcel fits through the side gate", "notify_by": ["push"]}
INVALID_PREFS = {"delivery_window": "midnight", "instructions": "x" * 200, "notify_by": ["push", "push"],
                 "address": "a street address would go here"}


@dataclass
class Case:
    name: str
    method: str
    path: str
    expected: int
    token: str | None = None
    body: bytes | None = None
    content_type: str = "application/json"


def forge_alg_none(issuer: toy_jwt.ToyIssuer) -> str:
    """A token whose header says alg "none" and carries no signature (a classic forgery)."""
    good = issuer.issue(OWNER, scope=READ)
    claims = good.split(".")[1]
    header = toy_jwt.encode_segment({"alg": "none", "typ": toy_jwt.TOKEN_TYPE, "kid": issuer.kid})
    return f"{header}.{claims}."


def tamper_subject(issuer: toy_jwt.ToyIssuer) -> str:
    """Keep the real header and signature but rewrite the payload to claim another customer."""
    header, payload, signature = issuer.issue(OWNER, scope=READ).split(".")
    claims = json.loads(toy_jwt.b64url_decode(payload))
    claims["sub"] = "customer-b2"
    return f"{header}.{toy_jwt.encode_segment(claims)}.{signature}"


def build_cases(issuer: toy_jwt.ToyIssuer) -> list[Case]:
    attacker = toy_jwt.ToyIssuer(toy_jwt.new_key(), kid=issuer.kid)  # right kid, wrong key
    now = time.time()
    read_token = issuer.issue(OWNER, scope=READ)
    write_token = issuer.issue(OWNER, scope=WRITE)
    prefs = "/shipments/SHP-1001/delivery-preferences"
    return [
        Case("no token", "GET", "/shipments/SHP-1001", 401),
        Case("tampered payload (sub changed)", "GET", "/shipments/SHP-1002", 401, tamper_subject(issuer)),
        Case("signed with another key", "GET", "/shipments/SHP-1001", 401, attacker.issue(OWNER, scope=READ)),
        Case("expired (issued 10 min ago, ttl 5 min)", "GET", "/shipments/SHP-1001", 401,
             issuer.issue(OWNER, scope=READ, ttl_s=300, now=now - 600)),
        Case("wrong audience (loyalty-api)", "GET", "/shipments/SHP-1001", 401,
             issuer.issue(OWNER, audience="loyalty-api", scope=READ)),
        Case('alg "none", no signature', "GET", "/shipments/SHP-1001", 401, forge_alg_none(issuer)),
        Case("own shipment", "GET", "/shipments/SHP-1001", 200, read_token),
        Case("someone else's shipment", "GET", f"/shipments/{OTHER_SHIPMENT}", 404, read_token),
        Case("shipment that does not exist", "GET", "/shipments/SHP-9999", 404, read_token),
        Case("write without the write scope", "POST", prefs, 403, read_token, json.dumps(VALID_PREFS).encode()),
        Case("wrong content type", "POST", prefs, 415, write_token, b"delivery_window=evening",
             "application/x-www-form-urlencoded"),
        Case("body over 2048 bytes", "POST", prefs, 413, write_token,
             json.dumps({"delivery_window": "any", "instructions": "y" * 3000}).encode()),
        Case("malformed JSON", "POST", prefs, 400, write_token, b'{"delivery_window": "evening",'),
        Case("invalid fields (enum, length, duplicate, address)", "POST", prefs, 422, write_token,
             json.dumps(INVALID_PREFS).encode()),
        Case("valid preferences", "POST", prefs, 200, write_token, json.dumps(VALID_PREFS).encode()),
    ]


def send(host, port, case: Case):
    conn = http.client.HTTPConnection(host, port, timeout=5)
    headers = {}
    if case.token is not None:
        headers["Authorization"] = f"Bearer {case.token}"
    if case.body is not None:
        headers["Content-Type"] = case.content_type
    try:
        conn.request(case.method, case.path, body=case.body, headers=headers)
        resp = conn.getresponse()
        raw = resp.read()
        return resp.status, dict(resp.getheaders()), json.loads(raw) if raw else None
    finally:
        conn.close()


def run_cases(host, port, server, issuer):
    """Run every case; return a list of result dicts (also used by the smoke test)."""
    results = []
    for case in build_cases(issuer):
        before = len(server.audit)
        status, headers, body = send(host, port, case)
        reason = server.audit[before][3] if len(server.audit) > before else "?"
        results.append({"case": case.name, "method": case.method, "expected": case.expected,
                        "status": status, "reason": reason, "headers": headers, "body": body})
    return results


def start_server():
    key = toy_jwt.key_from_env() or toy_jwt.new_key()
    issuer = toy_jwt.ToyIssuer(key, kid="k1")
    server = tracking_api.make_server("127.0.0.1", 0, toy_jwt.Verifier({"k1": key}))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, issuer


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Lab 10 client demo against an in-process toy API.")
    p.add_argument("--verbose", action="store_true", help="print each response body")
    args = p.parse_args(argv)
    server, issuer = start_server()
    host, port = server.server_address[:2]
    try:
        results = run_cases(host, port, server, issuer)
    finally:
        server.shutdown()
        server.server_close()

    print(f"Toy tracking API on http://{host}:<ephemeral>, fresh signing key (not printed), kid=k1\n")
    print(f"{'#':>2}  {'method':<6} {'case':<50} {'expect':>6} {'got':>4}  server-side reason")
    print(f"{'-' * 2}  {'-' * 6} {'-' * 50} {'-' * 6} {'-' * 4}  {'-' * 24}")
    failures = 0
    for i, r in enumerate(results, 1):
        ok = r["status"] == r["expected"]
        failures += not ok
        print(f"{i:>2}  {r['method']:<6} {r['case']:<50} {r['expected']:>6} {r['status']:>4}  {r['reason']}"
              + ("" if ok else "   <-- MISMATCH"))
        if args.verbose and r["body"] is not None:
            print("      " + json.dumps(r["body"], separators=(",", ":")))
    print(f"\n{len(results) - failures}/{len(results)} cases returned the expected status.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
