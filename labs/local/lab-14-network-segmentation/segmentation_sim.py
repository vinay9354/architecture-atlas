#!/usr/bin/env python3
"""Lab 14 network segmentation simulator: security groups, network ACLs, and flow logs.

Standard library only. No packets are sent: the script models one availability zone of AtlasMart's
production virtual network (zone a of the address plan) and evaluates, rule by rule, whether a TCP
connection between two hosts would be established.

The model, loosely shaped like a cloud virtual network:
- Subnets (zone a): public 10.10.0.0/22, private-app 10.10.16.0/20, private-data 10.10.32.0/22, and
  a second application subnet 10.10.48.0/20 taken from the zone's reserved space for experiment d.
- Security groups (SGs) are attached to a host's network interface. They hold allow rules only, and
  are STATEFUL: once a request is allowed, its return traffic is allowed automatically. A rule's
  source is either a CIDR block or another security group (meaning "any interface carrying that
  group", wherever its address is).
- Network ACLs (NACLs) are attached to a subnet. They hold numbered allow and deny rules, evaluated in
  ascending order until the first match, with a final implicit deny (shown as rule `*`). They are
  STATELESS: the response is a separate packet that must be allowed on its own, and its destination
  port is the client's ephemeral port. NACLs are checked only when a packet crosses a subnet boundary.
- The client picks an ephemeral source port from 32768-60999 (the Linux default range), seeded.
- Every packet produces one flow-log-style line on the interface where its fate was decided. Real
  provider flow logs record ACCEPT or REJECT per flow but not which rule decided; the `by=` column
  here is a teaching aid.

Run:  python3 segmentation_sim.py flat         # experiment a
      python3 segmentation_sim.py segmented    # experiment b
      python3 segmentation_sim.py nacl         # experiment c
      python3 segmentation_sim.py scale        # experiment d
      python3 segmentation_sim.py all --rules  # everything, with the rule tables printed
"""

import argparse
import ipaddress
import json
import random
import sys
from dataclasses import dataclass, field

EPHEMERAL_RANGE = (32768, 60999)   # Linux default net.ipv4.ip_local_port_range
ALL_PORTS = (0, 65535)
IMPLICIT_DENY = 32767              # the "*" rule, evaluated after every numbered rule


# --------------------------------------------------------------------------------------- rules

@dataclass(frozen=True)
class SgRule:
    """One security group allow rule. `peer` is a CIDR block or a security group id (sg-...)."""
    proto: str
    ports: tuple[int, int]
    peer: str

    def describe(self) -> str:
        return f"allow {fmt_traffic(self.proto, self.ports)} from {self.peer}"


@dataclass
class SecurityGroup:
    sg_id: str
    ingress: list[SgRule]
    egress: list[SgRule] = field(default_factory=lambda: [SgRule("all", ALL_PORTS, "0.0.0.0/0")])


@dataclass(frozen=True)
class NaclRule:
    number: int
    action: str            # "allow" or "deny"
    proto: str
    ports: tuple[int, int]
    cidr: str

    def describe(self) -> str:
        num = "*" if self.number == IMPLICIT_DENY else str(self.number)
        return f"{num} {self.action} {fmt_traffic(self.proto, self.ports)} {self.cidr}"


@dataclass
class Nacl:
    nacl_id: str
    inbound: list[NaclRule]
    outbound: list[NaclRule]

    def evaluate(self, direction: str, proto: str, dport: int, peer_ip: str) -> tuple[bool, str]:
        """First matching rule in number order wins; nothing matched means the implicit deny."""
        rules = self.inbound if direction == "in" else self.outbound
        for rule in sorted(rules, key=lambda r: r.number):
            if proto_matches(rule.proto, proto) and in_range(dport, rule.ports) and ip_in(peer_ip, rule.cidr):
                suffix = "" if rule.action == "allow" else " deny"
                return rule.action == "allow", f"{self.nacl_id} {direction} {rule.number}{suffix}"
        return False, f"{self.nacl_id} {direction} * (implicit deny)"


@dataclass(frozen=True)
class Subnet:
    name: str
    cidr: str
    nacl_id: str


@dataclass(frozen=True)
class Host:
    name: str
    ip: str
    subnet: str
    sgs: tuple[str, ...]
    role: str


