# Lab 11 — sample results

Runs on a laptop (macOS, Python 3.14.7) with the default seeds (load 11, tracking-api 11,
status-service 12). Every block below is copied from a real run, trimmed only of trailing blank
lines. Ports, timestamps, and durations change from run to run; trace and span ids, the shipments
requested, request counts, and statuses do not, because the id generators and the shipment choice
are seeded and requests are sent one at a time. `run_lab.py` was run in a copy of the lab directory
so that the log paths print as `logs/...`.

## Step 1 — Read and validate traceparent headers

```text
$ python3 traceparent.py
00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01                valid (sampled=True)
00-4BF92F3577B34DA6A3CE929D0E0E4736-00F067AA0BA902B7-01                trace-id is not 32 lowercase hex characters
00-00000000000000000000000000000000-00f067aa0ba902b7-01                trace-id is all zeros
ff-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01                version ff is forbidden
00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01-extra          version 00 must be 55 characters, got 61
01-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-09-future-field   valid (sampled=True)
```

The first header is the specification's own example. The uppercase one fails because the fields
must be lowercase hex; the all-zero trace-id and version `ff` are explicitly invalid; a version 00
value must be exactly 55 characters. The last one is a higher version (`01`): the receiver parses
the version 00 fields, checks that character 56 is a dash, and ignores the rest. Flags `09` is
binary `00001001`; only bit 0 (sampled) is defined, so it is sampled and bit 3 is dropped on output.

## Step 2 — Run both services and the load

```text
$ python3 run_lab.py
status-service http://127.0.0.1:51400   tracking-api http://127.0.0.1:51401   propagation on
probes (client-made traceparent headers):
  valid, sampled               00-7b89296c6dcbac5008577eb1924770d3-03cc0f2793fdcab8-01        -> HTTP 200
  uppercase hex                00-7B89296C6DCBAC5008577EB1924770D3-03CC0F2793FDCAB8-01        -> HTTP 200
  all-zero trace-id            00-00000000000000000000000000000000-03cc0f2793fdcab8-01        -> HTTP 200
  version ff                   ff-7b89296c6dcbac5008577eb1924770d3-03cc0f2793fdcab8-01        -> HTTP 200
  version 00 plus extra field  00-7b89296c6dcbac5008577eb1924770d3-03cc0f2793fdcab8-01-extra  -> HTTP 200
sent 200 requests, statuses {200: 194, 502: 6}
client-side latency ms: p50 9.7  p95 129.8  p99 136.9  max 139.7
logs: logs/tracking-api.log logs/status-service.log
```

All five probes return 200: an invalid `traceparent` never fails a request, it only restarts the
trace. Six requests out of 200 got 502 (the planted error, Step 5). The client-side p95 is far above
p50 (the planted slow path, Step 4).

The three-terminal variant was also run (20 requests, ports 8011 and 8012); its collector summary
was `traces: 25   spanning more than one service: 25   single-service: 0`.

## Step 3 — Follow one trace through both log files

```text
$ head -n 5 logs/tracking-api.log
{"timestamp":"2026-11-27T06:36:06.030019Z","level":"INFO","service":"tracking-api","trace_id":"7b89296c6dcbac5008577eb1924770d3","span_id":"dda1494c73cf256d","parent_span_id":"03cc0f2793fdcab8","route":"/track/{shipment_id}","status":200,"duration_ms":6.27,"method":"GET","shipment_id":"SHP-1000","tp_in":"valid"}
{"timestamp":"2026-11-27T06:36:06.035351Z","level":"INFO","service":"tracking-api","trace_id":"73ab48767734d7c1c7fde805ec99108d","span_id":"db5b5fab8f4d3e27","parent_span_id":null,"route":"/track/{shipment_id}","status":200,"duration_ms":4.74,"method":"GET","shipment_id":"SHP-1000","tp_in":"invalid: trace-id is not 32 lowercase hex characters"}
{"timestamp":"2026-11-27T06:36:06.043648Z","level":"INFO","service":"tracking-api","trace_id":"cdcc69292f45e678309d6b79965eda32","span_id":"dae445508201e2bd","parent_span_id":null,"route":"/track/{shipment_id}","status":200,"duration_ms":7.77,"method":"GET","shipment_id":"SHP-1000","tp_in":"invalid: trace-id is all zeros"}
{"timestamp":"2026-11-27T06:36:06.050585Z","level":"INFO","service":"tracking-api","trace_id":"2fa91425cb0088539d2c67eda13ffe79","span_id":"79cb9e86830c71c2","parent_span_id":null,"route":"/track/{shipment_id}","status":200,"duration_ms":6.43,"method":"GET","shipment_id":"SHP-1000","tp_in":"invalid: version ff is forbidden"}
{"timestamp":"2026-11-27T06:36:06.056795Z","level":"INFO","service":"tracking-api","trace_id":"89e7d15f17362f25244caf9c4dabb481","span_id":"7253edc618187993","parent_span_id":null,"route":"/track/{shipment_id}","status":200,"duration_ms":5.71,"method":"GET","shipment_id":"SHP-1000","tp_in":"invalid: version 00 must be 55 characters, got 61"}
```

