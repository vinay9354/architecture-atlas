# Lab 10 — sample results

Runs on a laptop (macOS, Python 3.14.7) on 2026-11-21. Every run generates a fresh signing key, so token
strings, `iat`/`exp`/`jti` values, and `Date` headers differ from run to run; status codes, reasons, and
response bodies do not.

## Step 1 — Run the client demo

```text
$ python3 client_demo.py
Toy tracking API on http://127.0.0.1:<ephemeral>, fresh signing key (not printed), kid=k1

 #  method case                                               expect  got  server-side reason
--  ------ -------------------------------------------------- ------ ----  ------------------------
 1  GET    no token                                              401  401  no_token
 2  GET    tampered payload (sub changed)                        401  401  bad_signature
 3  GET    signed with another key                               401  401  bad_signature
 4  GET    expired (issued 10 min ago, ttl 5 min)                401  401  expired
 5  GET    wrong audience (loyalty-api)                          401  401  wrong_audience
 6  GET    alg "none", no signature                              401  401  alg_not_allowed
 7  GET    own shipment                                          200  200  ok
 8  GET    someone else's shipment                               404  404  not_owner
 9  GET    shipment that does not exist                          404  404  no_such_shipment
10  POST   write without the write scope                         403  403  insufficient_scope
11  POST   wrong content type                                    415  415  wrong_content_type
12  POST   body over 2048 bytes                                  413  413  body_too_large
13  POST   malformed JSON                                        400  400  malformed_json: invalid JSON at line 1 column 31
14  POST   invalid fields (enum, length, duplicate, address)     422  422  validation_failed
15  POST   valid preferences                                     200  200  ok

15/15 cases returned the expected status.
```

The whole run took about 0.6 s of wall-clock time.

## Steps 2 and 4 — Response bodies (verbose mode, trimmed)

```text
$ python3 client_demo.py --verbose
 2  GET    tampered payload (sub changed)                        401  401  bad_signature
      {"type":"https://atlasmart.example/problems/invalid-token","title":"Unauthorized","status":401,"detail":"The access token is invalid or expired.","instance":"/shipments/SHP-1002"}
 4  GET    expired (issued 10 min ago, ttl 5 min)                401  401  expired
      {"type":"https://atlasmart.example/problems/invalid-token","title":"Unauthorized","status":401,"detail":"The access token is invalid or expired.","instance":"/shipments/SHP-1001"}
 6  GET    alg "none", no signature                              401  401  alg_not_allowed
      {"type":"https://atlasmart.example/problems/invalid-token","title":"Unauthorized","status":401,"detail":"The access token is invalid or expired.","instance":"/shipments/SHP-1001"}
 7  GET    own shipment                                          200  200  ok
      {"id":"SHP-1001","status":"in_transit","last_event":"departed hub","eta":"2026-11-24"}
 8  GET    someone else's shipment                               404  404  not_owner
      {"type":"https://atlasmart.example/problems/not-found","title":"Not Found","status":404,"detail":"No such shipment for this account.","instance":"/shipments/SHP-1002"}
 9  GET    shipment that does not exist                          404  404  no_such_shipment
      {"type":"https://atlasmart.example/problems/not-found","title":"Not Found","status":404,"detail":"No such shipment for this account.","instance":"/shipments/SHP-9999"}
14  POST   invalid fields (enum, length, duplicate, address)     422  422  validation_failed
      {"type":"https://atlasmart.example/problems/validation-error","title":"Your request is not valid.","status":422,"detail":"4 field(s) failed validation.","instance":"/shipments/SHP-1001/delivery-preferences","errors":[{"pointer":"/address","detail":"unknown field"},{"pointer":"/delivery_window","detail":"must be one of any, morning, afternoon, evening"},{"pointer":"/instructions","detail":"must be at most 140 characters"},{"pointer":"/notify_by","detail":"items must be unique"}]}
15  POST   valid preferences                                     200  200  ok
      {"id":"SHP-1001","delivery_preferences":{"delivery_window":"evening","safe_place":"porch","instructions":"Ring twice, parcel fits through the side gate","notify_by":["push"]}}
```

## Step 3 — Break the verifier on purpose

Each change was made in a scratch copy of the lab directory; rows 5 and 6 and the summary line shown.

```text
== change 1: alg allow-list removed
 5  GET    wrong audience (loyalty-api)                          401  401  wrong_audience
 6  GET    alg "none", no signature                              401  401  bad_signature
15/15 cases returned the expected status.
== change 2: audience check removed
 5  GET    wrong audience (loyalty-api)                          401  200  ok   <-- MISMATCH
 6  GET    alg "none", no signature                              401  401  alg_not_allowed
14/15 cases returned the expected status.
== change 3: compare_digest replaced by ==
 5  GET    wrong audience (loyalty-api)                          401  401  wrong_audience
 6  GET    alg "none", no signature                              401  401  alg_not_allowed
15/15 cases returned the expected status.
```

