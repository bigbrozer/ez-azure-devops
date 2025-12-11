"""Module for Git client API."""

import logging

from pathlib import PurePosixPath
from typing import Any

from ..base.clients import Client
from ..policy.configurations.models import PolicyConfigurationCollection
from .models import GitItem, GitItemCollection, GitItemDescriptor, GitItemsBatch, GitRefCollection, GitRepository

# Get a logger for this module
logger = logging.getLogger(__name__)


class GitRepositoryClient(Client):
    """Represent a client to Git repository API in Azure DevOps."""

    def get(self, repository: str) -> GitRepository:
        """Fetch a single Git repository."""
        logger.info("Fetching details for repository '%s'...", repository)
        return GitRepository.model_validate(self._client.get(repository).raise_for_status().json())

    def get_refs(self, repository: str, branch_startswith: str | None = None) -> GitRefCollection:
        """Fetch all refs for a single Git repository."""
        req_params = {}
        if branch_startswith:
            req_params.update({"filter": branch_startswith.replace("refs/", "")})
        return GitRefCollection.model_validate(
            self._client.get(f"/{repository}/refs", params=req_params).raise_for_status().json()
        )

    def get_items_batch(self, repository: str, item_descriptors: GitItemsBatch) -> GitItemCollection:
        """Git a batch of items (files and folders) from a repository."""
        request_body = item_descriptors.model_dump(mode="json")
        logger.debug("Items batch Body: %s", request_body)
        response = self._client.post(f"/{repository}/itemsbatch", json=request_body).raise_for_status()
        logger.debug("Items batch POST: %s", response.url)
        response_dict = response.json()
        _response = {"count": len(response_dict["value"][0]), "value": response_dict["value"][0]}
        serialized_response = GitItemCollection.model_validate(_response)
        logger.debug("Items batch response: %s", serialized_response)
        return serialized_response

    def get_item(self, repository: str, path: str | PurePosixPath, branch: str | None = None) -> GitItem:
        """Get an item (files, folders and symlinks) from a git repository."""
        if isinstance(path, str):
            _path = PurePosixPath(path)
        elif isinstance(path, PurePosixPath):
            _path = path
        else:
            raise ValueError("The path argument can be either a str or PurePosixPath instance !")

        req_params = {
            "path": _path.as_posix(),
            "download": "false",
            "includeContent": "true",
            "$format": "json",
        }

        if branch:
            req_params["versionDescriptor.version"] = branch

        response = self._client.get(f"/{repository}/items", params=req_params).raise_for_status()
        logger.debug("get_item: %s\nResponse: %s", response.url, response.json())
        return GitItem.model_validate(response.json())

    def list_files(self, repository: str, branch: str, path: PurePosixPath | str = "/") -> GitItemCollection:
        """Return files in a given path of a Git repository."""
        if not isinstance(path, PurePosixPath):
            _path = PurePosixPath(path)
        else:
            _path = path

        return self.get_items_batch(
            repository=repository,
            item_descriptors=GitItemsBatch(item_descriptors=[GitItemDescriptor(path=_path, version=branch)]),
        )

    def is_branch_locked(self, repository: str, branch: str) -> bool:
        """Check for branch lock status."""
        ref_info = self.get_refs(repository=repository, branch_startswith=branch)[0]
        logger.debug("Checking branch lock status for '%s@%s': %s", repository, branch, ref_info)
        return ref_info.locked if ref_info.locked else False

    def lock_branch_toggle(self, repository: str, branch: str, locked: bool) -> dict[str, Any]:
        """Lock / Unlock a branch on a single Git repository."""
        req_params = {}
        branch_status = "locked" if locked else "unlocked"
        if branch:
            req_params.update({"filter": branch.replace("refs/", "")})
        logger.info("Branch '%s' for '%s' repository is now %s.", branch, repository, branch_status)
        response = self._client.patch(
            f"/{repository}/refs", json={"isLocked": locked}, params=req_params
        ).raise_for_status()
        return response.json()


class GitPolicyConfigurationClient(Client):
    """Represent a client to Git Repository Policy Configuration API in Azure DevOps."""

    def get_policies_for_ref(
        self, repository_id: str, ref_name: str, policy_type: str
    ) -> PolicyConfigurationCollection:
        """Get all policies for a branch of a repository."""
        response = self._client.get(
            "", params={"repositoryId": repository_id, "refName": ref_name, "policyType": policy_type}
        ).raise_for_status()
        logger.debug("Request URL: %s\nResponse: %s", response.url, response.content)
        return PolicyConfigurationCollection.model_validate(response.json())

    def get_build_policies_for_ref(self, repository_id: str, ref_name: str) -> PolicyConfigurationCollection:
        """Get all build policies for a branch of a repository."""
        policies = self.get_policies_for_ref(
            repository_id=repository_id,
            ref_name=ref_name,
            policy_type="0609b952-1397-4640-95ec-e00a01b2c241",
        )
        return policies
