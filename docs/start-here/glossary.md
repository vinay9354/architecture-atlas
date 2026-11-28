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

## Computers, concurrency, and algorithms

**vCPU**
:   A virtual CPU sold by a cloud provider or allotted to a container; often one hardware thread rather than a whole core.

**Hardware thread (SMT)**
:   One of the instruction streams a single core interleaves, sharing that core's execution units with its sibling.

**Cache line**
:   The fixed-size block, commonly 64 bytes, in which data moves between main memory and the CPU caches.

**Page fault**
:   An access to a memory page that is not mapped; minor when the kernel resolves it from memory, major when it must read from disk.

**Page cache**
:   Kernel memory holding recently used file data, so repeated reads skip the storage device.

**Context switch**
:   The kernel saving one thread's state and restoring another's on a core; frequent switches cost CPU time.

**cgroup**
:   A Linux control group that limits and accounts CPU, memory, and I/O for a set of processes; the mechanism behind container resource limits.

**Steal time**
:   Time a virtual CPU was ready to run while the hypervisor ran another tenant's work.

**Big O**
:   An upper bound on how an algorithm's time or memory grows with input size, ignoring constant factors.

**Amortized cost**
:   The average cost per operation over a long sequence, even though a few operations in it are expensive.

**Hash table**
:   A structure that stores key-value pairs in buckets chosen by hashing the key, giving constant expected-time lookups. Its load factor (entries per bucket) is kept bounded by resizing.

**B-tree**
:   A balanced tree with many keys per node, each node sized to a storage page, so a lookup reads only a few pages. Most database indexes are B-trees.

**Heap (binary)**
:   An array-backed tree in which every parent is no larger than its children, so the smallest item is always at the root. The usual structure behind priority queues and timers.

**Topological sort**
:   An ordering of a directed acyclic graph in which every node comes after everything it depends on; it fails exactly when there is a cycle.

**Race condition**
:   A bug whose outcome depends on the timing or order of concurrent operations.

**Lost update**
:   Two concurrent read-modify-write operations in which one silently overwrites the other's result.

**Deadlock**
:   A set of actors each waiting for a resource another holds, so none can proceed.

**Starvation**
:   A runnable actor that never gets a resource because others are always chosen first.

**Mutex / semaphore**
:   A mutex is a lock held by one owner at a time. A semaphore is a counter of permits that lets up to N holders in at once.

**Compare-and-set (CAS)**
:   An atomic write that succeeds only if the value is still what the writer last read; the basis of optimistic concurrency control.

**Event loop**
:   A single thread that runs many tasks, switching to another whenever the current one waits on I/O.

**Garbage collection pause**
:   A period when a language runtime stops application threads to reclaim unreachable memory; it shows up as tail latency.

## Software design and architecture styles

**Coupling / cohesion**
:   Coupling is how far a change in one module forces changes in another; cohesion is how far a module's parts serve one purpose. Good designs have low coupling and high cohesion.

**Dependency injection / inversion of control**
:   Passing a component its collaborators instead of letting it create them; control over wiring moves to a framework or a composition root.

**Composition root**
:   The single place near program start where concrete implementations are created and wired together.

**Design by contract**
:   Stating each routine's preconditions, postconditions, and invariants explicitly so callers and implementers know who is responsible for what.

**Refactoring**
:   Changing code structure without changing behavior, in small steps each protected by tests.

**Design pattern**
:   A named, reusable arrangement of code elements with a stated intent and known trade-offs.

**Repository / Unit of Work**
:   A Repository is a collection-like interface that loads and saves domain objects without exposing storage. A Unit of Work tracks the changes of one business operation and commits or rolls them back together.

**State machine**
:   A set of states and the only transitions allowed between them, each triggered by a named event.

**Architecture style**
:   A named structure for a whole system, defined by its kinds of components, its connectors, and the rules for combining them.

**Modular monolith**
:   One deployable unit split into modules with enforced public interfaces and their own data.

**Hexagonal architecture (ports and adapters)**
:   The domain defines interfaces (ports) that technology code (adapters) implements, so source-code dependencies point toward the domain. Clean and onion architecture share the same dependency rule.

**Bounded context**
:   A part of the domain inside which one model and vocabulary stay consistent; the usual unit for drawing service boundaries.

**Conway's law**
:   The observation that systems tend to mirror the communication structure of the organizations that build them.

**Blast radius**
:   The share of users or functions affected by a single failure.

**Event-driven architecture**
:   A style in which components announce facts as events and others react, without the sender knowing who listens.

**Microservice**
:   An independently deployable service that owns one bounded context and its data.

**Distributed monolith**
:   Services that deploy separately but must still change, release, or fail together; the costs of distribution without its benefits.

**Temporal coupling**
:   Two components must both be available at the same moment for an operation to succeed, as with a synchronous call chain.

**API gateway**
:   The single public entry point that terminates TLS, checks tokens, applies rate limits, and routes requests to services.

**Backend for frontend (BFF)**
:   A server-side API tailored to one kind of client, owned by that client's team.

**Service mesh**
:   Sidecar proxies plus a control plane that handle mutual TLS, retries, timeouts, and telemetry for service-to-service traffic.

**Service discovery**
:   Resolving a service name to the addresses of its currently healthy instances.

**CQRS**
:   Command Query Responsibility Segregation: separating the model that changes state from read models shaped for queries.

**Event sourcing**
:   Storing every state change as an event in an append-only log and deriving current state by replaying it.

**Read model (projection)**
:   A copy of data shaped for specific queries, built from the write side's changes and usually eventually consistent with it.

**Strangler fig**
:   Replacing a legacy system piece by piece behind an interception point until nothing routes to the old system.

**Sidecar / ambassador**
:   A sidecar is a helper process deployed beside each application instance and sharing its lifecycle. An ambassador is a sidecar that handles the application's outbound calls.

**Claim check**
:   Storing a large payload elsewhere and passing only a reference to it through the message broker.

**Competing consumers**
:   Several consumers reading one queue so that each message is processed by only one of them.

## Testing

**Test double**
:   A stand-in for a real dependency in a test: a stub returns canned answers, a fake is a working lightweight implementation, a mock checks how it was called.

**Flaky test**
:   A test that both passes and fails on the same code; it erodes trust in the whole suite.

**Test pyramid / testing trophy**
:   Two suite shapes. The pyramid favors many unit tests, fewer integration tests, and few end-to-end tests; the trophy puts static checks at the base and makes integration tests the largest layer.

**Consumer-driven contract**
:   A contract generated from a consumer's tests, listing exactly what it uses of a provider, which the provider's pipeline verifies before release.

**Quality gate**
:   A pipeline stage whose failing checks block promotion to the next environment.

**Soak test**
:   A long run at realistic load that exposes leaks, drift, and slow resource exhaustion.

