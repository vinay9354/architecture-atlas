"""Smoke test for Lab 13 (GitOps reconciliation): the four experiments produce the outcomes taught.

Every Git command runs in a temporary directory outside the repository, with global and system Git
configuration disabled, so the test never reads or changes this repository's Git state.
"""
import contextlib
import importlib.util
import io
import os
import py_compile
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-13-gitops-reconciliation"
APP_DIR = "apps/order-tracking"
API = "Deployment/order-tracking/tracking-api"
CONFIG = "ConfigMap/order-tracking/tracking-api-config"
POLLER = "Deployment/order-tracking/legacy-poller"


def load(name):
    spec = importlib.util.spec_from_file_location(name, LAB / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TempRepo:
    """A throwaway desired-state repository driven by plain `git` through subprocess."""

    def __init__(self, root):
        self.root = Path(root)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                        GIT_AUTHOR_NAME="Lab 13 test", GIT_AUTHOR_EMAIL="",
                        GIT_COMMITTER_NAME="Lab 13 test", GIT_COMMITTER_EMAIL="",
                        GIT_CEILING_DIRECTORIES=str(self.root.parent))
        self.root.mkdir(parents=True)
        self.git("init", "-q", "-b", "main")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, env=self.env, check=True,
                              capture_output=True, text=True).stdout

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD").strip()

    def replace(self, rel, old, new):
        p = self.root / rel
        text = p.read_text(encoding="utf-8")
        assert old in text, (rel, old)
        p.write_text(text.replace(old, new), encoding="utf-8")


