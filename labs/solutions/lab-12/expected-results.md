# Lab 12 — sample results

This file has two kinds of output, and they are labelled differently:

- **Captured by the author** (Steps 1 and the smoke test): real output from a laptop on 2026-11-21
  (macOS, Python 3.14.7). The stub server and the smoke test need only Python, so they were run.
- **Expected shape, not captured by the author** (Steps 2-9): Docker was installed but not running
  on the author's machine and kind was not installed, so the cluster was never created. The blocks
  in those sections are **illustrative**: they show the columns and the kind of values to look for,
  written from the manifests and the Kubernetes and kind documentation. Pod names, IP addresses,
  ages, and hashes on your machine will differ. If you run the lab, please replace these blocks with
  your captured output.

## Step 1 — Run the stub on your laptop (captured by the author)

```text
$ POD_NAME=local-stub NODE_NAME=laptop python3 app/tracking_stub.py
tracking-stub 0.1.0 listening on 127.0.0.1:8080 (ready after 2.0s)
```

In a second terminal, first within two seconds of starting it, then again after:

```text
$ curl -s -w " %{http_code}\n" localhost:8080/readyz
{"status": "not-ready"} 503
$ curl -s -w " %{http_code}\n" localhost:8080/readyz
{"status": "ready"} 200
$ curl -s -w " %{http_code}\n" localhost:8080/healthz
{"status": "ok"} 200
$ curl -s -w " %{http_code}\n" localhost:8080/shipments/AM-1001
{"carrier": "carrier-a", "estimated_delivery": "2026-11-24", "last_scan_at": "2026-11-21T09:00:00Z", "served_by": {"node": "laptop", "pod": "local-stub"}, "shipment_id": "AM-1001", "status": "IN_TRANSIT"} 200
$ curl -s -w " %{http_code}\n" localhost:8080/shipments/not%20valid
{"error": "shipment id must be 1-32 letters, digits, or hyphens"} 400
$ curl -s -w " %{http_code}\n" localhost:8080/orders/1
{"error": "not found"} 404
```

After `kill -TERM <pid>` the server reports not-ready at once, keeps listening for its 2-second
grace period, then exits:

```text
$ curl -s -w " %{http_code}\n" localhost:8080/readyz
{"status": "not-ready"} 503
```

The server's own log (stderr, one JSON line per request; the `ts` values are Unix timestamps):

```text
{"ts": 1795219486.72, "client": "127.0.0.1", "msg": "\"GET /readyz HTTP/1.1\" 503 -"}
{"ts": 1795219488.955, "client": "127.0.0.1", "msg": "\"GET /readyz HTTP/1.1\" 200 -"}
{"ts": 1795219488.972, "client": "127.0.0.1", "msg": "\"GET /healthz HTTP/1.1\" 200 -"}
{"ts": 1795219488.986, "client": "127.0.0.1", "msg": "\"GET /shipments/AM-1001 HTTP/1.1\" 200 -"}
{"ts": 1795219488.998, "client": "127.0.0.1", "msg": "\"GET /shipments/not%20valid HTTP/1.1\" 400 -"}
{"ts": 1795219489.011, "client": "127.0.0.1", "msg": "\"GET /orders/1 HTTP/1.1\" 404 -"}
{"ts": 1795219489.345, "client": "127.0.0.1", "msg": "\"GET /readyz HTTP/1.1\" 503 -"}
tracking-stub stopped
```

The self-test that the Dockerfile's build stage runs (captured):

```text
$ python3 app/tracking_stub.py --self-test
self-test /healthz               expected 200 got 200
self-test /readyz                expected 200 got 200
self-test /shipments/AM-1001     expected 200 got 200
self-test /shipments/bad%20id    expected 400 got 400
self-test /nope                  expected 404 got 404
self-test passed
```

The probe client, against the running stub and against a port where nothing listens (captured; the
port number was ephemeral in this run and is shown as `$PORT`):

```text
$ python3 app/probe.py http://127.0.0.1:$PORT/shipments/AM-1002
HTTP 200 {"carrier": "carrier-a", "estimated_delivery": "2026-11-24", "last_scan_at": "2026-11-21T09:00:00Z", "served_by": {"node": "unknown", "pod": "<laptop hostname>"}, "shipment_id": "AM-1002", "status": "IN_TRANSIT"}
exit 0
$ python3 app/probe.py --timeout 1 http://127.0.0.1:9/shipments/AM-1002
FAILED ConnectionRefusedError: [Errno 61] Connection refused
exit 1
```

(In that run `POD_NAME` was not set, so the stub fell back to the machine's hostname; it is replaced
by a placeholder here.)

## Smoke test (captured by the author)