```text
$ head -n 2 logs/status-service.log
{"timestamp":"2026-11-27T06:36:06.027237Z","level":"INFO","service":"status-service","trace_id":"7b89296c6dcbac5008577eb1924770d3","span_id":"44dcda6a797d76de","parent_span_id":"dda1494c73cf256d","route":"/status/{shipment_id}","status":200,"duration_ms":2.94,"method":"GET","shipment_id":"SHP-1000","carrier":"carrier-a","tp_in":"valid"}
{"timestamp":"2026-11-27T06:36:06.029788Z","level":"INFO","service":"status-service","trace_id":"7b89296c6dcbac5008577eb1924770d3","span_id":"87751d4ca8501e2c","parent_span_id":"dda1494c73cf256d","route":"/eta/{shipment_id}","status":200,"duration_ms":1.88,"method":"GET","shipment_id":"SHP-1000","carrier":"carrier-a","tp_in":"valid"}
```

```text
$ python3 collect.py tree logs/*.log --trace 7b89296c6dcbac5008577eb1924770d3
trace 7b89296c6dcbac5008577eb1924770d3: 3 spans, 2 service(s) ['status-service', 'tracking-api'], 6.27 ms
(parent 03cc0f2793fdcab8 is not in these logs: a caller that does not log, or a lost span)
[+   0.00 ms] tracking-api   GET /track/{shipment_id}   200      6.27 ms  span=dda1494c73cf256d  shipment_id=SHP-1000
|-- [+   0.55 ms] status-service GET /status/{shipment_id}  200      2.94 ms  span=44dcda6a797d76de  shipment_id=SHP-1000 carrier=carrier-a
`-- [+   4.16 ms] status-service GET /eta/{shipment_id}     200      1.88 ms  span=87751d4ca8501e2c  shipment_id=SHP-1000 carrier=carrier-a
```

Answers:

1. `parent_span_id` in status-service's lines (`dda1494c73cf256d`) equals tracking-api's `span_id`,
   and both share `trace_id` `7b89296c6dcbac5008577eb1924770d3`.
2. The valid probe's header said the caller's span was `03cc0f2793fdcab8`. tracking-api continued
   that trace and recorded the load script's span as its parent, but the load script writes no log,
   so that span is not in the files. Real systems see this at the edge whenever an uninstrumented
   or external caller sends trace context.
3. Line 2, uppercase hex: `trace-id is not 32 lowercase hex characters`. Line 3: `trace-id is all
   zeros`. Line 4: `version ff is forbidden`. Line 5: `version 00 must be 55 characters, got 61`.
   In each case tracking-api ignored the header, generated a new trace id, and logged
   `parent_span_id: null`: the W3C "restart".

## Step 4 — Find the slow path from the logs

```text
$ python3 collect.py latency logs/*.log
service        route                   count  5xx      p50      p95      p99      max   (ms, nearest rank)
status-service /eta/{shipment_id}        199    0     3.51   126.03   130.13   131.91
status-service /status/{shipment_id}     205    6     3.33     5.10    33.67    34.73
tracking-api   /track/{shipment_id}      205    6     8.75   129.07   135.87   138.80
```

```text
$ python3 collect.py latency logs/*.log --by carrier
service        route                  carrier     count  5xx      p50      p95      p99      max   (ms, nearest rank)
status-service /eta/{shipment_id}     carrier-a     107    0     3.28     4.89     5.09     5.39
status-service /eta/{shipment_id}     carrier-b      79    0     3.37     4.98     5.14     5.14
status-service /eta/{shipment_id}     carrier-c      13    0   126.69   131.91   131.91   131.91
status-service /status/{shipment_id}  carrier-a     107    0     3.31     5.01     5.36     5.74
status-service /status/{shipment_id}  carrier-b      85    6     3.52    31.67    34.73    34.73
status-service /status/{shipment_id}  carrier-c      13    0     3.02     4.26     4.26     4.26
tracking-api   /track/{shipment_id}   None          205    6     8.75   129.07   135.87   138.80
```

```text
$ python3 collect.py tree logs/*.log --slowest
trace 3e06d750369a9ad71f9ca6ceb7b8b1a0: 3 spans, 2 service(s) ['status-service', 'tracking-api'], 138.80 ms
[+   0.00 ms] tracking-api   GET /track/{shipment_id}   200    138.80 ms  span=ec9a5dc8a440f745  shipment_id=SHP-1017
|-- [+   0.90 ms] status-service GET /status/{shipment_id}  200      3.77 ms  span=803a58569b459212  shipment_id=SHP-1017 carrier=carrier-c
`-- [+   5.72 ms] status-service GET /eta/{shipment_id}     200    131.91 ms  span=b4bdc5b1d7c6cee9  shipment_id=SHP-1017 carrier=carrier-c
```

Answers: status-service's `/eta/{shipment_id}` has p50 3.51 ms but p95 126 ms, and tracking-api's
`/track` inherits it (p95 129 ms). Grouping by carrier isolates it: `carrier-c` (13 calls) has p50
about 127 ms, every other carrier about 3 ms. In the slowest trace, 131.91 of 138.80 ms (95%) is the
`/eta` span for a `carrier-c` shipment. The calls are sequential because tracking-api only asks for
the ETA after `/status` has answered, so the `/eta` span starts at +5.72 ms, after `/status` ended.
tracking-api's own lines do not carry `carrier`; you find it only by following the trace to
status-service. (In the code: `SLOW_CARRIER` makes `/eta` sleep 120 ms, standing for an ETA
recomputed from the full event history.) The tracking-api row in the `--by carrier` table shows
`None` because tracking-api does not log that field.

## Step 5 — Find the error from the logs

```text
$ python3 collect.py traces logs/*.log
spans: 609 {'status-service': 404, 'tracking-api': 205}
traces: 205   spanning more than one service: 205   single-service: 0
root spans (no parent): 204   spans whose parent is not in the logs: 1
traces with an error (any span status >= 500): 6 (first 10 shown)
  1d849e2ba111f5fbfbe840360c046d96  status-service GET /status/{shipment_id}  503     33.67 ms  span=4f832ec84ffe831a  shipment_id=SHP-1013 carrier=carrier-b  "event store read timed out"
  a3d1863ba7b0e693890f6c23a1455615  status-service GET /status/{shipment_id}  503     31.80 ms  span=2e01ab2db21e137c  shipment_id=SHP-1013 carrier=carrier-b  "event store read timed out"
  88b48922a19ddc1add248e6f344acadf  status-service GET /status/{shipment_id}  503     30.66 ms  span=cf6f4c9003510e48  shipment_id=SHP-1013 carrier=carrier-b  "event store read timed out"
  1690a1f7ba00eb1b21ee3e333d45e04e  status-service GET /status/{shipment_id}  503     34.73 ms  span=7f8c74b1af5bc16c  shipment_id=SHP-1013 carrier=carrier-b  "event store read timed out"
  1d6d2a932f3dc5543087bbf925849de2  status-service GET /status/{shipment_id}  503     31.67 ms  span=5dced967db029df2  shipment_id=SHP-1013 carrier=carrier-b  "event store read timed out"
  478e5850421d9b0ac32c4da8ce08c67d  status-service GET /status/{shipment_id}  503     34.60 ms  span=97db1001072f6ac9  shipment_id=SHP-1013 carrier=carrier-b  "event store read timed out"
slowest 5 traces (first to last span):
  3e06d750369a9ad71f9ca6ceb7b8b1a0    138.80 ms  3 spans  root: tracking-api /track/{shipment_id} SHP-1017
  41d812cdfe4a5ce01d96ac56a3b00043    138.62 ms  3 spans  root: tracking-api /track/{shipment_id} SHP-1017
  356f8bd11711eb571304145212ca3f70    135.87 ms  3 spans  root: tracking-api /track/{shipment_id} SHP-1047
  b7baf0a6402448989f9f656382ae1988    133.69 ms  3 spans  root: tracking-api /track/{shipment_id} SHP-1007
  15c1d2dfa9964aef012d0ea67ff12229    133.06 ms  3 spans  root: tracking-api /track/{shipment_id} SHP-1037
```

```text
$ python3 collect.py tree logs/*.log --trace 1d849e2ba111f5fbfbe840360c046d96
trace 1d849e2ba111f5fbfbe840360c046d96: 2 spans, 2 service(s) ['status-service', 'tracking-api'], 37.87 ms
[+   0.00 ms] tracking-api   GET /track/{shipment_id}   502     37.87 ms  span=cbfe2f8d24105a49  shipment_id=SHP-1013  "status-service /status returned 503"
`-- [+   0.62 ms] status-service GET /status/{shipment_id}  503     33.67 ms  span=4f832ec84ffe831a  shipment_id=SHP-1013 carrier=carrier-b  "event store read timed out"
$ grep 1d849e2ba111f5fbfbe840360c046d96 logs/*.log
logs/tracking-api.log:{"timestamp":"2026-11-27T06:36:07.435441Z","level":"ERROR","service":"tracking-api","trace_id":"1d849e2ba111f5fbfbe840360c046d96","span_id":"cbfe2f8d24105a49","parent_span_id":null,"route":"/track/{shipment_id}","status":502,"duration_ms":37.87,"method":"GET","shipment_id":"SHP-1013","tp_in":"none","message":"status-service /status returned 503"}
logs/status-service.log:{"timestamp":"2026-11-27T06:36:07.431857Z","level":"ERROR","service":"status-service","trace_id":"1d849e2ba111f5fbfbe840360c046d96","span_id":"4f832ec84ffe831a","parent_span_id":"cbfe2f8d24105a49","route":"/status/{shipment_id}","status":503,"duration_ms":33.67,"method":"GET","shipment_id":"SHP-1013","carrier":"carrier-b","tp_in":"valid","message":"event store read timed out"}
```

Answers: status-service failed first: `/status/{shipment_id}` returned 503 with "event store read
timed out" for `SHP-1013` after about 34 ms. tracking-api turned that into 502 for the client, with
the message "status-service /status returned 503". The trace has two spans because tracking-api
never calls `/eta` after a failed `/status`. The error list shows each trace's span with the highest
status code, here the downstream 503. `/status`'s p99 (33.67 ms) in Step 4 is the same six requests: with 205
calls, the nearest-rank p99 is the 203rd value, inside the 6 slow failures.

## Step 6 — Remove propagation

```text
$ python3 run_lab.py --no-propagate --out logs-broken
status-service http://127.0.0.1:52011   tracking-api http://127.0.0.1:52012   propagation OFF
probes (client-made traceparent headers):
  valid, sampled               00-7b89296c6dcbac5008577eb1924770d3-03cc0f2793fdcab8-01        -> HTTP 200
  uppercase hex                00-7B89296C6DCBAC5008577EB1924770D3-03CC0F2793FDCAB8-01        -> HTTP 200
  all-zero trace-id            00-00000000000000000000000000000000-03cc0f2793fdcab8-01        -> HTTP 200
  version ff                   ff-7b89296c6dcbac5008577eb1924770d3-03cc0f2793fdcab8-01        -> HTTP 200
  version 00 plus extra field  00-7b89296c6dcbac5008577eb1924770d3-03cc0f2793fdcab8-01-extra  -> HTTP 200
sent 200 requests, statuses {200: 194, 502: 6}
client-side latency ms: p50 10.2  p95 133.8  p99 136.6  max 137.4
logs: logs-broken/tracking-api.log logs-broken/status-service.log
```

```text
$ python3 collect.py traces logs-broken/*.log --slowest 3
spans: 609 {'status-service': 404, 'tracking-api': 205}
traces: 609   spanning more than one service: 0   single-service: 609
root spans (no parent): 608   spans whose parent is not in the logs: 1
traces with an error (any span status >= 500): 12 (first 10 shown)
  1d849e2ba111f5fbfbe840360c046d96  tracking-api   GET /track/{shipment_id}   502     34.24 ms  span=cbfe2f8d24105a49  shipment_id=SHP-1013  "status-service /status returned 503"
  02a50ee6c03bf9e1406f3b3bd2eeeb1c  status-service GET /status/{shipment_id}  503     33.49 ms  span=2af42d39c0655543  shipment_id=SHP-1013 carrier=carrier-b  "event store read timed out"
  a3d1863ba7b0e693890f6c23a1455615  tracking-api   GET /track/{shipment_id}   502     33.13 ms  span=1be8bf7c724c9052  shipment_id=SHP-1013  "status-service /status returned 503"
  34c29d956f061d6dc38671b6c16b224c  status-service GET /status/{shipment_id}  503     32.14 ms  span=6eb19d944910c376  shipment_id=SHP-1013 carrier=carrier-b  "event store read timed out"
  88b48922a19ddc1add248e6f344acadf  tracking-api   GET /track/{shipment_id}   502     35.96 ms  span=89c666c428e3f793  shipment_id=SHP-1013  "status-service /status returned 503"
  d404ded32ec4a42cd33a5f7d25877cb8  status-service GET /status/{shipment_id}  503     34.32 ms  span=350d39f4128e7782  shipment_id=SHP-1013 carrier=carrier-b  "event store read timed out"
  1690a1f7ba00eb1b21ee3e333d45e04e  tracking-api   GET /track/{shipment_id}   502     36.60 ms  span=e3939895224961dc  shipment_id=SHP-1013  "status-service /status returned 503"
  85de306bb476bf9fa969495da3a339e2  status-service GET /status/{shipment_id}  503     34.53 ms  span=1f3bc11c016fe28f  shipment_id=SHP-1013 carrier=carrier-b  "event store read timed out"
  1d6d2a932f3dc5543087bbf925849de2  tracking-api   GET /track/{shipment_id}   502     33.16 ms  span=7b34f6d99199165c  shipment_id=SHP-1013  "status-service /status returned 503"
  cea4b100f208b62fade9b7431e77c085  status-service GET /status/{shipment_id}  503     30.76 ms  span=728c8f337bfec0ff  shipment_id=SHP-1013 carrier=carrier-b  "event store read timed out"
slowest 3 traces (first to last span):
  356f8bd11711eb571304145212ca3f70    136.15 ms  1 spans  root: tracking-api /track/{shipment_id} SHP-1047
  41d812cdfe4a5ce01d96ac56a3b00043    135.89 ms  1 spans  root: tracking-api /track/{shipment_id} SHP-1017
  b7baf0a6402448989f9f656382ae1988    135.64 ms  1 spans  root: tracking-api /track/{shipment_id} SHP-1007
```

```text
$ python3 collect.py tree logs-broken/*.log --slowest
trace 356f8bd11711eb571304145212ca3f70: 1 spans, 1 service(s) ['tracking-api'], 136.15 ms
[+   0.00 ms] tracking-api   GET /track/{shipment_id}   200    136.15 ms  span=62dc08d64bdbf090  shipment_id=SHP-1047
```

```text
$ grep -m 3 SHP-1017 logs-broken/*.log
logs-broken/tracking-api.log:{"timestamp":"2026-11-27T06:36:18.717149Z","level":"INFO","service":"tracking-api","trace_id":"41d812cdfe4a5ce01d96ac56a3b00043","span_id":"1734bc4414881edc","parent_span_id":null,"route":"/track/{shipment_id}","status":200,"duration_ms":135.89,"method":"GET","shipment_id":"SHP-1017","tp_in":"none"}
logs-broken/tracking-api.log:{"timestamp":"2026-11-27T06:36:19.234403Z","level":"INFO","service":"tracking-api","trace_id":"3e06d750369a9ad71f9ca6ceb7b8b1a0","span_id":"ec9a5dc8a440f745","parent_span_id":null,"route":"/track/{shipment_id}","status":200,"duration_ms":134.55,"method":"GET","shipment_id":"SHP-1017","tp_in":"none"}
logs-broken/tracking-api.log:{"timestamp":"2026-11-27T06:36:19.982086Z","level":"INFO","service":"tracking-api","trace_id":"ea31df803b8f801c22ef6a80db54e659","span_id":"962e58359c9919f2","parent_span_id":null,"route":"/track/{shipment_id}","status":200,"duration_ms":132.4,"method":"GET","shipment_id":"SHP-1017","tp_in":"none"}
logs-broken/status-service.log:{"timestamp":"2026-11-27T06:36:18.586179Z","level":"INFO","service":"status-service","trace_id":"9feb61d12c4a6dfb1238556175bd36c7","span_id":"9929dfeb80a1ee92","parent_span_id":null,"route":"/status/{shipment_id}","status":200,"duration_ms":4.19,"method":"GET","shipment_id":"SHP-1017","carrier":"carrier-c","tp_in":"none"}
logs-broken/status-service.log:{"timestamp":"2026-11-27T06:36:18.715704Z","level":"INFO","service":"status-service","trace_id":"9edb59ce52849d7ff0bace1b3478412f","span_id":"e3ac03436656b0e2","parent_span_id":null,"route":"/eta/{shipment_id}","status":200,"duration_ms":128.54,"method":"GET","shipment_id":"SHP-1017","carrier":"carrier-c","tp_in":"none"}
logs-broken/status-service.log:{"timestamp":"2026-11-27T06:36:19.104338Z","level":"INFO","service":"status-service","trace_id":"93c0180da66cdc362ddc6995a66bfd1c","span_id":"9222283ce9e2648b","parent_span_id":null,"route":"/status/{shipment_id}","status":200,"duration_ms":3.78,"method":"GET","shipment_id":"SHP-1017","carrier":"carrier-c","tp_in":"none"}
```

Answers: the same 609 spans now form 609 traces, none spanning both services; 608 are roots. The one
span with a missing parent is still the valid probe, because tracking-api continues the client's
trace on the way in even though it no longer passes it on. The slowest trace is a single
tracking-api span of 136 ms with nothing inside it: you can see that it was slow, not why. The error
list now shows 12 unconnected spans (6 tracking-api 502s and 6 status-service 503s) with different
trace ids. To pair them you would have to match `shipment_id` and timestamps (the 503 ends a few
milliseconds before the 502), which works here only because requests are sequential; under
concurrent load, with retries and many requests for the same shipment, timestamp matching
becomes guesswork.

## Smoke test

```text
$ python3 -m unittest tests.examples.test_lab11 -v
test_invalid_incoming_header_restarts_the_trace (tests.examples.test_lab11.Lab11Tests.test_invalid_incoming_header_restarts_the_trace) ... ok
test_outgoing_header_on_the_wire (tests.examples.test_lab11.Lab11Tests.test_outgoing_header_on_the_wire) ... ok
test_propagation_links_both_services (tests.examples.test_lab11.Lab11Tests.test_propagation_links_both_services) ... ok
test_sources_compile (tests.examples.test_lab11.Lab11Tests.test_sources_compile) ... ok
test_traceparent_rules_from_the_spec (tests.examples.test_lab11.Lab11Tests.test_traceparent_rules_from_the_spec) ... ok
test_without_propagation_each_request_falls_apart (tests.examples.test_lab11.Lab11Tests.test_without_propagation_each_request_falls_apart) ... ok

----------------------------------------------------------------------
Ran 6 tests in 3.871s

OK
```

The test starts both services on ephemeral ports of 127.0.0.1 (status-service with a 40 ms slow path
to stay fast) and checks the header on the wire with a stand-in downstream server.
