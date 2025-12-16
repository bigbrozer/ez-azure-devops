# EZ Azure Devops

A simple Python interface to interact with Azure DevOps API.

Contents:

* [Installation](#installation)
* [Quick start](#quick-start)
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
