from __future__ import annotations

import pytest
from pydantic import ValidationError

from nel_contracts.models.work import (
    DeliveryIntent,
    PublishIntent,
    SpendIntent,
    coerce_work_intent,
)
from tests.support import ULID_A, content_identity, fixed_now, human_actor


def _base() -> dict[str, object]:
    return {
        "intent_id": ULID_A,
        "actor": human_actor().model_dump(),
        "submitted_at": "2026-07-20T12:00:00Z",
    }


def test_discriminator_dispatches_to_the_right_member() -> None:
    publish = coerce_work_intent(
        {
            **_base(),
            "kind": "publish",
            "content_identity": {"content_digest": "a" * 64},
            "target_visibility": "public",
        }
    )
    assert isinstance(publish, PublishIntent)

    spend = coerce_work_intent(
        {**_base(), "kind": "spend", "amount_minor": 500, "currency": "USD", "payee": "acme"}
    )
    assert isinstance(spend, SpendIntent)


def test_publish_intent_forbids_a_rendered_body() -> None:
    with pytest.raises(ValueError, match="rendered body"):
        PublishIntent(
            intent_id=ULID_A,
            actor=human_actor(),
            submitted_at=fixed_now(),
            content_identity=content_identity(),
            target_visibility="public",  # type: ignore[arg-type]
            body="the brain body must never be held in the intent",  # type: ignore[call-arg]
        )


def test_delivery_intent_requires_content_identity() -> None:
    with pytest.raises(ValidationError):
        DeliveryIntent(
            intent_id=ULID_A,
            actor=human_actor(),
            submitted_at=fixed_now(),
            operation="deliver",  # type: ignore[arg-type]
        )


def test_delivery_binds_content_identity() -> None:
    delivery = DeliveryIntent(
        intent_id=ULID_A,
        actor=human_actor(),
        submitted_at=fixed_now(),
        content_identity=content_identity(),
        operation="deliver",  # type: ignore[arg-type]
    )
    assert delivery.content_identity.content_digest == "a" * 64
