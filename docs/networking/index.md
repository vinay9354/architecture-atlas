---
title: Networking and hybrid connectivity
description: "Every distributed system is a network application. Architects who cannot reason about CIDR blocks,."
---

# Networking and hybrid connectivity

Every distributed system is a network application. Architects who cannot reason about CIDR blocks,
routing, DNS, TLS, load balancing, and private connectivity design systems that fail in production for
reasons they cannot diagnose. This section builds networking knowledge from the OSI and TCP/IP models to
hybrid connectivity between data centers and clouds.

## What you will learn here

- Plan IP address space, subnets, and route tables for a multi-environment cloud network
- Explain TCP, UDP, QUIC, HTTP/1.1-3, and TLS at the level that affects application design
- Design segmentation, firewalls, load balancing (L4/L7), and traffic flows with trust boundaries
- Connect on-premises and cloud networks with VPN and dedicated links, including DNS and failover

**Prerequisites:** None beyond basic Linux familiarity.

## Topics in this section

Every topic from the master curriculum that belongs to this section is listed below with its
status. A link means the page exists; `planned:` shows where it will be created. Status meanings
are explained in the [coverage matrix](../appendices/coverage-matrix.md).

<!-- coverage:start -->
| ID | Topic | Status | Page |
|---|---|---|---|
| **D09** | **Networking and hybrid connectivity** | | |
| D09-T01 | Networking fundamentals: IP, CIDR, routing, and DNS | :material-circle-slice-5: Draft | [networking-fundamentals-ip-cidr-routing-and-dns](networking-fundamentals-ip-cidr-routing-and-dns.md) |
| D09-T02 | Transport and application protocols | :material-circle-slice-5: Draft | [transport-and-application-protocols](transport-and-application-protocols.md) |
| D09-T03 | Network security, load balancing, and traffic flow | :material-circle-outline: Planned | planned: `networking/network-security-load-balancing-and-traffic-flow.md` |
| D09-T04 | Hybrid connectivity and VPNs | :material-circle-outline: Planned | planned: `networking/hybrid-connectivity-and-vpns.md` |
<!-- coverage:end -->

## How to continue

- Follow the [learning paths](../start-here/learning-path.md) for a recommended order.
- Look up unfamiliar terms in the [glossary](../start-here/glossary.md).
- Want to write one of the planned pages? See the
  [contribution guide](https://github.com/vinay9354/architecture-atlas/blob/main/CONTRIBUTING.md).
