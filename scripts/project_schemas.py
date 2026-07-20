#!/usr/bin/env python
"""Project Pydantic models to canonical JSON Schema, guarded by generate-and-diff (design D13).

The wire schemas are generated from the pinned pydantic (>=2.11,<2.14) via ``model_json_schema``
plus the type-level ``OpenClassifier`` override, and written as canonical Draft 2020-12 schemas
under ``schemas/contracts/v1/`` with a version-pinned ``$id``. This is NOT a fully decoupled,
hand-controlled projection layer that owns the wire form independently of pydantic's emitter —
that fuller layer is deferred (K-phase). Instead, a generate-and-diff gate protects the wire
form: a pydantic bump (or a model change) that alters the emitted output fails ``--check`` in CI
until it is reviewed and regenerated. Run with ``--check`` in CI to fail on drift.

Minimal but runnable: extend ``SCHEMA_MODELS`` as the neutral surface grows.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Make ``src`` importable when run as a plain script (no install required in CI).
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from pydantic import BaseModel  # noqa: E402

from nel_contracts.ledger.event import LedgerEvent  # noqa: E402
from nel_contracts.ledger.redaction import RedactionEvent  # noqa: E402
from nel_contracts.models.actor import AttestedActor, ClaimedActor  # noqa: E402
from nel_contracts.models.approval import ApprovalRequest, DecisionRecord  # noqa: E402
from nel_contracts.models.capability import Capability, MediatedCapabilityGrant  # noqa: E402
from nel_contracts.models.content_identity import ContentIdentity  # noqa: E402
from nel_contracts.models.evidence import EvidenceEvent  # noqa: E402
from nel_contracts.models.metadata import RepoMetadata  # noqa: E402
from nel_contracts.models.policy import Policy, PolicyOutcome  # noqa: E402
from nel_contracts.models.seam import (  # noqa: E402
    SeamObservation,
    SeamReceipt,
    SeamReference,
)
from nel_contracts.models.visibility import RepositoryVisibility  # noqa: E402
from nel_contracts.models.work import (  # noqa: E402
    DeliveryIntent,
    DeployIntent,
    ExternalReadIntent,
    HistoryRewriteIntent,
    MigrationIntent,
    OtherIntent,
    PiiPolicyIntent,
    PublishIntent,
    SpendIntent,
    VisibilityChangeIntent,
)
from nel_contracts.seam.wire_envelope import WireEnvelope  # noqa: E402
from nel_contracts.version import SCHEMA_ID_BASE, generator_toolchain  # noqa: E402

_DRAFT = "https://json-schema.org/draft/2020-12/schema"

SCHEMA_MODELS: dict[str, type[BaseModel]] = {
    "claimed-actor": ClaimedActor,
    "attested-actor": AttestedActor,
    "content-identity": ContentIdentity,
    "publish-intent": PublishIntent,
    "delivery-intent": DeliveryIntent,
    "spend-intent": SpendIntent,
    "deploy-intent": DeployIntent,
    "external-read-intent": ExternalReadIntent,
    "visibility-change-intent": VisibilityChangeIntent,
    "migration-intent": MigrationIntent,
    "history-rewrite-intent": HistoryRewriteIntent,
    "pii-policy-intent": PiiPolicyIntent,
    "other-intent": OtherIntent,
    "seam-receipt": SeamReceipt,
    "seam-reference": SeamReference,
    "seam-observation": SeamObservation,
    "wire-envelope": WireEnvelope,
    "capability": Capability,
    "mediated-capability-grant": MediatedCapabilityGrant,
    "approval-request": ApprovalRequest,
    "decision-record": DecisionRecord,
    "evidence-event": EvidenceEvent,
    "policy": Policy,
    "policy-outcome": PolicyOutcome,
    "repository-visibility": RepositoryVisibility,
    "repo-metadata": RepoMetadata,
    "ledger-event": LedgerEvent,
    "redaction-event": RedactionEvent,
}


def _project(name: str, model: type[BaseModel]) -> dict[str, Any]:
    schema = model.model_json_schema(ref_template="#/$defs/{model}")
    version = generator_toolchain()["projector_version"]
    projected: dict[str, Any] = {
        "$schema": _DRAFT,
        "$id": f"{SCHEMA_ID_BASE}:{name}",
        "$comment": (
            f"generated from pinned pydantic + type-level overrides, guarded by "
            f"generate-and-diff (nel-contracts projector {version}); a fuller hand-controlled "
            f"projection layer is deferred (K-phase)"
        ),
    }
    projected.update(schema)
    return projected


def _render(name: str, model: type[BaseModel]) -> str:
    return json.dumps(_project(name, model), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _schema_dir() -> Path:
    return _REPO_ROOT / "schemas" / "contracts" / "v1"


def generate() -> int:
    target = _schema_dir()
    target.mkdir(parents=True, exist_ok=True)
    for name, model in SCHEMA_MODELS.items():
        (target / f"{name}.schema.json").write_text(_render(name, model), encoding="utf-8")
    print(f"generated {len(SCHEMA_MODELS)} schema(s) into {target}")
    return 0


def check() -> int:
    target = _schema_dir()
    drift: list[str] = []
    for name, model in SCHEMA_MODELS.items():
        path = target / f"{name}.schema.json"
        expected = _render(name, model)
        actual = path.read_text(encoding="utf-8") if path.exists() else ""
        if actual != expected:
            drift.append(name)
    if drift:
        print(f"schema drift detected: {', '.join(sorted(drift))}", file=sys.stderr)
        print("run: python scripts/project_schemas.py", file=sys.stderr)
        return 1
    print(f"no schema drift ({len(SCHEMA_MODELS)} schema(s) checked)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Project Pydantic models to JSON Schema.")
    parser.add_argument("--check", action="store_true", help="fail on drift instead of writing")
    args = parser.parse_args(argv)
    return check() if args.check else generate()


if __name__ == "__main__":
    raise SystemExit(main())
