from __future__ import annotations

import nel_contracts
from nel_contracts.version import PACKAGE_VERSION

_EXPECTED_EXPORTS = {
    "SeamPort",
    "SealedSeam",
    "resolve_seam",
    "WorkIntent",
    "SeamReceipt",
    "SeamObservation",
    "SeamReference",
    "GateClass",
    "LedgerEvent",
    "RedactionEvent",
    "canonical_json_bytes",
    "OpenClassifier",
}


def test_neutral_surface_is_exported() -> None:
    exported = set(nel_contracts.__all__)
    missing = _EXPECTED_EXPORTS - exported
    assert not missing, f"missing exports: {sorted(missing)}"
    for name in _EXPECTED_EXPORTS:
        assert hasattr(nel_contracts, name)


def test_no_provider_override_is_exported() -> None:
    assert "register_seam_provider" not in nel_contracts.__all__
    assert not hasattr(nel_contracts, "register_seam_provider")


def test_version_is_consistent() -> None:
    assert nel_contracts.__version__ == PACKAGE_VERSION
    assert PACKAGE_VERSION == "0.3.0"
