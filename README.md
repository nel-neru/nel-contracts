# nel-contracts

Neutral vocabulary and a fail-closed inversion-of-control **seam port** for the NEL Platform.

- **Distribution:** `nel-contracts` · **import root:** `nel_contracts`
- **Governor (author / versioner / sole provider):** `nel-os` (private kernel)
- **Host of record (eventual):** a standalone **public** repo. This tree is **local and
  unpushed**; creating and pushing the public repo, and publishing a version, are gated
  public-release actions (design D17).
- **License:** Apache-2.0 · **Runtime dependency:** a narrowly pinned pydantic v2, stdlib only.

> Status: DRAFT skeleton for an as-yet-unratified design (ADRs D1–D17). See
> `docs/plans/NEL_G1_CONTRACT_PACKAGE_DESIGN.md` in `nel-os` for the full dossier.

## §0 Confinement note (read first)

**This package ships vocabulary + a fail-closed default. It does NOT itself enforce
confinement.** Every mechanism here — `SealedSeam`, `resolve_seam()`, the seam DTOs — executes
**inside the untrusted world process**, and an in-process check is no defense against an
in-process adversary. Possessing a Pydantic class is full construction authority: any importer
can build a `SeamReceipt(state="accepted", authority="kernel")` or a human-authored
`DecisionRecord`. Those instances are **untrusted** because this package ships **no** kernel
verification key and **no** attestation secret.

What this package delivers:

- the neutral **vocabulary** (open-enum wire types that never crash on an unknown member),
- the two-verb **seam port** interface (`submit_intent`, `observe`),
- a **fail-closed default** resolution (`resolve_seam()` returns `SealedSeam`),
- **canonical bytes** (RFC-8785 JCS) and a hash-chained ledger envelope,
- CI/conformance **guards**.

The **real** confinement lives in **K1** (the private kernel) and is a set of preconditions
this package documents but cannot enforce:

1. the world runtime holds **zero external-mutation credentials**;
2. OS/network namespace **default-deny** to every destination except the kernel channel;
3. the kernel runs as a **separate authenticated process/host** that treats all inbound
   `intent`/`actor`/`authority` fields as untrusted and **re-derives** them.

Zero-call-on-block and negative credential/egress tests are *corroboration*, not the control.

## The seam

```python
from nel_contracts import resolve_seam, SealedSeam, WorkIntent

seam = resolve_seam()            # hardwired fail-closed -> SealedSeam unless a deployment
                                 # binding wires the out-of-process kernel channel (K1).
assert isinstance(seam, SealedSeam)
```

`SeamPort` has **exactly** two verbs and is governance-locked (design D12):

```python
class SeamPort(Protocol):
    def submit_intent(self, intent: WorkIntent) -> SeamReceipt: ...
    def observe(self, ref: SeamReference) -> SeamObservation: ...
```

There is deliberately **no** `register_seam_provider` and no world-callable in-process provider
override. Only an out-of-process deployment binding — supplied by the K1 kernel — can yield a
non-sealed seam.

## Consumption

Pin an exact tag and inject a provider at your composition root (`SealedSeam` by default). Pin,
**do not vendor**. Non-Python consumers generate types from the pinned `schemas/` release
assets. No public consumer installs or imports the private governor (`nel-os`); CI enforces that
no private package appears in any dependency section.

## Verification

```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows; use bin/activate on POSIX
pip install -e .[dev]
ruff check .
ruff format --check .
mypy src
pytest -q
python scripts/project_schemas.py --check          # schema drift
python scripts/check_no_private_deps.py            # no private dep in any section
```
