"""Azure DevOps Base Client."""

import atexit
import logging

import httpx

from .builds.clients import BuildClient
from .core.clients import ProjectClient
from .credentials import AzureCredential, TokenCredential
from .git.clients import GitPolicyConfigurationClient, GitRepositoryClient
from .git.pullrequests.clients import PullRequestClient
from .pipelines.clients import PipelineClient
from .policy.configurations.clients import PolicyConfigurationClient
from .policy.types.clients import PolicyTypeClient
from .servicehooks.subscriptions.clients import HookSubscriptionClient

# Get a logger for this module
logger = logging.getLogger(__name__)


class AzureDevOps:
    """Represent an Azure DevOps connection."""

    API_VERSION = "7.1"

    def __init__(self, org_url: str, timeout: int = 30):
        """Create a new Azure DevOps connection."""
        if not org_url.startswith("https://dev.azure.com/"):
            raise ValueError("You did not provide an URL to an Azure DevOps organization !")

        atexit.register(self._terminate)

        self.org_url = org_url
        self._token: str | None = None
        self._clients_cache: dict[int, httpx.Client] = {}
        self._timeout = timeout

    def authenticate(self, credentials: TokenCredential | None = None):
        """
        Authenticate on Azure DevOps.

        If `credentials` is not provided, will use default [Azure authentication](https://learn.microsoft.com/en-us/dotnet/azure/sdk/authentication/credential-chains?tabs=dac#defaultazurecredential-overview).
        """
        if not credentials:
            credentials = AzureCredential()
        self._token = credentials.get_token()

    def _build_client(self, endpoint: str) -> httpx.Client:
        """Return an HTTP client for interacting with an Azure DevOps API endpoint."""
        default_params = {"api-version": AzureDevOps.API_VERSION}
        client = httpx.Client(base_url=endpoint, timeout=self._timeout, params=default_params)
        if self._token:
            client.headers.update({"Authorization": f"Bearer {self._token}"})
        else:
            raise ValueError(
                "You are not connected to Azure DevOps ! Call one of *_authenticate() methods first to get a token."
            )
        fingerprint = hash((client.base_url, client.params))

        # Get a client from global cache or store a new one
        if fingerprint in self._clients_cache:
            existing_client = self._clients_cache[fingerprint]
            logger.debug("Found an existing client for %s (%d)", existing_client.base_url, fingerprint)
            return existing_client
        else:
            logger.debug("Create a new client in cache %s (%d)", client.base_url, fingerprint)
            self._clients_cache.update({fingerprint: client})
            return client

    def _terminate(self):
        """Terminate all client connections at exit."""
        logger.debug("Closing all Azure DevOps API clients...")
        for fingerprint, client in self._clients_cache.items():
            logger.debug("Terminating client for %s (%d).", client.base_url, fingerprint)
            client.close()

    def projects_client(self) -> ProjectClient:
        """Return an HTTP client for interacting with Projects endpoint."""
        _endpoint = [self.org_url, "_apis", "projects"]
        return ProjectClient(self._build_client(endpoint="/".join(_endpoint)))

    def pull_request_client(self, project: str, repository: str) -> PullRequestClient:
        """Return an HTTP client for interacting with Pull Request endpoint."""
        _endpoint = [self.org_url, project, "_apis", "git", "repositories", repository, "pullrequests"]
        return PullRequestClient(self._build_client(endpoint="/".join(_endpoint)))

    def git_repository_client(self, project: str | None = None) -> GitRepositoryClient:
        """Return an HTTP client for interacting with a Git repository endpoint."""
        _endpoint = [self.org_url, "_apis", "git", "repositories"]
        if project:
            _endpoint.insert(1, project)
        return GitRepositoryClient(self._build_client(endpoint="/".join(_endpoint)))

    def git_repository_policy_configuration_client(self, project: str) -> GitPolicyConfigurationClient:
        """Return an HTTP client for interacting with a Git Repository Policy Configuration endpoint."""
        _endpoint = [self.org_url, project, "_apis", "git", "policy", "configurations"]
        return GitPolicyConfigurationClient(self._build_client(endpoint="/".join(_endpoint)))

    def policy_configuration_client(self, project: str) -> PolicyConfigurationClient:
        """Return an HTTP client for interacting with Policy Configuration endpoint."""
        _endpoint = [self.org_url, project, "_apis", "policy", "configurations"]
        return PolicyConfigurationClient(self._build_client(endpoint="/".join(_endpoint)))

    def policy_types_client(self, project: str) -> PolicyTypeClient:
        """Return an HTTP client for interacting with Policy Types endpoint."""
        _endpoint = [self.org_url, project, "_apis", "policy", "types"]
        return PolicyTypeClient(self._build_client(endpoint="/".join(_endpoint)))

    def pipeline_client(self, project: str) -> PipelineClient:
        """Return an HTTP client for interacting with Pipelines endpoint."""
        _endpoint = [self.org_url, project, "_apis", "pipelines"]
        return PipelineClient(self._build_client(endpoint="/".join(_endpoint)))

    def builds_client(self, project: str) -> BuildClient:
        """Return an HTTP client for interacting with Builds endpoint."""
        _endpoint = [self.org_url, project, "_apis", "build"]
        return BuildClient(self._build_client(endpoint="/".join(_endpoint)))

    def hook_subscriptions_client(self) -> HookSubscriptionClient:
        """Return an HTTP client for interacting with Service Hooks' subscriptions endpoint."""
        _endpoint = [self.org_url, "_apis", "hooks", "subscriptions"]
        return HookSubscriptionClient(self._build_client(endpoint="/".join(_endpoint)))