**Steady-state hypothesis**
:   The measurable normal behavior a chaos experiment expects to hold while a failure is injected.

## Consistency and transactions

**Linearizability**
:   The strongest single-object consistency model: every operation appears to take effect at one instant between its start and end, so all clients see one up-to-date order.

**CAP theorem**
:   The result that, during a network partition, a replicated system must give up either linearizable consistency or availability for some requests. It says nothing about systems without partitions.

**PACELC**
:   An extension of CAP: if there is a Partition, choose Availability or Consistency; Else, choose Latency or Consistency. The else-branch is the everyday trade-off.

**Eventual consistency**
:   A guarantee only that replicas converge once writes stop, with no promise about what a read returns before then.

**Session guarantees**
:   Consistency promises made to one client's sequence of operations: read-your-writes (you see your own writes), monotonic reads (you never go back in time), monotonic writes, and writes-follow-reads.

**Replication lag / stale read**
:   Replication lag is the time between a write committing on the leader and a follower applying it. A stale read returns a version older than one already committed.

**Log sequence number (LSN)**
:   The position of a write in a database's ordered log, used to tell whether a replica has applied it.

**Last-write-wins (LWW)**
:   Resolving concurrent writes by keeping the one with the latest timestamp and silently discarding the rest.

**CRDT**
:   Conflict-free replicated data type: a data structure whose replicas can be updated independently and always merge to the same result without coordination.

**Two-phase commit (2PC)**
:   A protocol in which a coordinator asks all participants to prepare, then tells them all to commit or abort. A coordinator failure between the phases leaves participants blocked.

**Saga**
:   A long-running business transaction split into local transactions, each with a compensating action that semantically undoes it if a later step fails. Coordinated by choreography (events) or orchestration (a central coordinator).

**Compensating transaction**
:   An action that semantically undoes an earlier committed step, such as refunding a captured payment; it is not a rollback.

**Inbox (idempotent consumer)**
:   A table of processed message IDs that a consumer checks inside its own transaction so redelivered messages have no second effect.

## Resilience mechanics

**Timeout**
:   The maximum time a caller waits for a response before treating the call as failed; chosen from the callee's latency percentiles and the caller's own budget.

**Exponential backoff with jitter**
:   Waiting longer after each failed attempt (doubling the delay) and randomizing the wait, so retrying clients do not synchronize into waves.

**Retry amplification / retry storm**
:   Retries at several layers multiplying load on a struggling dependency (three layers of three attempts can mean 27 calls), which keeps it from recovering.

**Circuit breaker**
:   A guard that stops calls to a failing dependency after a threshold (open), fails fast while open, and lets trial calls through (half-open) to detect recovery.

**Bulkhead**
:   Separate resource pools per dependency or tenant, so exhaustion in one cannot consume the capacity of the others.

**Load shedding**
:   Deliberately rejecting some work when overloaded, cheapest and least important first, to keep serving the rest within its targets.

**Graceful degradation**
:   Continuing to serve a reduced but useful response when a dependency fails, such as cached data with a staleness notice.

**Cascading failure**
:   A failure that spreads because each overloaded component pushes extra load or latency onto the next.

**Liveness / readiness check**
:   Liveness asks whether a process should be restarted; readiness asks whether it should receive traffic now. Mixing them up causes restart loops and cascades.

**Poison message**
:   A message that fails processing every time it is delivered; without a receive limit and a dead-letter queue it blocks or wastes consumers forever.

## Partitioning and replication

**Partition (shard) / partition key**
:   A partition is a subset of a dataset stored and served independently. The partition key is the field whose value decides which partition a record lives in.

**Hot partition**
:   A partition receiving a disproportionate share of traffic, usually because of a skewed partition key.

**Consistent hashing**
:   Placing both nodes and keys on one hash ring so that adding or removing a node moves only about one node's share of keys.

**Virtual node**
:   One of many ring positions owned by a physical node, which evens out load and spreads recovery work.

**Rendezvous (highest random weight) hashing**
:   Each node scores a key from a hash of node and key together, and the highest score owns the key; like a ring, it moves few keys on membership change.

**Stable hash**
:   A hash function that returns the same value for the same input in every process and language; Python's built-in hash() is randomized per process and is not one.

**Leader-follower / multi-leader / leaderless replication**
:   Three replication arrangements: one node accepts writes and others copy it; several nodes accept writes and reconcile; or any replica accepts writes and quorums decide reads and writes.

**Rebalancing**
:   Moving partitions between nodes when the cluster grows, shrinks, or becomes uneven, ideally without downtime and without moving more data than necessary.

## Design exercises and AI decisions

**Timebox**
:   A fixed time allowance for a step; when it ends, open items are recorded and the work moves on.

**Base62**
:   Encoding numbers with the ten digits plus lower- and upper-case letters, 62 symbols in all; common for short identifiers.

**Birthday bound**
:   The approximation that among n random values drawn from N possibilities, the chance of at least one collision is about 1 − e^(−n²/2N).

**Open redirect**
:   An endpoint that sends users to any URL it is given, which attackers use to make phishing links look trustworthy.

**Token bucket / leaky bucket**
:   Rate-limiting algorithms. A token bucket refills at a fixed rate up to a capacity and each request spends a token, allowing bursts. A leaky bucket drains requests at a fixed rate, smoothing them.

**Fail open / fail closed**
:   When a protective check is unavailable, allow traffic (open) or reject it (closed); the right choice depends on what the check protects.

**Misfire (catch-up) policy**
:   What a scheduler does with runs missed during an outage: run them all, run one, or skip them.

**Dead-man's switch**
:   An alert that fires when an expected success has not happened within a time limit, catching jobs that silently stopped running.

**Retrieval-augmented generation (RAG)**
:   Fetching relevant documents at request time and adding them to a language model's prompt, instead of relying only on what the model learned in training.

**Guardrail (AI)**
:   A control outside the model that checks, filters, or blocks unsafe inputs, outputs, or actions.

## Cloud foundations

**IaaS**
:   Renting virtual machines, storage, and networks while you run everything from the operating system up.

**PaaS**
:   A managed runtime or component where the provider runs the OS and engine and you supply code, configuration, and data.

**SaaS**
:   A complete application run by a vendor; you keep configuration, users, and data.

**FaaS**
:   Code run per event, scaled to zero, billed per invocation and duration.

**CaaS**
:   A service that runs containers for you, usually with a provider-managed orchestrator.

**Private cloud**
:   Cloud-style self-service infrastructure dedicated to one organization.

**Shared responsibility model**
:   The provider's statement of which security and operational duties it owns and which stay with the customer.

**Control plane / data plane**
:   Management APIs that create and change resources / the part that does the service's job for existing resources.