- **Change 1** still rejects `alg: none`, now as `bad_signature`, because this toy always computes
  HMAC-SHA256 and the forged token's signature is empty. A general-purpose verifier that picks the
  algorithm from the header would have accepted it. Defence in depth saved this code; the allow-list
  is what makes the rejection deliberate rather than lucky.
- **Change 2** is the dangerous one: a token issued for the loyalty service now reads shipments. Any
  service that receives a customer token could replay it against the Tracking API.
- **Change 3** passes because the demo checks outcomes, not timing; it reintroduces a timing side
  channel that no functional test will catch. Code review and a lint rule are the controls.

## Step 5a — Decode a token

```text
$ export LAB10_SIGNING_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
$ TOKEN=$(python3 toy_jwt.py --sub customer-a1 --scope "tracking:read")
$ (header and payload segments decoded with base64.urlsafe_b64decode)
{"alg":"HS256","kid":"k1","typ":"at+jwt"}
{"aud":"tracking-api","exp":1795219641,"iat":1795219341,"iss":"https://id.atlasmart.example","jti":"6782ec832d3209d5","scope":"tracking:read","sub":"customer-a1"}
```

`exp - iat = 1795219641 - 1795219341 = 300` seconds: the default five-minute lifetime. The payload is
only encoded, not encrypted: anyone holding the token can read it.

## Step 5b — Standalone server and curl

```text
$ python3 tracking_api.py --port 8710 &
Tracking API on http://127.0.0.1:8710 (Ctrl+C to stop)

$ curl -s http://127.0.0.1:8710/shipments/SHP-1001 -H "Authorization: Bearer $READ"
{"id":"SHP-1001","status":"in_transit","last_event":"departed hub","eta":"2026-11-24"}

$ curl -s -i http://127.0.0.1:8710/shipments/SHP-1002 -H "Authorization: Bearer $READ"
HTTP/1.0 404 Not Found
Server: lab10-toy
Content-Type: application/problem+json
Content-Length: 167
Cache-Control: no-store

{"type":"https://atlasmart.example/problems/not-found","title":"Not Found","status":404,"detail":"No such shipment for this account.","instance":"/shipments/SHP-1002"}

$ curl -s -i -X POST http://127.0.0.1:8710/shipments/SHP-1001/delivery-preferences \
    -H "Authorization: Bearer $READ" -H "Content-Type: application/json" -d '{"delivery_window":"evening"}'
HTTP/1.0 403 Forbidden
Server: lab10-toy
Content-Type: application/problem+json
Content-Length: 218
Cache-Control: no-store
WWW-Authenticate: Bearer realm="tracking-api", error="insufficient_scope", scope="tracking:preferences:write"

{"type":"https://atlasmart.example/problems/insufficient-scope","title":"Forbidden","status":403,"detail":"This action needs the tracking:preferences:write scope.","instance":"/shipments/SHP-1001/delivery-preferences"}

$ curl -s -X POST http://127.0.0.1:8710/shipments/SHP-1001/delivery-preferences \
    -H "Authorization: Bearer $WRITE" -H "Content-Type: application/json" \
    -d '{"delivery_window":"evening","address":"1 Example Street"}'
{"type":"https://atlasmart.example/problems/validation-error","title":"Your request is not valid.","status":422,"detail":"1 field(s) failed validation.","instance":"/shipments/SHP-1001/delivery-preferences","errors":[{"pointer":"/address","detail":"unknown field"}]}

$ curl -s -X POST http://127.0.0.1:8710/shipments/SHP-1001/delivery-preferences \
    -H "Authorization: Bearer $WRITE" -H "Content-Type: application/json" \
    -d '{"delivery_window":"evening","safe_place":"porch"}'
{"id":"SHP-1001","delivery_preferences":{"delivery_window":"evening","safe_place":"porch"}}
```

(`Date` headers removed.) The server's own log, on stderr:

```text
GET /shipments/SHP-1001 -> 200 (ok)
GET /shipments/SHP-1002 -> 404 (not_owner)
POST /shipments/SHP-1001/delivery-preferences -> 403 (insufficient_scope)
POST /shipments/SHP-1001/delivery-preferences -> 422 (validation_failed)
POST /shipments/SHP-1001/delivery-preferences -> 200 (ok)
```

Without the environment variable, both scripts refuse to start rather than invent a key:

```text
$ python3 tracking_api.py
Set LAB10_SIGNING_KEY first (see the module docstring), or run client_demo.py, which starts its own server with a fresh key.
$ python3 toy_jwt.py
Set LAB10_SIGNING_KEY first (see the module docstring).
```

## Smoke test

```text
$ python3 -m unittest tests.examples.test_lab10 -v
test_api_end_to_end_status_codes ... ok
test_demo_cli_reports_all_cases ... ok
test_key_rotation_with_two_kids ... ok
test_sources_compile_and_no_committed_key ... ok
test_validator_rules ... ok
test_verifier_accepts_a_good_token ... ok
test_verifier_rejection_reasons ... ok

----------------------------------------------------------------------
Ran 7 tests in 1.099s

OK
```