def fmt_ports(ports: tuple[int, int]) -> str:
    lo, hi = ports
    if (lo, hi) == ALL_PORTS:
        return "all-ports"
    return str(lo) if lo == hi else f"{lo}-{hi}"


def fmt_traffic(proto: str, ports: tuple[int, int]) -> str:
    return "all" if proto == "all" else f"{proto} {fmt_ports(ports)}"


def proto_matches(rule_proto: str, proto: str) -> bool:
    return rule_proto in ("all", proto)


def in_range(port: int, ports: tuple[int, int]) -> bool:
    return ports[0] <= port <= ports[1]


def ip_in(ip: str, cidr: str) -> bool:
    return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr)


# ------------------------------------------------------------------------------------- network

SUBNETS = [
    Subnet("public-a", "10.10.0.0/22", "nacl-public"),
    Subnet("app-a", "10.10.16.0/20", "nacl-app"),
    Subnet("data-a", "10.10.32.0/22", "nacl-data"),
    Subnet("app-a2", "10.10.48.0/20", "nacl-app"),   # from zone a's reserved space (experiment d)
]

HOSTS = [
    Host("web-1", "10.10.0.10", "public-a", ("sg-web",), "internet-facing web/proxy host"),
    Host("app-1", "10.10.16.10", "app-a", ("sg-app",), "Tracking API instance"),
    Host("ingest-1", "10.10.16.20", "app-a", ("sg-ingest",), "Webhook Ingestor (never needs the database)"),
    Host("app-2", "10.10.48.10", "app-a2", ("sg-app",), "Tracking API instance after scale-out"),
    Host("db-1", "10.10.32.10", "data-a", ("sg-db",), "PostgreSQL primary (port 5432)"),
]


def allow_all_nacl(nacl_id: str) -> Nacl:
    rule = NaclRule(100, "allow", "all", ALL_PORTS, "0.0.0.0/0")
    return Nacl(nacl_id, [rule], [rule])


def security_groups(mode: str) -> dict[str, SecurityGroup]:
    """flat: everything open inside the VPC. group: SG-to-SG references. cidr: sg-db trusts a subnet."""
    if mode == "flat":
        open_rule = [SgRule("tcp", ALL_PORTS, "10.10.0.0/16")]
        return {sg: SecurityGroup(sg, list(open_rule)) for sg in ("sg-web", "sg-app", "sg-ingest", "sg-db")}
    db_peer = "sg-app" if mode == "group" else "10.10.16.0/20"
    return {
        "sg-web": SecurityGroup("sg-web", [SgRule("tcp", (443, 443), "0.0.0.0/0")]),
        "sg-app": SecurityGroup("sg-app", [SgRule("tcp", (8080, 8080), "sg-web")]),
        "sg-ingest": SecurityGroup("sg-ingest", [SgRule("tcp", (8080, 8080), "sg-web")]),
        "sg-db": SecurityGroup("sg-db", [SgRule("tcp", (5432, 5432), db_peer)]),
    }


def network_acls(mode: str) -> dict[str, Nacl]:
    """default: allow all everywhere. data-broken / data-fixed: a restrictive NACL on the data subnet."""
    nacls = {n: allow_all_nacl(n) for n in ("nacl-public", "nacl-app", "nacl-data")}
    if mode == "default":
        return nacls
    inbound = [
        NaclRule(50, "deny", "all", ALL_PORTS, "10.10.0.0/22"),          # public tier never talks to data
        NaclRule(100, "allow", "tcp", (5432, 5432), "10.10.16.0/20"),    # app subnet to PostgreSQL
    ]
    if mode == "data-broken":
        # The classic mistake: the outbound rule mirrors the inbound one, so responses (which go TO the
        # client's ephemeral port, not to 5432) match nothing and hit the implicit deny.
        outbound = [NaclRule(100, "allow", "tcp", (5432, 5432), "10.10.16.0/20")]
    elif mode == "data-fixed":
        outbound = [NaclRule(100, "allow", "tcp", (1024, 65535), "10.10.16.0/20")]
    else:
        raise ValueError(f"unknown NACL mode {mode!r}")
    nacls["nacl-data"] = Nacl("nacl-data", inbound, outbound)
    return nacls


