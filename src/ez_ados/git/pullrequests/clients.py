"""Module for Git Pull Request clients API."""

import logging

import niquests

from ...base.clients import Client
from ...identities.clients import IdentityClient
from .models import (
    IdentityRefCreate,
    IdentityRefWithVoteCollection,
    PullRequestThread,
    PullRequestThreadCollection,
    PullRequestThreadCreate,
)

# Get a logger for this module
logger = logging.getLogger(__name__)


class PullRequestClient(Client):
    """Represent a client to Pull Request API in Azure DevOps."""

    def __init__(self, client: niquests.Session, identity_client: IdentityClient | None = None):
        """Instantiate a new Pull Request client."""
        super().__init__(client)
        self._identity_client = identity_client

    def find_existing_thread(self, pr_id: int, plan: str) -> PullRequestThread | None:
        """Return the existing thread ID and associated comment IDs for a project."""
        threads = self._get_resource(f"/{pr_id}/threads", PullRequestThreadCollection)

        existing_thread = None
        for thread in threads:
            if not thread.deleted:
                logger.debug("Found thread: %s", thread)
                if thread.properties:
                    for property_key, property in thread.properties.items():
                        if "tfci.plan" in property_key:
                            if plan == property.value:
                                existing_thread = thread
                                logger.info("There is an existing thread for plan %s (id=%s)", plan, existing_thread)
                                logger.debug("Existing thread found: %s", existing_thread)
                                break
                    if existing_thread is not None:
                        break

        return existing_thread

    def delete_thread_comments(self, pr_id: int, thread: PullRequestThread):
        """Delete all comments for a given thread on a Pull Request."""
        logger.info("Deleting %d comments for thread with id=%s", len(thread.comments), thread.id)
        for comment in thread.comments:
            self._delete_resource(f"/{pr_id}/threads/{thread.id}/comments/{comment.id}")

    def new_thread(self, pr_id: int, thread: PullRequestThreadCreate):
        """Post a new thread on a pull request."""
        logger.info("Posting a thread to: %s%d", self.base_url, pr_id)
        self._raise_for_status(self._client.post(f"/{pr_id}/threads", json=thread.model_dump(exclude_none=True)))

    def list_reviewers(self, pr_id: int) -> IdentityRefWithVoteCollection:
        """Retrieve the reviewers for a pull request."""
        logger.info("Listing reviewers for PR #%d", pr_id)
        return self._get_resource(f"/{pr_id}/reviewers", IdentityRefWithVoteCollection)

    def add_reviewers(self, pr_id: int, reviewers: list[IdentityRefCreate]) -> IdentityRefWithVoteCollection:
        """Add reviewers to a pull request."""
        logger.info("Adding %d reviewer(s) to PR #%d", len(reviewers), pr_id)
        request_body = [r.model_dump(exclude_none=True) for r in reviewers]
        response = self._raise_for_status(self._client.post(f"/{pr_id}/reviewers", json=request_body))
        return IdentityRefWithVoteCollection.model_validate(response.json())

    def remove_reviewer(self, pr_id: int, reviewer_id: str) -> None:
        """Remove a reviewer from a pull request."""
        logger.info("Removing reviewer '%s' from PR #%d", reviewer_id, pr_id)
        self._delete_resource(f"/{pr_id}/reviewers/{reviewer_id}")

    def _require_identity_client(self) -> IdentityClient:
        """Return the identity client or raise if not available."""
        if self._identity_client is None:
            raise ValueError(
                "Identity client is required for email-based operations."
                " Use AzureDevOps.pull_request_client() to get a client with identity support."
            )
        return self._identity_client

    def add_reviewers_by_email(
        self, pr_id: int, emails: list[str], is_required: bool | None = None
    ) -> IdentityRefWithVoteCollection:
        """Add reviewers to a pull request by email address."""
        identity_client = self._require_identity_client()
        identities = identity_client.resolve_identities_by_email(emails)
        reviewers = [IdentityRefCreate(id=identity.id, is_required=is_required) for identity in identities]
        return self.add_reviewers(pr_id, reviewers)

    def remove_reviewer_by_email(self, pr_id: int, email: str) -> None:
        """Remove a reviewer from a pull request by email address."""
        identity_client = self._require_identity_client()
        identities = identity_client.resolve_identities_by_email([email])
        self.remove_reviewer(pr_id, identities[0].id)
