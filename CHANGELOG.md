# Changelog

All notable changes to `nel-contracts` are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to Semantic
Versioning with a wire-shape discipline:

- **Adding an open-enum member is a MINOR change** — old pinned consumers tolerate it because
  unknown members downgrade to a default-deny bucket (design D15).
- **A breaking wire-shape change is MAJOR** and moves the schema `$id` path segment
  (`.../contracts/v1/...`) and the per-envelope `schema_version` tag together.
- A documented compatibility window and deprecation policy governs any coordinated multi-repo
  bump (the governor is also a consumer, so a careless MAJOR must not strand public repos).

## [Unreleased]

## [0.3.0] - 2026-07-22

### Added
- K3 executor-competency + advisory-routing vocabulary (additive MINOR; realizes the neutral
  Executor/Capability shapes of ADR-0009 without granting any authority):
  - `models/executor.py`: `ExecutorCapability` (open vocabulary `implement`/`review`/`adjudicate`;
    unknown → the `non_executing` default-deny bucket — an unrecognized capability can never be
    scheduled), plus `RoutingSignal` and `RoutingAdvice` (ADVISORY shapes pinned
    `is_advisory=True`, modeled on the non-authoritative `ClaimedActor`: provider identity is the
    public `ActorKind` — a kernel maps its private runtime ids at the boundary, e.g. `claude` →
    `claude_code` — and counts are non-authoritative operator-calibration aggregates. A conforming
    consumer may at most reorder candidates its own hard filters admitted, re-deriving its
    exclusions AFTER reordering, and must fall back to its own deterministic order for any
    malformed hint).
  - Competency is deliberately DISTINCT from `models/capability.py::Capability`, whose
    default-deny invariant models egress blast radius, not competency.
  - Generated JSON Schemas (`routing-signal`, `routing-advice`) and conformance fixtures
    (valid and invalid, including the pinned-advisory rejection).

## [0.2.0] - 2026-07-20

### Added
- K2 neutral work generalization (additive MINOR; outward projection vocabulary only — the kernel
  `TaskEnvelope` remains the authoritative durable aggregate, ADR-0014 D3, nel-os K2 plan):
  - `models/workitem.py`: `WorkItem` (neutral core aggregate SHAPE — no git, no path, no routing),
    `GitWorkExtension` (public, **path-free**, mirrors `GitDeliveryExtension`; git-as-vocabulary,
    never git-as-location), `WorkItemId` (a superset of the ULID and the kernel `task-…` id shapes),
    `WorkStatus` (open projection of the kernel `TaskStatus`; unknown → `blocked`), `WorkKind`
    (unknown → `other`), `RiskLevel` (unknown → `critical`), `RiskClassification`.
  - `models/workflow.py`: `WorkflowDefinition`/`WorkflowNode` (neutral plan/DAG shell; full planner
    semantics land in W2) and `WorkflowRun` (advisory per D3). Distinct namespace from the nel-os
    kernel registry `WorkflowDefinition` — no rename, no collision.
  - Generated JSON Schemas (`work-item`, `git-work-extension`, `workflow-definition`, `workflow-run`)
    and conformance fixtures.

## [0.1.0]

### Added
- Initial local, unpushed G1 skeleton (DRAFT; ADRs D1–D17 unratified).
  - Neutral Pydantic v2 models: identifiers, open classifiers, actors (claimed vs attested),
    the `WorkIntent` discriminated union, content identity, seam DTOs, capability, approval
    (`GateClass` bound 1:1 to the human-gate SSOT), evidence, policy, visibility, repo metadata.
  - Two-verb `SeamPort` protocol, fail-closed `SealedSeam`, hardwired `resolve_seam()`, and the
    neutral wire-envelope shape.
  - RFC-8785 (JCS) reference canonicalizer and a hash-chained `LedgerEvent` / `RedactionEvent`.
  - Schema projector, private-dependency guard, and confinement/conformance tests.

Nothing is published. Cutting `v0.1.0` and pushing to a public repo are gated public-release
actions (design D17).
