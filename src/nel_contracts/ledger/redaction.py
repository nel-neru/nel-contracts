from __future__ import annotations

from datetime import datetime
from typing import Final, Literal

from nel_contracts.models.identifiers import StrictModel, Ulid, UtcTimestamp

REDACTION_PLACEHOLDER: Final[str] = "[REDACTED]"


class RedactionEvent(StrictModel):
    """A typed redaction record that carries **no** secret bytes and no secret-derived digest.

    Unsafe or unparseable secret-bearing payloads are discarded and represented by one of
    these. It records only the *location* (``redacted_key_path``) and *reason*, never the
    redacted content. ``extra="forbid"`` (via ``StrictModel``) structurally prevents smuggling
    a ``secret``/``content`` field into the record.
    """

    redaction_id: Ulid
    reason: Literal["secret_detected", "unparseable", "policy"]
    redacted_key_path: str | None = None
    placeholder: Literal["[REDACTED]"] = "[REDACTED]"
    occurred_at: UtcTimestamp

    @classmethod
    def for_secret(
        cls, *, redaction_id: str, key_path: str, occurred_at: datetime
    ) -> RedactionEvent:
        return cls(
            redaction_id=redaction_id,
            reason="secret_detected",
            redacted_key_path=key_path,
            occurred_at=occurred_at,
        )
