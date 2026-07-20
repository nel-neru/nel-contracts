from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

from pydantic import Field

from nel_contracts.canonical.jcs import canonical_json_bytes, sha256_hex
from nel_contracts.models.identifiers import Sha256Hex, StrictModel, Ulid, UtcTimestamp

# The genesis link: the first event chains from 64 zero hex digits.
GENESIS_DIGEST: Final[str] = "0" * 64


class LedgerEvent(StrictModel):
    """A reusable append-only ledger envelope with a digest hash chain (design D2 extension).

    The digest binds the previous link to EVERY non-chaining field of this event. The exact
    preimage is the raw bytes of ``prev_event_digest`` concatenated with the D14 canonical JSON
    of the full non-chaining field set ``{event_id, sequence, issued_at, body}``::

        preimage     = bytes.fromhex(prev_event_digest) + canonical_bytes(
                           {event_id, sequence, issued_at, body})
        event_digest = sha256(preimage)                      # 64 lowercase hex

    ``event_digest`` is derived, not stored. Computing over the canonical bytes (not
    re-serialized bodies) is what lets all four language ports reproduce identical digests.
    World-authored instances are non-authoritative — this is a shared envelope, not a trust root.
    """

    event_id: Ulid
    sequence: int = Field(ge=0)
    prev_event_digest: Sha256Hex
    body: dict[str, Any] = Field(default_factory=dict)
    issued_at: UtcTimestamp

    def canonical_content_bytes(self) -> bytes:
        """Canonical bytes over the full non-chaining field set ``{event_id, sequence,
        issued_at, body}``. ``prev_event_digest`` is excluded here and prepended as raw bytes
        in :meth:`event_digest`; ``event_digest`` is derived and never part of the preimage."""
        content = self.model_dump(mode="json", exclude={"prev_event_digest"})
        return canonical_json_bytes(content)

    def event_digest(self) -> str:
        """This event's digest, chaining over ``prev_event_digest`` and the content bytes."""
        return sha256_hex(bytes.fromhex(self.prev_event_digest) + self.canonical_content_bytes())


def link_event(
    *,
    event_id: str,
    body: Mapping[str, Any],
    issued_at: Any,
    previous: LedgerEvent | None,
) -> LedgerEvent:
    """Build the next event in a chain from the previous event (or genesis)."""
    if previous is None:
        sequence = 0
        prev_digest = GENESIS_DIGEST
    else:
        sequence = previous.sequence + 1
        prev_digest = previous.event_digest()
    return LedgerEvent(
        event_id=event_id,
        sequence=sequence,
        prev_event_digest=prev_digest,
        body=dict(body),
        issued_at=issued_at,
    )


def verify_chain(events: Sequence[LedgerEvent]) -> bool:
    """Verify sequence contiguity and the digest hash chain over an event sequence."""
    expected_prev = GENESIS_DIGEST
    for index, event in enumerate(events):
        if event.sequence != index:
            return False
        if event.prev_event_digest != expected_prev:
            return False
        expected_prev = event.event_digest()
    return True
