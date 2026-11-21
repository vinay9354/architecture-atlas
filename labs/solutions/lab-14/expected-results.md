# Lab 14 — sample results

Runs on a laptop (macOS, Python 3.14.7) with the default seed 14. The simulator is deterministic: the
same command gives the same output on any machine with Python 3.10 or newer. The seed only chooses the
clients' ephemeral source ports (from 32768-60999); outcomes never depend on it. Every block below is
copied from a real run, trimmed only of trailing blank lines.

## Step 1 — Experiment a: the flat network

```text
$ python3 segmentation_sim.py flat --rules
=== a. Flat network: every SG allows all TCP from 10.10.0.0/16, every NACL allows all

-- security groups: flat, network ACLs: default
  security groups (flat):
    sg-web     in:  allow tcp all-ports from 10.10.0.0/16
    sg-app     in:  allow tcp all-ports from 10.10.0.0/16
    sg-ingest  in:  allow tcp all-ports from 10.10.0.0/16
    sg-db      in:  allow tcp all-ports from 10.10.0.0/16
  network ACLs (default):
    nacl-public in  100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-public out 100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-app    in  100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-app    out 100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-data   in  100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-data   out 100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
web-1 -> db-1:5432     CONNECTED
    eni-db-1     10.10.0.10:36268 -> 10.10.32.10:5432 tcp ACCEPT by=sg-web out#1 > nacl-public out 100 > nacl-data in 100 > sg-db in#1
    eni-web-1    10.10.32.10:5432 -> 10.10.0.10:36268 tcp ACCEPT by=sg-db tracked > nacl-data out 100 > nacl-public in 100 > sg-web tracked
app-1 -> db-1:5432     CONNECTED
    eni-db-1     10.10.16.10:52949 -> 10.10.32.10:5432 tcp ACCEPT by=sg-app out#1 > nacl-app out 100 > nacl-data in 100 > sg-db in#1
    eni-app-1    10.10.32.10:5432 -> 10.10.16.10:52949 tcp ACCEPT by=sg-db tracked > nacl-data out 100 > nacl-app in 100 > sg-app tracked
```

## Step 2 — Experiment b: segmented with security groups

```text
$ python3 segmentation_sim.py segmented
=== b. Segmented with security groups that reference each other (NACLs still allow all)

-- security groups: group, network ACLs: default
web-1 -> db-1:5432     TIMEOUT: request dropped by sg-db in (no allow rule matched)
    eni-db-1     10.10.0.10:36268 -> 10.10.32.10:5432 tcp REJECT by=sg-db in (no allow rule matched)
web-1 -> app-1:8080    CONNECTED
    eni-app-1    10.10.0.10:52949 -> 10.10.16.10:8080 tcp ACCEPT by=sg-web out#1 > nacl-public out 100 > nacl-app in 100 > sg-app in#1
    eni-web-1    10.10.16.10:8080 -> 10.10.0.10:52949 tcp ACCEPT by=sg-app tracked > nacl-app out 100 > nacl-public in 100 > sg-web tracked
app-1 -> db-1:5432     CONNECTED
    eni-db-1     10.10.16.10:55790 -> 10.10.32.10:5432 tcp ACCEPT by=sg-app out#1 > nacl-app out 100 > nacl-data in 100 > sg-db in#1
    eni-app-1    10.10.32.10:5432 -> 10.10.16.10:55790 tcp ACCEPT by=sg-db tracked > nacl-data out 100 > nacl-app in 100 > sg-app tracked
ingest-1 -> db-1:5432  TIMEOUT: request dropped by sg-db in (no allow rule matched)
    eni-db-1     10.10.16.20:57514 -> 10.10.32.10:5432 tcp REJECT by=sg-db in (no allow rule matched)
```

## Step 3 — Experiment c: a NACL that forgets the ephemeral ports, then the fix

