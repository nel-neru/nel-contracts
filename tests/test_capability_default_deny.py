from __future__ import annotations

import pytest
from pydantic import ValidationError

from nel_contracts.models.capability import Capability, CapabilityClassification


def test_internal_only_requires_no_egress() -> None:
    ok = Capability(
        capability_id="read-fixture",
        classification=CapabilityClassification("internal_only"),
        egress="none",
    )
    assert ok.egress == "none"


def test_internal_only_with_external_egress_is_rejected() -> None:
    with pytest.raises(ValidationError, match="internal_only"):
        Capability(
            capability_id="read-fixture",
            classification=CapabilityClassification("internal_only"),
            egress="external",
        )


def test_internal_only_with_kernel_channel_is_rejected() -> None:
    with pytest.raises(ValidationError, match="internal_only"):
        Capability(
            capability_id="read-fixture",
            classification=CapabilityClassification("internal_only"),
            egress="kernel_channel",
        )


def test_unknown_classification_downgrades_to_external() -> None:
    assert CapabilityClassification("mystery").classification == "external"
    # An unknown classification is external, so a capability with egress is allowed.
    cap = Capability(
        capability_id="net-call",
        classification=CapabilityClassification("mystery"),
        egress="external",
    )
    assert cap.classification.classification == "external"
