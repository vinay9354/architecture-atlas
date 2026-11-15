---
title: Retrieval-Augmented Generation and vector search
description: "Retrieval-Augmented Generation (RAG) grounds model answers in your own documents. Done well it is the."
---

# Retrieval-Augmented Generation and vector search

Retrieval-Augmented Generation (RAG) grounds model answers in your own documents. Done well it is the
most practical enterprise AI pattern; done badly it hallucinates with citations. This section covers
RAG architecture and when to prefer it over fine-tuning or long context, ingestion and chunking,
embeddings and vector indexes, retrieval and reranking, advanced patterns (hybrid, GraphRAG, agentic,
multimodal, multi-tenant), and the components of a production RAG platform.

## What you will learn here

- Decide between RAG, fine-tuning, long context, and classic search
- Design an ingestion pipeline with chunking, metadata, deduplication, and re-indexing
- Choose embeddings, similarity metrics, and index types (HNSW, IVF, PQ) for scale
- Combine lexical, vector, and reranked retrieval and measure retrieval quality
- Enforce document-level access control and tenant isolation in retrieval

**Prerequisites:** [Generative AI and LLMs](../generative-ai-and-llms/index.md) and [Databases, storage, and caching](../databases-and-storage/index.md).

## Topics in this section

Every topic from the master curriculum that belongs to this section is listed below with its
status. A link means the page exists; `planned:` shows where it will be created. Status meanings
are explained in the [coverage matrix](../appendices/coverage-matrix.md).

<!-- coverage:start -->
| ID | Topic | Status | Page |
|---|---|---|---|
| **D22** | **Retrieval-Augmented Generation and vector search** | | |
| D22-T01 | RAG fundamentals | :material-circle-outline: Planned | planned: `rag-and-vector-search/rag-fundamentals.md` |
| D22-T02 | Document ingestion and chunking | :material-circle-outline: Planned | planned: `rag-and-vector-search/document-ingestion-and-chunking.md` |
| D22-T03 | Embeddings and vector indexes | :material-circle-outline: Planned | planned: `rag-and-vector-search/embeddings-and-vector-indexes.md` |
| D22-T04 | Retrieval, hybrid search, and reranking | :material-circle-outline: Planned | planned: `rag-and-vector-search/retrieval-hybrid-search-and-reranking.md` |
| D22-T05 | Advanced RAG patterns | :material-circle-outline: Planned | planned: `rag-and-vector-search/advanced-rag-patterns.md` |
| D22-T06 | RAG platform components | :material-circle-outline: Planned | planned: `rag-and-vector-search/rag-platform-components.md` |
<!-- coverage:end -->

## How to continue

- Follow the [learning paths](../start-here/learning-path.md) for a recommended order.
- Look up unfamiliar terms in the [glossary](../start-here/glossary.md).
- Want to write one of the planned pages? See the
  [contribution guide](https://github.com/vinay9354/architecture-atlas/blob/main/CONTRIBUTING.md).