class Lab13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = load("gitops_reconciler")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="lab13-test-")
        tmp = Path(self._tmp.name).resolve()
        self.assertFalse(tmp.is_relative_to(ROOT), "the test repository must live outside this repository")
        self.repo = TempRepo(tmp / "atlas-config")
        shutil.copytree(LAB / "starter-repo", self.repo.root, dirs_exist_ok=True)
        self.first = self.repo.commit("Add order-tracking app")
        self.cluster = self.rec.new_cluster()

    def tearDown(self):
        self._tmp.cleanup()

    def sync(self, **flags):
        return self.rec.reconcile_once(self.repo.root, self.cluster, **flags)

    def image(self):
        return self.cluster["objects"][API]["spec"]["template"]["spec"]["containers"][0]["image"]

    def test_sources_compile_and_starter_manifests_validate(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)
        files = sorted((LAB / "starter-repo" / APP_DIR).glob("*.yaml"))
        self.assertEqual(len(files), 4)
        for f in files:
            doc = yaml.safe_load(f.read_text(encoding="utf-8"))
            self.rec.validate(doc, f.name)
            self.assertEqual(doc["metadata"]["namespace"], "order-tracking")

    def test_a_new_commit_converges(self):
        first = self.sync()
        self.assertEqual((first["action"], first["sync_status"], first["health"]), ("sync", "Synced", "Healthy"))
        self.assertEqual(len(self.cluster["objects"]), 4)
        self.repo.replace(f"{APP_DIR}/tracking-api.yaml", "tracking-api:1.4.0", "tracking-api:1.5.0")
        # Uncommitted edits are not desired state: nothing changes until the commit lands.
        self.assertEqual(self.sync()["action"], "none")
        self.assertTrue(self.image().endswith(":1.4.0"))
        release = self.repo.commit("Release tracking-api 1.5.0")
        res = self.sync()
        self.assertEqual(res["applied"], ["deployment.apps/tracking-api configured"])
        self.assertEqual((res["sync_status"], self.cluster["sync"]["revision"]), ("Synced", release))
        self.assertTrue(self.image().endswith(":1.5.0"))
        self.assertEqual(self.sync()["action"], "none")   # steady state: the next poll does nothing

    def test_b_drift_is_reported_without_self_heal_and_reverted_with_it(self):
        self.sync()
        self.rec.edit_live(self.cluster, API, "spec.replicas=1")
        self.rec.edit_live(self.cluster, CONFIG, "data.STATUS_CACHE_TTL_SECONDS=300")
        report = self.sync(self_heal=False)
        self.assertEqual((report["action"], report["sync_status"]), ("report-only", "OutOfSync"))
        self.assertEqual(report["applied"], [])
        self.assertEqual(self.cluster["objects"][API]["spec"]["replicas"], 1)   # left in place
        drift = {row[0]: row[3] for row in report["rows"] if row[1] == "OutOfSync"}
        self.assertEqual(drift[API], [("~", "spec.replicas: 1 -> 3")])
        self.assertEqual(drift[CONFIG], [("~", "data.STATUS_CACHE_TTL_SECONDS: 300 -> 30")])
        healed = self.sync(self_heal=True)
        self.assertEqual((healed["action"], healed["sync_status"]), ("self-heal", "Synced"))
        self.assertEqual(self.cluster["objects"][API]["spec"]["replicas"], 3)
        self.assertEqual(self.cluster["objects"][CONFIG]["data"]["STATUS_CACHE_TTL_SECONDS"], "30")

    def test_c_bad_commit_is_fixed_by_git_revert_not_by_editing_the_cluster(self):
        self.sync(self_heal=True)
        self.repo.replace(f"{APP_DIR}/tracking-api.yaml", "tracking-api:1.4.0", "tracking-api:1.6.0")
        self.repo.commit("Release tracking-api 1.6.0")
        bad = self.sync(self_heal=True)
        self.assertEqual((bad["sync_status"], bad["health"]), ("Synced", "Degraded"))
        self.assertIn("ImagePullBackOff", self.cluster["objects"][API]["status"]["message"])
        # A hand fix on the cluster works for a moment, then self-heal restores what Git says.
        self.rec.edit_live(self.cluster, API,
                           "spec.template.spec.containers[0].image="
                           "registry.atlasmart.example/order-tracking/tracking-api:1.4.0")
        self.assertEqual(self.cluster["objects"][API]["status"]["health"], "Healthy")
        undone = self.sync(self_heal=True)
        self.assertEqual((undone["action"], undone["health"]), ("self-heal", "Degraded"))
        self.assertTrue(self.image().endswith(":1.6.0"))
        self.repo.git("revert", "--no-edit", "HEAD")
        fixed = self.sync(self_heal=True)
        self.assertEqual((fixed["action"], fixed["sync_status"], fixed["health"]), ("sync", "Synced", "Healthy"))
        self.assertTrue(self.image().endswith(":1.4.0"))
        log = self.repo.git("log", "--format=%s").splitlines()
        self.assertEqual(log[:2], ['Revert "Release tracking-api 1.6.0"', "Release tracking-api 1.6.0"])

    def test_d_removed_manifest_is_pruned_only_when_prune_is_on(self):
        self.sync()
        self.cluster["objects"]["ConfigMap/order-tracking/created-by-hand"] = {
            "apiVersion": "v1", "kind": "ConfigMap", "data": {},
            "metadata": {"name": "created-by-hand", "namespace": "order-tracking", "resourceVersion": 1},
            "status": {"health": "Healthy", "message": ""}}
        self.repo.git("rm", "-q", f"{APP_DIR}/legacy-poller.yaml")
        self.repo.commit("Retire legacy poller")
        kept = self.sync(prune=False)
        self.assertEqual((kept["sync_status"], kept["pruned"]), ("OutOfSync", []))
        self.assertIn(POLLER, self.cluster["objects"])
        pruned = self.sync(prune=True)
        self.assertEqual(pruned["pruned"], ["deployment.apps/legacy-poller pruned"])
        self.assertEqual(pruned["sync_status"], "Synced")
        self.assertNotIn(POLLER, self.cluster["objects"])
        # Objects the reconciler did not create carry no tracking mark and are never pruned.
        self.assertIn("ConfigMap/order-tracking/created-by-hand", self.cluster["objects"])

    def test_invalid_manifest_stops_the_whole_sync(self):
        self.sync()
        before = {k: dict(v["metadata"]) for k, v in self.cluster["objects"].items()}
        (self.repo.root / APP_DIR / "broken.yaml").write_text("kind: ConfigMap\ndata: [unclosed\n", encoding="utf-8")
        self.repo.replace(f"{APP_DIR}/tracking-api.yaml", "tracking-api:1.4.0", "tracking-api:1.5.0")
        self.repo.commit("Release 1.5.0 with a broken file")
        res = self.sync()
        self.assertEqual((res["action"], res["sync_status"]), ("error", "Unknown"))
        self.assertIn("broken.yaml", res["error"])
        self.assertTrue(self.image().endswith(":1.4.0"))   # nothing applied: all or nothing
        self.assertEqual(before, {k: dict(v["metadata"]) for k, v in self.cluster["objects"].items()})

    def test_demo_cli_prints_sync_status_lines(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.rec.main(["demo"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertEqual(text.count("=== "), 5)
        for line in ("sync: same revision, live state drifted: not applied",
                     "sync: same revision, live state drifted: self-heal sync",
                     "result: Synced to ",
                     "app health Degraded",
                     "deployment.apps/legacy-poller pruned",
                     "1 object(s) require pruning, prune is off: left running"):
            self.assertIn(line, text)


if __name__ == "__main__":
    unittest.main()
