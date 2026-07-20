from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from nel_contracts.models.approval import GATE_CLASS_IDENTIFIERS, GateClass

_VENDORED_SSOT = Path(__file__).resolve().parent / "data" / "human_gates.yaml"


def _load_human_gates(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    gates = data["human_gates"]
    assert isinstance(gates, list)
    return [str(item) for item in gates]


def test_gateclass_is_1to1_with_vendored_ssot() -> None:
    gates = _load_human_gates(_VENDORED_SSOT)
    assert GateClass.known_values() == set(gates)
    assert tuple(gates) == GATE_CLASS_IDENTIFIERS


def test_every_gate_is_human_gated() -> None:
    for identifier in GATE_CLASS_IDENTIFIERS:
        assert GateClass(identifier).is_human_gated is True


def test_gateclass_matches_live_state_yaml_when_available() -> None:
    location = os.environ.get("NEL_OS_STATE_YAML")
    if not location:
        pytest.skip("NEL_OS_STATE_YAML unset; the vendored SSOT is authoritative for this repo")
    path = Path(location)
    if not path.exists():
        pytest.skip(f"state file not found: {path}")
    live = _load_human_gates(path)
    assert tuple(live) == GATE_CLASS_IDENTIFIERS
