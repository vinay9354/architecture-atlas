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

**Architecture principle**
:   A short, durable rule that guides decisions across a portfolio ("prefer managed services unless
    the data cannot leave our network"), always stated with its rationale and implications.

**Architecture review board (ARB)**
:   A standing group that reviews significant designs against principles and standards. Useful for
    irreversible decisions; harmful when it must approve every change.

**Design review**
:   A structured conversation about a proposed design before it is built, focused on requirements
    coverage, trade-offs, risks, and the decisions that are expensive to reverse.

**Threat model**
:   A structured analysis, per trust boundary, of how an attacker could compromise a system and which
    control mitigates each threat; STRIDE is a common checklist of threat types.

**Technology lifecycle / end of life (EOL)**
:   The stages a technology passes through in an organization (assess, trial, adopt, hold, retire).
    End of life is the date after which the vendor stops support and security fixes, which must be
    planned for before it arrives.

**Business capability**
:   Something the organization does or needs to do, stated independently of how ("track shipments"),
    used to map stakeholders, systems, and investment.

**Key performance indicator (KPI)**
:   A business measure with a target and a baseline that tells whether a goal is being met, for
    example the number of order-status support calls per week.

**RAID log**
:   A living register of Risks, Assumptions, Issues, and Dependencies, each with an owner, a status,
    and what will resolve it.

**MoSCoW**
:   A prioritization scheme that sorts requirements into Must have, Should have, Could have, and Won't
    have (this time).

**As-Is / To-Be architecture**
:   The current state of a system or landscape (As-Is) and the intended future state (To-Be); the
    difference between them is the gap analysis.

**Gap analysis**
:   A comparison of As-Is against To-Be that lists what must be built, bought, changed, or retired to
    get from one to the other.

**Proof of concept (PoC) / Minimum viable product (MVP)**
:   A PoC answers one technical question ("can carrier webhooks arrive within 60 seconds?") and is
    thrown away. An MVP is the smallest product that delivers real value to real users and is kept.

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

**Fault domain / failure domain**
:   A set of components that fail together: a host, a rack, an availability zone, a region, a
    deployment. Redundancy only helps across fault domains.

**Availability zone (AZ)**
:   A provider-defined fault domain within a region: separate power, cooling, and networking, with
    low-latency links to the other zones in the same region.

**Active-active / active-passive**
:   Two redundancy arrangements. Active-active: all copies serve traffic at once. Active-passive: one
    serves, the other waits and takes over on failure (with a failover delay).

**Failover**
:   Switching traffic or a role (such as database primary) from a failed component to a healthy one,
    automatically or by hand.

**Health check**
:   A periodic probe that decides whether an instance should receive traffic; a failing check removes
    the instance from the load balancer or triggers failover.

**Error budget policy**
:   The agreed rules for what happens as the error budget is consumed: for example, freezing risky
    releases when it is exhausted.

**Burn rate**
:   How fast an error budget is being spent relative to the rate that would use it up exactly at the
    end of the window; a burn rate of 1 exhausts the budget in one window, 10 exhausts it in a tenth.

**Critical (hard) dependency**
:   A dependency whose failure makes the service's own SLI fail; its availability caps the SLO the
    service can promise.

**Measurement point**
:   Where an SLI is observed (client, gateway, service, synthetic prober); different points give
    different numbers, so an SLO must name one.

**Region**
:   A group of availability zones in one geography; regions are far enough apart that replication
    between them is asynchronous.

**Failover window**
:   The time from a failure to a completed failover; it counts as downtime unless something masks it.

**Cell-based architecture**
:   Partitioning customers across independent, full-stack copies of a system (cells) behind a thin
    router, so a failure affects one cell's customers rather than everyone.

**Static stability**
:   The property of continuing to operate through a dependency's failure without needing that
    dependency to recover first, usually by relying only on state already held locally.

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

**Utilization**
:   The fraction of a resource's capacity in use (CPU busy time, worker threads occupied). Queueing
    delay grows steeply as utilization approaches 100%.

**Saturation**
:   The state in which a resource has no spare capacity: more arriving work only lengthens the queue.
    Throughput stops rising; latency keeps rising.

**Queueing delay**
:   Time a request spends waiting for a resource before service begins. The part of latency that
    load adds.

**Closed-loop / open-loop load**
:   Closed-loop: each client waits for a response before sending the next request, so requests in
    flight are bounded. Open-loop: requests arrive at a rate independent of responses, as real
    traffic does, so an overloaded system's queue grows without bound.

**IOPS**
:   Input/output operations per second: a storage throughput measure, distinct from bandwidth
    (bytes per second).

**Service time**
:   The time a resource spends doing one unit of work, excluding any waiting. Latency = queueing
    delay + service time (+ network).

**Fan-out**
:   One request causing many parallel downstream requests; the slowest of them governs the response,
    so the tail of each dependency becomes the median of the whole.

**Latency budget**
:   The allocation of a latency target across the hops of a request path, so each component owns a
    number.

**Hedged request**
:   Sending a duplicate of a slow request to another replica after a short delay and using whichever
    response arrives first; trades extra load for a shorter tail.

**Coordinated omission**
:   A measurement error in which a load generator that waits for responses stops sampling during slow
    periods and therefore under-reports tail latency.

**Baseline (performance)**
:   A recorded measurement of normal latency, throughput, and utilization under a known load, used to
    detect regressions.

## Networking

**OSI model / TCP/IP model**
:   Two layered models of networking. OSI has seven conceptual layers; TCP/IP has four or five that
    match real protocols. Architects mostly reason at the network (IP), transport (TCP/UDP/QUIC), and
    application (HTTP, TLS) layers.

**IP address**
:   A numeric identifier for a network interface. IPv4 addresses are 32 bits; IPv6 addresses are
    128 bits. Private ranges are not routable on the public internet.

**CIDR**
:   Classless Inter-Domain Routing notation: an address plus a prefix length (`10.0.0.0/16`) that
    says how many leading bits identify the network. A `/16` holds 65,536 addresses; each extra bit
    halves the block.

**Subnet**
:   A contiguous block of addresses inside a larger network, usually tied to one zone and one role
    (public, private application, private data), with its own route table.

**Route table**
:   The rules that decide where a packet leaving a subnet goes next, matched by longest prefix.

**NAT (network address translation)**
:   Rewriting addresses so that instances with private addresses can reach the internet through a
    shared public address. Port address translation (PAT) is the many-to-one form.

**DNS**
:   The Domain Name System: a distributed, cached directory that maps names to addresses and other
    records. Time to live (TTL) on records limits how fast a change propagates.

**MTU**
:   Maximum transmission unit: the largest packet a link carries without fragmentation.

**TCP / UDP / QUIC**
:   Transport protocols. TCP: ordered, reliable byte stream with connection setup and congestion
    control. UDP: unreliable datagrams, no setup. QUIC: a reliable, multiplexed, encrypted transport
    on top of UDP, used by HTTP/3.

**TLS**
:   Transport Layer Security: the protocol that encrypts and authenticates connections (the S in
    HTTPS). TLS 1.3 completes its handshake in one round trip.

**Round-trip time (RTT)**
:   The time for a packet to go to a peer and a reply to come back. Connection setup and handshakes
    cost a number of RTTs, which dominates latency on mobile networks.

**Head-of-line blocking**
:   A lost or delayed item holding back later, independent items behind it in the same queue or
    stream; the reason HTTP/2 over TCP still stalls on packet loss and HTTP/3 over QUIC does not.

**0-RTT**
:   Application data sent in the first flight of a resumed TLS 1.3 or QUIC session, before the
    handshake completes. It can be replayed, so only idempotent requests belong in it.

**Mutual TLS (mTLS)**
:   TLS in which both sides present certificates, giving service-to-service authentication as well
    as encryption.

**Supernet**
:   A shorter prefix that covers several aligned subnets, used to summarize them in one route or
    firewall rule.

**Load balancer**
:   A component that spreads requests across instances and removes unhealthy ones. Layer 4 balances
    connections; layer 7 understands HTTP and can route by path or header.

## Data and caching

**ACID**
:   Atomicity, consistency, isolation, durability: the guarantees a transactional database gives to
    a group of operations.

**Isolation level**
:   How much a transaction is protected from seeing other concurrent transactions' effects: read
    uncommitted, read committed, repeatable read, serializable. Stronger isolation costs throughput.

**Index**
:   A data structure (usually a B-tree) that lets the database find rows by a column value without
    scanning the table. Indexes speed reads and slow writes.

**Normalization / denormalization**
:   Normalization structures tables so each fact is stored once. Denormalization copies data to make
    specific reads cheaper at the cost of update complexity.

**Replication**
:   Keeping copies of data on several nodes. Synchronous replication waits for the copy before
    acknowledging a write; asynchronous replication acknowledges first and copies later (replication
    lag).

**Connection pool**
:   A set of reusable database connections kept open by an application so that requests do not pay
    connection setup each time. Sized from concurrency (Little's Law) plus headroom.

**Cache-aside / read-through / write-through / write-behind**
:   Caching patterns. Cache-aside: the application checks the cache, then loads and fills it on a
    miss. Read-through: the cache loads on a miss itself. Write-through: writes go to cache and store
    together. Write-behind: writes go to cache and are flushed to the store later.

**Time to live (TTL)**
:   How long a cached item (or DNS record) is considered valid before it must be refreshed.

**Cache stampede**
:   Many requests missing the same cache key at once and all hitting the backing store, typically
    when a popular item expires.

**Hot key**
:   A single key that receives a disproportionate share of traffic, overloading the one node or
    partition that holds it.

**Working set**
:   The data that is actively used over a period; if it fits in the cache, hit rates can be high.

## Messaging and distributed systems

**Message queue / broker**
:   Infrastructure that accepts messages from producers, stores them, and delivers them to consumers
    asynchronously, decoupling the two in time and rate.

**At-most-once / at-least-once / exactly-once delivery**
:   Delivery guarantees. At-most-once may lose messages; at-least-once may duplicate them; exactly-once
    end to end is only achievable with idempotent or transactional consumers.

**Idempotency**
:   The property that doing an operation more than once has the same effect as doing it once. An
    idempotency key lets a server recognize and ignore a retried request.

**Dead-letter queue (DLQ)**
:   A queue that receives messages that failed processing after the allowed retries, so they can be
    inspected and replayed instead of blocking others.

**Visibility timeout**
:   In a queue, the period during which a message handed to a consumer is hidden from others; if it
    is not acknowledged in time it becomes visible again for redelivery.

**Backpressure**
:   A mechanism by which a slow consumer slows its producer (or a queue bounds its depth) instead of
    accepting work it cannot finish.

**Webhook**
:   An HTTP request a provider sends to a consumer's URL when an event happens; the consumer must
    verify its origin and tolerate duplicates.

**Partial failure**
:   The defining difficulty of distributed systems: some nodes or links fail while others keep
    working, and a node cannot always tell which happened.

**Network partition**
:   A failure that splits a system into groups of nodes that cannot communicate with each other
    while each group keeps running.

**Clock skew**
:   The difference between two machines' clocks. Wall-clock timestamps cannot be used to order
    events across machines without a bound on skew.

**Logical clock (Lamport timestamp, vector clock)**
:   Counters that order events by causality rather than by wall-clock time. Lamport timestamps give a
    total order consistent with causality; vector clocks can also detect concurrent events.

**Leader election**
:   Choosing one node to perform a role that must not be done by two at once; usually implemented
    with a consensus service and a lease.

**Lease**
:   Time-limited ownership of a role or lock that expires unless renewed, so a crashed holder does
    not block forever.

**Fencing token**
:   A number that increases with each lease grant; a resource rejects requests carrying an older
    token, which stops a stale holder from acting after its lease expired.

**Quorum**
:   The minimum number of nodes that must agree for an operation to count, chosen so that any two
    quorums overlap (for example, a majority).

**Consensus**
:   Agreement among nodes on one value or sequence of operations despite failures; implemented by
    protocols such as Paxos and Raft and used for leader election and replicated logs.

**Split brain**
:   Two parts of a partitioned system each believing they are the leader and both accepting writes,
    which produces conflicting state.

**Gossip protocol**
:   A way for nodes to spread membership and state information by periodically exchanging it with
    random peers, without a central coordinator.

## APIs and integration

**API contract**
:   The agreed, versioned description of an API's requests, responses, and errors (for example an
    OpenAPI document) that producers and consumers build against.

**Pagination**
:   Returning a large result in pages. Offset pagination skips N items; cursor pagination returns an
    opaque pointer to continue from, which stays correct while data changes.

**Deprecation**
:   Announcing, while it still works, that an API operation or version will be removed on a stated
    date, with its replacement named.

**Transactional outbox**
:   Writing an outgoing event to a table inside the same database transaction as the state change,
    with a relay publishing it afterwards, so that neither happens without the other.

**Anti-corruption layer**
:   A translation boundary that keeps another system's data model and vocabulary from leaking into
    your own.

**Master data**
:   Shared reference entities (customers, products, locations) with one designated authoritative
    source that other systems take their copies from.

**Rate limiting / throttling / quota**
:   Rate limiting rejects requests above a rate; throttling slows them; a quota caps total usage
    over a period. All three protect capacity and fairness.

**Enterprise service bus (ESB) / iPaaS**
:   Centralized integration middleware that routes and transforms messages between systems. An
    iPaaS is the hosted, subscription form. Both centralize integration logic, with the risks that
    implies.

**EDI**
:   Electronic Data Interchange: standardized document formats for business transactions between
    organizations, still common with carriers, retailers, and suppliers.

**Reconciliation**
:   Comparing two systems' records after the fact to find and repair differences that event delivery
    missed.

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