**Lock-in**
:   The cost, time, and risk of moving a workload to another provider or platform.

**Resource hierarchy**
:   The tree of containers (organization, groups, accounts or projects) where policy, billing, and quotas attach and inherit.

**Principal**
:   An identity (person, group, or workload) that can be granted permissions.

**Service quota**
:   A provider-enforced cap per scope, sometimes raisable on request.

**Availability domain**
:   OCI's term for an isolated data-centre group within a region.

**Hypervisor**
:   Software that runs virtual machines and shares physical hardware among them (type 1 on hardware, type 2 on a host OS).

**Virtual machine**
:   An emulated computer with its own kernel and virtual devices, run by a hypervisor.

**Bare metal instance**
:   A whole physical server rented from a provider with no provider hypervisor in between.

**Instance group**
:   Identical VMs from one template managed as a unit, with autoscaling and health-based replacement.

**Spot capacity**
:   Discounted spare provider capacity that the provider can reclaim after a short notice (also called preemptible); fits interruptible work.

**Serverless function**
:   Code the provider runs per event, scaling sandboxes with demand, billed per invocation and duration.

**Cold start**
:   Extra latency when an invocation must first create and initialize a new sandbox.

**Landing zone**
:   A governed, multi-account cloud environment whose shared foundation (identity, network, logging, guardrails) every account inherits before workloads arrive.

**Organizational unit (OU)**
:   A group of cloud accounts under an organization that receives the same inherited policies (Azure management group, Google Cloud folder).

**Guardrail (cloud)**
:   An automated rule that keeps accounts within policy; preventive ones block an action, proactive ones reject a definition before creation, detective ones report non-compliance.

**Account vending**
:   An automated, self-service process that turns an approved request into a new account with the full baseline applied and verified.

**Infrastructure as code (IaC)**
:   Defining infrastructure in version-controlled files that a tool applies to reach the described state.

**Policy as code**
:   Guardrails and compliance rules written as versioned, testable code that machines evaluate.

**Drift**
:   Any difference between live resources or objects and the declared desired state in code or Git.

**Golden image**
:   A hardened, scanned, signed, versioned base image that all compute in an estate starts from.

**Immutable infrastructure**
:   Never changing running servers in place; every change ships as a new image that replaces them.

**Hub-and-spoke**
:   A topology where every network connects only to a central hub, which owns shared routing, inspection, egress, and hybrid links.

**Service control policy (SCP)**
:   An organization-level policy that caps the maximum permissions principals in member accounts can use, whatever their own policies grant (AWS term; Azure Policy and Google Cloud organization policies play similar roles).

**Data perimeter**
:   A set of preventive policies that let only trusted identities, from expected networks, reach trusted resources.

**Tenant isolation**
:   Keeping one customer's data, performance, and failures from affecting another customer on a shared platform.

## Containers and Kubernetes

**Container image**
:   A read-only, content-addressed package of filesystem layers plus the configuration to start a container.

**Image layer**
:   A tar archive of filesystem changes; layers stack to form the image's root filesystem.

**Digest**
:   A content hash identifying exact bytes; any change gives a new digest.

**Registry**
:   A service that stores and serves images over the OCI distribution API.

**OCI (Open Container Initiative)**
:   The Open Container Initiative, publisher of the image, runtime, and distribution specifications.

**Linux namespace**
:   A kernel feature giving a process its own view of one resource type.

**Pod**
:   The smallest unit Kubernetes schedules; one or more containers sharing a network identity and volumes.

**Kubernetes control plane**
:   The API server, etcd, scheduler, and controller managers that store desired state and drive the cluster toward it.

**Controller / reconciliation loop**
:   A process that repeatedly compares declared state with actual state and acts to close the gap; the core mechanism of Kubernetes (not the same as data reconciliation above).

**Request / limit**
:   The resources the scheduler reserves for a container / the ceiling the kernel enforces.

**Allocatable**
:   A node's capacity minus what is reserved for the OS, kubelet, and eviction thresholds.

**QoS class**
:   Guaranteed, Burstable, or BestEffort, derived from requests and limits; decides eviction order.

**Taint / toleration**
:   A node mark that repels Pods / a Pod's permission to ignore it.

**Topology spread constraint**
:   A scheduling rule that keeps a workload's replicas balanced across zones or nodes.

**PodDisruptionBudget**
:   A limit on how many replicas voluntary disruptions such as drains may take down at once.

**Cordon / drain**
:   Mark a node unschedulable / also evict its Pods while respecting their disruption budgets.

**CNI / CSI / CRI**
:   Plugin interfaces for Pod networking, volumes, and container runtimes.

**Service (Kubernetes)**
:   A stable virtual IP and DNS name in front of the ready Pods matching a label selector.

**NetworkPolicy**
:   A Kubernetes object stating which traffic may reach or leave selected Pods, enforced by the network plugin.

**PersistentVolumeClaim / StorageClass**
:   A request for storage / the recipe used to provision it.

**Gateway API**
:   A role-based family of Kubernetes routing resources (GatewayClass, Gateway, routes) that succeeds Ingress.

**Ambient (sidecarless) mesh**
:   A mesh data plane using shared per-node L4 proxies and optional L7 waypoints instead of a proxy per Pod.

**Admission controller**
:   Code in the Kubernetes API server's request path that can change or reject an object before it is stored; policy engines and image-signature checks run here.

**Pod Security Admission**
:   The built-in check that rejects Pods not meeting the privileged, baseline, or restricted profile set on their namespace.

**CustomResourceDefinition (CRD)**
:   An extension that adds a new object type to the Kubernetes API.

**Operator**
:   A controller plus CRDs that encodes how to run one piece of software.

**GitOps**
:   Operating a system from desired state kept in a versioned store, pulled and continuously reconciled by agents inside the system.

**Helm chart / release**
:   A package of templated manifests with default values / one installed copy of it, with revision history.

**Kustomize overlay**
:   A directory that points at base manifests and patches them for one environment.

**kind**
:   A tool that runs a Kubernetes cluster with each node as a Docker container.

## Network security and hybrid connectivity

**East-west / north-south traffic**
:   Traffic between services inside the platform / traffic entering or leaving it.

**Security group / network ACL**
:   Stateful allow-list on an interface vs stateless numbered allow/deny list on a subnet that also needs return-traffic rules.

**Ephemeral port**
:   The temporary source port a client picks for a connection; replies are addressed to it.

**WAF (web application firewall)**
:   A filter that inspects decrypted HTTP requests and blocks attack or abuse patterns.

**DMZ**
:   A perimeter network for internet-facing components, filtered on both sides.

**Anycast**
:   One prefix announced from many locations so routing picks a nearby one.

**Private endpoint**
:   A private-address interface in your network that fronts a provider or partner service.

