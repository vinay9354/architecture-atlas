#!/usr/bin/env python3
"""Lab 13 GitOps reconciler: a pull-based sync loop between a Git repository and a simulated cluster.

Standard library plus PyYAML. No Kubernetes is needed: the "cluster" is a JSON file holding live
objects (Deployments and ConfigMaps as dicts), and "applying" means writing that file.

The model, shaped like Argo CD's automated sync (and Flux's Kustomization):
- Desired state is the YAML under --path in the commit that `main` points to. Only committed
  content counts: uncommitted edits in the working tree are ignored, as a GitOps agent would.
- Each poll: fetch main's commit, load and validate its manifests, diff them field by field
  against the live objects, then decide:
    * a NEW commit is applied automatically (creates and updates);
    * the SAME commit with live differences is drift: reverted only when --self-heal is on,
      otherwise reported as OutOfSync and left alone;
    * live objects this app created but Git no longer contains are deleted only when --prune is
      on; otherwise the app stays OutOfSync with "requires pruning".
- The reconciler marks every object it creates with a tracking annotation and only ever prunes
  objects carrying its own mark, so objects created by other tools are never deleted.
- Health is simulated: a Deployment is Healthy when every container image exists in the cluster's
  registry list, otherwise Degraded (ImagePullBackOff). ConfigMaps are always Healthy.
- A manifest that fails to parse or validate stops the whole sync (ComparisonError) and nothing
  is applied: a sync is all or nothing.

Subcommands:
  init-cluster  create an empty simulated cluster file with a registry of pushed images
  diff          compare main with the cluster, apply nothing
  sync          one poll of the loop (what a controller does every interval)
  watch         poll every --interval seconds, --iterations times (0 = until Ctrl-C)
  edit-live     change a live object by hand, like `kubectl edit` (creates drift)
  history       print the cluster's sync history
  demo          run experiments a-d in a temporary directory and print everything
"""

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

APP = "order-tracking"
TRACKING_ANNOTATION = "gitops.atlasmart.example/tracking-id"
SUPPORTED = {"Deployment": ("apps/v1", "deployment.apps"), "ConfigMap": ("v1", "configmap")}
REGISTRY = "registry.atlasmart.example/order-tracking"
DEFAULT_IMAGES = [f"{REGISTRY}/tracking-api:1.4.0", f"{REGISTRY}/tracking-api:1.5.0",
                  f"{REGISTRY}/webhook-ingestor:2.1.0", f"{REGISTRY}/legacy-poller:0.9.3"]
LAB_DIR = Path(__file__).resolve().parent


class ComparisonError(Exception):
    """The desired state could not be loaded or validated; nothing is applied."""


# ------------------------------------------------------------------------------------------ git

def git(repo, *args, env=None):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise ComparisonError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def load_desired(repo, path, branch="main"):
    """Return (commit, subject, {key: manifest}) for the branch tip. Reads the commit, not the tree."""
    commit = git(repo, "rev-parse", f"refs/heads/{branch}").strip()
    subject = git(repo, "log", "-1", "--format=%s", commit).strip()
    files = [f for f in git(repo, "ls-tree", "-r", "--name-only", commit, "--", path).splitlines()
             if f.endswith((".yaml", ".yml"))]
    desired = {}
    for name in sorted(files):
        try:
            docs = list(yaml.safe_load_all(git(repo, "show", f"{commit}:{name}")))
        except yaml.YAMLError as exc:
            raise ComparisonError(f"{name}: invalid YAML ({exc.__class__.__name__})") from exc
        for doc in docs:
            if doc is None:
                continue
            key = validate(doc, name)
            if key in desired:
                raise ComparisonError(f"{name}: duplicate object {key}")
            desired[key] = doc
    return commit, subject, desired


def validate(doc, source):
    if not isinstance(doc, dict):
        raise ComparisonError(f"{source}: a manifest must be a mapping")
    kind = doc.get("kind")
    if kind not in SUPPORTED:
        raise ComparisonError(f"{source}: unsupported kind {kind!r} (lab supports {', '.join(SUPPORTED)})")
    if doc.get("apiVersion") != SUPPORTED[kind][0]:
        raise ComparisonError(f"{source}: {kind} needs apiVersion {SUPPORTED[kind][0]}")
    meta = doc.get("metadata") or {}
    if not meta.get("name"):
        raise ComparisonError(f"{source}: metadata.name is required")
    return f"{kind}/{meta.get('namespace', 'default')}/{meta['name']}"


