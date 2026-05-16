# ez_ados

A simple Python interface to interact with Azure DevOps API.

## Codebase Overview

`ez_ados` follows a **facade pattern**: the top-level `AzureDevOps` class in `client.py` manages authentication (`azure-identity`) and caches `niquests.Session` objects per API endpoint. It exposes factory methods that return domain-specific clients.

### Domain modules under `src/ez_ados/`

Each Azure DevOps API surface area has its own subdirectory (e.g. `git/`, `builds/`, `pipelines/`). Nested sub-surfaces live in subdirectories of the parent module (e.g. `git/pullrequests/`).

Alongside the domain modules, supporting modules at the package root handle cross-cutting concerns: `credentials.py` (token credential wrappers), `exceptions.py` (`APIError`, `NotFoundError`, `AuthenticationError`), `constants.py`, `logs.py`.

### Per-module file pattern

Each domain module typically contains:
- `models.py` — Pydantic v2 models mapping camelCase wire format to snake_case Python fields
- `clients.py` — HTTP client wrapping `niquests.Session`, delegating errors to `exceptions.py`
- `enums.py` (optional) — `StrIntEnum` subclasses for API enum values
- `validators.py` / `error_handlers.py` (optional) — field-level validation helpers

### Stack

Python 3.12+ · Pydantic v2 · niquests · azure-identity · uv · ruff · mypy

## Running tests

```bash
uv run pytest          # full suite with coverage
uv run pytest -x -q    # stop on first failure, quiet output
uv run pytest tests/test_git.py  # single file
```

Ruff lint:

```bash
uv run ruff check tests/
```

## Test layout

One test file per domain module under `tests/`, named `test_<domain>.py` mirroring the source package name. Nested modules (e.g. `git/pullrequests/`) get their own dedicated file (e.g. `test_pullrequests.py`).

`ez_ados/client.py` (the top-level `AzureDevOps` facade) and `AzureCredential`/`ServicePrincipalCredential` are intentionally not tested here.

## Shared infrastructure (`tests/conftest.py`)

### Mock helpers (importable as plain functions)

```python
from conftest import ok_response, error_response, delete_ok_response
```

| Helper                             | Use for                                                                                          |
|------------------------------------|--------------------------------------------------------------------------------------------------|
| `ok_response(payload)`             | Happy-path GET/POST/PUT — returns mock with `status_code=200` and `json()` returning *payload*   |
| `delete_ok_response()`             | Successful DELETE — returns mock with `status_code=204`                                          |
| `error_response(status_code, url)` | Error path — `raise_for_status()` raises `niquests.HTTPError` with a correctly wired `.response` |

### `mock_session` fixture

```python
def test_something(mock_session):
    mock_session.get.return_value = ok_response({"id": "x"})
    client = SomeClient(mock_session)
    ...
```

All `Client` subclasses accept a `niquests.Session` as their first argument. Inject `mock_session` directly — no HTTP patching library is needed.

### Spec constants

Module-level dicts that represent the wire format sent by the Azure DevOps API:

```
PROJECT_SPEC, GIT_REPOSITORY_SPEC, PIPELINE_SPEC,
POLICY_TYPE_SPEC, POLICY_SCOPE_SPEC, POLICY_SETTINGS_SPEC,
POLICY_CONFIGURATION_SPEC, IDENTITY_SPEC, HOOK_SUBSCRIPTION_SPEC,
DATETIME_STR, PR_COMMENT_SPEC, PR_THREAD_SPEC
```

They are also available as pytest fixtures (same name, snake_case) that return a shallow copy.

When you add a new domain module, add a corresponding spec constant here so the rest of the suite can reuse it.

## Adding tests for a new domain module

1. Create `tests/test_<domain>.py`.
2. Add any necessary wire-format spec dicts to `conftest.py`.
3. Follow this structure:
   - Model validation tests first (happy path, invalid types, alias coercion).
   - Then client tests using `mock_session`.

Minimal template:

```python
"""Tests for <domain> models and <Domain>Client."""

import pydantic
import pytest

from conftest import ok_response

from ez_ados.<domain>.clients import <Domain>Client
from ez_ados.<domain>.models import <Model>


def test_model_valid():
    obj = <Model>.model_validate({...})
    assert obj.field == "expected"


def test_model_invalid_type():
    with pytest.raises(pydantic.ValidationError):
        <Model>.model_validate({"field": None})  # None not accepted


def test_client_get(mock_session):
    mock_session.get.return_value = ok_response({...})
    client = <Domain>Client(mock_session)

    result = client.get("identifier")

    assert isinstance(result, <Model>)
    mock_session.get.assert_called_once_with("identifier", params=None)
```

## Common patterns

- **Error paths** — use `error_response(404)` and assert `NotFoundError` is raised; use `error_response(500)` for `APIError`.
- **DELETE (204 No Content)** — set `mock_session.delete.return_value` to a mock with `status_code=204`; assert with `mock_session.delete.assert_called_once_with(...)`.
- **Enum validators** — use `@pytest.mark.parametrize` to cover both string and integer inputs; assert invalid values raise `ValueError`.
- **Pydantic aliases** — models use `serialize_by_alias=True` and accept both camelCase (wire) and snake_case (Python) field names; test both forms via `model_validate`.
- **POST/PUT request bodies** — `pytest.approx` does **not** support nested dicts; inspect `mock_session.post.call_args` directly to assert on the URL and individual JSON body fields.

## Ruff rules for test files

`S101` (assert), `S105` (hardcoded password literals in tokens/fixtures), `D100`/`D103` (module and function docstrings), and `PLR2004` (magic values in comparisons) are suppressed for `tests/*.py` in `pyproject.toml`. All other rules apply, including:

- `I` — imports must be sorted and at module level (no inline imports inside functions)
- `F401` — unused imports are errors
- `E501` — line length ≤ 120 characters

## Key technical notes

- **niquests** is a drop-in fork of `requests`. Use `niquests.HTTPError`, `niquests.Session`, `niquests.Response` when referencing HTTP types.
- **pydantic v2** `BeforeValidator` is **not** called for a field's default value when the field is absent from the input dict — only when the key is explicitly provided.
- `PurePosixPath("\\Builds")` on Linux does **not** parse the backslash as a separator. Use forward slashes or construct the expected path programmatically from the actual return value when asserting on `fullname`-style computed fields that involve `PureWindowsPath`.
- `bool` fields in pydantic v2 coerce many string values (including `"yes"`, `"on"`, `"true"`). Use a non-coercible type (e.g. a `dict`) to test invalid values.
