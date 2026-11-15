---
title: "Quiz: Architecture thinking, requirements, and design fundamentals (D01)"
description: "Fifteen self-assessment questions across three levels for the architecture fundamentals domain, with hidden answers and links back to the pages."
domain: "Architecture thinking, requirements, and design fundamentals"
level: Mixed
status: Draft
estimated_time: "30-40 minutes"
last_verified: 2026-11-15
tags:
  - quiz
  - architecture-fundamentals
  - level-1-understand
  - level-2-apply
  - level-3-architect
---

# Quiz: Architecture thinking, requirements, and design fundamentals (D01)

Fifteen questions in three levels. Write your answer before opening the hidden one; the point is to
notice what you cannot yet explain. Every answer links to the page that covers it. Questions use the
AtlasMart order-tracking scenario that runs through the D01 pages; nothing here tests product names
or numbers you would look up in practice.

!!! abstract "Quiz facts"
    **Covers:** D01-T01 to D01-T08 · **Questions:** 15 (5 per level) · **Time:** 30-40 minutes ·
    **Status:** Draft · **Last verified:** 2026-11-15

## Level 1 — Understand

**1.** A stakeholder says "the tracking page must be reliable." Name the three distinct quality
attributes this sentence could mean, and say why an architect cannot design to it as written.

??? success "Answer"
    Availability (reachable when needed), durability (acknowledged data is not lost), and correctness
    or reliability in the narrow sense (behaves as specified). Each is measured differently and
    protected by different mechanisms, so one word cannot be turned into a design or a test. The
    [requirements page](../architecture-fundamentals/functional-vs-non-functional-requirements.md)
    shows the rewrite into separate, measurable statements.

**2.** What is the difference between a functional requirement and a non-functional requirement, and
which of the two shapes architecture more?

??? success "Answer"
    A functional requirement states what the system must do (a behaviour or capability); a
    non-functional requirement states how well it must do it (a measurable quality attribute target).
    Non-functional requirements shape architecture more: the same features at 99% versus 99.99%
    availability, or at 10 versus 10,000 requests per second, lead to different systems.
    ([Functional vs non-functional requirements](../architecture-fundamentals/functional-vs-non-functional-requirements.md))

**3.** Put these in the right relationship: SLA, SLO, SLI, error budget.

??? success "Answer"
    An SLI is the measurement (for example, the fraction of requests served under 300 ms). An SLO is
    the internal target for that SLI over a period. The error budget is what the SLO permits to go
    wrong (100% minus the SLO), spent by incidents and risky changes. An SLA is the external contract,
    set looser than the SLO, with consequences if missed.
    ([SLAs, SLOs, SLIs, error budgets](../architecture-fundamentals/slas-slos-slis-error-budgets-and-recovery-objectives.md))

**4.** Which C4 diagram would you show a new engineer on their first day, and which would you show
the head of customer experience? Why the difference?

??? success "Answer"
    The engineer: the container diagram, which shows the deployable units, their technologies, and
    how they talk. The head of customer experience: the system context diagram, which shows the
    system as one box with its users and external systems. Each audience needs a different zoom
    level; showing the wrong one wastes the meeting.
    ([The C4 model](../architecture-fundamentals/c4-model.md))

**5.** What is a constraint, and how does it differ from a requirement?

??? success "Answer"
    A constraint is a fixed condition the design must satisfy and cannot negotiate away (a
    regulation, an existing platform standard, a budget, a deadline). A requirement describes what
    the system must achieve and can be traded, prioritized, or rewritten. Constraints narrow the
    design space before any option is considered.
    ([Constraints, assumptions, dependencies, risks, and scope](../architecture-fundamentals/constraints-assumptions-dependencies-risks-and-scope.md))

## Level 2 — Apply

**6.** AtlasMart's NFR-2 says the tracking view is available 99.9% per calendar month. How many
minutes of downtime does that allow in a 30-day month, and what single design choice does it rule out
first?

??? success "Answer"
    0.1% of 30 × 24 × 60 = 43,200 minutes is about 43.2 minutes (the pages round to 43.8 using a
    30.4-day average month; either is fine at this precision). It rules out any single instance or
    single zone for the read path, because one host or zone failure plus recovery time would consume
    the whole month's budget in one event.
    ([Quality attributes and trade-offs](../architecture-fundamentals/quality-attributes-and-trade-offs.md))

**7.** Rewrite "the system should scale" into a testable non-functional requirement for AtlasMart,
naming where the number would come from.

??? success "Answer"
    Something like: "The tracking service handles 210 tracking reads per second and 70 scan events
    per second with CPU utilization under 70% and p95 latency within the NFR-3 target." The numbers
    come from the capacity estimate (DAU, orders per day, views per order, peak factor, sale-day
    burst), not from preference.
    ([Capacity estimation](../performance-and-scalability/capacity-estimation.md))

**8.** The head of customer experience asked for "a mobile app". Why was that the wrong first
question, and what should the architect have asked instead?

??? success "Answer"
    It is a solution, not a problem statement. The business goal was fewer "where is my order"
    support calls; the stakeholder analysis and capability map show that customers lack timely status
    information, which can be fixed in the existing web account for far less. The right first
    questions are: what outcome, measured how, for whom, by when, under which constraints.
    ([Stakeholders, business capabilities, and success metrics](../architecture-fundamentals/stakeholders-business-capabilities-and-success-metrics.md))

