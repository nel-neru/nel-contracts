# Conformance corpus

A portable, synthetic fixture corpus that pins the wire contract's behavior across all future
language ports. Fixtures contain **no** `C:\Users` paths and no private repo names.

## `fixtures/canonical/`

Golden canonical byte-fixtures for the RFC-8785 (JCS) profile (design D14). `basic.json` is the
input; `basic.bytes` is the exact canonical UTF-8 output. The digest chain computes over these
bytes, so every language port must reproduce them byte-for-byte. Pinned by
`tests/test_canonical_golden_bytes.py`.

## `fixtures/openenum/`

Inputs whose wire classification member is unknown to a pinned consumer. They must **downgrade
to the default-deny bucket, never raise** (design D15) — e.g. an unknown `kind` becomes
`OtherIntent` (external/blocked). Behavior pinned by `tests/test_open_enum_downgrade.py`.

## `fixtures/forgery/`

World-constructed receipts / decision records that *claim* kernel authority. They are
indistinguishable from a genuine one **at the shape level**, which is exactly the point: the
package ships no verification key, so they are provably untrusted (design §0). Behavior pinned
by `tests/test_forged_authority_untrusted.py`.

> The authoritative confinement controls live in K1 (credential absence, OS default-deny
> egress, an out-of-process authenticating kernel). This corpus is corroboration, not the
> control.
