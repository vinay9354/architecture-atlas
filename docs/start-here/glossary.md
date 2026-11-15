---
title: Glossary
description: "One consistent definition per term, used the same way on every page."
---

# Glossary

One definition per term. Pages link here instead of redefining terms. If you find a page using a
term differently, that is a bug: open a content correction issue. Terms are grouped by theme;
use the search box for a specific word.

## Roles and process

**Solutions Architect (SA)**
:   The person accountable for the significant technical decisions of a solution: the decisions that
    are expensive to change later, cross team or system boundaries, or determine whether quality
    attribute targets can be met. Works between business stakeholders and engineering teams.

**Enterprise Architect (EA)**
:   Focuses on the organization's whole technology portfolio over years: capability maps, standards,
    roadmaps, and governance, rather than one solution.

**Software Architect**
:   Focuses on the internal structure of one application or service: modules, patterns, code-level
    quality, and the team's engineering practices.

**Stakeholder**
:   Anyone who affects or is affected by the system: sponsors, users, operators, security, compliance,
    finance, partner teams.

**Architecture Decision Record (ADR)**
:   A short, numbered document recording one significant decision: context, options, decision,
    consequences. Immutable once accepted; superseded by a newer ADR rather than edited.

**Trade-off**
:   A choice in which improving one quality attribute or goal worsens another. Architecture is largely
    the management of trade-offs under constraints.

**Constraint**
:   A fixed condition the design must satisfy and cannot negotiate away: a regulation, a budget, an
    existing system, a deadline, a mandated technology.

**Assumption**
:   Something taken to be true that has not been verified. Every assumption is a risk until checked.

**Technical debt**
:   The future cost created by a design or implementation shortcut taken now. Sometimes a deliberate
    trade-off; always something to record and pay down intentionally.

**Fitness function**
:   An automated check that measures whether the architecture still has a required property (for
    example "no module in the domain layer imports the web layer", or "p95 latency under 300 ms").

**Architecture Tradeoff Analysis Method (ATAM)**
:   A structured review method from the Software Engineering Institute (SEI) that elicits quality
    attribute scenarios, builds a utility tree, and identifies sensitivity points, trade-off points,
    and risks.

## Requirements

**Business requirement**
:   A statement of what the organization needs to achieve: an outcome, usually measurable, such as
    "reduce order-status support calls by 40%".

**Functional requirement (FR)**
:   A statement of what the system must do: a behavior, feature, or capability, such as "a customer
    can see the current location of each shipment".

**Non-functional requirement (NFR)**
:   A statement of how well the system must do it: a quality attribute target with a measure, such as
    "shipment status is visible within 60 seconds of the carrier scan for 99% of events". Also called a
    quality attribute requirement. Constraints are often grouped with NFRs but are distinct.

**Quality attribute**
:   A measurable property of a system that determines whether it is fit for its purpose: availability,
    performance, security, maintainability, and so on. Often called "-ilities".

**Quality attribute scenario**
:   A structured way to write an NFR so it can be tested: source, stimulus, artifact, environment,
    response, response measure.

**Acceptance criteria**
:   Conditions that must be true for a requirement to be considered met; the test that decides done.

**Use case**
:   A description of how an actor achieves a goal through the system, including main and alternative
    flows.

**User story**
:   A short, user-centered statement of a need ("As a ..., I want ..., so that ..."), elaborated with
    acceptance criteria.

## Quality attributes

**Availability**
:   The fraction of time a system is able to perform its function, usually stated as a percentage over
    a period ("99.9% monthly"). Measured, not promised.

**Reliability**
:   The probability that the system performs correctly for a given period under stated conditions.
    A reliable system fails rarely; an available system is reachable often. They are related but not
    identical.

**Resilience**
:   The ability to continue operating, possibly in a degraded mode, when components or dependencies
    fail, and to recover afterwards.

**Fault tolerance**
:   The property of continuing correct operation despite the failure of some components, usually
    through redundancy.

**Durability**
:   The guarantee that data, once acknowledged as written, will not be lost.

**Scalability**
:   The ability to handle more load by adding resources, with cost growing in a predictable and
    acceptable way.

**Elasticity**
:   The ability to add and remove resources automatically as load changes, so that capacity tracks
    demand.

**Performance**
:   How quickly and efficiently the system does its work, typically measured as latency, throughput,
    and resource utilization.

**Latency**
:   The time between a request being issued and its response being received. Reported with
    percentiles, not averages.

**Throughput**
:   The amount of work completed per unit of time, for example requests per second (RPS) or
    megabytes per second.

**Tail latency**
:   The latency experienced by the slowest requests, described by high percentiles such as p99.
    Tail latency dominates user experience when a page depends on many backend calls.

