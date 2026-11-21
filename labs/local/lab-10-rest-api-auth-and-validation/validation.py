#!/usr/bin/env python3
"""Lab 10: a hand-written validator for the delivery-preferences request body.

Standard library only. A real service would use a schema library (JSON Schema, Pydantic, and so on);
writing the checks by hand here makes each rule visible. The rules:

  - the body is a JSON object, with no duplicate keys
  - required fields are present; unknown fields are rejected (allow-list, not deny-list)
  - each field has the right type (true/false is not accepted where a number or string is expected)
  - enumerated fields take only listed values
  - strings and arrays have length limits; strings contain no control characters

NFR-6 (no delivery addresses stored) is enforced by construction: there is no address field, and an
unknown field such as "address" is rejected instead of being silently ignored and stored. The free-text
"instructions" field is the remaining risk; see the lab page for the trade-off.

Errors are collected, not raised on the first one, so the client can fix everything in one round trip.
Each error has a JSON Pointer (RFC 6901) to the offending member, which the API returns inside an
RFC 9457 problem-details document.
"""
import json

MAX_BODY_BYTES = 2048

DELIVERY_WINDOWS = ("any", "morning", "afternoon", "evening")
SAFE_PLACES = ("none", "porch", "reception", "garage")
CHANNELS = ("push", "sms", "email")
MAX_INSTRUCTIONS = 140

SCHEMA_FIELDS = ("delivery_window", "safe_place", "instructions", "notify_by")
REQUIRED = ("delivery_window",)


class MalformedJson(Exception):
    """The body is not parseable JSON (HTTP 400), as opposed to valid JSON with bad content (422)."""


def _reject_duplicates(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise MalformedJson(f"duplicate key {key!r}")
        seen[key] = value
    return seen


def parse_json(raw: bytes):
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise MalformedJson("body is not UTF-8") from None
    try:
        return json.loads(text, object_pairs_hook=_reject_duplicates,
                          parse_constant=lambda name: _raise(MalformedJson(f"{name} is not JSON")))
    except json.JSONDecodeError as exc:
        raise MalformedJson(f"invalid JSON at line {exc.lineno} column {exc.colno}") from None


def _raise(exc):
    raise exc


def _is_str(v):
    return isinstance(v, str)


def _has_control_chars(s):
    return any(ord(c) < 32 or ord(c) == 127 for c in s)


def validate_preferences(body) -> list[dict]:
    """Return a list of {"pointer", "detail"} errors; an empty list means the body is valid."""
    if not isinstance(body, dict):
        return [{"pointer": "", "detail": "must be a JSON object"}]
    errors = []

    for name in sorted(set(body) - set(SCHEMA_FIELDS)):
        errors.append({"pointer": f"/{_escape(name)}", "detail": "unknown field"})
    for name in REQUIRED:
        if name not in body:
            errors.append({"pointer": f"/{name}", "detail": "required field is missing"})

    if "delivery_window" in body:
        v = body["delivery_window"]
        if not _is_str(v) or v not in DELIVERY_WINDOWS:
            errors.append({"pointer": "/delivery_window", "detail": f"must be one of {', '.join(DELIVERY_WINDOWS)}"})

    if "safe_place" in body:
        v = body["safe_place"]
        if not _is_str(v) or v not in SAFE_PLACES:
            errors.append({"pointer": "/safe_place", "detail": f"must be one of {', '.join(SAFE_PLACES)}"})

    if "instructions" in body:
        v = body["instructions"]
        if not _is_str(v):
            errors.append({"pointer": "/instructions", "detail": "must be a string"})
        elif len(v) > MAX_INSTRUCTIONS:
            errors.append({"pointer": "/instructions", "detail": f"must be at most {MAX_INSTRUCTIONS} characters"})
        elif _has_control_chars(v):
            errors.append({"pointer": "/instructions", "detail": "must not contain control characters"})

    if "notify_by" in body:
        v = body["notify_by"]
        if not isinstance(v, list):
            errors.append({"pointer": "/notify_by", "detail": "must be an array"})
        elif len(v) > len(CHANNELS):
            errors.append({"pointer": "/notify_by", "detail": f"must have at most {len(CHANNELS)} items"})
        else:
            for i, item in enumerate(v):
                if not _is_str(item) or item not in CHANNELS:
                    errors.append({"pointer": f"/notify_by/{i}", "detail": f"must be one of {', '.join(CHANNELS)}"})
            names = [x for x in v if _is_str(x)]
            if len(set(names)) != len(names):
                errors.append({"pointer": "/notify_by", "detail": "items must be unique"})
    return errors


def _escape(name):
    """JSON Pointer escaping (RFC 6901): ~ becomes ~0 and / becomes ~1."""
    return str(name).replace("~", "~0").replace("/", "~1")