**Transit router**
:   A managed router that networks attach to, segmented by its route tables.

**Site-to-site VPN**
:   An IPsec tunnel joining two networks through gateway devices.

**IPsec / IKE**
:   IP-layer encryption / the protocol that negotiates its keys.

**BGP / ASN**
:   The inter-network routing protocol / the number identifying each routing domain.

**Route propagation**
:   Automatically copying learned routes into chosen route tables.

**AS path prepending**
:   Repeating your own ASN so a path looks longer and less preferred.

**Conditional forwarding**
:   A resolver rule that sends one domain's queries to named servers.

**MSS clamping**
:   Rewriting the TCP maximum segment size so segments fit a smaller path MTU.

**Dedicated private connection**
:   A private circuit into a provider's network that carries BGP sessions.

**ZTNA (zero trust network access)**
:   A broker grants one user on a healthy device access to one application per session instead of network-level access.

**Content delivery network (CDN)**
:   A network of edge caches that serves static and cacheable content close to users and shields the origin from traffic surges.

**Flow registry**
:   A reviewed list of allowed network flows between segments, each with an owner and an expiry, from which firewall rules are generated.

## Security principles, identity, and data protection

**CIA triad**
:   Confidentiality, integrity, availability, the three properties security controls protect.

**Defense in depth**
:   Layering independent controls so one failing control does not mean a breach.

**Least privilege**
:   Each identity gets only the access its task needs, for only as long as needed.

**Zero Trust**
:   No implicit trust from network location; every request authenticated and authorized against dynamic policy.

**STRIDE**
:   Six threat categories (spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege), each violating one security property.

**Identity provider (IdP)**
:   The service that authenticates users and issues signed assertions or tokens about them to applications.

**OAuth 2.0**
:   A framework that issues a client a limited access token for an API, on behalf of a user or itself.

**OpenID Connect (OIDC)**
:   An identity layer on OAuth 2.0 adding an ID token that tells the client who signed in.

**JSON Web Token (JWT)**
:   A compact signed set of claims (issuer, audience, subject, expiry) the recipient must verify before trusting.

**PKCE (Proof Key for Code Exchange)**
:   A one-time secret whose hash accompanies the authorization request so a stolen code cannot be redeemed without it.

**Phishing-resistant MFA**
:   Authentication whose cryptographic response is bound to the genuine site's origin.

**Workload identity**
:   A short-lived credential the platform issues to a running workload instead of a stored key.

**Just-in-time (JIT) access**
:   Privileged rights granted on approved request for a short window, then removed automatically.

**SQL injection**
:   Input that becomes part of a SQL statement's text, so the database runs it as code.

**Cross-site scripting (XSS)**
:   Attacker-supplied script that runs in another user's browser with that user's session.

**Cross-site request forgery (CSRF)**
:   A hostile site gets the victim's browser to send a request the target accepts because cookies are attached automatically.

**Server-side request forgery (SSRF)**
:   The server is tricked into requesting a destination the attacker chooses, often an internal one.

**BOLA (broken object level authorization)**
:   Broken object level authorization; an API acts on an object without checking the caller may access it.

**SAST (static application security testing)**
:   Static application security testing; analyzes source or bytecode without running it.

**DAST (dynamic application security testing)**
:   Dynamic application security testing; probes the running application from outside.

**SCA (software composition analysis)**
:   Software composition analysis; inventories third-party components and matches known vulnerabilities and licenses.

**Data classification**
:   Giving each data element a sensitivity level that decides its handling rules.

**Envelope encryption**
:   Data encrypted with a data key that is itself encrypted by a key-encryption key that never leaves the KMS.

**Key management service (KMS)**
:   A managed service that creates, stores, and uses keys without exposing root keys, with access policies and audit logs.

**HSM (hardware security module)**
:   Tamper-resistant hardware that generates and uses keys so they never leave it in plaintext.

**Tokenization**
:   Replacing a sensitive value with a random token, the mapping held in a separate protected vault.

**Pseudonymization**
:   Processing personal data so it cannot be linked to a person without separately kept extra information.

**Anonymization**
:   Irreversibly removing the ability to identify a person by any means reasonably likely to be used.

**Crypto-shredding**
:   Making data unreadable everywhere, backups included, by destroying its encryption key.

**Policy enforcement point (PEP)**
:   The component in front of a resource (proxy, gateway, or sidecar) that lets a request through only when a policy decision allows it.

**Policy decision point (PDP)**
:   The logic that evaluates identity, device, and context signals against policy and returns allow or deny.

**Identity-aware proxy**
:   A reverse proxy that authenticates the user through single sign-on and checks device state before forwarding a request to one application.

**Device posture**
:   A device's security state (managed or not, patch level, encryption, endpoint protection), used as an input to access decisions.

**Sender-constrained token**
:   An access token bound to a key the client holds (mTLS certificate binding or DPoP), so a stolen copy is useless without that key.

**Break-glass access**
:   A few sealed emergency identities that work outside the normal sign-in path, are used only in a declared emergency, alert on every use, and are rotated afterwards.

**Separation of duties**
:   Splitting change, approval, and oversight of a control between different people, so no single person can both act and hide the act.

**Access package**
:   A bundle of group memberships and application rights for one purpose, with an approver, an expiry, and a renewal rule.

**SCIM (System for Cross-domain Identity Management)**
:   A standard protocol (RFC 7643 and RFC 7644) that an identity provider uses to create, update, and remove user accounts in other applications.

## Security operations, supply chain, and compliance

**SBOM (software bill of materials)**
:   A machine-readable list of the components in an artifact, with versions and identifiers.

**Provenance**
:   Verifiable metadata, produced by the build platform, about how an artifact was built (source, builder, inputs).

**Artifact signing**
:   A cryptographic signature over an artifact's digest that lets consumers verify who produced it and that it is unchanged.

**SLSA (Supply-chain Levels for Software Artifacts)**
:   An OpenSSF framework of tracks and levels for software supply-chain integrity.

**CSPM / CWPP / CIEM**
:   Continuous checks of cloud configuration, workload security, and cloud entitlements.

**KEV (Known Exploited Vulnerabilities catalog)**
:   CISA's catalogue of vulnerabilities with evidence of exploitation in the wild.

**SIEM (security information and event management)**
:   A central store and analytics engine for security events that produces alerts.

**SOAR (security orchestration, automation, and response)**
:   Workflow automation that runs response playbooks on alerts.

**Detection rule**
:   A versioned query that turns matching events into an alert with a severity and an owner.

**Playbook**
:   A documented, often partly automated, sequence of response steps for one alert or incident type.

**Threat intelligence**
:   Evidence-based knowledge about adversaries, their methods, and indicators, used to guide detection and response.

**IOC / TTP**
:   Observable artifacts tied to malicious activity / how an adversary operates.

