from __future__ import annotations

from typing import Any, Literal

from nel_contracts.models.identifiers import SchemaVersion, Sha256Hex, StrictModel, UtcTimestamp


class WireEnvelope(StrictModel):
    """The neutral wire-envelope **schema** (a shape only) — NO client, NO network.

    It describes how a payload crosses the seam so non-Python consumers can validate the
    frame. The functional transport client is excluded from the behavior-free core (design §4)
    and lives kernel-side / in an OS-sandboxed runtime shim / behind an optional extra.
    """

    protocol_version: SchemaVersion
    schema_id: str
    payload_kind: Literal[
        "intent", "receipt", "reference", "observation", "decision", "ledger_event"
    ]
    body: dict[str, Any]
    content_digest: Sha256Hex | None = None
    issued_at: UtcTimestamp
