"""Falsifiable tests for the K3 executor-competency + advisory-routing vocabulary."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from nel_contracts.models.capability import Capability
from nel_contracts.models.executor import (
    EXECUTOR_CAPABILITY_IDENTIFIERS,
    ExecutorCapability,
    RoutingAdvice,
    RoutingSignal,
)


def test_known_capabilities_classify_to_themselves() -> None:
    assert EXECUTOR_CAPABILITY_IDENTIFIERS == ("implement", "review", "adjudicate")
    for member in EXECUTOR_CAPABILITY_IDENTIFIERS:
        capability = ExecutorCapability(member)
        assert capability.is_known
        assert capability.classification == member


def test_unknown_capability_downgrades_to_the_non_executing_bucket() -> None:
    unknown = ExecutorCapability("deliver")
    assert not unknown.is_known
    assert unknown.classification == "non_executing"
    assert unknown.raw == "deliver"  # the wire value is preserved verbatim


def test_executor_capability_is_not_the_egress_capability() -> None:
    # Competency (what role a runtime can serve) is deliberately DISTINCT from
    # models/capability.py::Capability (whose default-deny invariant models egress blast radius).
    assert ExecutorCapability is not Capability
    assert not issubclass(ExecutorCapability, Capability)
    assert not issubclass(Capability, ExecutorCapability)


def test_routing_signal_is_pinned_advisory() -> None:
    signal = RoutingSignal.model_validate({"provider": "claude_code"})
    assert signal.is_advisory is True
    assert str(signal.provider) == "claude_code"
    with pytest.raises(ValidationError):
        RoutingSignal.model_validate({"provider": "codex", "is_advisory": False})


def test_routing_signal_counts_are_non_negative() -> None:
    with pytest.raises(ValidationError):
        RoutingSignal.model_validate({"provider": "codex", "false_positives": -1})


def test_routing_advice_is_pinned_advisory_and_open_on_provider() -> None:
    advice = RoutingAdvice.model_validate(
        {
            "signals": [{"provider": "codex", "finding_adoptions": 1}],
            "preferred": ["codex", "claude_code", "some-future-provider"],
        }
    )
    assert advice.is_advisory is True
    # An unknown provider deserializes (open vocabulary) and classifies to the untrusted bucket —
    # forward compatibility without granting the unknown member any standing.
    assert advice.preferred[2].classification == "external_unknown"
    with pytest.raises(ValidationError):
        RoutingAdvice.model_validate({"is_advisory": False})


def test_routing_shapes_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        RoutingSignal.model_validate({"provider": "codex", "authoritative": True})
    with pytest.raises(ValidationError):
        RoutingAdvice.model_validate({"gate_outcome": "approved"})
