# Lab 13 — sample results

Runs on a laptop (macOS, Python 3.14.7, PyYAML 6.0.3, Git 2.54.0). Every block below is copied from a
real run, trimmed only where marked. The `demo` subcommand commits with a fixed identity ("Lab 13",
empty email) and a fixed clock, so its commit ids are the same on every machine with the same Git
object format; your own commits in Steps 1-5 of the lab will have different ids, and every outcome
will be the same. Paths under the temporary directory are shown as `$LAB13`.

## The whole lab in one run: `demo`

`python3 gitops_reconciler.py demo` creates a repository and a cluster file in a temporary directory,
runs experiments a-d in order on the same repository, prints every poll, and deletes the directory.
Lines starting with `$` are the Git commands it ran (with the short commit id it produced); lines
starting with `#` are hand edits to the live cluster, the simulated `kubectl edit`.

### Experiment a — a new commit converges the cluster

```text
$ python3 gitops_reconciler.py demo
=== a. A new commit converges the cluster

$ git commit -m "Add order-tracking app"   # 4b7e276
--- poll 1  main@4b7e276 "Add order-tracking app"  self-heal=off prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   OutOfSync  Missing
    + (new object)
Deployment order-tracking  legacy-poller         OutOfSync  Missing
    + (new object)
Deployment order-tracking  tracking-api          OutOfSync  Missing
    + (new object)
Deployment order-tracking  webhook-ingestor      OutOfSync  Missing
    + (new object)
sync: new revision 4b7e276 (was none): automated sync
  configmap/tracking-api-config created
  deployment.apps/legacy-poller created
  deployment.apps/tracking-api created
  deployment.apps/webhook-ingestor created
result: Synced to 4b7e276, app health Healthy

$ git commit -am "Release tracking-api 1.5.0"   # 63d1e44
--- poll 2  main@63d1e44 "Release tracking-api 1.5.0"  self-heal=off prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   Synced     Healthy
Deployment order-tracking  legacy-poller         Synced     Healthy
Deployment order-tracking  tracking-api          OutOfSync  Healthy
    ~ spec.template.spec.containers[0].image: tracking-api:1.4.0 -> tracking-api:1.5.0
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: new revision 63d1e44 (was 4b7e276): automated sync
  deployment.apps/tracking-api configured
result: Synced to 63d1e44, app health Healthy
--- poll 3  main@63d1e44 "Release tracking-api 1.5.0"  self-heal=off prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   Synced     Healthy
Deployment order-tracking  legacy-poller         Synced     Healthy
Deployment order-tracking  tracking-api          Synced     Healthy
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: same revision, nothing to apply
result: Synced to 63d1e44, app health Healthy
```

### Experiment b — drift, reported and then self-healed

```text
=== b. Drift: someone edits the live cluster

# edited by hand: Deployment/order-tracking/tracking-api spec.replicas=1

# edited by hand: ConfigMap/order-tracking/tracking-api-config data.STATUS_CACHE_TTL_SECONDS=300
--- poll 4  main@63d1e44 "Release tracking-api 1.5.0"  self-heal=off prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   OutOfSync  Healthy
    ~ data.STATUS_CACHE_TTL_SECONDS: 300 -> 30
Deployment order-tracking  legacy-poller         Synced     Healthy
Deployment order-tracking  tracking-api          OutOfSync  Healthy
    ~ spec.replicas: 1 -> 3
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: same revision, live state drifted: not applied
  note: drift detected, self-heal is off: live changes left in place
result: OutOfSync (last sync 63d1e44), app health Healthy
--- poll 5  main@63d1e44 "Release tracking-api 1.5.0"  self-heal=on prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   OutOfSync  Healthy
    ~ data.STATUS_CACHE_TTL_SECONDS: 300 -> 30
Deployment order-tracking  legacy-poller         Synced     Healthy
Deployment order-tracking  tracking-api          OutOfSync  Healthy
    ~ spec.replicas: 1 -> 3
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: same revision, live state drifted: self-heal sync
  configmap/tracking-api-config configured
  deployment.apps/tracking-api configured
result: Synced to 63d1e44, app health Healthy
```

