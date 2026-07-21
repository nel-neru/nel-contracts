from __future__ import annotations

from nel_contracts.canonical.jcs import (
    canonical_json,
    canonical_json_bytes,
    canonical_timestamp,
    sha256_hex,
)
from nel_contracts.ledger.event import (
    GENESIS_DIGEST,
    LedgerEvent,
    link_event,
    verify_chain,
)
from nel_contracts.ledger.redaction import REDACTION_PLACEHOLDER, RedactionEvent
from nel_contracts.models.actor import (
    ActorKind,
    AttestedActor,
    ClaimedActor,
    KernelAttestation,
)
from nel_contracts.models.approval import (
    GATE_CLASS_IDENTIFIERS,
    ApprovalRequest,
    DecisionRecord,
    GateClass,
)
from nel_contracts.models.capability import (
    Capability,
    CapabilityClassification,
    MediatedCapabilityGrant,
)
from nel_contracts.models.content_identity import ContentIdentity
from nel_contracts.models.evidence import EvidenceClassification, EvidenceEvent
from nel_contracts.models.executor import (
    EXECUTOR_CAPABILITY_IDENTIFIERS,
    ExecutorCapability,
    RoutingAdvice,
    RoutingSignal,
)
from nel_contracts.models.identifiers import (
    GitObjectId,
    OpaqueScopeDescriptor,
    RepoRef,
    ResourceRef,
    SchemaVersion,
    Sha256Hex,
    Slug,
    StrictModel,
    Ulid,
    UtcTimestamp,
)
from nel_contracts.models.metadata import (
    DEFAULT_STALE_AFTER_DAYS,
    FreshnessState,
    RepoMetadata,
)
from nel_contracts.models.openclass import OpenClassifier
from nel_contracts.models.policy import Policy, PolicyOutcome
from nel_contracts.models.seam import (
    SeamAuthority,
    SeamObservation,
    SeamReceipt,
    SeamReference,
    SubmissionState,
    can_verify_kernel_attestation,
    package_establishes_trust,
)
from nel_contracts.models.visibility import RepositoryVisibility, VisibilityLevel
from nel_contracts.models.work import (
    KNOWN_INTENT_KINDS,
    AnyWorkIntent,
    DeliveryIntent,
    DeliveryOperation,
    DeployIntent,
    ExternalReadIntent,
    GitDeliveryExtension,
    HistoryRewriteIntent,
    MigrationIntent,
    OtherIntent,
    PiiPolicyIntent,
    PublishIntent,
    SpendIntent,
    VisibilityChangeIntent,
    WorkIntent,
    WorkIntentUnion,
    coerce_work_intent,
)
from nel_contracts.models.workflow import (
    WorkflowDefinition,
    WorkflowNode,
    WorkflowRun,
)
from nel_contracts.models.workitem import (
    RISK_LEVEL_IDENTIFIERS,
    WORK_STATUS_IDENTIFIERS,
    GitWorkExtension,
    RiskClassification,
    RiskLevel,
    WorkItem,
    WorkItemId,
    WorkKind,
    WorkStatus,
)
from nel_contracts.seam.port import SEAM_PORT_VERBS, SeamPort
from nel_contracts.seam.resolver import DeploymentBinding, resolve_seam
from nel_contracts.seam.sealed import SealedSeam
from nel_contracts.seam.wire_envelope import WireEnvelope
from nel_contracts.version import (
    CONTRACT_MAJOR,
    PACKAGE_VERSION,
    PROTOCOL_VERSION,
    SCHEMA_ID_BASE,
)

__version__ = PACKAGE_VERSION

# NOTE: there is deliberately no ``register_seam_provider`` export. The seam is resolved
# fail-closed and can be overridden only by an out-of-process deployment binding (design §4).

__all__ = [  # noqa: RUF022  (grouped by domain for readability, not alphabetized)
    # version
    "PACKAGE_VERSION",
    "CONTRACT_MAJOR",
    "PROTOCOL_VERSION",
    "SCHEMA_ID_BASE",
    "__version__",
    # canonical
    "canonical_json",
    "canonical_json_bytes",
    "canonical_timestamp",
    "sha256_hex",
    # base / identifiers
    "StrictModel",
    "OpenClassifier",
    "Ulid",
    "Slug",
    "Sha256Hex",
    "GitObjectId",
    "SchemaVersion",
    "UtcTimestamp",
    "RepoRef",
    "ResourceRef",
    "OpaqueScopeDescriptor",
    # actor
    "ActorKind",
    "ClaimedActor",
    "AttestedActor",
    "KernelAttestation",
    # work
    "WorkIntent",
    "WorkIntentUnion",
    "AnyWorkIntent",
    "PublishIntent",
    "DeliveryIntent",
    "SpendIntent",
    "DeployIntent",
    "ExternalReadIntent",
    "VisibilityChangeIntent",
    "MigrationIntent",
    "HistoryRewriteIntent",
    "PiiPolicyIntent",
    "OtherIntent",
    "DeliveryOperation",
    "GitDeliveryExtension",
    "KNOWN_INTENT_KINDS",
    "coerce_work_intent",
    # work item / workflow (neutral generalization, K2)
    "WorkItem",
    "WorkItemId",
    "WorkStatus",
    "WorkKind",
    "RiskLevel",
    "RiskClassification",
    "GitWorkExtension",
    "WORK_STATUS_IDENTIFIERS",
    "RISK_LEVEL_IDENTIFIERS",
    "WorkflowDefinition",
    "WorkflowNode",
    "WorkflowRun",
    # executor competency + advisory routing (K3)
    "ExecutorCapability",
    "EXECUTOR_CAPABILITY_IDENTIFIERS",
    "RoutingSignal",
    "RoutingAdvice",
    # content identity
    "ContentIdentity",
    # seam DTOs
    "SeamReceipt",
    "SeamReference",
    "SeamObservation",
    "SeamAuthority",
    "SubmissionState",
    "can_verify_kernel_attestation",
    "package_establishes_trust",
    # capability
    "Capability",
    "CapabilityClassification",
    "MediatedCapabilityGrant",
    # approval
    "GateClass",
    "GATE_CLASS_IDENTIFIERS",
    "ApprovalRequest",
    "DecisionRecord",
    # evidence
    "EvidenceEvent",
    "EvidenceClassification",
    # policy
    "Policy",
    "PolicyOutcome",
    # visibility
    "VisibilityLevel",
    "RepositoryVisibility",
    # metadata
    "RepoMetadata",
    "FreshnessState",
    "DEFAULT_STALE_AFTER_DAYS",
    # ledger
    "LedgerEvent",
    "GENESIS_DIGEST",
    "link_event",
    "verify_chain",
    "RedactionEvent",
    "REDACTION_PLACEHOLDER",
    # seam surface
    "SeamPort",
    "SEAM_PORT_VERBS",
    "SealedSeam",
    "resolve_seam",
    "DeploymentBinding",
    "WireEnvelope",
]
