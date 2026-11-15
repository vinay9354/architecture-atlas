---
title: Databases, storage, and caching
description: "Data outlives applications, so storage decisions are the hardest to reverse. This section goes from."
---

# Databases, storage, and caching

Data outlives applications, so storage decisions are the hardest to reverse. This section goes from
relational internals (indexes, query plans, isolation levels, locking) through NoSQL families and their
access-pattern-driven design, to sharding, replication, global databases, block/object/file storage,
and the caching layer that sits in front of all of it.

Every page states the workload under which its advice holds. "NoSQL is faster" is not a sentence you
will find here; "a wide-column store serves this access pattern at this scale because..." is.

## What you will learn here

- Model data relationally and know when to denormalize
- Read a query plan and fix the index, not the query, when that is the right move
- Pick a NoSQL family from the access pattern and design its partition key
- Design replication, failover, backups, and point-in-time recovery
- Choose a caching pattern and defend against stampedes, hot keys, and stale data

**Prerequisites:** [Foundations](../foundations/index.md) (data structures) and [Distributed systems](../distributed-systems/index.md) (consistency).

## Topics in this section

Every topic from the master curriculum that belongs to this section is listed below with its
status. A link means the page exists; `planned:` shows where it will be created. Status meanings
are explained in the [coverage matrix](../appendices/coverage-matrix.md).

<!-- coverage:start -->
| ID | Topic | Status | Page |
|---|---|---|---|
| **D06** | **Database, storage, and caching architecture** | | |
| D06-T01 | Relational databases and SQL internals | :material-circle-slice-5: Draft | [relational-databases-and-sql-internals](relational-databases-and-sql-internals.md) |
| D06-T02 | NoSQL databases | :material-circle-outline: Planned | planned: `databases-and-storage/nosql-databases.md` |
| D06-T03 | Advanced database architecture | :material-circle-outline: Planned | planned: `databases-and-storage/advanced-database-architecture.md` |
| D06-T04 | Storage architecture | :material-circle-outline: Planned | planned: `databases-and-storage/storage-architecture.md` |
| D06-T05 | Caching architecture | :material-circle-slice-5: Draft | [caching-architecture](caching-architecture.md) |
<!-- coverage:end -->

## How to continue

- Follow the [learning paths](../start-here/learning-path.md) for a recommended order.
- Look up unfamiliar terms in the [glossary](../start-here/glossary.md).
- Want to write one of the planned pages? See the
  [contribution guide](https://github.com/vinay9354/architecture-atlas/blob/main/CONTRIBUTING.md).