```text
$ python3 segmentation_sim.py nacl --rules
=== c. A data-subnet NACL whose outbound rule forgets the ephemeral ports, then the fix

-- security groups: group, network ACLs: data-broken
  security groups (group):
    sg-web     in:  allow tcp 443 from 0.0.0.0/0
    sg-app     in:  allow tcp 8080 from sg-web
    sg-ingest  in:  allow tcp 8080 from sg-web
    sg-db      in:  allow tcp 5432 from sg-app
  network ACLs (data-broken):
    nacl-public in  100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-public out 100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-app    in  100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-app    out 100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-data   in  50 deny all 10.10.0.0/22 | 100 allow tcp 5432 10.10.16.0/20 | * deny all 0.0.0.0/0
    nacl-data   out 100 allow tcp 5432 10.10.16.0/20 | * deny all 0.0.0.0/0
app-1 -> db-1:5432     TIMEOUT: response dropped by nacl-data out * (implicit deny)
    eni-db-1     10.10.16.10:36268 -> 10.10.32.10:5432 tcp ACCEPT by=sg-app out#1 > nacl-app out 100 > nacl-data in 100 > sg-db in#1
    eni-db-1     10.10.32.10:5432 -> 10.10.16.10:36268 tcp REJECT by=nacl-data out * (implicit deny)
web-1 -> db-1:5432     TIMEOUT: request dropped by nacl-data in 50 deny
    eni-db-1     10.10.0.10:52949 -> 10.10.32.10:5432 tcp REJECT by=nacl-data in 50 deny

-- security groups: group, network ACLs: data-fixed
  security groups (group):
    sg-web     in:  allow tcp 443 from 0.0.0.0/0
    sg-app     in:  allow tcp 8080 from sg-web
    sg-ingest  in:  allow tcp 8080 from sg-web
    sg-db      in:  allow tcp 5432 from sg-app
  network ACLs (data-fixed):
    nacl-public in  100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-public out 100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-app    in  100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-app    out 100 allow all 0.0.0.0/0 | * deny all 0.0.0.0/0
    nacl-data   in  50 deny all 10.10.0.0/22 | 100 allow tcp 5432 10.10.16.0/20 | * deny all 0.0.0.0/0
    nacl-data   out 100 allow tcp 1024-65535 10.10.16.0/20 | * deny all 0.0.0.0/0
app-1 -> db-1:5432     CONNECTED
    eni-db-1     10.10.16.10:36268 -> 10.10.32.10:5432 tcp ACCEPT by=sg-app out#1 > nacl-app out 100 > nacl-data in 100 > sg-db in#1
    eni-app-1    10.10.32.10:5432 -> 10.10.16.10:36268 tcp ACCEPT by=sg-db tracked > nacl-data out 100 > nacl-app in 100 > sg-app tracked
web-1 -> db-1:5432     TIMEOUT: request dropped by nacl-data in 50 deny
    eni-db-1     10.10.0.10:52949 -> 10.10.32.10:5432 tcp REJECT by=nacl-data in 50 deny
```

## Step 4 — Experiment d: CIDR versus group references when the tier scales