### Experiment c — a bad commit, a hand fix that does not stick, and a revert

```text
=== c. A bad commit, a hand fix, and a git revert

$ git commit -am "Release tracking-api 1.6.0"   # 84fe51a
--- poll 6  main@84fe51a "Release tracking-api 1.6.0"  self-heal=on prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   Synced     Healthy
Deployment order-tracking  legacy-poller         Synced     Healthy
Deployment order-tracking  tracking-api          OutOfSync  Healthy
    ~ spec.template.spec.containers[0].image: tracking-api:1.5.0 -> tracking-api:1.6.0
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: new revision 84fe51a (was 63d1e44): automated sync
  deployment.apps/tracking-api configured
result: Synced to 84fe51a, app health Degraded

# edited by hand: Deployment/order-tracking/tracking-api spec.template.spec.containers[0].image=tracking-api:1.5.0
  live health now: Healthy
--- poll 7  main@84fe51a "Release tracking-api 1.6.0"  self-heal=on prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   Synced     Healthy
Deployment order-tracking  legacy-poller         Synced     Healthy
Deployment order-tracking  tracking-api          OutOfSync  Healthy
    ~ spec.template.spec.containers[0].image: tracking-api:1.5.0 -> tracking-api:1.6.0
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: same revision, live state drifted: self-heal sync
  deployment.apps/tracking-api configured
result: Synced to 84fe51a, app health Degraded

$ git revert --no-edit HEAD   # 0238f4d
--- poll 8  main@0238f4d "Revert "Release tracking-api 1.6.0""  self-heal=on prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   Synced     Healthy
Deployment order-tracking  legacy-poller         Synced     Healthy
Deployment order-tracking  tracking-api          OutOfSync  Degraded
    ~ spec.template.spec.containers[0].image: tracking-api:1.6.0 -> tracking-api:1.5.0
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: new revision 0238f4d (was 84fe51a): automated sync
  deployment.apps/tracking-api configured
result: Synced to 0238f4d, app health Healthy

$ git log --oneline
0238f4d Revert "Release tracking-api 1.6.0"
84fe51a Release tracking-api 1.6.0
63d1e44 Release tracking-api 1.5.0
4b7e276 Add order-tracking app
```

### Experiment d — pruning

```text
=== d. Pruning: a manifest removed from Git

$ git rm legacy-poller.yaml && git commit -m "Retire legacy poller"   # c1128cb
--- poll 9  main@c1128cb "Retire legacy poller"  self-heal=on prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   Synced     Healthy
Deployment order-tracking  legacy-poller         OutOfSync  Healthy
    - not in Git (requires pruning)
Deployment order-tracking  tracking-api          Synced     Healthy
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: new revision c1128cb (was 0238f4d): automated sync
  note: 1 object(s) require pruning, prune is off: left running
result: OutOfSync (last sync c1128cb), app health Healthy
--- poll 10  main@c1128cb "Retire legacy poller"  self-heal=on prune=on
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   Synced     Healthy
Deployment order-tracking  legacy-poller         OutOfSync  Healthy
    - not in Git (requires pruning)
Deployment order-tracking  tracking-api          Synced     Healthy
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: same revision: pruning objects removed from Git
  deployment.apps/legacy-poller pruned
result: Synced to c1128cb, app health Healthy
```

### Sync history

```text
=== sync history (newest last)
   1  4b7e276  sync       Add order-tracking app: configmap/tracking-api-config created; deployment.apps/legacy-poller created; deployment.apps/tracking-api created; deployment.apps/webhook-ingestor created
   2  63d1e44  sync       Release tracking-api 1.5.0: deployment.apps/tracking-api configured
   3  63d1e44  self-heal  Release tracking-api 1.5.0: configmap/tracking-api-config configured; deployment.apps/tracking-api configured
   4  84fe51a  sync       Release tracking-api 1.6.0: deployment.apps/tracking-api configured
   5  84fe51a  self-heal  Release tracking-api 1.6.0: deployment.apps/tracking-api configured
   6  0238f4d  sync       Revert "Release tracking-api 1.6.0": deployment.apps/tracking-api configured
   7  c1128cb  prune      Retire legacy poller: deployment.apps/legacy-poller pruned
```

