# EZ Azure Devops

A simple Python interface to interact with Azure DevOps API.

Contents:

* [Installation](#installation)
* [Quick start](#quick-start)
* [Usage](#usage)
  * [Authentication](#authentication)
  * [Projects](#projects)
  * [Git repositories](#git-repositories)
  * [Pull requests](#pull-requests)
  * [Pipelines](#pipelines)
  * [Builds](#builds)
  * [Identities](#identities)
  * [Policies](#policies)
  * [Service hook subscriptions](#service-hook-subscriptions)
  * [Error handling](#error-handling)
* [Development](#development)
  * [Requirements](#requirements)
  * [Install tools](#install-tools)
  * [Virtual environment](#virtual-environment)
  * [Tests](#tests)

## Installation

With [uv](https://docs.astral.sh/uv/):

```sh
uv add ez_ados
```

With [pip](https://pip.pypa.io/en/stable/):

```sh
pip install ez_ados
```

## Quick start

```python
from ez_ados import AzureDevOps

# Init a client for an organization
my_org = AzureDevOps("https://dev.azure.com/myorg")

# Authenticate using EntraID
# See https://learn.microsoft.com/en-us/dotnet/azure/sdk/authentication/credential-chains?tabs=dac#defaultazurecredential-overview
my_org.authenticate()

# Get a project
projects = my_org.projects_client()
print(projects.get(name="my_project"))
```

## Usage

All clients are obtained from an authenticated `AzureDevOps` instance.

### Authentication

Three credential types are available, all importable from `ez_ados`:

**Default Azure credential** — uses the [DefaultAzureCredential](https://learn.microsoft.com/en-us/dotnet/azure/sdk/authentication/credential-chains?tabs=dac#defaultazurecredential-overview) chain (environment variables, managed identity, Azure CLI, …):

```python
from ez_ados import AzureDevOps

org = AzureDevOps("https://dev.azure.com/myorg")
org.authenticate()  # uses AzureCredential by default
```

**Personal access token (PAT) / bearer token**:

```python
from ez_ados import AzureDevOps
from ez_ados.credentials import AccessTokenCredential

org = AzureDevOps("https://dev.azure.com/myorg")
org.authenticate(AccessTokenCredential(token="my-pat-or-bearer-token"))
```

**Service principal**:

```python
from ez_ados import AzureDevOps
from ez_ados.credentials import ServicePrincipalCredential

org = AzureDevOps("https://dev.azure.com/myorg")
org.authenticate(ServicePrincipalCredential(
    client_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    client_secret="my-client-secret",
    tenant_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
))
```

---

### Projects

Manage Azure DevOps projects.

```python
projects = org.projects_client()

project = projects.get(name="my-project")
print(project.id, project.name)
```

---

### Git repositories

Browse and manage Git repositories, refs, and file content.

```python
git = org.git_repository_client(project="my-project")

# Get a repository
repo = git.get(repository="my-repo")

# List all refs (branches, tags)
refs = git.get_refs(repository="my-repo")

# List refs starting with a prefix
main_refs = git.get_refs(repository="my-repo", branch_startswith="heads/main")

# List files in a directory on a branch
files = git.list_files(repository="my-repo", branch="main", path="/src")

# Fetch file content
item = git.get_item(repository="my-repo", path="/README.md", branch="main")
print(item.content)

# Check whether a branch is locked
locked = git.is_branch_locked(repository="my-repo", branch="main")

# Lock or unlock a branch
git.lock_branch_toggle(repository="my-repo", branch="main", locked=True)
git.lock_branch_toggle(repository="my-repo", branch="main", locked=False)
```

To fetch a batch of items at once, use `get_items_batch` with an explicit `GitItemsBatch` descriptor:

```python
from pathlib import PurePosixPath
from ez_ados.git.models import GitItemDescriptor, GitItemsBatch
from ez_ados.git.enums import RecursionType

git = org.git_repository_client(project="my-project")

batch = GitItemsBatch(item_descriptors=[
    GitItemDescriptor(path=PurePosixPath("/src"), version="main"),
    GitItemDescriptor(path=PurePosixPath("/README.md"), version="main"),
])
items = git.get_items_batch(repository="my-repo", item_descriptors=batch)
```

---

### Pull requests

Manage reviewers and comment threads on pull requests.

```python
pr = org.pull_request_client(project="my-project", repository="my-repo")

# List current reviewers
reviewers = pr.list_reviewers(pr_id=42)

# Add reviewers by email (required=True makes them required reviewers)
pr.add_reviewers_by_email(pr_id=42, emails=["alice@example.com", "bob@example.com"])
pr.add_reviewers_by_email(pr_id=42, emails=["charlie@example.com"], is_required=True)

# Remove a reviewer by email
pr.remove_reviewer_by_email(pr_id=42, email="bob@example.com")
```

To add reviewers when you already have identity IDs, use `add_reviewers` directly:

```python
from ez_ados.git.pullrequests.models import IdentityRefCreate

pr.add_reviewers(pr_id=42, reviewers=[
    IdentityRefCreate(id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", is_required=True),
])
```

To remove a reviewer by identity ID, use `remove_reviewer`:

```python
pr.remove_reviewer(pr_id=42, reviewer_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
```

To post a comment thread or interact with existing ones:

```python
from ez_ados.git.pullrequests.models import PullRequestThreadCreate, PullRequestThreadCommentCreate
from ez_ados.git.pullrequests.enums import CommentTypeEnum, ThreadStatusEnum

# Post a new thread
thread = PullRequestThreadCreate(
    comments=[PullRequestThreadCommentCreate(content="Needs a change here.", comment_type=CommentTypeEnum.text)],
    status=ThreadStatusEnum.active,
)
pr.new_thread(pr_id=42, thread=thread)

# Find a thread by a custom plan property
existing = pr.find_existing_thread(pr_id=42, plan="my-plan-id")
if existing:
    # Delete all its comments before reposting
    pr.delete_thread_comments(pr_id=42, thread=existing)
```

---

### Pipelines

Manage YAML pipelines in a project.

```python
pipelines = org.pipeline_client(project="my-project")

# List all pipelines
all_pipelines = pipelines.list()

# Get a pipeline by ID
pipeline = pipelines.get(id=10)

# Create a pipeline pointing to a YAML file in a repository
new_pipeline = pipelines.create(
    name="my-pipeline",
    folder="\\MyTeam\\CI",
    yaml_path="/pipelines/ci.yml",
    yaml_repository_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
)
```

---

### Builds

Manage classic and YAML build definitions.

```python
builds = org.builds_client(project="my-project")

# List all build definitions
all_defs = builds.list_build_definitions()

# Filter by repository
repo = git.get(repository="my-repo")
repo_defs = builds.list_build_definitions(repository=repo)

# Get a build definition by ID
definition = builds.get_build_definition(id="5")

# Create a build definition
from pathlib import PurePosixPath, PureWindowsPath
from ez_ados.builds.models import BuildDefinitionCreate, BuildProcess, BuildRepository

new_def = builds.create_build_definition(BuildDefinitionCreate(
    name="my-build",
    path=PureWindowsPath("\\MyTeam"),
    process=BuildProcess(yaml_filename=PurePosixPath("/pipelines/build.yml")),
    repository=BuildRepository(id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"),
))

# Delete a build definition
builds.delete_build_definition(id=new_def.id)
```

---

### Identities

Resolve Azure DevOps identities.

```python
identities = org.identity_client()

# Search by email
collection = identities.search_by_email("alice@example.com")
for identity in collection:
    print(identity.id, identity.provider_display_name)

# Resolve a list of emails to identity objects (raises if any email is not found)
resolved = identities.resolve_identities_by_email(["alice@example.com", "bob@example.com"])
```

---

### Policies

#### Policy types

Inspect the policy types available in a project.

```python
types = org.policy_types_client(project="my-project")

# List all policy types
all_types = types.list()

# Get a specific type by ID
policy_type = types.get(id="fa4e907d-c16b-452d-8106-7efa0cb84489")
print(policy_type.display_name)
```

#### Policy configurations

Create, update, or delete policy configurations on a project.

```python
from ez_ados.policy.configurations.models import PolicyConfigurationPayload, PolicySettings, PolicyScope
from ez_ados.policy.types.models import PolicyType

policy_type = PolicyType(
    id="fa4e907d-c16b-452d-8106-7efa0cb84489",
    url="https://dev.azure.com/myorg/my-project/_apis/policy/types/fa4e907d-c16b-452d-8106-7efa0cb84489",
    display_name="Build",
)

payload = PolicyConfigurationPayload(
    enabled=True,
    required=True,
    enterprise_managed=False,
    type=policy_type,
    settings=PolicySettings(
        display_name="CI gate",
        build_definition_id=5,
        never_expire=False,
        manual_trigger=False,
        valid_duration=720,
        scope=[PolicyScope(repository_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", ref_name="refs/heads/main", match_kind="Exact")],
    ),
)

configs = org.policy_configuration_client(project="my-project")

# Create a build policy
new_policy = configs.create_build_policy(payload)

# Update it
updated = configs.update_build_policy(id=new_policy.id, definition=payload)

# Delete it
configs.delete_policy(id=new_policy.id)
```

#### Git repository policy configurations

Query policies applied to a specific branch of a repository.

```python
git_policies = org.git_repository_policy_configuration_client(project="my-project")

# Get all build policies for a branch
build_policies = git_policies.get_build_policies_for_ref(
    repository_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    ref_name="refs/heads/main",
)

# Get policies of a specific type
policies = git_policies.get_policies_for_ref(
    repository_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    ref_name="refs/heads/main",
    policy_type="fa4e907d-c16b-452d-8106-7efa0cb84489",
)
```

---

### Service hook subscriptions

Manage service hook subscriptions at the organization level.

```python
hooks = org.hook_subscriptions_client()

# List all subscriptions
all_hooks = hooks.list()

# Filter subscriptions for git push events
push_hooks = all_hooks.for_git_push_event(branch_name="main", repository_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")

# Get a single subscription by ID
hook = hooks.get(id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")

# Create a new subscription
from ez_ados.servicehooks.subscriptions.models import HookSubscriptionCreate

new_hook = hooks.create(HookSubscriptionCreate(
    publisher_id="tfs",
    event_type="git.push",
    resource_version="1.0",
    consumer_id="webHooks",
    consumer_action_id="httpRequest",
    publisher_inputs={
        "branch": "main",
        "projectId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        "repository": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    },
    consumer_inputs={
        "url": "https://my-webhook-endpoint.example.com/hook",
    },
))

# Delete a subscription
hooks.delete(id=new_hook.id)
```

---

### Error handling

All exceptions inherit from `AzureDevOpsError` and are importable from `ez_ados.exceptions`.

| Exception             | When it is raised                                 |
|-----------------------|---------------------------------------------------|
| `AzureDevOpsError`    | Base class for all package errors                 |
| `AuthenticationError` | A client method is called before `authenticate()` |
| `APIError`            | The API returns a non-2xx response                |
| `NotFoundError`       | The API returns HTTP 404 (subclass of `APIError`) |

`APIError` and `NotFoundError` expose `.status_code` (int) and `.url` (str) attributes.

```python
from ez_ados import AzureDevOps
from ez_ados.exceptions import APIError, AuthenticationError, NotFoundError

org = AzureDevOps("https://dev.azure.com/myorg")

try:
    org.projects_client()
except AuthenticationError as exc:
    print(f"Not authenticated: {exc}")

org.authenticate()
projects = org.projects_client()

try:
    project = projects.get(name="nonexistent-project")
except NotFoundError as exc:
    print(f"Project not found ({exc.status_code}): {exc.url}")
except APIError as exc:
    print(f"API error {exc.status_code}: {exc}")
```

---

## Development

### Requirements

* [uv](https://docs.astral.sh/uv/getting-started/installation/)
* [asdf](https://asdf-vm.com/)

### Install tools

Install [Task](https://taskfile.dev/):

```sh
asdf plugin add task
asdf plugin add git-cliff
asdf install
```

### Virtual environment

Init your python environment with:

```bash
task venv
```

You're all set !

### Tests

Run all tests with:

```bash
task tests
```
