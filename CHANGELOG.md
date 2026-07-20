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