# -------------------------------------------------------------------------------------- cluster

def new_cluster(images=None):
    return {"registry": list(images or DEFAULT_IMAGES), "objects": {},
            "sync": {"revision": None, "status": "Unknown", "health": "Unknown"}, "history": []}


def load_cluster(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_cluster(path, cluster):
    Path(path).write_text(json.dumps(cluster, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def object_health(obj, registry):
    if obj["kind"] != "Deployment":
        return "Healthy", ""
    for c in obj.get("spec", {}).get("template", {}).get("spec", {}).get("containers", []):
        if c.get("image") not in registry:
            return "Degraded", f"ImagePullBackOff: {c.get('image', '?').rsplit('/', 1)[-1]} not in registry"
    return "Healthy", ""


def refresh_status(obj, registry):
    health, message = object_health(obj, registry)
    replicas = obj.get("spec", {}).get("replicas", 1) if obj["kind"] == "Deployment" else None
    obj["status"] = {"health": health, "message": message}
    if replicas is not None:
        obj["status"]["readyReplicas"] = replicas if health == "Healthy" else 0


def normalize(obj):
    """The part of an object that is compared: everything except status and bookkeeping."""
    out = {k: copy.deepcopy(v) for k, v in obj.items() if k not in ("status",)}
    meta = out.get("metadata", {})
    meta.setdefault("namespace", "default")
    for k in ("resourceVersion", "generation"):
        meta.pop(k, None)
    ann = {k: v for k, v in meta.get("annotations", {}).items() if k != TRACKING_ANNOTATION}
    if ann:
        meta["annotations"] = ann
    else:
        meta.pop("annotations", None)
    return out


def flatten(value, prefix=""):
    if isinstance(value, dict) and value:
        out = {}
        for k in sorted(value):
            out.update(flatten(value[k], f"{prefix}.{k}" if prefix else str(k)))
        return out
    if isinstance(value, list) and value:
        out = {}
        for i, item in enumerate(value):
            out.update(flatten(item, f"{prefix}[{i}]"))
        return out
    return {prefix: value}


def field_diff(live, desired):
    """List of (path, live_value, desired_value) where they differ; None means absent."""
    a, b = flatten(normalize(live)), flatten(normalize(desired))
    return [(p, a.get(p), b.get(p)) for p in sorted(set(a) | set(b)) if a.get(p) != b.get(p)]


def short(value):
    if value is None:
        return "<absent>"
    text = json.dumps(value) if not isinstance(value, str) else value
    return text.replace(REGISTRY + "/", "")


# ----------------------------------------------------------------------------------- reconcile

def compare(desired, cluster):
    """Per-object comparison: creates, updates (with field diffs), and prune candidates."""
    live = cluster["objects"]
    creates = [k for k in sorted(desired) if k not in live]
    updates = {k: field_diff(live[k], desired[k]) for k in sorted(desired) if k in live}
    updates = {k: d for k, d in updates.items() if d}
    prunes = [k for k in sorted(live) if k not in desired
              and live[k].get("metadata", {}).get("annotations", {}).get(TRACKING_ANNOTATION, "")
              .startswith(f"{APP}:")]
    return creates, updates, prunes


def apply_object(cluster, key, manifest):
    live = cluster["objects"].get(key)
    obj = copy.deepcopy(manifest)
    meta = obj.setdefault("metadata", {})
    meta.setdefault("namespace", "default")
    meta.setdefault("annotations", {})[TRACKING_ANNOTATION] = f"{APP}:{key}"
    meta["resourceVersion"] = (live or {}).get("metadata", {}).get("resourceVersion", 0) + 1
    refresh_status(obj, cluster["registry"])
    cluster["objects"][key] = obj
    return f"{SUPPORTED[obj['kind']][1]}/{meta['name']} {'configured' if live else 'created'}"


def app_health(cluster):
    states = [o["status"]["health"] for o in cluster["objects"].values()
              if o.get("metadata", {}).get("annotations", {}).get(TRACKING_ANNOTATION, "").startswith(f"{APP}:")]
    return "Degraded" if "Degraded" in states else ("Healthy" if states else "Missing")


def reconcile_once(repo, cluster, path=f"apps/{APP}", self_heal=False, prune=False, branch="main"):
    """One poll. Mutates `cluster` and returns a result dict describing what happened."""
    result = {"self_heal": self_heal, "prune": prune, "previous": cluster["sync"]["revision"],
              "applied": [], "pruned": [], "rows": [], "notes": []}
    try:
        commit, subject, desired = load_desired(repo, path, branch)
    except ComparisonError as exc:
        cluster["sync"]["status"] = "Unknown"
        result.update(revision=None, subject="", action="error", sync_status="Unknown",
                      health=app_health(cluster), error=str(exc))
        return result
    result.update(revision=commit, subject=subject)
    creates, updates, prunes = compare(desired, cluster)
    for key in sorted(set(desired) | set(prunes)):
        obj = cluster["objects"].get(key)
        health = obj["status"]["health"] if obj else "Missing"
        if key in creates:
            row = (key, "OutOfSync", health, [("+", "(new object)")])
        elif key in updates:
            row = (key, "OutOfSync", health,
                   [("~", f"{p}: {short(a)} -> {short(b)}") for p, a, b in updates[key]])
        elif key in prunes:
            row = (key, "OutOfSync", health, [("-", "not in Git (requires pruning)")])
        else:
            row = (key, "Synced", health, [])
        result["rows"].append(row)

    new_revision = commit != cluster["sync"]["revision"]
    changes = bool(creates or updates)
    if new_revision:
        action = "sync"
    elif changes and self_heal:
        action = "self-heal"
    elif changes:
        action = "report-only"
        result["notes"].append("drift detected, self-heal is off: live changes left in place")
    else:
        action = "none"
    if action in ("sync", "self-heal"):
        for key in creates + list(updates):
            result["applied"].append(apply_object(cluster, key, desired[key]))
    if prunes and prune and action != "report-only":
        for key in prunes:
            obj = cluster["objects"].pop(key)
            result["pruned"].append(f"{SUPPORTED[obj['kind']][1]}/{obj['metadata']['name']} pruned")
    elif prunes and not prune:
        result["notes"].append(f"{len(prunes)} object(s) require pruning, prune is off: left running")

    if action in ("sync", "self-heal"):
        cluster["sync"]["revision"] = commit
    creates, updates, prunes = compare(desired, cluster)
    sync_status = "Synced" if not (creates or updates or prunes) else "OutOfSync"
    health = app_health(cluster)
    cluster["sync"].update(status=sync_status, health=health)
    if result["applied"] or result["pruned"]:
        cluster["history"].append({"id": len(cluster["history"]) + 1, "revision": commit[:7],
                                   "subject": subject,
                                   "reason": action if action in ("sync", "self-heal") else "prune",
                                   "changes": result["applied"] + result["pruned"]})
    result.update(action=action, sync_status=sync_status, health=health,
                  synced_revision=cluster["sync"]["revision"])
    return result


def format_result(result, poll=None):
    lines = []
    head = f"--- poll {poll}" if poll is not None else "---"
    flags = f"self-heal={'on' if result['self_heal'] else 'off'} prune={'on' if result['prune'] else 'off'}"
    if result["action"] == "error":
        lines.append(f"{head}  {flags}")
        lines.append(f"ComparisonError: {result['error']}")
        lines.append(f"result: sync status Unknown, nothing applied, app health {result['health']}")
        return "\n".join(lines)
    lines.append(f"{head}  main@{result['revision'][:7]} \"{result['subject']}\"  {flags}")
    lines.append(f"{'KIND':<11}{'NAMESPACE':<16}{'NAME':<22}{'STATUS':<11}HEALTH")
    for key, status, health, details in result["rows"]:
        kind, ns, name = key.split("/")
        lines.append(f"{kind:<11}{ns:<16}{name:<22}{status:<11}{health}")
        for mark, text in details:
            lines.append(f"    {mark} {text}")
    prev = (result["previous"] or "none")[:7]
    verb = {"sync": f"new revision {result['revision'][:7]} (was {prev}): automated sync",
            "self-heal": "same revision, live state drifted: self-heal sync",
            "report-only": "same revision, live state drifted: not applied",
            "none": "same revision, nothing to apply",
            "diff": "diff only, nothing applied"}[result["action"]]
    if result["action"] == "none" and result["pruned"]:
        verb = "same revision: pruning objects removed from Git"
    lines.append(f"sync: {verb}")
    for text in result["applied"] + result["pruned"]:
        lines.append(f"  {text}")
    for note in result["notes"]:
        lines.append(f"  note: {note}")
    synced = (result.get("synced_revision") or "none")[:7]
    state = f"Synced to {synced}" if result["sync_status"] == "Synced" else f"OutOfSync (last sync {synced})"
    lines.append(f"result: {state}, app health {result['health']}")
    return "\n".join(lines)


# ----------------------------------------------------------------------------------- edit-live

def set_path(obj, path, value):
    parts = [p for p in re.split(r"\.(?![^\[]*\])", path) if p]
    target = obj
    for i, part in enumerate(parts):
        m = re.fullmatch(r"([^\[]+)((?:\[\d+\])*)", part)
        if not m:
            raise ValueError(f"bad path segment {part!r}")
        name, indexes = m.group(1), [int(x) for x in re.findall(r"\[(\d+)\]", m.group(2))]
        last = i == len(parts) - 1
        if not indexes:
            if last:
                target[name] = value
                return
            target = target.setdefault(name, {})
            continue
        target = target[name]
        for j, idx in enumerate(indexes):
            if last and j == len(indexes) - 1:
                target[idx] = value
                return
            target = target[idx]


def edit_live(cluster, key, assignment):
    """Change one field of a live object by hand, like kubectl edit. Returns a log line."""
    if key not in cluster["objects"]:
        raise KeyError(f"no live object {key}")
    path, _, raw = assignment.partition("=")
    value = raw if path.startswith("data.") else yaml.safe_load(raw)
    obj = cluster["objects"][key]
    set_path(obj, path, value)
    obj["metadata"]["resourceVersion"] += 1
    refresh_status(obj, cluster["registry"])
    return f"edited by hand: {key} {path}={short(value)}"


# ---------------------------------------------------------------------------------------- demo

class LabRepo:
    """A throwaway Git repository with a fixed identity and clock, so commit ids are reproducible."""

    def __init__(self, root):
        self.root = Path(root)
        self.tick = 0
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                        GIT_AUTHOR_NAME="Lab 13", GIT_AUTHOR_EMAIL="",
                        GIT_COMMITTER_NAME="Lab 13", GIT_COMMITTER_EMAIL="")
        self.root.mkdir(parents=True, exist_ok=True)
        self.run("init", "-q", "-b", "main")

    def run(self, *args):
        self.tick += 1
        stamp = f"2026-11-27T09:{self.tick:02d}:00+00:00"
        env = dict(self.env, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
        return git(self.root, *args, env=env)

    def commit_all(self, message):
        self.run("add", "-A")
        self.run("commit", "-q", "-m", message)
        return self.run("rev-parse", "--short", "HEAD").strip()

    def replace(self, rel, old, new):
        p = self.root / rel
        p.write_text(p.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def run_demo(workdir, out=print):
    """Run experiments a-d. Returns {name: result} for the polls the smoke test checks."""
    import shutil
    repo = LabRepo(Path(workdir) / "atlas-config")
    shutil.copytree(LAB_DIR / "starter-repo", repo.root, dirs_exist_ok=True)
    api = "apps/order-tracking/tracking-api.yaml"
    cluster = new_cluster()
    seen, poll = {}, [0]

    def step(name, **flags):
        poll[0] += 1
        res = reconcile_once(repo.root, cluster, **flags)
        out(format_result(res, poll[0]))
        seen[name] = copy.deepcopy(res)
        return res

    def say(text):
        out(f"\n$ {text}")

    def by_hand(key, assignment):
        out(f"\n# {edit_live(cluster, key, assignment)}")

    out("=== a. A new commit converges the cluster")
    say("git commit -m \"Add order-tracking app\"   # " + repo.commit_all("Add order-tracking app"))
    step("a_initial")
    repo.replace(api, "tracking-api:1.4.0", "tracking-api:1.5.0")
    say("git commit -am \"Release tracking-api 1.5.0\"   # " + repo.commit_all("Release tracking-api 1.5.0"))
    step("a_release")
    step("a_steady")

    out("\n=== b. Drift: someone edits the live cluster")
    by_hand("Deployment/order-tracking/tracking-api", "spec.replicas=1")
    by_hand("ConfigMap/order-tracking/tracking-api-config", "data.STATUS_CACHE_TTL_SECONDS=300")
    step("b_report_only", self_heal=False)
    step("b_self_heal", self_heal=True)

    out("\n=== c. A bad commit, a hand fix, and a git revert")
    repo.replace(api, "tracking-api:1.5.0", "tracking-api:1.6.0")
    say("git commit -am \"Release tracking-api 1.6.0\"   # " + repo.commit_all("Release tracking-api 1.6.0"))
    step("c_bad", self_heal=True)
    by_hand("Deployment/order-tracking/tracking-api",
            f"spec.template.spec.containers[0].image={REGISTRY}/tracking-api:1.5.0")
    out(f"  live health now: {cluster['objects']['Deployment/order-tracking/tracking-api']['status']['health']}")
    step("c_hand_fix_undone", self_heal=True)
    repo.run("revert", "--no-edit", "HEAD")
    say("git revert --no-edit HEAD   # " + repo.run("rev-parse", "--short", "HEAD").strip())
    step("c_revert", self_heal=True)
    say("git log --oneline")
    out(repo.run("log", "--oneline").rstrip())

    out("\n=== d. Pruning: a manifest removed from Git")
    repo.run("rm", "-q", "apps/order-tracking/legacy-poller.yaml")
    say("git rm legacy-poller.yaml && git commit -m \"Retire legacy poller\"   # "
        + repo.commit_all("Retire legacy poller"))
    step("d_prune_off", self_heal=True, prune=False)
    step("d_prune_on", self_heal=True, prune=True)

    out("\n=== sync history (newest last)")
    for h in cluster["history"]:
        out(f"  {h['id']:>2}  {h['revision']}  {h['reason']:<9}  {h['subject']}: {'; '.join(h['changes'])}")
    seen["cluster"] = cluster
    return seen


# ----------------------------------------------------------------------------------------- cli

def main(argv=None):
    parser = argparse.ArgumentParser(description="Lab 13 GitOps reconciler (simulated cluster).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init-cluster")
    p.add_argument("--cluster", required=True)
    for name in ("diff", "sync", "watch"):
        p = sub.add_parser(name)
        p.add_argument("--repo", required=True)
        p.add_argument("--cluster", required=True)
        p.add_argument("--path", default=f"apps/{APP}")
        p.add_argument("--self-heal", action="store_true")
        p.add_argument("--prune", action="store_true")
        if name == "watch":
            p.add_argument("--interval", type=float, default=5.0)
            p.add_argument("--iterations", type=int, default=0)
    p = sub.add_parser("edit-live")
    p.add_argument("--cluster", required=True)
    p.add_argument("object", help="Kind/namespace/name, e.g. Deployment/order-tracking/tracking-api")
    p.add_argument("assignment", help="dotted.path=value, e.g. spec.replicas=1")
    p = sub.add_parser("history")
    p.add_argument("--cluster", required=True)
    sub.add_parser("demo")
    args = parser.parse_args(argv)

    if args.cmd == "demo":
        with tempfile.TemporaryDirectory(prefix="lab13-") as tmp:
            run_demo(tmp)
        return 0
    if args.cmd == "init-cluster":
        save_cluster(args.cluster, new_cluster())
        print(f"created {args.cluster} with an empty cluster and {len(DEFAULT_IMAGES)} pushed images")
        return 0
    cluster = load_cluster(args.cluster)
    if args.cmd == "history":
        for h in cluster["history"]:
            print(f"{h['id']:>3}  {h['revision']}  {h['reason']:<9}  {h['subject']}: {'; '.join(h['changes'])}")
        return 0
    if args.cmd == "edit-live":
        print(edit_live(cluster, args.object, args.assignment))
        save_cluster(args.cluster, cluster)
        return 0
    if args.cmd == "diff":
        trial = copy.deepcopy(cluster)
        trial["sync"]["revision"] = None   # pretend a sync would run, but never save it
        res = reconcile_once(args.repo, trial, args.path, args.self_heal, args.prune)
        if res["action"] == "error":
            print(format_result(res))
            return 1
        res.update(action="diff", applied=[], pruned=[], notes=[], previous=cluster["sync"]["revision"],
                   synced_revision=cluster["sync"]["revision"], health=app_health(cluster))
        res["sync_status"] = "OutOfSync" if any(r[1] != "Synced" for r in res["rows"]) else "Synced"
        print(format_result(res))
        return 0
    polls = 1 if args.cmd == "sync" else args.iterations
    n = 0
    try:
        while True:
            n += 1
            cluster = load_cluster(args.cluster)   # re-read: edit-live may have run in between
            res = reconcile_once(args.repo, cluster, args.path, args.self_heal, args.prune)
            save_cluster(args.cluster, cluster)
            print(format_result(res, n), flush=True)
            if polls and n >= polls:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nstopped")
    return 0 if res["action"] != "error" else 1


if __name__ == "__main__":
    sys.exit(main())
