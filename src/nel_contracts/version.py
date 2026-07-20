from __future__ import annotations

from typing import Final

import pydantic

# Distribution version of ``nel-contracts`` (SemVer). Enum-add == MINOR, breaking wire
# shape == MAJOR (embedded in the schema ``$id`` path). See CHANGELOG.md.
PACKAGE_VERSION: Final[str] = "0.2.0"

# The contract MAJOR line. A breaking shape change increments this and the schema ``$id``
# path segment (``.../contracts/v1/...``) together.
CONTRACT_MAJOR: Final[int] = 1

# Base ``$id`` for every generated JSON Schema. A URN is used deliberately for the local,
# unpublished skeleton so no public host/domain is claimed before the D17 publish gate.
# TODO(K1/K3): the D17 public-release gate may rebase this to the public host-of-record URL.
SCHEMA_ID_BASE: Final[str] = f"urn:nel:contracts:v{CONTRACT_MAJOR}"

# Negotiated protocol handshake version. A provider rejects an incompatible contract
# version fail-closed rather than silently degrading (design §7).
PROTOCOL_VERSION: Final[str] = "1.0"

# Projector version, recorded alongside each generated schema. The wire form is generated from
# pinned pydantic + type-level overrides and guarded by a generate-and-diff gate: a pydantic
# bump that changes the emitted output fails CI until it is reviewed and regenerated. This is
# not a fully decoupled hand-controlled projection layer — that is deferred (K-phase) (§7).
PROJECTOR_VERSION: Final[str] = "1"

# The package ships NO kernel verification key and NO attestation secret (design §0/§4).
# Trust in a receipt/decision is established only by the out-of-process K1 kernel, never by
# this in-world package. This constant is the grounded reason every package-side trust check
# is fail-closed.
KERNEL_VERIFICATION_KEY: Final[None] = None


def generator_toolchain() -> dict[str, str]:
    """Return the toolchain identity recorded alongside each generated schema asset."""
    return {
        "projector_version": PROJECTOR_VERSION,
        "pydantic_version": pydantic.VERSION,
        "contract_major": str(CONTRACT_MAJOR),
        "package_version": PACKAGE_VERSION,
    }
