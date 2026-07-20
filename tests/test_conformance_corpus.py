from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

from nel_contracts.models.capability import Capability
from nel_contracts.models.content_identity import ContentIdentity
from nel_contracts.models.seam import SeamReceipt
from nel_contracts.models.work import PublishIntent
from nel_contracts.models.workflow import WorkflowRun
from nel_contracts.models.workitem import GitWorkExtension, WorkItem

_FIXTURES = Path(__file__).resolve().parent.parent / "conformance" / "fixtures"
_VALID = _FIXTURES / "valid"
_INVALID = _FIXTURES / "invalid"

# Registry mapping a fixture's ``schema`` tag to the model it must (in)validate against.
_MODELS: dict[str, type[BaseModel]] = {
    "seam-receipt": SeamReceipt,
    "publish-intent": PublishIntent,
    "content-identity": ContentIdentity,
    "capability": Capability,
    "work-item": WorkItem,
    "git-work-extension": GitWorkExtension,
    "workflow-run": WorkflowRun,
}


def _cases(directory: Path) -> list[Path]:
    return sorted(directory.glob("*.json"))


def test_valid_and_invalid_corpora_are_populated() -> None:
    assert _cases(_VALID), "valid corpus is empty"
    assert _cases(_INVALID), "invalid corpus is empty"


@pytest.mark.parametrize("path", _cases(_VALID), ids=lambda path: path.name)
def test_valid_fixtures_validate(path: Path) -> None:
    doc = json.loads(path.read_text(encoding="utf-8"))
    model = _MODELS[doc["schema"]]
    model.model_validate(doc["data"])  # must not raise


@pytest.mark.parametrize("path", _cases(_INVALID), ids=lambda path: path.name)
def test_invalid_fixtures_are_rejected(path: Path) -> None:
    doc = json.loads(path.read_text(encoding="utf-8"))
    model = _MODELS[doc["schema"]]
    with pytest.raises(ValidationError):
        model.model_validate(doc["data"])