class Network:
    def __init__(self, sg_mode: str, nacl_mode: str, seed: int = 14):
        self.sg_mode, self.nacl_mode = sg_mode, nacl_mode
        self.subnets = {s.name: s for s in SUBNETS}
        self.hosts = {h.name: h for h in HOSTS}
        self.by_ip = {h.ip: h for h in HOSTS}
        self.sgs = security_groups(sg_mode)
        self.nacls = network_acls(nacl_mode)
        self.rng = random.Random(seed)
        for s in SUBNETS:   # sanity: every host address lies inside its subnet
            for h in HOSTS:
                if h.subnet == s.name:
                    assert ip_in(h.ip, s.cidr), (h, s)

    def peer_matches(self, peer: str, ip: str) -> bool:
        if peer.startswith("sg-"):
            host = self.by_ip.get(ip)
            return host is not None and peer in host.sgs
        return ip_in(ip, peer)

    def sg_check(self, host: Host, direction: str, proto: str, port: int, peer_ip: str) -> tuple[bool, str]:
        """Any attached SG with a matching allow rule admits the packet (SG rules are a union)."""
        for sg_id in host.sgs:
            rules = self.sgs[sg_id].ingress if direction == "in" else self.sgs[sg_id].egress
            for i, rule in enumerate(rules, 1):
                if proto_matches(rule.proto, proto) and in_range(port, rule.ports) and self.peer_matches(rule.peer, peer_ip):
                    return True, f"{sg_id} {direction}#{i}"
        return False, f"{'/'.join(host.sgs)} {direction} (no allow rule matched)"

    def nacl_of(self, host: Host) -> Nacl:
        return self.nacls[self.subnets[host.subnet].nacl_id]

    def connect(self, src_name: str, dst_name: str, port: int, proto: str = "tcp") -> dict:
        """Evaluate one TCP connection attempt: the request packet, then (if delivered) the response."""
        src, dst = self.hosts[src_name], self.hosts[dst_name]
        sport = self.rng.randint(*EPHEMERAL_RANGE)
        crosses = src.subnet != dst.subnet
        logs: list[str] = []

        # Request: client SG egress -> client subnet NACL out -> server subnet NACL in -> server SG ingress.
        req_path: list[str] = []
        steps = [("src", lambda: self.sg_check(src, "out", proto, port, dst.ip))]
        if crosses:
            steps.append(("src", lambda: self.nacl_of(src).evaluate("out", proto, port, dst.ip)))
            steps.append(("dst", lambda: self.nacl_of(dst).evaluate("in", proto, port, src.ip)))
        steps.append(("dst", lambda: self.sg_check(dst, "in", proto, port, src.ip)))
        for side, check in steps:
            ok, label = check()
            req_path.append(label)
            if not ok:
                eni = src if side == "src" else dst
                logs.append(flow_line(eni, src.ip, sport, dst.ip, port, proto, "REJECT", req_path))
                return result(self, src, dst, port, "TIMEOUT", "request", label, logs)
        logs.append(flow_line(dst, src.ip, sport, dst.ip, port, proto, "ACCEPT", req_path))

        # Response: server SG (tracked) -> server subnet NACL out -> client subnet NACL in -> client SG (tracked).
        resp_path = [f"{'/'.join(dst.sgs)} tracked"]
        steps = []
        if crosses:
            steps.append(("dst", lambda: self.nacl_of(dst).evaluate("out", proto, sport, src.ip)))
            steps.append(("src", lambda: self.nacl_of(src).evaluate("in", proto, sport, dst.ip)))
        for side, check in steps:
            ok, label = check()
            resp_path.append(label)
            if not ok:
                eni = src if side == "src" else dst
                logs.append(flow_line(eni, dst.ip, port, src.ip, sport, proto, "REJECT", resp_path))
                return result(self, src, dst, port, "TIMEOUT", "response", label, logs)
        resp_path.append(f"{'/'.join(src.sgs)} tracked")
        logs.append(flow_line(src, dst.ip, port, src.ip, sport, proto, "ACCEPT", resp_path))
        return result(self, src, dst, port, "CONNECTED", "", "", logs)


def flow_line(eni: Host, sip: str, sport: int, dip: str, dport: int, proto: str, action: str, path: list[str]) -> str:
    decided = path[-1] if action == "REJECT" else " > ".join(path)
    return f"eni-{eni.name:<8} {sip}:{sport} -> {dip}:{dport} {proto} {action} by={decided}"


