---
title: Agentic AI, multi-agent systems, MCP, and A2A
description: "Agents are LLM-driven programs that plan, call tools, observe results, and iterate toward a goal."
---

# Agentic AI, multi-agent systems, MCP, and A2A

Agents are LLM-driven programs that plan, call tools, observe results, and iterate toward a goal.
This section covers what distinguishes an agent from an assistant, the components of an agent
runtime, single- and multi-agent patterns (ReAct, plan-and-execute, supervisor-worker, critic loops,
human-in-the-loop), memory, tool design and authorization, the Model Context Protocol (MCP) and
Agent-to-Agent (A2A) protocols, and the hard parts of long-running, durable, governed agents.
Protocol details are checked against current specifications and dated.

## What you will learn here

- Decide when a deterministic workflow beats an autonomous agent
- Design an agent runtime with tool registry, authorization, approvals, and audit
- Choose a multi-agent pattern and bound its autonomy and cost
- Explain MCP hosts, clients, servers, tools, resources, and transports, and A2A discovery and delegation
- Make agents durable: checkpoint, resume, loop detection, execution limits

**Prerequisites:** [Generative AI and LLMs](../generative-ai-and-llms/index.md) and [RAG and vector search](../rag-and-vector-search/index.md).

## Topics in this section

Every topic from the master curriculum that belongs to this section is listed below with its
status. A link means the page exists; `planned:` shows where it will be created. Status meanings
are explained in the [coverage matrix](../appendices/coverage-matrix.md).

<!-- coverage:start -->
| ID | Topic | Status | Page |
|---|---|---|---|
| **D23** | **Agentic AI, multi-agent systems, MCP, and A2A** | | |
| D23-T01 | Agent fundamentals | :material-circle-outline: Planned | planned: `agentic-ai/agent-fundamentals.md` |
| D23-T02 | Agent components and runtime | :material-circle-outline: Planned | planned: `agentic-ai/agent-components-and-runtime.md` |
| D23-T03 | Agent and multi-agent patterns | :material-circle-outline: Planned | planned: `agentic-ai/agent-and-multi-agent-patterns.md` |
| D23-T04 | Agent memory | :material-circle-outline: Planned | planned: `agentic-ai/agent-memory.md` |
| D23-T05 | Tools and actions | :material-circle-outline: Planned | planned: `agentic-ai/tools-and-actions.md` |
| D23-T06 | MCP and A2A protocols | :material-circle-outline: Planned | planned: `agentic-ai/mcp-and-a2a-protocols.md` |
| D23-T07 | Advanced and long-running agents | :material-circle-outline: Planned | planned: `agentic-ai/advanced-and-long-running-agents.md` |
<!-- coverage:end -->

## How to continue

- Follow the [learning paths](../start-here/learning-path.md) for a recommended order.
- Look up unfamiliar terms in the [glossary](../start-here/glossary.md).
- Want to write one of the planned pages? See the
  [contribution guide](https://github.com/vinay9354/architecture-atlas/blob/main/CONTRIBUTING.md).
