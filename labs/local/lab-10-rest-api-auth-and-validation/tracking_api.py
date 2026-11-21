#!/usr/bin/env python3
"""Lab 10: a TEACHING TOY tracking API with bearer-token authentication, owner-only access, and
request validation. Standard library only (http.server). Not for production use.

Routes
  GET  /shipments/{id}                       scope tracking:read, owner only
  POST /shipments/{id}/delivery-preferences  scope tracking:preferences:write, owner only,
                                             JSON body checked by validation.py
  GET  /health                               no token

Every error is an RFC 9457 problem-details document (Content-Type: application/problem+json).

Decisions worth reading the code for
  * 401 versus 403: 401 means "I do not know who you are" (no token, or a token that fails any check);
    403 means "I know who you are and you may not do this" (missing scope).
  * Someone else's shipment returns 404, byte-for-byte the same body as a shipment that does not exist,
    so a caller cannot use the API to learn which shipment ids exist (BOLA / IDOR probing).
  * Checks run in a fixed order: authenticate, authorize the action (scope), authorize the object
    (owner), then validate the body. An unauthenticated caller learns nothing about validation rules.
  * The reason a token was rejected is written to the server's audit list and stderr, never to the
    client: telling an attacker "signature fine, audience wrong" helps them.
  * No delivery address is stored anywhere (NFR-6); shipments hold only status data.

Run standalone (the key must be shared with toy_jwt.py, so it comes from the environment):
  export LAB10_SIGNING_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  python3 tracking_api.py --port 8010
"""
import argparse
import json
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import toy_jwt
import validation

PROBLEM_BASE = "https://atlasmart.example/problems/"
DRAIN_LIMIT_BYTES = 64 * 1024  # read and discard at most this much of an oversized body
SHIPMENT_RE = re.compile(r"^/shipments/([A-Z]{3}-[0-9]{4})$")
PREFS_RE = re.compile(r"^/shipments/([A-Z]{3}-[0-9]{4})/delivery-preferences$")


def seed_shipments():
    """Fictional seed data. Owners are opaque customer ids from the identity provider, not names."""
    return {
        "SHP-1001": {"owner": "customer-a1", "status": "in_transit", "last_event": "departed hub", "eta": "2026-11-24"},
        "SHP-1002": {"owner": "customer-b2", "status": "out_for_delivery", "last_event": "on vehicle", "eta": "2026-11-21"},
        "SHP-1003": {"owner": "customer-a1", "status": "delivered", "last_event": "delivered", "eta": "2026-11-19"},
    }


class TrackingServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, verifier, quiet=True):
        super().__init__(address, Handler)
        self.verifier = verifier
        self.quiet = quiet
        self.shipments = seed_shipments()
        self.preferences = {}
        self.audit = []  # (method, path, status, reason) - what a real service sends to its log pipeline
        self.lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    server: TrackingServer

    def version_string(self):  # do not advertise the Python version in the Server header
        return "lab10-toy"

    # ---- routing -------------------------------------------------------------------------------
    def do_GET(self):  # noqa: N802 (http.server naming)
        if self.path == "/health":
            self._json(200, {"status": "ok"}, "health")
            return
        m = SHIPMENT_RE.match(self.path)
        if not m:
            self._problem(404, "not-found", "Not Found", "No such resource.", "no_route")
            return
        claims = self._authenticate()
        if claims is None or not self._require_scope(claims, "tracking:read"):
            return
        shipment = self._owned_shipment(m.group(1), claims["sub"])
        if shipment is None:
            return
        body = {"id": m.group(1), **{k: v for k, v in shipment.items() if k != "owner"}}
        self._json(200, body, "ok")

    def do_POST(self):  # noqa: N802
        raw, too_large, length_error = self._read_body()
        m = PREFS_RE.match(self.path)
        if not m:
            self._problem(404, "not-found", "Not Found", "No such resource.", "no_route")
            return
        claims = self._authenticate()
        if claims is None or not self._require_scope(claims, "tracking:preferences:write"):
            return
        if self._owned_shipment(m.group(1), claims["sub"]) is None:
            return
        ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if ctype != "application/json":
            self._problem(415, "unsupported-media-type", "Unsupported Media Type",
                          "Send the body as application/json.", "wrong_content_type")
            return
        if length_error:
            self._problem(411, "length-required", "Length Required",
                          "Send a valid Content-Length header.", "no_content_length")
            return
        if too_large:
            self._problem(413, "body-too-large", "Content Too Large",
                          f"The body must be at most {validation.MAX_BODY_BYTES} bytes.", "body_too_large")
            return
        try:
            body = validation.parse_json(raw)
        except validation.MalformedJson as exc:
            self._problem(400, "malformed-json", "Bad Request", "The body is not valid JSON.", f"malformed_json: {exc}")
            return
        errors = validation.validate_preferences(body)
        if errors:
            self._problem(422, "validation-error", "Your request is not valid.",
                          f"{len(errors)} field(s) failed validation.", "validation_failed", errors=errors)
            return
        with self.server.lock:
            self.server.preferences[m.group(1)] = body
        self._json(200, {"id": m.group(1), "delivery_preferences": body}, "ok")

    # ---- checks --------------------------------------------------------------------------------
    def _authenticate(self):
        header = self.headers.get("Authorization")
        if not header:
            self._problem(401, "unauthenticated", "Unauthorized", "An access token is required.",
                          "no_token", www_authenticate='Bearer realm="tracking-api"')
            return None
        scheme, _, token = header.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            self._problem(401, "unauthenticated", "Unauthorized", "An access token is required.",
                          "not_bearer", www_authenticate='Bearer realm="tracking-api"')
            return None
        try:
            return self.server.verifier.verify(token.strip())
        except toy_jwt.TokenError as exc:
            # Same response for every reason; the reason goes to the audit log only.
            self._problem(401, "invalid-token", "Unauthorized", "The access token is invalid or expired.",
                          exc.reason, www_authenticate='Bearer realm="tracking-api", error="invalid_token"')
            return None

    def _require_scope(self, claims, needed):
        granted = str(claims.get("scope", "")).split()
        if needed in granted:
            return True
        self._problem(403, "insufficient-scope", "Forbidden", f"This action needs the {needed} scope.",
                      "insufficient_scope",
                      www_authenticate=f'Bearer realm="tracking-api", error="insufficient_scope", scope="{needed}"')
        return False

    def _owned_shipment(self, shipment_id, subject):
        shipment = self.server.shipments.get(shipment_id)
        if shipment is None or shipment["owner"] != subject:
            reason = "no_such_shipment" if shipment is None else "not_owner"
            # Identical client-visible response for both reasons (see module docstring).
            self._problem(404, "not-found", "Not Found", "No such shipment for this account.", reason)
            return None
        return shipment

    def _read_body(self):
        """Return (raw, too_large, length_error). Always consume what the client sent (up to a cap)
        so the connection closes cleanly, but never keep more than MAX_BODY_BYTES in memory."""
        try:
            length = int(self.headers.get("Content-Length", ""))
            if length < 0:
                raise ValueError
        except ValueError:
            return b"", False, True
        if length > validation.MAX_BODY_BYTES:
            remaining = min(length, DRAIN_LIMIT_BYTES)
            while remaining > 0:
                chunk = self.rfile.read(min(remaining, 8192))
                if not chunk:
                    break
                remaining -= len(chunk)
            if length > DRAIN_LIMIT_BYTES:
                self.close_connection = True
            return b"", True, False
        return self.rfile.read(length), False, False

    # ---- responses -----------------------------------------------------------------------------
    def _problem(self, status, slug, title, detail, reason, www_authenticate=None, **extensions):
        doc = {"type": PROBLEM_BASE + slug, "title": title, "status": status, "detail": detail,
               "instance": self.path.split("?")[0], **extensions}
        headers = {"WWW-Authenticate": www_authenticate} if www_authenticate else {}
        self._send(status, doc, "application/problem+json", reason, headers)

    def _json(self, status, payload, reason):
        self._send(status, payload, "application/json", reason, {})

    def _send(self, status, payload, ctype, reason, headers):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        with self.server.lock:  # record before replying, so a client that reads the log sees it
            self.server.audit.append((self.command, self.path, status, reason))
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)
        if not self.server.quiet:
            print(f"{self.command} {self.path} -> {status} ({reason})", file=sys.stderr)

    def log_message(self, format, *args):  # noqa: A002 - replaced by the audit list above
        return


def make_server(host, port, verifier, quiet=True):
    return TrackingServer((host, port), verifier, quiet=quiet)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Lab 10 toy tracking API (teaching only).")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8010)
    args = p.parse_args(argv)
    key = toy_jwt.key_from_env()
    if key is None:
        print(f"Set {toy_jwt.KEY_ENV_VAR} first (see the module docstring), "
              "or run client_demo.py, which starts its own server with a fresh key.", file=sys.stderr)
        return 2
    server = make_server(args.host, args.port, toy_jwt.Verifier({"k1": key}), quiet=False)
    print(f"Tracking API on http://{args.host}:{server.server_address[1]} (Ctrl+C to stop)", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
