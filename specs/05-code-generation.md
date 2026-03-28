# Code Generation Specification

## Overview

This spec defines **what** Ipê generates and **why** -- the qualities, structure, and conventions of the generated code. For **how** the generation pipeline works (SpecAnalyzer, LanguageTarget, TemplateRenderer), see [02-architecture.md](02-architecture.md).

Data models used in the generation process (APIBlueprint, StandardOperation, StandardModel, OutputFile, etc.) are defined in [02-architecture.md](02-architecture.md#canonical-data-models).

## Requirements for Generated Code

### 1. Resource-Based Client Organization
API operations are logically grouped by resource, creating intuitive client interfaces that mirror the API's structure and common usage patterns.

### 2. Strong Type Safety
Generated code includes comprehensive type information, client-side validation, and schema-aware request/response handling to catch errors early.

### 3. Comprehensive Error Handling
HTTP errors are mapped to language-appropriate exception hierarchies with clear, actionable error messages and proper error context.

### 4. Idiomatic Code
Generated code follows the conventions, patterns, and best practices of the target language, appearing as if written by an experienced developer.

### 5. Schema Validation
All request and response data is validated against the OpenAPI schema, ensuring API contract compliance and providing immediate feedback for data inconsistencies.

### 6. Forward Compatibility
Generated clients handle unknown fields gracefully and work with evolving APIs without breaking existing code.

## Developer Experience Goals

The generated clients should provide an intuitive, discoverable API that feels natural in the target language.

**Python Example:**
```python
from petstore.client import PetStoreClient

client = PetStoreClient(api_key="your-key")

# Resource-based organization
users = client.users.list(status="active", limit=50)
user = client.users.get(user_id="123")
new_user = client.users.create(name="John", email="john@example.com")

# Comprehensive error handling
try:
    user = client.users.get("invalid-id")
except PetStoreClient.NotFoundError:
    print("User not found")
except PetStoreClient.ValidationError as e:
    print(f"Invalid data: {e.detail}")
```

**TypeScript (future target):**
```typescript
import { PetStoreClient } from './petstore-client';

const client = new PetStoreClient({ apiKey: 'your-key' });

const users: User[] = await client.users.list({ status: 'active', limit: 50 });
const user: User = await client.users.get({ userId: '123' });

try {
    const user = await client.users.get({ userId: 'invalid-id' });
} catch (error) {
    if (error instanceof PetStoreClient.NotFoundError) {
        console.log('User not found');
    }
}
```

## Generated Output Structure

```
petstore/
├── __init__.py              # Public API: re-exports client and models
├── client.py                # Main client with resource accessors
├── exceptions.py            # Exception hierarchy
├── auth.py                  # Authentication handlers
├── models/
│   ├── __init__.py          # Re-exports all model classes
│   ├── user.py              # User, CreateUserRequest, UpdateUserRequest
│   └── pet.py               # Pet, PetStatus
└── resources/
    ├── __init__.py           # Re-exports all resource managers
    ├── users.py              # UsersResource with list, get, create, update, delete
    └── pets.py               # PetsResource with list, get, create
```

Each schema in the OpenAPI spec becomes its own file under `models/`. Each logical group of endpoints becomes its own file under `resources/`. This keeps generated code navigable and diff-friendly.

## Grouping Rules

### Operations → Resources

Operations are grouped by their primary tag. When tags are absent, the first non-parameterized path segment is used. Each group produces a single resource file in `resources/`.

| Path | Tag | Resource | File |
|------|-----|----------|------|
| `GET /users` | `users` | `users` | `resources/users.py` |
| `GET /users/{id}` | `users` | `users` | `resources/users.py` |
| `POST /pets` | _(none)_ | `pets` (from path) | `resources/pets.py` |

### Schemas → Model Files

Related models are grouped by the resource they belong to. Request/response variants (e.g., `User`, `CreateUserRequest`, `UpdateUserRequest`) live together. Schemas not tied to a specific resource go into `common.py`.

### Method Naming

Standard CRUD patterns are detected from the HTTP method:

| HTTP Method | Path Pattern | Generated Method |
|-------------|-------------|-----------------|
| `GET` | `/resources` | `list()` |
| `GET` | `/resources/{id}` | `get()` |
| `POST` | `/resources` | `create()` |
| `PUT` / `PATCH` | `/resources/{id}` | `update()` |
| `DELETE` | `/resources/{id}` | `delete()` |

For non-standard operations, the `operationId` is used via the target's `NamingConvention`.

## Generated Exception Hierarchy

Error classes are generated based on the HTTP status codes found across all operations in the spec. Only status codes actually present in the spec produce error classes.

```python
# Generated exceptions.py
class PetStoreError(Exception):
    def __init__(self, message: str, status_code: int, detail: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


class NotFoundError(PetStoreError):
    """Raised when the requested resource does not exist (404)."""


class ValidationError(PetStoreError):
    """Raised when the request data fails validation (422)."""
```

The full status code → error class mapping is defined in the target implementation. See [02-architecture.md](02-architecture.md#target-implementation-example-python) for the Python target's error mappings.

## Generated Authentication

Support for essential authentication schemes, generated based on the `securitySchemes` in the OpenAPI spec.

**Supported in v0.1:** API key, Bearer token, Basic auth.

```python
# Generated auth.py
class AuthHandler:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        bearer_token: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.username = username
        self.password = password

    def apply(self, headers: dict[str, str]) -> dict[str, str]:
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.username and self.password:
            import base64
            credentials = base64.b64encode(
                f"{self.username}:{self.password}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {credentials}"
        return headers
```

## Generated File Upload Handling

Operations that accept `multipart/form-data` produce methods with file parameters:

```python
# Generated resource method with file upload
def upload_avatar(
    self,
    user_id: str,
    file: BinaryIO,
    *,
    filename: str | None = None,
) -> User:
    files = {"file": (filename or "upload", file)}
    response = self._client.request(
        "POST",
        f"/users/{user_id}/avatar",
        files=files,
    )
    return User.model_validate(response.json())
```

## Template Directory Structure

Each target has a self-contained template directory with Jinja2 files:

```
targets/python/templates/
├── __init__.py.jinja            # Package root
├── client.py.jinja              # Main client class
├── auth.py.jinja                # Authentication handlers
├── exceptions.py.jinja          # Exception hierarchy
├── models/
│   ├── __init__.py.jinja        # Model re-exports
│   └── model.py.jinja           # Rendered once per model group
└── resources/
    ├── __init__.py.jinja        # Resource re-exports
    └── resource.py.jinja        # Rendered once per resource
```

The target's `plan()` method determines which templates are rendered and where the output goes. See [02-architecture.md](02-architecture.md#target-implementation-example-python) for how the Python target assembles its render plan.

## Quality Standards

### Code Generation Checklist

- Every public class and method has a docstring
- Every function parameter and return value is type-annotated
- All model fields declare default values or are marked required
- Re-export `__init__.py` files provide clean public API surfaces
- Exception classes carry `status_code` and `detail` for debugging
- Generated code passes the target language's standard linter without configuration

### Python-Specific Standards

1. **Type Safety**: Comprehensive type annotations (modern `list[str]` syntax)
2. **Validation**: Request and response data validated via Pydantic models
3. **Performance**: Connection pooling via httpx
4. **Conventions**: PEP 8 compliant, ruff-clean output

### MVP Scope

- **Python**: Full support (MVP target)
- **TypeScript**: Planned as the second language target (see [99-future-features.md](99-future-features.md))