## What to notice

1. **Six different token failures, one response.** Cases 2-6 fail for five different reasons, but the
   client sees the same 401 body and `WWW-Authenticate: Bearer ... error="invalid_token"` each time.
   The reason lives only in the server's log. An attacker probing the API learns nothing about which
   check stopped them; an operator investigating an incident sees exactly which one.
2. **The tampered token is caught by the signature, not by the owner check.** Case 2 rewrote `sub` to
   another customer and asked for that customer's shipment. Without signature verification, the API
   would have believed the token and the owner check would have passed. Authorization is only as good
   as the authentication in front of it.
3. **`alg: none` fails before any cryptography runs.** The verifier decides the algorithm from its own
   allow-list, never from the token header. A verifier that trusts the header can be told to skip the
   signature entirely.
4. **401 and 403 mean different things.** Case 10 had a perfectly valid token without the write scope:
   the API knows who is calling and refuses the action, so it returns 403 with `insufficient_scope`.
5. **Someone else's shipment is a 404, identical to a missing shipment.** Compare cases 8 and 9: only
   `instance` differs. The server log distinguishes `not_owner` from `no_such_shipment`; the client
   cannot, so shipment ids cannot be enumerated through the API (broken object-level authorization,
   also called IDOR, is the attack this blocks).
6. **400 versus 422.** Case 13 is not JSON at all (400). Case 14 is valid JSON that breaks four rules;
   the API reports all four at once with JSON Pointers, so the client fixes them in one round trip.
7. **The address never reaches storage (NFR-6).** The validator rejects unknown fields instead of
   ignoring them, so `"address"` produces a 422. A validator that silently dropped unknown fields
   would also keep the address out of storage, but would hide the client's mistake; one that passed
   the whole object through would store it.
8. **Checks run in order.** The 415, 413, 400, and 422 cases all used a valid write token on the
   caller's own shipment. Send the same bad bodies without a token and you get 401 every time: an
   unauthenticated caller cannot learn the validation rules.

## Answers to the questions in the lab page

- **Why 404 rather than 403 for someone else's shipment?** A 403 confirms that the shipment exists and
  belongs to someone else, which helps an attacker enumerate ids. AtlasMart shipment ids appear in
  emails and on parcels and are not secret, so the safer default is to make "not yours" and "does not
  exist" indistinguishable. A 403 is reasonable where the caller already knows the object exists (an
  internal admin tool) and a clear refusal helps more than it leaks.
- **Why must the verifier ignore the token's `alg`?** Because the token is attacker-controlled input
  until the signature has been checked. Letting it choose `none`, or switch an asymmetric verifier to
  HMAC with the public key as the secret, lets an attacker forge tokens. RFC 8725 makes the
  allow-list a requirement.
- **Why does the lab use a shared HMAC key, and why is that wrong for production?** It keeps the code
  to the standard library. With HS256 every service that can verify a token can also mint one, so a
  compromise of the Tracking API would let an attacker impersonate any customer to every other service
  sharing the key. With asymmetric keys the identity provider alone holds the private key and
  services fetch only public keys from its JWKS endpoint.
- **What does `hmac.compare_digest` protect against?** A byte-by-byte `==` can return as soon as the
  first byte differs, so response time leaks how much of a guessed signature was right. Constant-time
  comparison takes the same time however many bytes match.
- **What does the 2048-byte limit protect?** Memory and CPU: without a limit, a client can send a huge
  body that the server buffers and parses. The server checks `Content-Length` before reading, keeps at
  most 2048 bytes, and closes the connection for anything larger than 64 KiB instead of reading it.
- **Step 1: what differs between the 401 bodies of cases 2-6?** Only `instance`. The uniform answer
  is deliberate: the specific reason is useful to an attacker and is kept for the server log.
- **Step 1: what if the API decoded tokens without verifying them?** Case 2 would have returned
  `SHP-1002` to a caller who is not `customer-b2`: the owner check compares against a `sub` the
  attacker wrote. Decoding is not verification.
- **Step 2: why is case 10 a 403?** The token is valid, so the caller is authenticated; what is
  missing is permission for this action. 401 asks the client to (re)authenticate; 403 tells it that
  authenticating again will not help.
- **Step 2: what if the owner check lived in the Tracking Web UI?** Anyone calling the API directly
  (curl, a script, a modified browser) would bypass it. Authorization must be enforced by the
  component that holds the data; the UI may hide things for usability, never for security.
- **Step 4: three ways to treat an unknown field.** Reject it with an error (this lab), drop it
  silently, or accept and store it. Only the third can store an address; dropping silently keeps the
  data out but hides client bugs and makes later schema changes ambiguous. Rejecting is the
  allow-list approach.
- **Step 4: why check `Content-Length` before reading?** So the server decides how much to read
  before allocating memory for it; reading first and checking afterwards lets a client make the
  server buffer whatever it sends.
