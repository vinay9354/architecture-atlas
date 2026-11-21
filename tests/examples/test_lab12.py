"""Smoke test for Lab 12 (local Kubernetes deployment).

CI has no Docker and no kind, so the cluster steps are not run here. Instead this test:
- parses every manifest and the kind config with PyYAML and checks the invariants the lab teaches
  (replicas, zone spread, probes, requests and limits, security context, selectors that match,
  a default-deny NetworkPolicy plus allow rules);
- checks the Dockerfile is multi-stage, pinned, and non-root;
- starts the tracking stub on an ephemeral 127.0.0.1 port and checks its endpoints and readiness.
"""
import contextlib
import importlib.util
import io
import json
import py_compile
import re
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-12-local-kubernetes-deployment"
MANIFESTS = LAB / "manifests"
NAMESPACE = "atlas-tracking-lab"
APP_LABELS = {"app.kubernetes.io/name": "tracking-stub"}
ZONE_KEY = "topology.kubernetes.io/zone"


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, LAB / "app" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_objects():
    objs = []
    for path in sorted(MANIFESTS.glob("*.yaml")):
        if path.name == "kustomization.yaml":
            continue
        for doc in yaml.safe_load_all(path.read_text()):
            if doc:
                objs.append(doc)
    return objs


def selector_matches(match_labels, labels):
    return bool(match_labels) and all(labels.get(k) == v for k, v in match_labels.items())


