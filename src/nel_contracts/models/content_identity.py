from __future__ import annotations

from pydantic import model_validator

from nel_contracts.models.identifiers import GitObjectId, Sha256Hex, StrictModel


class ContentIdentity(StrictModel):
    """A repo-agnostic identity for the content an intent acts on.

    At least one identifier is required. For non-git intents the kernel persists the exact
    submitted payload immutably at submit time and recomputes ``content_digest`` over the
    stored copy, executing only against that stored copy (resolves the non-git TOCTOU
    finding) — behavior documented here, enforced kernel-side.
    """

    content_tree_oid: GitObjectId | None = None
    commit_sha: GitObjectId | None = None
    pr_head_sha: GitObjectId | None = None
    content_digest: Sha256Hex | None = None

    @model_validator(mode="after")
    def require_at_least_one(self) -> ContentIdentity:
        if not any((self.content_tree_oid, self.commit_sha, self.pr_head_sha, self.content_digest)):
            raise ValueError("ContentIdentity requires at least one identifier")
        return self
