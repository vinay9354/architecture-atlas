#!/usr/bin/env python3
"""Lab 10: a TEACHING TOY token issuer and verifier for HS256, JWT-shaped access tokens.

Standard library only (hmac, hashlib, base64, json, secrets). It exists so you can see every check a
resource server must make on a bearer token, and what happens when one is skipped.

!!! Do not use this in production. !!!
Production services use a vetted JOSE/JWT library and asymmetric keys (for example RS256 or ES256)
published by the identity provider as a JSON Web Key Set (JWKS). With a shared HMAC key, as here,
every service that can verify a token can also mint one; that is acceptable for a local lab only.

The signing key is never stored in the repository. It is generated at runtime with
secrets.token_bytes(), or read as hex from the LAB10_SIGNING_KEY environment variable so that a
separately started server and this script's CLI share one key.

Verification order (each failure has its own reason code, logged server-side only):
  1. three base64url segments that decode to JSON objects           -> malformed
  2. header "alg" on the allow-list (HS256 only, so never "none")     -> alg_not_allowed
  3. header "typ" is "at+jwt" (explicit typing, RFC 8725 / RFC 9068)  -> wrong_typ
  4. header "kid" names a key the verifier holds (rotation)           -> unknown_kid
  5. HMAC-SHA256 signature, compared in constant time                 -> bad_signature
  6. claims: iss, aud, exp, nbf, iat, sub                             -> wrong_issuer, wrong_audience,
                                                                         expired, not_yet_valid,
                                                                         issued_in_future, missing_claim

CLI (mint a token for a separately started tracking_api.py):
  export LAB10_SIGNING_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  python3 toy_jwt.py --sub customer-a1 --scope "tracking:read"
"""
import argparse
import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
import sys
import time

ISSUER = "https://id.atlasmart.example"
AUDIENCE = "tracking-api"
TOKEN_TYPE = "at+jwt"
ALLOWED_ALGS = frozenset({"HS256"})
# The value below is the NAME of an environment variable, not a key; the key itself is generated
# at runtime and never stored in the repository.
KEY_ENV_VAR = "LAB10_SIGNING_KEY"  # gitleaks:allow
MIN_KEY_BYTES = 32  # 256 bits for HMAC-SHA256


class TokenError(Exception):
    """A token failed verification. `reason` is for server logs only, never for the client."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def b64url_decode(text: str) -> bytes:
    if not text or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in text):
        raise TokenError("malformed")
    try:
        return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
    except (binascii.Error, ValueError):
        raise TokenError("malformed") from None


def encode_segment(obj: dict) -> str:
    return b64url_encode(json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8"))


def sign(signing_input: str, key: bytes) -> str:
    return b64url_encode(hmac.new(key, signing_input.encode("ascii"), hashlib.sha256).digest())


def new_key() -> bytes:
    return secrets.token_bytes(MIN_KEY_BYTES)


def key_from_env() -> bytes | None:
    value = os.environ.get(KEY_ENV_VAR)
    if not value:
        return None
    try:
        key = bytes.fromhex(value)
    except ValueError:
        raise SystemExit(f"{KEY_ENV_VAR} must be hex, for example from secrets.token_hex(32)") from None
    if len(key) < MIN_KEY_BYTES:
        raise SystemExit(f"{KEY_ENV_VAR} must be at least {MIN_KEY_BYTES} bytes ({2 * MIN_KEY_BYTES} hex digits)")
    return key


class ToyIssuer:
    """Stands in for the customer identity provider's token endpoint after a successful sign-in."""

    def __init__(self, key: bytes, kid: str = "k1", issuer: str = ISSUER):
        self.key, self.kid, self.issuer = key, kid, issuer

    def issue(self, sub, audience=AUDIENCE, scope="tracking:read", ttl_s=300, now=None) -> str:
        now = int(time.time() if now is None else now)
        header = {"alg": "HS256", "typ": TOKEN_TYPE, "kid": self.kid}
        claims = {"iss": self.issuer, "aud": audience, "sub": sub, "scope": scope,
                  "iat": now, "exp": now + ttl_s, "jti": secrets.token_hex(8)}
        signing_input = f"{encode_segment(header)}.{encode_segment(claims)}"
        return f"{signing_input}.{sign(signing_input, self.key)}"


class Verifier:
    """What a resource server (the Tracking API) does with a bearer token before trusting it."""

    def __init__(self, keys: dict, issuer: str = ISSUER, audience: str = AUDIENCE, leeway_s: int = 30,
                 clock=time.time):
        self.keys = dict(keys)  # kid -> key; holding two kids at once is how rotation works
        self.issuer, self.audience, self.leeway_s, self.clock = issuer, audience, leeway_s, clock

    def verify(self, token: str) -> dict:
        parts = token.split(".")
        if len(parts) != 3:
            raise TokenError("malformed")
        header, claims = self._json(parts[0]), self._json(parts[1])

        # 2-4: decide HOW to verify from a fixed policy, never from what the token asks for.
        if header.get("alg") not in ALLOWED_ALGS:
            raise TokenError("alg_not_allowed")
        if header.get("typ") != TOKEN_TYPE:
            raise TokenError("wrong_typ")
        key = self.keys.get(header.get("kid"))
        if key is None:
            raise TokenError("unknown_kid")

        # 5: constant-time comparison, so response timing does not reveal how many bytes matched.
        expected = sign(f"{parts[0]}.{parts[1]}", key)
        if not hmac.compare_digest(expected.encode("ascii"), parts[2].encode("ascii", "replace")):
            raise TokenError("bad_signature")

        # 6: only now are the claims trustworthy enough to read.
        now = self.clock()
        for name in ("iss", "aud", "sub", "exp", "iat"):
            if name not in claims:
                raise TokenError("missing_claim")
        if claims["iss"] != self.issuer:
            raise TokenError("wrong_issuer")
        aud = claims["aud"] if isinstance(claims["aud"], list) else [claims["aud"]]
        if self.audience not in aud:
            raise TokenError("wrong_audience")
        if not all(isinstance(claims[c], int) and not isinstance(claims[c], bool) for c in ("exp", "iat")):
            raise TokenError("malformed")
        if now >= claims["exp"] + self.leeway_s:
            raise TokenError("expired")
        if "nbf" in claims and now + self.leeway_s < claims["nbf"]:
            raise TokenError("not_yet_valid")
        if claims["iat"] > now + self.leeway_s:
            raise TokenError("issued_in_future")
        if not isinstance(claims["sub"], str) or not claims["sub"]:
            raise TokenError("missing_claim")
        return claims

    @staticmethod
    def _json(segment: str) -> dict:
        try:
            value = json.loads(b64url_decode(segment))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise TokenError("malformed") from None
        if not isinstance(value, dict):
            raise TokenError("malformed")
        return value


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Mint a toy access token (teaching only).")
    p.add_argument("--sub", default="customer-a1", help="subject: the customer's opaque id")
    p.add_argument("--aud", default=AUDIENCE)
    p.add_argument("--scope", default="tracking:read")
    p.add_argument("--ttl", type=int, default=300, help="lifetime in seconds (default 300)")
    p.add_argument("--kid", default="k1")
    args = p.parse_args(argv)
    key = key_from_env()
    if key is None:
        print(f"Set {KEY_ENV_VAR} first (see the module docstring).", file=sys.stderr)
        return 2
    print(ToyIssuer(key, kid=args.kid).issue(args.sub, args.aud, args.scope, args.ttl))
    return 0


if __name__ == "__main__":
    sys.exit(main())