```text
$ python3 -m unittest tests.examples.test_lab12 -v
test_dockerfile_multi_stage_pinned_non_root (...Lab12ClusterAndImageTests...) ... ok
test_kind_config_has_three_zoned_workers (...Lab12ClusterAndImageTests...) ... ok
test_sources_compile (...Lab12ClusterAndImageTests...) ... ok
test_all_objects_are_namespaced_in_the_lab_namespace (...Lab12ManifestTests...) ... ok
test_deployment_replicas_and_selector (...Lab12ManifestTests...) ... ok
test_image_is_the_locally_loaded_tag (...Lab12ManifestTests...) ... ok
test_kustomization_lists_every_manifest (...Lab12ManifestTests...) ... ok
test_network_policies (...Lab12ManifestTests...) ... ok
test_pdb_matches_the_deployment (...Lab12ManifestTests...) ... ok
test_probes (...Lab12ManifestTests...) ... ok
test_requests_and_limits (...Lab12ManifestTests...) ... ok
test_security_context (...Lab12ManifestTests...) ... ok
test_service_selects_the_pods_and_targets_the_named_port (...Lab12ManifestTests...) ... ok
test_test_clients_meet_restricted_profile (...Lab12ManifestTests...) ... ok
test_topology_spread_on_zone_label (...Lab12ManifestTests...) ... ok
test_bad_id_and_unknown_path (...Lab12StubServerTests...) ... ok
test_healthz (...Lab12StubServerTests...) ... ok
test_post_is_rejected (...Lab12StubServerTests...) ... ok
test_probe_client (...Lab12StubServerTests...) ... ok
test_readiness_warm_up_and_shutdown (...Lab12StubServerTests...) ... ok
test_readyz (...Lab12StubServerTests...) ... ok
test_self_test_cli (...Lab12StubServerTests...) ... ok
test_shipment_returns_fixed_json (...Lab12StubServerTests...) ... ok

----------------------------------------------------------------------
Ran 23 tests in 1.988s

OK
```

(Test ids are shortened with `...`.)

## Steps 2-9 — the cluster (expected shape, not captured by the author)

> **Illustrative only.** Nothing in this section was produced by running the commands. It is the
> shape a correct run should have, derived from the manifests and the cited documentation.

### Step 2 — Nodes and zones (illustrative)

```text
$ kubectl get nodes -L topology.kubernetes.io/zone
NAME                        STATUS   ROLES           AGE   VERSION   ZONE
atlas-lab12-control-plane   Ready    control-plane   2m    v1.37.0
atlas-lab12-worker          Ready    <none>          2m    v1.37.0   zone-a
atlas-lab12-worker2         Ready    <none>          2m    v1.37.0   zone-b
atlas-lab12-worker3         Ready    <none>          2m    v1.37.0   zone-c
```

What matters: four Ready nodes, the three workers each in a different zone, the control plane with
no zone. Which worker gets which zone follows the order in `kind-cluster.yaml`.

### Step 4 — One replica per zone (illustrative)

```text
$ kubectl -n atlas-tracking-lab get pods -l app.kubernetes.io/name=tracking-stub -o wide
NAME                             READY   STATUS    RESTARTS   AGE   IP           NODE
tracking-stub-6d9c7b5f4d-2xkqp   1/1     Running   0          40s   10.244.1.2   atlas-lab12-worker
tracking-stub-6d9c7b5f4d-8wz7n   1/1     Running   0          40s   10.244.2.2   atlas-lab12-worker2
tracking-stub-6d9c7b5f4d-qm4tl   1/1     Running   0          40s   10.244.3.2   atlas-lab12-worker3
```

What matters: three Pods, `1/1` ready, each on a different worker. None on the control plane (it is
tainted against ordinary workloads in a multi-node kind cluster).

### Step 5 — Port-forward and curl (illustrative)

```text
$ curl -s localhost:8080/shipments/AM-1001
{"carrier": "carrier-a", "estimated_delivery": "2026-11-24", "last_scan_at": "2026-11-21T09:00:00Z", "served_by": {"node": "atlas-lab12-worker2", "pod": "tracking-stub-6d9c7b5f4d-8wz7n"}, "shipment_id": "AM-1001", "status": "IN_TRANSIT"}
```

What matters: `served_by` now names a real Pod and node. Repeating the request usually shows the
same Pod, because `kubectl port-forward svc/...` picks one Pod when the forward starts.

### Step 6 — NetworkPolicy from inside the cluster (illustrative)

```text
$ kubectl -n atlas-tracking-lab exec allowed-client -- python /app/probe.py http://tracking-stub/shipments/AM-1001
HTTP 200 {"carrier": "carrier-a", ... "status": "IN_TRANSIT"}
$ kubectl -n atlas-tracking-lab exec blocked-client -- python /app/probe.py http://tracking-stub/shipments/AM-1001
FAILED TimeoutError: timed out
command terminated with exit code 1
```