def get(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        with err:
            return err.code, json.loads(err.read())


class Lab12ManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.objs = load_objects()

        def one(kind, name=None):
            found = [o for o in cls.objs if o["kind"] == kind and (name is None or o["metadata"]["name"] == name)]
            assert len(found) == 1, f"expected one {kind} {name or ''}, found {len(found)}"
            return found[0]

        cls.deploy = one("Deployment", "tracking-stub")
        cls.service = one("Service", "tracking-stub")
        cls.pdb = one("PodDisruptionBudget", "tracking-stub")
        cls.pod_spec = cls.deploy["spec"]["template"]["spec"]
        cls.container = cls.pod_spec["containers"][0]
        cls.template_labels = cls.deploy["spec"]["template"]["metadata"]["labels"]

    def test_kustomization_lists_every_manifest(self):
        kust = yaml.safe_load((MANIFESTS / "kustomization.yaml").read_text())
        files = sorted(p.name for p in MANIFESTS.glob("*.yaml") if p.name != "kustomization.yaml")
        self.assertEqual(sorted(kust["resources"]), files)

    def test_all_objects_are_namespaced_in_the_lab_namespace(self):
        ns = [o for o in self.objs if o["kind"] == "Namespace"]
        self.assertEqual([n["metadata"]["name"] for n in ns], [NAMESPACE])
        self.assertEqual(ns[0]["metadata"]["labels"]["pod-security.kubernetes.io/enforce"], "restricted")
        for o in self.objs:
            if o["kind"] != "Namespace":
                self.assertEqual(o["metadata"].get("namespace"), NAMESPACE, o["metadata"]["name"])

    def test_deployment_replicas_and_selector(self):
        self.assertEqual(self.deploy["spec"]["replicas"], 3)
        self.assertEqual(self.deploy["spec"]["selector"]["matchLabels"], APP_LABELS)
        self.assertTrue(selector_matches(self.deploy["spec"]["selector"]["matchLabels"], self.template_labels))

    def test_topology_spread_on_zone_label(self):
        spread = self.pod_spec["topologySpreadConstraints"]
        zone = [c for c in spread if c["topologyKey"] == ZONE_KEY]
        self.assertEqual(len(zone), 1)
        c = zone[0]
        self.assertEqual(c["maxSkew"], 1)
        self.assertEqual(c["whenUnsatisfiable"], "DoNotSchedule")
        self.assertTrue(selector_matches(c["labelSelector"]["matchLabels"], self.template_labels))

    def test_probes(self):
        ports = {p["name"]: p["containerPort"] for p in self.container["ports"]}
        for probe, path in (("readinessProbe", "/readyz"), ("livenessProbe", "/healthz")):
            http = self.container[probe]["httpGet"]
            self.assertEqual(http["path"], path)
            self.assertIn(http["port"], ports)

    def test_requests_and_limits(self):
        res = self.container["resources"]
        for section in ("requests", "limits"):
            self.assertIn("cpu", res[section])
            self.assertIn("memory", res[section])

    def test_security_context(self):
        pod_sc, sc = self.pod_spec["securityContext"], self.container["securityContext"]
        self.assertTrue(pod_sc["runAsNonRoot"] or sc.get("runAsNonRoot"))
        self.assertGreater(pod_sc["runAsUser"], 0)
        self.assertTrue(sc["readOnlyRootFilesystem"])
        self.assertFalse(sc["allowPrivilegeEscalation"])
        self.assertEqual(sc["capabilities"]["drop"], ["ALL"])
        self.assertNotIn("add", sc["capabilities"])
        self.assertEqual(pod_sc["seccompProfile"]["type"], "RuntimeDefault")

    def test_image_is_the_locally_loaded_tag(self):
        self.assertEqual(self.container["image"], "tracking-stub:0.1.0")
        self.assertIn(self.container["imagePullPolicy"], ("IfNotPresent", "Never"))

    def test_service_selects_the_pods_and_targets_the_named_port(self):
        spec = self.service["spec"]
        self.assertEqual(spec["type"], "ClusterIP")
        self.assertTrue(selector_matches(spec["selector"], self.template_labels))
        ports = {p["name"] for p in self.container["ports"]}
        self.assertIn(spec["ports"][0]["targetPort"], ports)

    def test_pdb_matches_the_deployment(self):
        spec = self.pdb["spec"]
        self.assertTrue(selector_matches(spec["selector"]["matchLabels"], self.template_labels))
        self.assertEqual(spec["selector"]["matchLabels"], self.deploy["spec"]["selector"]["matchLabels"])
        self.assertLess(spec["minAvailable"], self.deploy["spec"]["replicas"])  # a drain can make progress

    def test_network_policies(self):
        pols = [o for o in self.objs if o["kind"] == "NetworkPolicy"]
        deny = [p for p in pols if p["spec"]["podSelector"] == {} and not p["spec"].get("ingress")
                and not p["spec"].get("egress")]
        self.assertEqual(len(deny), 1, "exactly one default-deny policy")
        self.assertEqual(sorted(deny[0]["spec"]["policyTypes"]), ["Egress", "Ingress"])
        allow_in = [p for p in pols if p["spec"].get("ingress")
                    and selector_matches(p["spec"]["podSelector"].get("matchLabels"), self.template_labels)]
        self.assertEqual(len(allow_in), 1, "one ingress allow rule for the tracking stub")
        rule = allow_in[0]["spec"]["ingress"][0]
        self.assertEqual(rule["ports"][0]["port"], 8080)
        allowed_from = rule["from"][0]["podSelector"]["matchLabels"]
        clients = {o["metadata"]["name"]: o for o in self.objs if o["kind"] == "Pod"}
        self.assertTrue(selector_matches(allowed_from, clients["allowed-client"]["metadata"]["labels"]))
        self.assertFalse(selector_matches(allowed_from, clients["blocked-client"]["metadata"]["labels"]))

    def test_test_clients_meet_restricted_profile(self):
        for pod in (o for o in self.objs if o["kind"] == "Pod"):
            sc = pod["spec"]["containers"][0]["securityContext"]
            self.assertTrue(pod["spec"]["securityContext"]["runAsNonRoot"])
            self.assertEqual(sc["capabilities"]["drop"], ["ALL"])
            self.assertFalse(sc["allowPrivilegeEscalation"])


class Lab12ClusterAndImageTests(unittest.TestCase):
    def test_kind_config_has_three_zoned_workers(self):
        cfg = yaml.safe_load((LAB / "kind-cluster.yaml").read_text())
        self.assertEqual(cfg["apiVersion"], "kind.x-k8s.io/v1alpha4")
        roles = [n["role"] for n in cfg["nodes"]]
        self.assertEqual(roles.count("control-plane"), 1)
        self.assertEqual(roles.count("worker"), 3)
        zones = [n["labels"][ZONE_KEY] for n in cfg["nodes"] if n["role"] == "worker"]
        self.assertEqual(sorted(zones), ["zone-a", "zone-b", "zone-c"])
        for n in cfg["nodes"]:
            self.assertRegex(n["image"], r"^kindest/node:v\d+\.\d+\.\d+@sha256:[0-9a-f]{64}$")

    def test_dockerfile_multi_stage_pinned_non_root(self):
        text = (LAB / "Dockerfile").read_text()
        froms = re.findall(r"^FROM\s+(\S+)", text, flags=re.M)
        self.assertEqual(len(froms), 2)
        for image in froms:
            self.assertRegex(image, r"^python:\d+\.\d+\.\d+-slim")  # exact patch version, never latest
        self.assertIn("COPY --from=build", text)
        users = re.findall(r"^USER\s+(\d+)", text, flags=re.M)
        self.assertTrue(users and int(users[-1]) > 0)
        deploy = yaml.safe_load((MANIFESTS / "10-deployment.yaml").read_text())
        self.assertEqual(int(users[-1]), deploy["spec"]["template"]["spec"]["securityContext"]["runAsUser"])

    def test_sources_compile(self):
        for p in (LAB / "app").glob("*.py"):
            py_compile.compile(str(p), doraise=True)


class Lab12StubServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stub = load_module("tracking_stub")
        cls.probe = load_module("probe")
        cls.server, cls.state = cls.stub.build_server("127.0.0.1", 0, ready_delay_s=0.0, quiet=True)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_healthz(self):
        self.assertEqual(get(self.base + "/healthz"), (200, {"status": "ok"}))

    def test_readyz(self):
        self.assertEqual(get(self.base + "/readyz"), (200, {"status": "ready"}))

    def test_shipment_returns_fixed_json(self):
        code, body = get(self.base + "/shipments/AM-1001")
        self.assertEqual(code, 200)
        self.assertEqual(body["shipment_id"], "AM-1001")
        self.assertEqual(body["status"], "IN_TRANSIT")
        self.assertEqual(set(body["served_by"]), {"pod", "node"})
        self.assertNotIn("address", json.dumps(body))  # NFR-6: no delivery address

    def test_bad_id_and_unknown_path(self):
        self.assertEqual(get(self.base + "/shipments/not%20valid")[0], 400)
        self.assertEqual(get(self.base + "/shipments/" + "x" * 33)[0], 400)
        self.assertEqual(get(self.base + "/orders/1")[0], 404)

    def test_post_is_rejected(self):
        req = urllib.request.Request(self.base + "/shipments/AM-1001", data=b"{}", method="POST")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req, timeout=3)
        ctx.exception.close()
        self.assertEqual(ctx.exception.code, 405)

    def test_probe_client(self):
        ok, msg = self.probe.fetch(self.base + "/shipments/AM-1001", 3)
        self.assertTrue(ok)
        self.assertTrue(msg.startswith("HTTP 200"))
        ok, msg = self.probe.fetch("http://127.0.0.1:9/never", 1)  # discard port: nothing listens
        self.assertFalse(ok)

    def test_readiness_warm_up_and_shutdown(self):
        server, state = self.stub.build_server("127.0.0.1", 0, ready_delay_s=0.3, quiet=True)
        base = f"http://127.0.0.1:{server.server_address[1]}"
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            self.assertEqual(get(base + "/readyz")[0], 503)  # warming up
            self.assertEqual(get(base + "/healthz")[0], 200)  # but alive
            time.sleep(0.4)
            self.assertEqual(get(base + "/readyz")[0], 200)
            state.shutting_down.set()  # what the SIGTERM handler does first
            self.assertEqual(get(base + "/readyz")[0], 503)
            self.assertEqual(get(base + "/healthz")[0], 200)
        finally:
            server.shutdown()
            server.server_close()

    def test_self_test_cli(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.stub.main(["--self-test"])
        self.assertEqual(code, 0)
        self.assertIn("self-test passed", out.getvalue())


if __name__ == "__main__":
    unittest.main()
