---
title: AI infrastructure, model serving, and LLMOps
description: "Serving models is a systems problem: GPUs are expensive, memory-bound, and awkward to schedule."
---

# AI infrastructure, model serving, and LLMOps

Serving models is a systems problem: GPUs are expensive, memory-bound, and awkward to schedule.
This section covers GPU architecture and distributed training, model serving and inference
optimization (batching, KV cache, quantization, streaming, autoscaling), the serving technology
landscape (Triton, vLLM, TensorRT-LLM, KServe, Ray, BentoML, and more), and the platform layer
(registries, gateways, prompt management, experiment tracking, LLMOps).

## What you will learn here

- Explain why inference is memory-bound and what KV cache and batching do about it
- Design a serving architecture with routing, fallback, quotas, and autoscaling
- Compare serving technologies on the dimensions that matter for your workload
- Build an AI platform with multi-tenancy, isolation, and CI/CD for models

**Prerequisites:** [Containers and Kubernetes](../containers-and-kubernetes/index.md) and [Generative AI and LLMs](../generative-ai-and-llms/index.md).

## Topics in this section

Every topic from the master curriculum that belongs to this section is listed below with its
status. A link means the page exists; `planned:` shows where it will be created. Status meanings
are explained in the [coverage matrix](../appendices/coverage-matrix.md).

<!-- coverage:start -->
| ID | Topic | Status | Page |
|---|---|---|---|
| **D24** | **AI infrastructure, model serving, and LLMOps/GenAIOps** | | |
| D24-T01 | GPU infrastructure and distributed training | :material-circle-outline: Planned | planned: `ai-infrastructure-and-llmops/gpu-infrastructure-and-distributed-training.md` |
| D24-T02 | Model serving and inference | :material-circle-outline: Planned | planned: `ai-infrastructure-and-llmops/model-serving-and-inference.md` |
| D24-T03 | Serving technologies compared | :material-circle-outline: Planned | planned: `ai-infrastructure-and-llmops/serving-technologies-compared.md` |
| D24-T04 | AI platform and LLMOps | :material-circle-outline: Planned | planned: `ai-infrastructure-and-llmops/ai-platform-and-llmops.md` |
<!-- coverage:end -->

## How to continue

- Follow the [learning paths](../start-here/learning-path.md) for a recommended order.
- Look up unfamiliar terms in the [glossary](../start-here/glossary.md).
- Want to write one of the planned pages? See the
  [contribution guide](https://github.com/vinay9354/architecture-atlas/blob/main/CONTRIBUTING.md).