What matters: the allowed client gets a 200; the blocked client fails. A policy drop usually shows
as a timeout (packets silently discarded), not as "connection refused"; the exact exception text can
differ. If the blocked client also gets a 200, NetworkPolicy is not being enforced (see the lab
page's troubleshooting table).

### Step 7 — Delete a Pod and watch it come back (illustrative)

```text
$ kubectl -n atlas-tracking-lab get pods -l app.kubernetes.io/name=tracking-stub -w
NAME                             READY   STATUS              RESTARTS   AGE
tracking-stub-6d9c7b5f4d-2xkqp   1/1     Terminating         0          5m
tracking-stub-6d9c7b5f4d-v7rfx   0/1     Pending             0          0s
tracking-stub-6d9c7b5f4d-v7rfx   0/1     ContainerCreating   0          0s
tracking-stub-6d9c7b5f4d-v7rfx   0/1     Running             0          1s
tracking-stub-6d9c7b5f4d-v7rfx   1/1     Running             0          6s
```

What matters: a new Pod with a new name appears at once (the ReplicaSet controller restores the count
of 3); it is `0/1` while the stub warms up (`READY_DELAY_SECONDS=3`) and becomes `1/1` after the next
readiness probe; it lands on the same worker, because zone-a is the only zone with no replica.

### Step 8 — Drain two nodes and watch the PDB (illustrative)

First drain (zone-a): the eviction is allowed because 3 ready replicas minus 1 still meets
`minAvailable: 2`.

```text
$ kubectl drain atlas-lab12-worker --ignore-daemonsets --delete-emptydir-data
node/atlas-lab12-worker cordoned
evicting pod atlas-tracking-lab/tracking-stub-6d9c7b5f4d-v7rfx
pod/tracking-stub-6d9c7b5f4d-v7rfx evicted
node/atlas-lab12-worker drained
$ kubectl -n atlas-tracking-lab get pdb tracking-stub
NAME            MIN AVAILABLE   MAX UNAVAILABLE   ALLOWED DISRUPTIONS   AGE
tracking-stub   2               N/A               1                     9m
```

Second drain (zone-b) while zone-a is still cordoned: the node may hold two replicas by now, and the
PDB lets only one go at a time, so the drain retries until the replacement is ready.

```text
$ kubectl drain atlas-lab12-worker2 --ignore-daemonsets --delete-emptydir-data
node/atlas-lab12-worker2 cordoned
evicting pod atlas-tracking-lab/tracking-stub-6d9c7b5f4d-8wz7n
evicting pod atlas-tracking-lab/tracking-stub-6d9c7b5f4d-k2l9d
error when evicting pods/"tracking-stub-6d9c7b5f4d-k2l9d" -n "atlas-tracking-lab" (will retry after 5s): Cannot evict pod as it would violate the pod's disruption budget.
pod/tracking-stub-6d9c7b5f4d-8wz7n evicted
evicting pod atlas-tracking-lab/tracking-stub-6d9c7b5f4d-k2l9d
pod/tracking-stub-6d9c7b5f4d-k2l9d evicted
node/atlas-lab12-worker2 drained
```

What matters: the "would violate the pod's disruption budget" retry line, then success once a
replacement is ready elsewhere. At the end all three replicas run on the zone-c worker: the spread
constraint (with `nodeTaintsPolicy: Honor`) ignores cordoned nodes, so it no longer stops them
crowding into one zone. After `kubectl uncordon` the Pods stay where they are; spread constraints
apply only when a Pod is scheduled.

### Step 9 — Cleanup (illustrative)

```text
$ kind delete cluster --name atlas-lab12
Deleting cluster "atlas-lab12" ...
Deleted nodes: ["atlas-lab12-worker" "atlas-lab12-worker3" "atlas-lab12-control-plane" "atlas-lab12-worker2"]
```

## Answers to the questions in the lab page

- **Why does the replacement Pod in Step 7 land in zone-a?** With `maxSkew: 1` on the zone label,
  zone-a has 0 replicas and zones b and c have 1 each; placing the new Pod in b or c would make the
  skew 2 - 0 = 2, which `DoNotSchedule` forbids. Only the zone-a worker is eligible.
- **Why is the first drain smooth and the second throttled?** Before the first drain 3 replicas are
  ready and the budget needs 2, so one eviction is allowed. During the second drain the node holds
  two replicas; evicting both at once would leave 1, so the eviction API refuses the second until
  the first one's replacement is ready.
- **What would happen without `nodeTaintsPolicy: Honor`?** The cordoned zone-a node would still
  count as a domain with 0 replicas, so the replacement Pod could not go to b or c (skew 2) and would
  stay `Pending` until zone-a is uncordoned. That is the "hard spread plus lost zone" trap: it
  protects spread at the cost of capacity. Many teams use `ScheduleAnyway` for exactly this reason.
- **Why does port-forward not test the NetworkPolicy?** The forwarded connection is opened inside
  the Pod's network namespace by the node's kubelet and container runtime rather than arriving from
  another Pod, so in common implementations the Pod-to-Pod rules never see it (and traffic from the
  Pod's own node is always allowed). That is why the lab tests the policy from client Pods.
- **Why must the image tag not be `latest`?** With `latest`, the default pull policy is `Always`, so
  the kubelet tries to pull from Docker Hub instead of using the image that `kind load` put on the
  nodes, and the Pods fail with an image pull error.