**Chain of custody**
:   A record of who collected and handled each piece of evidence, when, and how its integrity was protected.

**Immutable backup**
:   A backup that cannot be changed or deleted before its retention ends, even by an administrator.

**Compliance**
:   Showing, with evidence an outsider accepts, that an organization meets a defined set of external requirements.

**Control (security)**
:   A safeguard or practice that addresses a risk or requirement, with an owner and a way to test it.

**Control mapping**
:   A table linking each internal control to the framework requirements it helps satisfy.

**Attestation report**
:   An independent practitioner's opinion on a described system and its controls, such as a SOC 2 report.

**Data controller / data fiduciary**
:   The party that decides why and how personal data is processed (GDPR / India DPDP term).

**DPIA (data protection impact assessment)**
:   A documented assessment of risks to individuals, done before high-risk processing.

**Cardholder data environment (CDE)**
:   People, processes, and systems that store, process, or transmit card data, plus connected systems.

**Data residency**
:   Where data is stored, processed, and accessed from; a design choice sometimes required by law, contract, or policy.

**Write-once retention (WORM)**
:   Storage that blocks overwriting or deleting an object until its retention period ends; in compliance mode not even administrators can shorten it.

## Deployment and data recovery

**Rolling deployment**
:   Replacing a fleet's instances with a new version in small batches while the rest keep serving traffic.

**Blue-green deployment**
:   Running two complete environments and switching traffic from the old one to the new one in one step, which also gives a fast rollback.

**Golden signals**
:   The four service-health measures of latency, traffic, errors, and saturation, tracked for every tier.

**Synchronous standby**
:   A database replica that must confirm each change before the primary acknowledges the commit, so promoting it loses no committed data.

**Read replica**
:   An asynchronously updated database copy that serves reads and may lag behind the primary.

**Point-in-time recovery (PITR)**
:   Restoring a database to a chosen moment by replaying archived transaction logs on top of a base backup.

## Reliability and disaster recovery

**FMEA (failure mode and effects analysis)**
:   A table of each component's failure modes with effects, causes, and current controls, scored to rank risk.

**Risk priority number (RPN)**
:   Severity × occurrence × detection; a rough ranking aid, not a measure of risk.

**Fault tree analysis**
:   A top-down diagram from one undesired event through AND/OR gates to the basic events that cause it.

**Minimal cut set**
:   A smallest set of basic events that together cause the top event.

**Reliability block diagram**
:   A diagram of which components must all work (series) and which can stand in for each other (parallel or k-out-of-n).

**Common-cause failure**
:   One cause that fails several redundant copies at once.

**Fault injection**
:   Deliberately introducing errors, latency, crashes, or partitions to observe how a system responds.

**Metastable failure**
:   A degraded state that persists after its trigger is gone because a feedback loop keeps load above capacity.

**Shuffle sharding**
:   Giving each customer a nearly unique combination of shared resources so one customer's failure rarely takes out another's whole combination.

**Witness**
:   A data-less voting member in a third fault domain that breaks ties between two data nodes.

**Epoch (term)**
:   A number that increases with every leadership change and is stamped on writes so stale leaders can be recognized.

**Thundering herd**
:   Many clients acting at the same instant, for example reconnecting after an outage.

**Degraded operating mode**
:   A designed, labelled reduced service with a trigger, a scope, and an exit criterion.

**Quorum loss**
:   Losing enough members that no majority can form, so the cluster stops accepting writes.

**Pilot light**
:   A DR strategy where data is replicated and core infrastructure exists in the recovery location, but compute stays off until a disaster is declared.

**Warm standby**
:   A scaled-down but fully working copy of the stack in the recovery location that can serve traffic immediately.

**Hot standby**
:   A full-scale running copy of the stack that serves no traffic until failover.

**Full / incremental / differential backup**
:   A complete copy / changes since the previous backup of any kind / changes since the last full backup.

**Air-gapped backup**
:   A copy the production environment cannot reach by network or identity ("logical" when separated by account, credentials, and policy).

**Runbook**
:   A written step-by-step procedure with owners, commands, checks, and expected durations.

**Game day**
:   A planned exercise in which a team injects a failure or runs a recovery and measures the result.

**BCP / DRP**
:   The plan that keeps business functions going during a disruption / the plan that restores the technology.

**Failback**
:   Returning service to the original region after a failover, as a planned switchover after re-seeding, never by merging old data.

**Global load balancer**
:   An entry point with one address that spreads traffic across regions by health and proximity at the connection level, rather than through DNS caches.

**Waiting room (virtual queue)**
:   A front-end queue that admits users to a scarce-capacity flow at a controlled rate, recording each place in a signed pass.

**Recovery wave**
:   A group of recovery steps run together that may start only after the previous wave's gate checks pass.

**Decision deadline**
:   A tier's RTO minus the work that follows a failover declaration: the latest moment a failover can still meet the target.

**Capacity reservation**
:   Compute capacity held in a region in advance, so scale-out during a regional event does not depend on on-demand availability.

## Observability and operations

**Trace**
:   All spans sharing one trace id, describing one request's or message's journey through a system.

**Span**
:   One timed operation within a trace, with its own id, its parent's id, a duration, attributes, and a status.

**Context propagation**
:   Carrying trace identifiers between services by writing them into outgoing requests or messages and reading them on arrival.

**Structured logging**
:   Writing log records as named fields, usually JSON, so they can be filtered, counted, and joined to traces.

**Cardinality**
:   The number of distinct values a field takes; for metrics, each distinct label combination is a separate time series.

**Head sampling / tail sampling**
:   Deciding whether to keep a trace when it starts / after its spans arrive and its outcome is known.

**OpenTelemetry Collector**
:   A vendor-neutral process that receives, processes (batching, redaction, sampling), and exports telemetry.

**OTLP (OpenTelemetry Protocol)**
:   The OpenTelemetry Protocol for sending traces, metrics, and logs between SDKs, Collectors, and backends.

**APM (application performance monitoring)**
:   In-process measurement of each request's latency, errors, and downstream calls, usually through tracing.

**RUM (real user monitoring)**
:   Timings and errors measured in real users' browsers and apps.

**Synthetic monitoring**
:   Scripted requests or journeys run on a schedule from outside the system to test availability and correctness.

**RED method**
:   For each request-driven service, track Rate, Errors, and Duration.

**USE method**
:   For each resource, check Utilization, Saturation, and Errors.

**Alert fatigue**
:   Responders get more alerts than they can handle and start ignoring them.

**Escalation policy**
:   The written order of who is notified next, and after how long, when a page is not acknowledged or needs help.

**Interruption budget**
:   The page and ticket load an on-call shift is designed to absorb, used as the target for alert tuning.