**9.** Give one example each of a technical constraint, a business constraint, an assumption, and a
dependency for the tracking project, and say what should happen to the assumption.

??? success "Answer"
    Technical constraint: PostgreSQL is the platform's standard relational database. Business
    constraint: launch before peak season. Assumption: carriers deliver webhooks within seconds of a
    scan. Dependency: the Order Management System exposes order ownership by order ID. An assumption
    is a risk until verified, so it goes into the RAID log with an owner and a verification step (for
    example, the proof of concept measures webhook latency).
    ([Constraints, assumptions, dependencies, risks, and scope](../architecture-fundamentals/constraints-assumptions-dependencies-risks-and-scope.md))

**10.** An ADR for AtlasMart's queue choice has been accepted. Six months later a better option
appears. What do you do with the ADR?

??? success "Answer"
    Leave it unchanged and write a new ADR that supersedes it, linking both ways. ADRs are a history
    of decisions with their context at the time; editing an accepted one destroys the record of why
    the earlier choice made sense.
    ([Trade-offs, principles, ADRs, and governance](../architecture-fundamentals/trade-offs-principles-adrs-and-architecture-governance.md))

## Level 3 — Architect

**11.** Build versus buy: AtlasMart could license a tracking-page SaaS product. Name three criteria
that would favour buying, two that would favour building, and the question that usually decides it.

??? success "Answer"
    Favour buying: the capability is not a differentiator, time to market matters (peak season), and
    the vendor already integrates with the carriers. Favour building: the data and privacy constraint
    (no delivery addresses leaving the platform; NFR-6) and tight integration with the order system and
    identity provider. The deciding question: is this capability core to how AtlasMart competes, or a
    commodity? Commodities are bought; differentiators are built.
    ([As-Is and To-Be architecture, gap analysis, and build vs buy](../architecture-fundamentals/as-is-and-to-be-architecture-gap-analysis-and-build-vs-buy.md))

**12.** The team wants NFR-1 tightened from 60 seconds to 5 seconds of freshness. Describe the
trade-offs that change and what you would ask before agreeing.

??? success "Answer"
    Freshness trades against cost and complexity: a 5-second target makes the 30-second cache TTL
    unusable, pushes toward event-driven cache invalidation or push updates, tightens the queue's
    allowable backlog, and makes carrier latency (outside AtlasMart's control) the dominant risk.
    Ask: which customer outcome needs 5 seconds, how would we measure it end to end including the
    carrier, and what is the cost of the extra machinery against the support-call goal.
    ([Quality attributes and trade-offs](../architecture-fundamentals/quality-attributes-and-trade-offs.md))

**13.** Explain why the Tracking API runs three instances when the capacity estimate shows one would
carry the peak, and name the requirement that forces it.

??? success "Answer"
    NFR-2 (99.9% monthly) requires surviving a zone failure, the platform standard is three zones, and
    N+1 means the instances that remain after a failure must still carry the peak under the
    utilization target. The footprint is set by availability, not load.
    ([Capacity estimation](../performance-and-scalability/capacity-estimation.md))

**14.** A new product launch has unknown demand; the peak factor could be anywhere from 3 to 15.
How do you write the scale requirement and the operating plan so that you neither over-build nor
fail on launch day?

??? success "Answer"
    State the uncertainty explicitly: design for a peak factor of 3-5 with autoscaling, load-test to
    15, and define degradation behaviour (rate limiting, cached or simplified responses, load
    shedding of non-critical work) above the tested point. Put the shedding thresholds and the
    launch-day on-call plan in the requirements, and measure the actual peak so the next estimate
    replaces the guess.
    ([Capacity estimation](../performance-and-scalability/capacity-estimation.md) and
    [SLOs and error budgets](../architecture-fundamentals/slas-slos-slis-error-budgets-and-recovery-objectives.md))

**15.** Design a lightweight governance process for a 40-engineer company that wants ADRs and design
reviews without an architecture review board that blocks every change. What are the parts and what
makes it lightweight?

??? success "Answer"
    Parts: a short set of principles with rationale; ADRs required only for decisions that are
    expensive to reverse or cross team boundaries; a design review that is a conversation on a one-page
    design plus the ADR, with a clear "who must attend" rule; fitness functions in CI for the
    properties the principles protect; a technical-debt register reviewed quarterly. It is lightweight
    because approval is pushed to the team for reversible decisions, reviews are asynchronous by
    default, and the automated checks replace standing committees.
    ([Trade-offs, principles, ADRs, and governance](../architecture-fundamentals/trade-offs-principles-adrs-and-architecture-governance.md))

## Scoring yourself

- 12-15 explained without opening the answers: you are ready for the distributed systems and data
  pages.
- 8-11: reread the pages linked in the answers you missed; they are short.
- Under 8: start again from [What does a Solutions Architect do?](../architecture-fundamentals/what-does-a-solutions-architect-do.md)
  and do the in-page labs rather than reading only.

## Review notes

- Answers for questions 8, 9, 10, 11, and 15 depend on the Phase 2 pages; a reviewer should check
  they match those pages' wording once reviewed.
- Question 6 notes the 43.2 versus 43.8 minute difference explicitly so that neither page nor quiz
  looks wrong to a careful reader.
