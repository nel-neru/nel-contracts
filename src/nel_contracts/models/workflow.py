from __future__ import annotations

from pydantic import Field

from nel_contracts.models.identifiers import (
    SchemaVersion,
    Slug,
    StrictModel,
    Ulid,
    UtcTimestamp,
)
from nel_contracts.models.workitem import RiskLevel, WorkItemId, WorkStatus


class WorkflowNode(StrictModel):
    """One node of a neutral plan/DAG. A minimal shell in K2; the full planner/execution semantics
    (node kinds, gating, fan-out) are owned by W2. ``kind`` is a free string here deliberately — no
    authority attaches to a not-yet-executed plan node."""

    node_id: Slug
    kind: str
    depends_on: list[Slug] = Field(default_factory=list)


class WorkflowDefinition(StrictModel):
    """A neutral plan/DAG shape (design §4.2). Distinct from the nel-os kernel registry
    ``WorkflowDefinition`` (a stage-list): different package/namespace, no rename, no collision.
    Full planner semantics land in W2; K2 ships only the shell that makes the D3 projection legible.
    """

    definition_id: Slug
    version: SchemaVersion
    nodes: list[WorkflowNode] = Field(default_factory=list)
    allowed_risk: list[RiskLevel] = Field(default_factory=list)


class WorkflowRun(StrictModel):
    """The neutral, ADVISORY (per ADR-0014 D3) projection of a bounded resumable execution.

    A world/Pantheon ``WorkflowRun`` is an OUTWARD projection of kernel truth: no ``WorkflowRun``
    event may satisfy, mutate, or unblock a kernel gate. Kernel-only concerns — budgets, timeouts,
    active-time intervals — are intentionally absent from this neutral shape.
    """

    run_id: Ulid
    definition_id: Slug
    work_item_ref: WorkItemId
    status: WorkStatus
    node_states: dict[str, WorkStatus] = Field(default_factory=dict)
    projection_sequence: int = Field(ge=1)
    created_at: UtcTimestamp
    updated_at: UtcTimestamp