```text
$ python3 segmentation_sim.py scale
=== d. sg-db by CIDR versus by group when the app tier scales into 10.10.48.0/20

-- security groups: cidr, network ACLs: default
app-1 -> db-1:5432     CONNECTED
    eni-db-1     10.10.16.10:36268 -> 10.10.32.10:5432 tcp ACCEPT by=sg-app out#1 > nacl-app out 100 > nacl-data in 100 > sg-db in#1
    eni-app-1    10.10.32.10:5432 -> 10.10.16.10:36268 tcp ACCEPT by=sg-db tracked > nacl-data out 100 > nacl-app in 100 > sg-app tracked
app-2 -> db-1:5432     TIMEOUT: request dropped by sg-db in (no allow rule matched)
    eni-db-1     10.10.48.10:52949 -> 10.10.32.10:5432 tcp REJECT by=sg-db in (no allow rule matched)
ingest-1 -> db-1:5432  CONNECTED
    eni-db-1     10.10.16.20:55790 -> 10.10.32.10:5432 tcp ACCEPT by=sg-ingest out#1 > nacl-app out 100 > nacl-data in 100 > sg-db in#1
    eni-ingest-1 10.10.32.10:5432 -> 10.10.16.20:55790 tcp ACCEPT by=sg-db tracked > nacl-data out 100 > nacl-app in 100 > sg-ingest tracked

-- security groups: group, network ACLs: default
app-1 -> db-1:5432     CONNECTED
    eni-db-1     10.10.16.10:36268 -> 10.10.32.10:5432 tcp ACCEPT by=sg-app out#1 > nacl-app out 100 > nacl-data in 100 > sg-db in#1
    eni-app-1    10.10.32.10:5432 -> 10.10.16.10:36268 tcp ACCEPT by=sg-db tracked > nacl-data out 100 > nacl-app in 100 > sg-app tracked
app-2 -> db-1:5432     CONNECTED
    eni-db-1     10.10.48.10:52949 -> 10.10.32.10:5432 tcp ACCEPT by=sg-app out#1 > nacl-app out 100 > nacl-data in 100 > sg-db in#1
    eni-app-2    10.10.32.10:5432 -> 10.10.48.10:52949 tcp ACCEPT by=sg-db tracked > nacl-data out 100 > nacl-app in 100 > sg-app tracked
ingest-1 -> db-1:5432  TIMEOUT: request dropped by sg-db in (no allow rule matched)
    eni-db-1     10.10.16.20:55790 -> 10.10.32.10:5432 tcp REJECT by=sg-db in (no allow rule matched)

-- security groups: group, network ACLs: data-fixed
app-1 -> db-1:5432     CONNECTED
    eni-db-1     10.10.16.10:36268 -> 10.10.32.10:5432 tcp ACCEPT by=sg-app out#1 > nacl-app out 100 > nacl-data in 100 > sg-db in#1
    eni-app-1    10.10.32.10:5432 -> 10.10.16.10:36268 tcp ACCEPT by=sg-db tracked > nacl-data out 100 > nacl-app in 100 > sg-app tracked
app-2 -> db-1:5432     TIMEOUT: request dropped by nacl-data in * (implicit deny)
    eni-db-1     10.10.48.10:52949 -> 10.10.32.10:5432 tcp REJECT by=nacl-data in * (implicit deny)
ingest-1 -> db-1:5432  TIMEOUT: request dropped by sg-db in (no allow rule matched)
    eni-db-1     10.10.16.20:55790 -> 10.10.32.10:5432 tcp REJECT by=sg-db in (no allow rule matched)
```

## Step 5 — A different seed (summary lines only)

```text
$ python3 segmentation_sim.py all --seed 1 | grep -E "^[a-z=]|^$"
=== a. Flat network: every SG allows all TCP from 10.10.0.0/16, every NACL allows all

web-1 -> db-1:5432     CONNECTED
app-1 -> db-1:5432     CONNECTED

=== b. Segmented with security groups that reference each other (NACLs still allow all)

web-1 -> db-1:5432     TIMEOUT: request dropped by sg-db in (no allow rule matched)
web-1 -> app-1:8080    CONNECTED
app-1 -> db-1:5432     CONNECTED
ingest-1 -> db-1:5432  TIMEOUT: request dropped by sg-db in (no allow rule matched)

=== c. A data-subnet NACL whose outbound rule forgets the ephemeral ports, then the fix

app-1 -> db-1:5432     TIMEOUT: response dropped by nacl-data out * (implicit deny)
web-1 -> db-1:5432     TIMEOUT: request dropped by nacl-data in 50 deny

app-1 -> db-1:5432     CONNECTED
web-1 -> db-1:5432     TIMEOUT: request dropped by nacl-data in 50 deny

=== d. sg-db by CIDR versus by group when the app tier scales into 10.10.48.0/20

app-1 -> db-1:5432     CONNECTED
app-2 -> db-1:5432     TIMEOUT: request dropped by sg-db in (no allow rule matched)
ingest-1 -> db-1:5432  CONNECTED

app-1 -> db-1:5432     CONNECTED
app-2 -> db-1:5432     CONNECTED
ingest-1 -> db-1:5432  TIMEOUT: request dropped by sg-db in (no allow rule matched)

app-1 -> db-1:5432     CONNECTED
app-2 -> db-1:5432     TIMEOUT: request dropped by nacl-data in * (implicit deny)
ingest-1 -> db-1:5432  TIMEOUT: request dropped by sg-db in (no allow rule matched)
```

Every outcome matches the default seed; only the port numbers in the (omitted) flow-log lines differ.

## What to notice