def result(net: Network, src: Host, dst: Host, port: int, outcome: str, dropped: str, decided_by: str, logs: list[str]) -> dict:
    return {
        "sg_mode": net.sg_mode, "nacl_mode": net.nacl_mode,
        "flow": f"{src.name} -> {dst.name}:{port}", "src": src.name, "dst": dst.name, "port": port,
        "outcome": outcome, "dropped": dropped, "decided_by": decided_by, "flow_log": logs,
    }


# ---------------------------------------------------------------------------------- experiments

EXPERIMENTS = {
    "flat": {
        "title": "a. Flat network: every SG allows all TCP from 10.10.0.0/16, every NACL allows all",
        "phases": [("flat", "default", [("web-1", "db-1", 5432), ("app-1", "db-1", 5432)])],
    },
    "segmented": {
        "title": "b. Segmented with security groups that reference each other (NACLs still allow all)",
        "phases": [("group", "default", [("web-1", "db-1", 5432), ("web-1", "app-1", 8080),
                                         ("app-1", "db-1", 5432), ("ingest-1", "db-1", 5432)])],
    },
    "nacl": {
        "title": "c. A data-subnet NACL whose outbound rule forgets the ephemeral ports, then the fix",
        "phases": [("group", "data-broken", [("app-1", "db-1", 5432), ("web-1", "db-1", 5432)]),
                   ("group", "data-fixed", [("app-1", "db-1", 5432), ("web-1", "db-1", 5432)])],
    },
    "scale": {
        "title": "d. sg-db by CIDR versus by group when the app tier scales into 10.10.48.0/20",
        "phases": [("cidr", "default", [("app-1", "db-1", 5432), ("app-2", "db-1", 5432), ("ingest-1", "db-1", 5432)]),
                   ("group", "default", [("app-1", "db-1", 5432), ("app-2", "db-1", 5432), ("ingest-1", "db-1", 5432)]),
                   ("group", "data-fixed", [("app-1", "db-1", 5432), ("app-2", "db-1", 5432), ("ingest-1", "db-1", 5432)])],
    },
}


def run_experiment(name: str, seed: int = 14) -> list[dict]:
    results = []
    for sg_mode, nacl_mode, flows in EXPERIMENTS[name]["phases"]:
        net = Network(sg_mode, nacl_mode, seed)
        results.extend(net.connect(s, d, p) for s, d, p in flows)
    return results


def print_rules(sg_mode: str, nacl_mode: str) -> None:
    net = Network(sg_mode, nacl_mode)
    print(f"  security groups ({sg_mode}):")
    for sg in net.sgs.values():
        print(f"    {sg.sg_id:<10} in:  " + "; ".join(r.describe() for r in sg.ingress))
    print(f"  network ACLs ({nacl_mode}):")
    for nacl in net.nacls.values():
        for direction, rules in (("in", nacl.inbound), ("out", nacl.outbound)):
            shown = sorted(rules, key=lambda r: r.number) + [NaclRule(IMPLICIT_DENY, "deny", "all", ALL_PORTS, "0.0.0.0/0")]
            print(f"    {nacl.nacl_id:<11} {direction:<3} " + " | ".join(r.describe() for r in shown))


def describe(res: dict) -> str:
    if res["outcome"] == "CONNECTED":
        return "CONNECTED"
    return f"TIMEOUT: {res['dropped']} dropped by {res['decided_by']}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("experiment", choices=[*EXPERIMENTS, "all"], help="which experiment to run")
    ap.add_argument("--rules", action="store_true", help="print the SG and NACL rules of each phase")
    ap.add_argument("--seed", type=int, default=14, help="seed for the clients' ephemeral ports")
    ap.add_argument("--json", metavar="FILE", help="also write every result to FILE as JSON")
    args = ap.parse_args(argv)

    names = list(EXPERIMENTS) if args.experiment == "all" else [args.experiment]
    everything: dict[str, list[dict]] = {}
    for name in names:
        print(f"=== {EXPERIMENTS[name]['title']}")
        results = run_experiment(name, args.seed)
        everything[name] = results
        phase = None
        for res in results:
            if (res["sg_mode"], res["nacl_mode"]) != phase:
                phase = (res["sg_mode"], res["nacl_mode"])
                print(f"\n-- security groups: {phase[0]}, network ACLs: {phase[1]}")
                if args.rules:
                    print_rules(*phase)
            print(f"{res['flow']:<22} {describe(res)}")
            for line in res["flow_log"]:
                print(f"    {line}")
        print()
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(everything, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