**Incident commander**
:   Holds the overall state of an incident, assigns roles, and makes decisions without hands-on fixing.

**Postmortem**
:   A written review after an incident covering impact, timeline, contributing factors, and tracked actions.

**Contributing factor**
:   One of several conditions that together allowed an incident, none sufficient alone.

**Toil**
:   Manual, repetitive, automatable operational work with no lasting value that grows with the service.

**Production readiness review**
:   A structured check that a service meets operational standards before launch or handover.

**Service catalog**
:   A registry of services with owners, on-call, tier, SLOs, runbooks, and dependencies.

**Severity level**
:   An impact-based incident grade that decides who is engaged and how often updates go out.

## Delivery and platforms

**Trunk-based development**
:   Everyone integrates into one shared branch at least daily, using short-lived branches or direct commits.

**GitFlow**
:   A branching model with long-lived main and develop branches plus feature, release, and hotfix branches.

**Pull request**
:   A proposal to merge a branch, carrying the diff, automated check results, and review discussion.

**Feature flag**
:   A runtime switch that changes behaviour without deploying new code.

**Flag debt**
:   The cost of flags that outlive their purpose; n flags allow 2^n code paths.

**Change lead time**
:   The time from a change being committed to it running in production.

**Continuous integration**
:   Merging every change to trunk often and verifying it with an automated build and tests.

**Continuous delivery**
:   Every change that passes the pipeline could be deployed to production at any moment.

**Continuous deployment**
:   Every change that passes the pipeline is deployed to production automatically.

**Canary release**
:   Sending a small share of real traffic to a new version, comparing it with the old, and widening only if healthy.

**Progressive delivery**
:   Canary-style rollouts whose steps, analysis, and abort are automated by a controller.

**Shadow traffic**
:   Copying live requests to a new version and discarding its responses.

**Promotion**
:   Moving the same artifact to the next environment by changing what that environment references.

**Roll-forward**
:   Fixing a bad deployment by deploying a newer version instead of reverting.

**IaC state**
:   The tool's record mapping each declared resource to its real object id and last known attributes.

**State locking**
:   A backend mechanism that lets only one run write a given state at a time.

**Plan (IaC)**
:   The list of create, update, replace, and destroy actions a declarative tool computes before changing anything.

**Module (IaC)**
:   A reusable, versioned package of infrastructure code with inputs and outputs.

**DevSecOps**
:   Making security a shared, automated, continuous part of delivery rather than a final gate.

**Shift left**
:   Moving security and quality activities earlier in the lifecycle, where fixes cost less.

**Poisoned pipeline execution**
:   Getting a CI/CD pipeline to run attacker-controlled commands by changing its definition or injecting input.

