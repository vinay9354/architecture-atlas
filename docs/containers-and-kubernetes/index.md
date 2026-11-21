---
title: Containers, Kubernetes, and cloud-native architecture
description: "Containers package software with its dependencies; Kubernetes schedules and heals them at scale. This."
---

# Containers, Kubernetes, and cloud-native architecture

Containers package software with its dependencies; Kubernetes schedules and heals them at scale. This
section covers images and runtimes, the Kubernetes control plane and workload objects, networking,
storage, and service mesh, and the surrounding ecosystem (Helm, Argo CD, Karpenter, cert-manager,
OpenTelemetry, Istio, Cilium, Kyverno, and others). The goal is to design and operate platforms, not to
memorize kubectl commands.

## What you will learn here

- Explain namespaces, cgroups, images, layers, and supply-chain controls (signing, SBOM, scanning)
- Describe how a Pod gets scheduled, networked, and given storage, and what breaks at each step
- Design multi-tenant, highly available clusters with RBAC, network policies, and admission control
- Pick ecosystem tools for GitOps, autoscaling, secrets, certificates, and observability

**Prerequisites:** [Foundations](../foundations/index.md) (operating systems) and [Networking](../networking/index.md).

## Topics in this section

Every topic from the master curriculum that belongs to this section is listed below with its
status. A link means the page exists; `planned:` shows where it will be created. Status meanings
are explained in the [coverage matrix](../appendices/coverage-matrix.md).

<!-- coverage:start -->
| ID | Topic | Status | Page |
|---|---|---|---|
| **D11** | **Containers, Kubernetes, and cloud-native architecture** | | |
| D11-T01 | Containers and images | :material-circle-slice-5: Draft | [containers-and-images](containers-and-images.md) |
| D11-T02 | Kubernetes architecture and workloads | :material-circle-slice-5: Draft | [kubernetes-architecture-and-workloads](kubernetes-architecture-and-workloads.md) |
| D11-T03 | Kubernetes networking, storage, and service mesh | :material-circle-slice-5: Draft | [kubernetes-networking-storage-and-service-mesh](kubernetes-networking-storage-and-service-mesh.md) |
| D11-T04 | Cloud-native ecosystem tools | :material-circle-slice-5: Draft | [cloud-native-ecosystem-tools](cloud-native-ecosystem-tools.md) |
<!-- coverage:end -->

## How to continue

- Follow the [learning paths](../start-here/learning-path.md) for a recommended order.
- Look up unfamiliar terms in the [glossary](../start-here/glossary.md).
- Want to write one of the planned pages? See the
  [contribution guide](https://github.com/vinay9354/architecture-atlas/blob/main/CONTRIBUTING.md).
