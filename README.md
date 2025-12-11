# EZ Azure Devops

A simple Python interface to interact with Azure DevOps API.

Contents:

* [Installation](#installation)
* [Development](#development)
  * [Requirements](#requirements)
  * [Install tools](#install-tools)
  * [Virtual environment](#virtual-environment)
  * [Tests](#tests)

## Installation

With [uv](https://docs.astral.sh/uv/):

```sh
uv add git+https://github.com/bigbrozer/ez-azure-devops.git
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