**Workload identity federation**
:   Exchanging a platform-issued identity token (such as a CI job's OIDC token) for short-lived cloud credentials with no stored key.

**Compliance gate**
:   A pipeline check that blocks promotion unless required signed evidence is present and passing.

**Platform engineering**
:   Building and running an internal platform as a product that gives developers self-service capabilities with the organization's rules built in.

**Internal developer platform (IDP)**
:   The integrated capabilities, automation, and interfaces a platform team provides to internal teams.

**Developer portal**
:   A web interface to the platform (catalog, templates, docs, status), one of several possible interfaces.

**Golden path (paved road)**
:   A supported, opinionated route for a common job, packaged as a template, automation, and documentation.

**Thinnest viable platform**
:   The smallest platform layer that delivers consistency, built mostly on managed services.

**DORA metrics**
:   DORA's software delivery measures of throughput and instability, meant to be applied per service.

**SPACE framework**
:   A view of developer productivity along five dimensions, so no single metric stands for productivity.

**Self-heal / prune (GitOps)**
:   Reverting live-state drift automatically / deleting live objects whose manifests were removed from Git.

**Snowflake cluster**
:   A cluster built and changed by hand until no two are alike, so none can be rebuilt or upgraded the same way.

**Soft / hard multi-tenancy**
:   Tenants sharing a cluster under namespace controls because they partly trust each other, versus tenants kept apart by separate clusters, nodes, or control planes.

**Blue-green cluster upgrade**
:   Upgrading by building a new cluster at the target version, shifting traffic to it, and retiring the old one.

**Policy exception**
:   A recorded, scoped, time-limited object that lets named resources skip a named admission policy.

**Emergency signer**
:   A separately controlled signing identity, used only under two-person approval when normal CI cannot build, whose every admission raises an alert.

**Evidence pack**
:   The linked records that prove one change or one running workload went through the required controls.

**Sync window**
:   A scheduled period in which a GitOps controller allows or denies automatic syncs.

**Version skew**
:   The allowed difference in minor versions between Kubernetes components, such as kubelets and the API server.

## Cost and sustainability

**FinOps**
:   A cross-functional practice that makes technology spend attributable and timely so teams can trade cost against business value.

**Showback**
:   Reporting each team's allocated cost to it without moving money between budgets.

**Chargeback**
:   Debiting allocated cost to the consuming team's budget.

**Unit economics**
:   Cost expressed per unit of business output, such as per order or per API call.

**Commitment coverage**
:   The share of eligible usage billed at a committed rather than on-demand rate.

**Commitment utilization**
:   The share of a purchased commitment actually consumed; unused commitment is still paid.

**Cost unit (CU)**
:   An abstract, illustrative unit of money this site uses for arithmetic instead of real prices.

**FOCUS (FinOps Open Cost and Usage Specification)**
:   The FinOps Open Cost and Usage Specification, a common format for billing data across vendors.

**Carbon intensity**
:   Grams of CO2-equivalent emitted per kWh of electricity for a given grid and time.

**Operational emissions**
:   Energy consumed by software multiplied by the carbon intensity of that energy.

**Embodied emissions**
:   Emissions from making, shipping, and disposing of hardware, allocated by time and resource share.

**Carbon-aware computing**
:   Software that changes when, where, or how much it computes in response to a grid carbon signal.

**Time shifting**
:   Running deferrable work in the lowest-intensity window before its deadline.

**Software Carbon Intensity (SCI)**
:   The Green Software Foundation specification, published as ISO/IEC 21031:2024, scoring emissions per functional unit as ((E × I) + M) per R.

**Functional unit**
:   The unit of useful output a carbon score is divided by.

**Power usage effectiveness (PUE)**
:   Total facility energy divided by the energy delivered to IT equipment.

## Enterprise architecture, migration, and frameworks

**Enterprise architecture (practice)**
:   Keeping strategy, business capabilities, and the application, data, and technology portfolio aligned across an organization over years.

**Application portfolio**
:   The inventory of applications with owner, capabilities served, cost, technical health, business fit, and lifecycle dates, used for keep, change, or retire decisions.

**TIME (Tolerate, Invest, Migrate, Eliminate)**
:   A rationalization model attributed to Gartner that places each application by functional and technical fit.

**Transition architecture**
:   An intermediate state between current and target architecture that the organization actually runs for a period.

**System of record**
:   The one application whose copy of a data entity is authoritative.

**Reference architecture**
:   A reusable solution template for a recurring problem, with components and decisions already made.

**Framework tailoring**
:   Choosing in writing which parts of a framework to use, renaming them locally, and dropping the rest with reasons.

**Framework theatre**
:   Producing a framework's artifacts and ceremonies without them changing any decision.

**7 Rs**
:   The seven migration strategies (rehost, replatform, refactor or re-architect, repurchase, retain, retire, relocate) chosen per application in a portfolio.

**Migration wave**
:   A batch of applications whose changes go live in the same planned window, grouped by dependency and risk.

**Move group**
:   The smallest set of components that must change together because splitting them across environments breaks or slows them.

**Cutover**
:   The controlled switch of traffic, writes, and ownership from an old system to its replacement.

**Parallel run**
:   Running old and new systems on the same inputs and comparing outputs before trusting the new one.

**Change data capture (CDC)**
:   Reading a database's change log to replicate inserts, updates, and deletes continuously to another store.

**Cloud adoption framework (CAF)**
:   Provider guidance on the organizational capabilities, decisions, and sequence needed to adopt its cloud.

**Cloud operating model**
:   Who decides, builds, runs, secures, and pays for cloud resources, and how those roles interact.

**Workload**
:   A set of components (code, configuration, cloud resources) that together deliver a business outcome; the unit an architecture review covers.

**Pillar (Well-Architected)**
:   One quality area, such as reliability or cost, under which a Well-Architected framework groups its principles and review questions.

**Lens (AWS Well-Architected)**
:   An extra set of questions and best practices for a technology, industry, or organization-specific context.

**High risk issue / medium risk issue (HRI / MRI)**
:   AWS's labels for a missing best practice that could cause significant, or lesser, business impact.

**Improvement plan**
:   The prioritised list of actions, with owners and targets, that removes risks found in a review.

**Milestone (review)**
:   A saved snapshot of a workload's review answers, used to show progress between reviews.

**Hybrid cloud**
:   On-premises or private infrastructure and at least one public cloud run as one estate with shared identity, network, data flows, and operations.

**Multi-cloud**
:   Using two or more public cloud providers, split by workload or running one workload on several.

**Cloud bursting**
:   Sending excess load from on premises (or one cloud) to a cloud when demand peaks.

**Data gravity**
:   The tendency of large data sets to keep applications near them because moving data costs time and money.

**Egress (data transfer)**
:   Data leaving a provider's network, usually metered per gigabyte.

**Exit plan**
:   A documented, periodically tested procedure and estimate for leaving a provider.

**Sovereign cloud**
:   A cloud offering designed so operations, access, and legal control stay within one jurisdiction.

**Rollback point**
:   The last moment at which returning to the old system is only a re-point, with no new writes to copy back.

**Logical replication**
:   Replicating row changes per table from a publisher to a subscriber, rather than copying physical storage blocks.

**Replication slot**
:   A server-side marker that keeps write-ahead log until a replica confirms receipt, so changes are not lost while it lags.

**Hypercare**
:   A fixed period of heightened monitoring and support right after go-live, during which rollback stays possible.

## Databases and storage

**Sort key**
:   A second key that orders items within one partition key and supports range and prefix queries.

**Item collection**
:   All items sharing one partition key value, readable together in one query.

**Access pattern**
:   A named question the application asks, with its inputs, ordering, rate, and latency target.

**Single-table design**
:   Storing several entity types in one table, keyed so items read together share a partition key.

**Global secondary index**
:   An index with its own partition key, stored apart from the base table and updated asynchronously.

**Local secondary index**
:   An index that keeps the base table's partition key but orders items by a different sort key.

**Write sharding (key salting)**
:   Adding a suffix to a hot partition key so its writes spread over several partitions, at the cost of read fan-out.

**Adaptive capacity**
:   A managed-service behaviour that shifts throughput toward, or splits, partitions that run hot.

**Declarative partitioning**
:   Declaring a table as partitioned in the schema so the engine routes rows to child tables by key and can prune them.

**Partition pruning**
:   The planner skipping partitions whose bounds cannot match a query's predicate.

**Federation (database)**
:   Splitting data into separate databases by function or domain, each owned by one service.

**Distributed SQL**
:   A SQL database that partitions and replicates data across nodes while keeping transactional guarantees across them.

**Logical decoding**
:   Converting write-ahead log records into row-level change events for consumers.

**Connection pooler**
:   A proxy that shares a small pool of server connections among many client connections.

**Write-ahead log (WAL)**
:   The ordered change log written before data pages, used for crash recovery, replication, and PITR.

**Hot/warm/cold data**
:   Data classified by how often it is read, which decides its storage tier and lifecycle.

**Query plan**
:   The access path and steps the engine has chosen for a query, as shown by EXPLAIN.

**Covering index**
:   An index containing every column a query needs, so the table is never visited.

**Composite index**
:   An index on several columns, sorted by the first column and then by each next one.

**Expression index**
:   An index on a computed expression, serving predicates written with that same expression.

**Block storage**
:   Raw volumes addressed by block offset that one host formats with its own filesystem.

**Object storage**
:   A flat namespace of whole, immutable objects read and written by key over HTTP.

**File storage (NAS)**
:   A shared directory tree served over NFS or SMB to many clients.

**Erasure coding**
:   Storing data as k fragments plus m parity fragments so that any k can rebuild it.

**Crash-consistent vs application-consistent snapshot**
:   A disk image as if power was cut, versus an image taken after the application flushed and marked a consistent point.

**Lifecycle policy**
:   Rules on a bucket that move objects to cheaper tiers and delete them by age or condition.

**Content-addressable storage**
:   Storing data under the hash of its bytes, so identical content has one address.

## Data engineering and analytics

**Data lineage**
:   The recorded path of data from its sources through each transformation to its consumers.

**Data steward**
:   The role that maintains a data set's definitions, quality rules, and catalog entry day to day.

**Data profiling**
:   Computing statistics on actual data (null rates, distinct values, ranges) to discover its real shape.

**Data quality dimension**
:   A measurable aspect of fitness for use, such as completeness, validity, or timeliness.

**OLTP (online transaction processing)**
:   A workload of many short transactions that read or write a few rows by key with strict correctness.

**OLAP (online analytical processing)**
:   A workload of large queries that scan many rows, read few columns, and aggregate them.

**Fact table**
:   A table of measurements of a business process, one row per event or state at the declared grain.

**Dimension table**
:   A table of descriptive attributes used to filter and group facts.

**Grain**
:   The exact business meaning of one row in a fact table.

**Star schema**
:   A fact table joined directly to denormalized dimension tables.

**Slowly changing dimension**
:   A technique (types 1, 2, 3, and hybrids) for handling changes to dimension attributes over time.

**Semantic layer**
:   A governed layer that defines business metrics and joins once for all BI tools.

**ETL / ELT**
:   ETL transforms data in a separate engine before loading; ELT loads raw data first and transforms it inside the destination.

**DAG (pipeline)**
:   A directed acyclic graph of tasks with dependency edges and no cycles, the shape an orchestrator runs.

**Backfill**
:   Running a pipeline for past periods to fill a gap or apply corrected logic to history.

**Idempotent task**
:   A pipeline task whose rerun for the same period gives the same output and no duplicates.

**Schema registry**
:   A service that stores versioned schemas per subject and checks each new version against a compatibility mode.

**Data contract**
:   An agreement between a producing team and consumers about a dataset's schema, meaning, quality, and how changes are announced.

**Write-audit-publish**
:   Writing new data where readers cannot see it, checking it, and making it visible only if checks pass.

**Late-arriving data**
:   Records whose event time falls in a period that has already been processed.

**Shuffle (data processing)**
:   Redistributing records across workers by key between stages (not shuffle sharding).

**Data skew**
:   Uneven spread of records over keys or partitions so one task does far more work than the rest.

**Salting**
:   Adding a suffix to a hot key so its records spread over several tasks, then merging partial results.

**Time travel**
:   Querying a table as of an earlier snapshot, version, or timestamp.

**Watermark**
:   A stream engine's running estimate that no more events older than time T will arrive, used to decide when a window can be finalized.

**Event time vs processing time**
:   When something happened at the source versus when the engine processes it.

**Data warehouse**
:   A database designed for analytical queries over integrated, historical, structured data, with its schema defined before loading.

**Data lake**
:   Low-cost object storage holding raw data in its original formats, given structure only when read.

**Lakehouse**
:   A data lake whose files are managed by an open table format, so warehouse-style SQL and machine learning share one transactional copy.

**Data mart**
:   A subset of analytical data shaped for one business area, fed from an EDW (dependent) or straight from sources (independent).

**Operational data store (ODS)**
:   An integrated, frequently updated, current-state copy of data from several operational systems, used for operational reporting.

**Data mesh**
:   An approach in which business domains own and publish analytical data as products on a self-serve platform under federated governance.

**Data product**
:   A data set published by its owning domain with a named owner, documented schema and meaning, quality and freshness objectives, and access rules.

**Medallion architecture**
:   A lake or lakehouse layering convention of Bronze (raw), Silver (cleaned, conformed), and Gold (business aggregates), with a contract at each boundary.

**Open table format**
:   A metadata specification over immutable data files that records each table version as a snapshot, giving atomic commits, schema evolution, and time travel.

**Data catalog**
:   A searchable register of datasets with owners, meanings, classifications, lineage, and the metadata pointers engines use to find and commit tables.

**Compaction**
:   Rewriting many small data files of a table into fewer large ones to cut metadata, request, and query-planning overhead.

**Snapshot expiry**
:   Removing old table versions so files only they reference can be deleted; retention and erasure are not physically complete until it runs.

**Schema drift**
:   An unannounced change in incoming data structure (renamed field, changed type) that breaks or silently corrupts downstream processing.

**Card chargeback (dispute)**
:   A cardholder's bank reversing a card payment on the merchant after a dispute (not the FinOps cost-allocation sense of chargeback).

**Feature store (online / offline)**
:   A system that serves the latest feature values per key at low latency (online) and keeps full feature history for training (offline) from shared definitions.

**Training/serving skew**
:   A model receiving different feature values in production than it was trained on, because of different code, data, or timing.

**Point-in-time join**
:   A join that attaches to each training example the feature values as they were at that example's timestamp, never later ones.

**Label maturity**
:   The age after which a decision's outcome label is treated as final for training.

## Event-driven systems and streaming

**Event time**
:   The time an event actually happened at its source, as opposed to when the pipeline received or processed it.

**Domain event**
:   An event belonging to one bounded context's internal model that may change whenever that model changes.

**Integration event**
:   An event published across team or service boundaries as a stable, versioned contract.

**Event contract**
:   The envelope, payload schema, meaning, and compatibility promises of an event type.

**CloudEvents**
:   A CNCF specification for common event metadata (id, source, type, specversion, and optional attributes) across systems.

**AsyncAPI**
:   A specification for describing event-driven APIs as channels, operations (send/receive), and messages.

**Dual write**
:   Updating a database and a broker as two separate operations, so one can succeed without the other.

**Offset**
:   The fixed position number a record receives when appended to a partition; consumers use it to remember where they stopped.

**Consumer lag**
:   How far a consumer group is behind the newest record in a partition, measured in records or, more usefully, in time.

**In-sync replica (ISR)**
:   A partition copy that is alive and caught up with the leader within a configured bound, so it can take over without losing acknowledged records.

**Hopping / sliding / session window**
:   Overlapping fixed-size windows / windows aligned to record timestamps / per-key windows that close after a gap of inactivity.

**Consumer group**
:   Consumer instances sharing one subscription to a topic, each partition read by one member at a time.

**Kafka-compatible**
:   A service that accepts the Kafka wire protocol, so Kafka clients connect by configuration change alone.

**Server-side filtering**
:   The broker evaluates a subscription's rule and delivers only matching messages.

**Replay**
:   Re-delivering already-consumed messages from retained data or an archive.

**Replica identity**
:   The columns PostgreSQL writes as the old-row key in update and delete events so a subscriber can find the affected row.

**Tombstone**
:   A record with a key and a null value that marks the key deleted, so log compaction can drop the key's earlier records.

**Log compaction**
:   A retention mode that keeps at least the newest record for each key instead of deleting records by age.

**Incremental (chunked) snapshot**
:   Copying existing rows in key-ordered chunks while change streaming continues, so no long transaction holds the source open.

**Heartbeat table**
:   A small table a CDC connector writes to regularly so the replication slot keeps advancing when captured tables are quiet.

**Allowed lateness**
:   How long a window's state is kept after the watermark passes, so late events can still update its result.

**Tumbling window**
:   A fixed-size event-time window that does not overlap the next one, such as each whole minute.

**Real-time OLAP store**
:   A column-oriented database that ingests continuously and answers aggregation queries over fresh data in under a second.

**HyperLogLog**
:   A small, mergeable sketch that estimates how many distinct items a set contains within a known error.

**Two-phase (local) aggregation**
:   Combining counts per key locally before sending them to the keyed operator, so one hot key cannot overload a single task.

**Request coalescing**
:   Merging identical concurrent requests into one backend query whose result is shared.

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
