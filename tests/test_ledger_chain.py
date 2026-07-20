from __future__ import annotations

from nel_contracts.ledger.event import GENESIS_DIGEST, LedgerEvent, link_event, verify_chain
from tests.support import ULID_A, ULID_B, ULID_C, fixed_now


def _chain() -> list[LedgerEvent]:
    e0 = link_event(event_id=ULID_A, body={"kind": "genesis"}, issued_at=fixed_now(), previous=None)
    e1 = link_event(event_id=ULID_B, body={"kind": "decision"}, issued_at=fixed_now(), previous=e0)
    e2 = link_event(event_id=ULID_C, body={"kind": "capture"}, issued_at=fixed_now(), previous=e1)
    return [e0, e1, e2]


def test_genesis_and_contiguity() -> None:
    events = _chain()
    assert events[0].prev_event_digest == GENESIS_DIGEST
    assert [event.sequence for event in events] == [0, 1, 2]
    assert verify_chain(events) is True


def test_digest_is_deterministic_and_hex() -> None:
    events = _chain()
    digest = events[1].event_digest()
    assert len(digest) == 64
    assert all(character in "0123456789abcdef" for character in digest)
    assert events[1].event_digest() == digest


def test_broken_prev_link_fails_verification() -> None:
    events = _chain()
    tampered = events[1].model_copy(update={"prev_event_digest": "0" * 63 + "1"})
    assert verify_chain([events[0], tampered, events[2]]) is False


def test_body_tamper_breaks_downstream_link() -> None:
    events = _chain()
    # Rewriting an event's body changes its digest, so the next event's prev link no longer
    # matches — the chain fails downstream even though the rewritten event looks internally fine.
    forged_e1 = events[1].model_copy(update={"body": {"kind": "decision", "tampered": True}})
    assert verify_chain([events[0], forged_e1, events[2]]) is False