**Percentile (p50, p95, p99)**
:   The value below which that percentage of observations fall. p95 = 300 ms means 95% of requests
    completed in 300 ms or less.

**Consistency**
:   The degree to which all readers see the same data at the same time. Ranges from strong to
    eventual; defined precisely in the distributed-systems pages.

**Maintainability**
:   How easily the system can be understood, modified, tested, and extended. Includes modularity,
    reusability, analysability, modifiability, and testability.

**Observability**
:   How well the internal state of the system can be inferred from its external outputs (logs,
    metrics, traces). A prerequisite for operability.

**Operability**
:   How easily the system can be run day to day: deployed, configured, monitored, diagnosed, scaled,
    and recovered.

**Portability / Interoperability**
:   Portability: how easily the system moves to a different environment. Interoperability: how easily
    it exchanges information with other systems.

**Sustainability**
:   The energy and carbon cost of running the system, treated as a quality attribute alongside
    financial cost.

## Service levels and recovery

**Service Level Indicator (SLI)**
:   A quantitative measure of some aspect of service, such as the fraction of requests served under
    300 ms, or the fraction of successful requests.

**Service Level Objective (SLO)**
:   A target value or range for an SLI over a period, such as "99.9% of requests succeed per 30 days".
    Internal; drives engineering priorities.

**Service Level Agreement (SLA)**
:   A contract with consequences (credits, penalties) if service levels are not met. External; set
    looser than the SLO.

**Error budget**
:   The amount of unreliability an SLO permits (100% minus the SLO). Spent by incidents and risky
    changes; when exhausted, reliability work takes priority.

**Recovery Time Objective (RTO)**
:   The maximum acceptable time between a failure and restoration of service.

**Recovery Point Objective (RPO)**
:   The maximum acceptable amount of data loss measured in time: an RPO of 5 minutes means losing at
    most the last 5 minutes of writes.

**Mean Time To Recovery (MTTR), Mean Time To Detect (MTTD), Mean Time Between Failures (MTBF)**
:   Averages of recovery time, detection time, and operating time between failures. Availability over
    many cycles ≈ MTBF ÷ (MTBF + MTTR).

**Single point of failure (SPOF)**
:   A component whose failure alone takes the whole system down.

## Capacity and load

**Load**
:   Demand placed on a system, described by request rate, concurrent users, data volume, or job size.

**Capacity**
:   The maximum load a system can handle while meeting its SLOs.

**Capacity planning**
:   Estimating future load and provisioning capacity, with headroom, ahead of need.

**Headroom**
:   Spare capacity kept above expected peak load to absorb surprises; expressed as a utilization target
    (for example, run at 60-70% of capacity).

**Peak factor**
:   The ratio of peak load to average load over a period. Daily patterns commonly give peak factors of
    2-5; events can give far more.

**Daily Active Users (DAU)**
:   The number of distinct users who use the system in a day. The usual starting point for load
    estimates.

**Concurrency**
:   The number of requests (or users) in the system at the same moment. Related to throughput and
    latency by Little's Law.

**Little's Law**
:   For a stable system, average number in system = average arrival rate × average time in system
    (L = λW). Lets you convert between concurrency, throughput, and latency.

**Back-of-the-envelope estimate**
:   An order-of-magnitude calculation from a few stated assumptions, good enough to choose between
    designs and spot impossibilities.

**Bottleneck**
:   The component with the least capacity relative to its load; it determines the system's throughput.

**Horizontal / vertical scaling**
:   Horizontal: adding more instances. Vertical: making one instance bigger.

## Diagrams and documentation

**C4 model**
:   A set of four zoom levels for describing software architecture: System Context, Container,
    Component, and Code, plus supplementary System Landscape, Dynamic, and Deployment diagrams.

**Container (C4)**
:   A separately deployable or runnable unit that executes code or stores data: a web application, an
    API service, a database, a message broker, a mobile app. Not the same as a Docker container,
    although a Docker container often hosts one.

**Component (C4)**
:   A grouping of related functionality inside a container with a well-defined interface, for example
    a module or a set of classes.

**System context diagram**
:   The C4 Level 1 diagram: the system as one box, the people who use it, and the external systems it
    talks to.

**Deployment diagram**
:   Shows where containers run at runtime: regions, zones, networks, hosts, and the infrastructure
    around them.

**Trust boundary**
:   A line in a diagram across which the level of trust changes, for example between the internet
    and a private network, or between tenants. Controls (authentication, validation, encryption) belong
    at trust boundaries.

**Mermaid**
:   A text syntax for diagrams rendered in the browser; the default diagram format in this repository.