1. **Flat means the first foothold wins.** In experiment a, `web-1`, the internet-facing host an
   attacker reaches first, connects to the database exactly as the Tracking API does. Nothing in the
   network distinguishes them.
2. **Group references express intent.** In experiment b, `sg-db` allows 5432 only from interfaces
   carrying `sg-app`. `web-1` is rejected at `sg-db in`, logged on `eni-db-1`; so is `ingest-1`,
   although it sits in the same subnet as `app-1`: the rule is about what a host is, not where it is.
   This is STRIDE finding T6 from the threat modeling page, enforced in the network.
3. **Stateful means no return rules.** In every accepted flow the response passes `sg-db tracked` and
   `sg-app tracked`: the security groups remember the connection, so neither needs an outbound or
   return rule.
4. **Stateless means the reply is a stranger.** In the `data-broken` phase the request passes every
   check, the database receives it and answers, and the reply to port 36268 matches no outbound rule
   (only 5432 is allowed), so the implicit deny drops it. The client sees a timeout, the same symptom
   as a dropped request. The flow log on `eni-db-1` tells the two apart: ACCEPT for the request, then
   REJECT for the reply. That pair, on the server's interface, is the signature of a missing
   ephemeral-port rule.
5. **Explicit deny as a guard rail.** NACL rule 50 rejects anything from the public subnet before any
   security group is consulted, in both phases. If someone later loosens `sg-db`, the public tier
   still cannot reach the data tier: defense in depth with an independent second layer.
6. **The fix is a port range, not a port.** `data-fixed` allows outbound TCP 1024-65535 to the app
   subnet, the range AWS suggests to cover common clients. It also lets the database start connections
   to high ports on the app subnet, which is the price of stateless filtering.
7. **CIDR rules are wrong in both directions.** With `sg-db` trusting `10.10.16.0/20`, the scaled-out
   `app-2` in `10.10.48.0/20` is rejected (a false negative that looks like an outage after a scaling
   event) and `ingest-1` is admitted (a false positive that nobody notices). The group rule reverses
   both.
8. **NACLs only know addresses.** In the last phase the group rule admits `app-2`, but the data
   subnet's NACL allows 5432 only from `10.10.16.0/20`, so the request dies at `nacl-data in *`. When a
   tier gains a subnet, every CIDR-based layer must be updated, or the address plan must keep the tier
   under one summary prefix.

## Answers to the questions in the lab page

- **Which rule stopped `web-1 -> db-1:5432` in Step 2, and where was it logged?** `sg-db in`, no allow
  rule matched; logged on `eni-db-1`, the database's interface, because that is where the inbound
  security group is evaluated.
- **Why is `ingest-1` rejected though it shares `app-1`'s subnet?** Its interface carries `sg-ingest`,
  not `sg-app`, and `sg-db` references the group, not the subnet.
- **Why does `sg-db` need no outbound rule for the reply?** Security groups are stateful: the reply
  belongs to a connection the inbound rule already allowed.
- **What does the ACCEPT-then-REJECT pair tell on-call?** That the request reached the server and the
  reply was blocked leaving the server's subnet: a return-path rule problem, not a server, routing, or
  security-group problem. The client's "timed out" cannot tell these apart.
- **The 3 × 3 table for Step 4:**

| sg-db rule and NACL | app-1 (10.10.16.0/20) | app-2 (10.10.48.0/20) | ingest-1 (10.10.16.0/20) |
|---|---|---|---|
| CIDR `10.10.16.0/20`, NACLs allow all | CONNECTED | TIMEOUT at `sg-db in` | CONNECTED (should not be) |
| Group `sg-app`, NACLs allow all | CONNECTED | CONNECTED | TIMEOUT at `sg-db in` |
| Group `sg-app`, data NACL from Step 3 | CONNECTED | TIMEOUT at `nacl-data in *` | TIMEOUT at `sg-db in` |

- **Stretch 1 (deny renumbered to 150 after an allow-all at 100):** the deny never fires, because the
  first matching rule wins and rule 100 matches first. Checked by evaluating the modified ACL in a
  Python session: `nacl-data in 100` allowed `web-1`'s request, and only `sg-db in` then stopped it.
  Explicit denies must have lower numbers than the allows they are meant to override.
