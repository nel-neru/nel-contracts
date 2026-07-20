from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from nel_contracts.models.identifiers import Slug, Ulid
from nel_contracts.models.work import KNOWN_INTENT_KINDS
from nel_contracts.models.workflow import WorkflowRun
from nel_contracts.models.workitem import (
    RISK_LEVEL_IDENTIFIERS,
    WORK_STATUS_IDENTIFIERS,
    GitWorkExtension,
    RiskLevel,
    WorkItem,
    WorkItemId,
    WorkKind,
    WorkStatus,
)

# A real kernel task id: lowercase + hyphens, 69 chars -> overflows Slug (max 64) and is not a ULID.
_REAL_TASK_ID = "task-20260720-141530-generalize-the-task-envelope-to-neutral-workitem"


def test_work_status_ssot_is_the_ratified_task_lifecycle() -> None:
    # Self-consistency of the wire SSOT; a nel-os parity test asserts equality with TaskStatus.
    assert WORK_STATUS_IDENTIFIERS == (
        "planned",
        "running",
        "reviewing",
        "revising",
        "verifying",
        "delivering",
        "capturing",
        "blocked",
        "failed",
        "completed",
        "cancelled",
    )
    assert WorkStatus.known_values() == frozenset(WORK_STATUS_IDENTIFIERS)


def test_unknown_work_status_downgrades_to_blocked() -> None:
    status = WorkStatus("teleported_from_the_future")
    assert status.is_known is False
    assert status.classification == "blocked"


def test_unknown_work_kind_downgrades_to_other() -> None:
    assert WorkKind("brand_new_kind").classification == "other"
    # git_implementation is the sole existing specialization; the WorkIntent kinds are all known.
    assert WorkKind("git_implementation").is_known is True
    for kind in KNOWN_INTENT_KINDS:
        assert WorkKind(kind).is_known is True


def test_unknown_risk_level_downgrades_to_most_restrictive() -> None:
    assert RISK_LEVEL_IDENTIFIERS == ("low", "medium", "high", "critical")
    assert RiskLevel("nuclear").classification == "critical"


def test_work_item_id_is_a_superset_of_ulid_and_slug() -> None:
    # A real long task id validates as a WorkItemId ...
    assert TypeAdapter(WorkItemId).validate_python(_REAL_TASK_ID) == _REAL_TASK_ID
    # ... while failing BOTH Slug (caps at 64) and Ulid (uppercase Crockford charset).
    with pytest.raises(ValidationError):
        TypeAdapter(Slug).validate_python(_REAL_TASK_ID)
    with pytest.raises(ValidationError):
        TypeAdapter(Ulid).validate_python(_REAL_TASK_ID)


def test_git_work_extension_is_path_free() -> None:
    # A path field is rejected (StrictModel extra="forbid"): git-as-vocabulary, not git-as-location.
    with pytest.raises(ValidationError):
        GitWorkExtension.model_validate(
            {
                "repo": {"repo": "nel-os"},
                "base_ref": "main",
                "target_visibility": "private",
                "path": "C:/Users/neoma/NEL/nel-os",
            }
        )


def test_work_item_round_trips_through_json() -> None:
    item = WorkItem.model_validate(
        {
            "work_item_id": _REAL_TASK_ID,
            "title": "round trip",
            "kind": "git_implementation",
            "acceptance": ["x"],
            "status": "completed",
            "risk": {"level": "low"},
            "projection_sequence": 1,
            "created_at": "2026-07-20T12:00:00Z",
            "updated_at": "2026-07-20T12:00:00Z",
        }
    )
    again = WorkItem.model_validate(item.model_dump(mode="json"))
    assert again == item
    assert again.status.raw == "completed"


def test_workflow_run_round_trips_and_is_advisory_status() -> None:
    run = WorkflowRun.model_validate(
        {
            "run_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
            "definition_id": "git-delivery",
            "work_item_ref": _REAL_TASK_ID,
            "status": "running",
            "node_states": {"implement": "completed"},
            "projection_sequence": 2,
            "created_at": "2026-07-20T12:00:00Z",
            "updated_at": "2026-07-20T12:30:00Z",
        }
    )
    again = WorkflowRun.model_validate(run.model_dump(mode="json"))
    assert again == run
    assert again.node_states["implement"].classification == "completed"
