"""Module for Git Pull Request clients API."""

import logging

from ...base.clients import Client
from .models import PullRequestThread, PullRequestThreadCollection, PullRequestThreadCreate

# Get a logger for this module
logger = logging.getLogger(__name__)


class PullRequestClient(Client):
    """Represent a client to Pull Request API in Azure DevOps."""

    def find_existing_thread(self, pr_id: int, plan: str) -> PullRequestThread | None:
        """Return the existing thread ID and associated comment IDs for a project."""
        response = self._client.get(f"/{pr_id}/threads").raise_for_status()
        threads = PullRequestThreadCollection.model_validate(response.json())

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
            delete_request = self._client.delete(f"/{pr_id}/threads/{thread.id}/comments/{comment.id}")
            delete_request.raise_for_status()

    def new_thread(self, pr_id: int, thread: PullRequestThreadCreate):
        """Post a new thread on a pull request."""
        logger.info("Posting a thread to: %s%d", self.base_url, pr_id)
        new_thread_req = self._client.post(f"/{pr_id}/threads", json=thread.model_dump(exclude_none=True))
        new_thread_req.raise_for_status()