## The same flow with the step-by-step commands

These come from manual runs of the lab page's commands, with commits made at the real time, so the
commit ids differ from the demo. Steps 1-3 are one run; Step 5 and the stretch come from two other
runs.

Step 1, `diff` before the first sync (the first `sync` printed the same table as the demo's poll 1,
with this run's commit id), then the uncommitted edit of Step 2 being ignored:

```text
$ python3 gitops_reconciler.py init-cluster --cluster "$LAB13/cluster.json"
created $LAB13/cluster.json with an empty cluster and 4 pushed images
$ python3 gitops_reconciler.py diff --repo "$LAB13/atlas-config" --cluster "$LAB13/cluster.json"
---  main@99973ad "Add order-tracking app"  self-heal=off prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   OutOfSync  Missing
    + (new object)
Deployment order-tracking  legacy-poller         OutOfSync  Missing
    + (new object)
Deployment order-tracking  tracking-api          OutOfSync  Missing
    + (new object)
Deployment order-tracking  webhook-ingestor      OutOfSync  Missing
    + (new object)
sync: diff only, nothing applied
result: OutOfSync (last sync none), app health Missing
$ perl -pi -e 's/tracking-api:1\.4\.0/tracking-api:1.5.0/' "$LAB13/atlas-config/apps/order-tracking/tracking-api.yaml"
$ python3 gitops_reconciler.py sync --repo "$LAB13/atlas-config" --cluster "$LAB13/cluster.json"
--- poll 1  main@99973ad "Add order-tracking app"  self-heal=off prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   Synced     Healthy
Deployment order-tracking  legacy-poller         Synced     Healthy
Deployment order-tracking  tracking-api          Synced     Healthy
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: same revision, nothing to apply
result: Synced to 99973ad, app health Healthy
```

Step 2, `watch` after the commit (two polls, one second apart):

```text
$ python3 gitops_reconciler.py watch --interval 1 --iterations 2 --repo "$LAB13/atlas-config" --cluster "$LAB13/cluster.json"
--- poll 1  main@b27c2e0 "Release tracking-api 1.5.0"  self-heal=off prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   Synced     Healthy
Deployment order-tracking  legacy-poller         Synced     Healthy
Deployment order-tracking  tracking-api          OutOfSync  Healthy
    ~ spec.template.spec.containers[0].image: tracking-api:1.4.0 -> tracking-api:1.5.0
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: new revision b27c2e0 (was 99973ad): automated sync
  deployment.apps/tracking-api configured
result: Synced to b27c2e0, app health Healthy
--- poll 2  main@b27c2e0 "Release tracking-api 1.5.0"  self-heal=off prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   Synced     Healthy
Deployment order-tracking  legacy-poller         Synced     Healthy
Deployment order-tracking  tracking-api          Synced     Healthy
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: same revision, nothing to apply
result: Synced to b27c2e0, app health Healthy
```

Step 3, drift through the command line (the `sync` outputs are trimmed to their last lines):

```text
$ python3 gitops_reconciler.py edit-live --cluster "$LAB13/cluster.json" Deployment/order-tracking/tracking-api spec.replicas=1
edited by hand: Deployment/order-tracking/tracking-api spec.replicas=1
$ python3 gitops_reconciler.py edit-live --cluster "$LAB13/cluster.json" ConfigMap/order-tracking/tracking-api-config data.STATUS_CACHE_TTL_SECONDS=300
edited by hand: ConfigMap/order-tracking/tracking-api-config data.STATUS_CACHE_TTL_SECONDS=300
$ python3 gitops_reconciler.py diff --repo "$LAB13/atlas-config" --cluster "$LAB13/cluster.json"
---  main@b27c2e0 "Release tracking-api 1.5.0"  self-heal=off prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   OutOfSync  Healthy
    ~ data.STATUS_CACHE_TTL_SECONDS: 300 -> 30
Deployment order-tracking  legacy-poller         Synced     Healthy
Deployment order-tracking  tracking-api          OutOfSync  Healthy
    ~ spec.replicas: 1 -> 3
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: diff only, nothing applied
result: OutOfSync (last sync b27c2e0), app health Healthy
$ python3 gitops_reconciler.py sync --repo "$LAB13/atlas-config" --cluster "$LAB13/cluster.json"
[...]
sync: same revision, live state drifted: not applied
  note: drift detected, self-heal is off: live changes left in place
result: OutOfSync (last sync b27c2e0), app health Healthy
$ python3 gitops_reconciler.py sync --self-heal --repo "$LAB13/atlas-config" --cluster "$LAB13/cluster.json"
[...]
sync: same revision, live state drifted: self-heal sync
  configmap/tracking-api-config configured
  deployment.apps/tracking-api configured
result: Synced to b27c2e0, app health Healthy
```

Step 5, pruning through the command line, then the history (a separate run that went straight from
1.4.0 to the bad 1.6.0 commit, so it has five history entries rather than seven):

```text
$ git -C "$LAB13/atlas-config" rm -q apps/order-tracking/legacy-poller.yaml
$ git -C "$LAB13/atlas-config" commit -q -m "Retire legacy poller"
$ python3 gitops_reconciler.py sync --repo "$LAB13/atlas-config" --cluster "$LAB13/cluster.json"
--- poll 1  main@98b875d "Retire legacy poller"  self-heal=off prune=off
KIND       NAMESPACE       NAME                  STATUS     HEALTH
ConfigMap  order-tracking  tracking-api-config   Synced     Healthy
Deployment order-tracking  legacy-poller         OutOfSync  Healthy
    - not in Git (requires pruning)
Deployment order-tracking  tracking-api          Synced     Healthy
Deployment order-tracking  webhook-ingestor      Synced     Healthy
sync: new revision 98b875d (was a26f61f): automated sync
  note: 1 object(s) require pruning, prune is off: left running
result: OutOfSync (last sync 98b875d), app health Healthy
$ python3 gitops_reconciler.py sync --prune --repo "$LAB13/atlas-config" --cluster "$LAB13/cluster.json"
[...]
sync: same revision: pruning objects removed from Git
  deployment.apps/legacy-poller pruned
result: Synced to 98b875d, app health Healthy
$ python3 gitops_reconciler.py history --cluster "$LAB13/cluster.json"
  1  b9fa2b9  sync       Add order-tracking app: configmap/tracking-api-config created; deployment.apps/legacy-poller created; deployment.apps/tracking-api created; deployment.apps/webhook-ingestor created
  2  2a68966  sync       Release tracking-api 1.6.0: deployment.apps/tracking-api configured
  3  2a68966  self-heal  Release tracking-api 1.6.0: deployment.apps/tracking-api configured
  4  a26f61f  sync       Revert "Release tracking-api 1.6.0": deployment.apps/tracking-api configured
  5  98b875d  prune      Retire legacy poller: deployment.apps/legacy-poller pruned
```

Stretch 1, a manifest that does not parse stops the whole sync (`broken.yaml` is a ConfigMap whose
`data` value is `[unclosed`):

```text
$ git -C "$LAB13/atlas-config" add -A
$ git -C "$LAB13/atlas-config" commit -q -m "Add broken config"
$ python3 gitops_reconciler.py sync --repo "$LAB13/atlas-config" --cluster "$LAB13/cluster.json"; echo "exit=$?"
--- poll 1  self-heal=off prune=off
ComparisonError: apps/order-tracking/broken.yaml: invalid YAML (ParserError)
result: sync status Unknown, nothing applied, app health Healthy
exit=1
```

## What the runs show

1. **Only commits count.** Editing the file without committing changed nothing: the reconciler reads
   the commit `main` points to, never the working tree. The commit is the unit of change, review,
   and audit.
2. **Convergence is a diff, not a script.** A new commit produced exactly one field-level change
   (`containers[0].image`) and one `configured` line; the next poll found nothing to do. Running the
   same sync again is harmless, which is what makes a loop safe.
3. **Drift is visible either way; correcting it is a policy.** With self-heal off the reconciler
   reported both hand edits (`spec.replicas: 1 -> 3`, `STATUS_CACHE_TTL_SECONDS: 300 -> 30`) and left
   them; with self-heal on it reverted them in the next poll. Argo CD's documentation describes the
   same split: automated sync acts on new commits, and live-state changes trigger a sync only when
   self-healing is enabled.
4. **Synced is not Healthy.** After the 1.6.0 commit the app was `Synced` (the cluster matches Git)
   and `Degraded` (the image does not exist). The two statuses answer different questions.
5. **The hand fix did not stick.** Setting the image back to 1.5.0 on the cluster made it healthy
   until the next poll, when self-heal restored 1.6.0 from Git and broke it again. The revert commit
   fixed it for good, and `git log` now records the bad release and its reversal.
6. **Pruning is opt-in.** Deleting `legacy-poller.yaml` left the Deployment running and the app
   `OutOfSync` with "requires pruning" until prune was enabled. Argo CD's automated sync also does not
   delete by default, and Flux's Kustomization has a required `prune` field.
7. **A broken commit applies nothing.** One file that does not parse turned the whole sync into a
   `ComparisonError` and left every live object at its previous version.

## Answers to the questions in the lab page

- **Step 1: why `Missing` and not `Degraded`?** The objects do not exist yet; health describes live
  objects, and there are none.
- **Step 2: why did the sync before the commit do nothing?** The reconciler reads the commit on
  `main`, and the edit was not committed. In a real setup the edit would also need to be pushed to
  the remote the controller polls.
- **Step 3: what would on-call see with self-heal off, and why might a team keep it off?** A
  permanently `OutOfSync` app listing the edited fields. Teams keep it off while they still make
  emergency changes by hand, or for fields another controller owns; the price is that Git and the
  cluster disagree until someone acts.
- **Step 4: why is `git revert` better than fixing the cluster?** It works with self-heal instead
  of against it, it leaves an audit record (who reverted what and when), it goes through the same
  review and pipeline as any change, and the repository again describes what runs, so the next
  unrelated commit cannot bring the bad version back.
- **Step 5: why is prune off by default in real tools?** A file deleted by mistake, or a path or
  branch changed in the controller's configuration, would otherwise delete live workloads; pruning
  turns a Git mistake into an outage. Turn it on deliberately, and protect objects such as
  namespaces that hold persistent data.

## Smoke test

```text
$ python -m unittest tests.examples.test_lab13 -v
test_a_new_commit_converges (tests.examples.test_lab13.Lab13Tests.test_a_new_commit_converges) ... ok
test_b_drift_is_reported_without_self_heal_and_reverted_with_it (tests.examples.test_lab13.Lab13Tests.test_b_drift_is_reported_without_self_heal_and_reverted_with_it) ... ok
test_c_bad_commit_is_fixed_by_git_revert_not_by_editing_the_cluster (tests.examples.test_lab13.Lab13Tests.test_c_bad_commit_is_fixed_by_git_revert_not_by_editing_the_cluster) ... ok
test_d_removed_manifest_is_pruned_only_when_prune_is_on (tests.examples.test_lab13.Lab13Tests.test_d_removed_manifest_is_pruned_only_when_prune_is_on) ... ok
test_demo_cli_prints_sync_status_lines (tests.examples.test_lab13.Lab13Tests.test_demo_cli_prints_sync_status_lines) ... ok
test_invalid_manifest_stops_the_whole_sync (tests.examples.test_lab13.Lab13Tests.test_invalid_manifest_stops_the_whole_sync) ... ok
test_sources_compile_and_starter_manifests_validate (tests.examples.test_lab13.Lab13Tests.test_sources_compile_and_starter_manifests_validate) ... ok

----------------------------------------------------------------------
Ran 7 tests in 5.096s

OK
```
