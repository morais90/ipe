# Future Features

This document outlines planned features and enhancements for future releases of Ipê.

## Built-in Extension System

### Core Concept
Ipê will feature a comprehensive built-in system where users can select which extensions they want included in their generated output. All extensions are maintained as part of the core project, ensuring quality and compatibility.

### Extension Selection
Users select extensions through configuration:

```json
{
  "generator": "python",
  "output_dir": "./src/clients",
  "module_name": "api_client",
  "extensions": [
    "testing",
    "async_client", 
    "pydantic_v2",
    "cli_wrapper",
    "fastapi_integration"
  ]
}
```

## Language Generator Extensions

### Python Generator Extensions

#### Testing Extension
Generates complete test suites for the API client:

```
my_api_client/
├── tests/
│   ├── __init__.py
│   ├── test_client.py          # Client method tests
│   ├── test_models.py          # Model validation tests
│   ├── conftest.py             # Pytest fixtures
│   └── test_integration.py     # Integration tests
├── pytest.ini                 # Pytest configuration
└── requirements-test.txt       # Testing dependencies
```

Features:
- Mock server setup with responses
- Comprehensive model validation tests
- Authentication testing
- Error handling tests
- Integration test examples

#### CLI Wrapper Extension
Generates a CLI wrapper for the API client:

```python
# Generated CLI
@click.group()
def cli():
    """Auto-generated CLI for MyAPI"""
    pass

@cli.command()
@click.option('--user-id', required=True)
def get_user(user_id: str):
    """Get user by ID"""
    client = APIClient()
    user = client.get_user(user_id)
    click.echo(json.dumps(user.model_dump(), indent=2))
```

#### FastAPI Integration Extension
Generates FastAPI integration utilities:

```python
# Generated FastAPI integration
from fastapi import Depends
from .client import APIClient
from .models import User

def get_api_client() -> APIClient:
    """FastAPI dependency for API client"""
    return APIClient()

@router.get("/proxy/users/{user_id}")
async def proxy_get_user(
    user_id: str,
    client: APIClient = Depends(get_api_client)
) -> User:
    """Proxy endpoint for external API"""
    return await client.get_user(user_id)
```

#### Auto-Pagination Extension
Enhanced pagination support with iterator patterns:

```python
# Auto-pagination with iterators
for user in client.users.list_iter(status="active"):
    process(user)

# Batch operations
async def batch_requests(operations: List[APIOperation]) -> List[APIResponse]:
    """Execute multiple API calls concurrently"""
    pass
```

#### Advanced Validation Extension
Enhanced validation and data processing:

```python
# Generated validation utilities
class APIValidator:
    """Enhanced validation for API requests/responses"""
    
    def validate_request(self, endpoint: str, data: dict) -> ValidationResult:
        """Validate request data before sending"""
        pass
        
    def sanitize_response(self, response: dict) -> dict:
        """Clean and validate response data"""
        pass
```

### TypeScript Generator Extensions

#### React Integration Extension
React hooks and components for API integration:

```typescript
// Generated React hooks
export function useGetUser(userId: string) {
  return useQuery(['user', userId], () => apiClient.getUser(userId));
}

export function useCreateUser() {
  return useMutation((userData: CreateUserRequest) => 
    apiClient.createUser(userData)
  );
}
```

#### Vue Integration Extension
Vue.js composables and utilities:

```typescript
// Generated Vue composables
export function useApiClient() {
  const { data, loading, error } = useAsyncData();
  // Generated composable logic
}
```

#### Node.js Server Extension
Express.js middleware and server utilities:

```typescript
// Generated Express middleware
export function createAPIProxy(config: ProxyConfig) {
  return express.Router()
    .get('/users/:id', proxyGetUser)
    .post('/users', proxyCreateUser);
}
```

## Advanced Code Generation Features

### Template Hooks System
Pre and post-generation hooks for advanced customization:

```
templates/{language}/
└── hooks/
    ├── pre_gen.py              # Execute before generation
    └── post_gen.py             # Execute after generation
```

Example hooks:
```python
# pre_gen.py
def execute(context: TemplateContext) -> TemplateContext:
    """Modify template context before generation"""
    # Custom logic to enhance or modify generation data
    return enhanced_context

# post_gen.py  
def execute(output_dir: Path, context: TemplateContext) -> None:
    """Process generated files after generation"""
    # Custom post-processing, formatting, additional file creation
    pass
```

### Automatic Test Generation
Comprehensive test suite generation for generated clients:

```python
def generate_test_suite(client_structure: ClientStructure, language: str) -> TestSuite:
    """Generate comprehensive test suite for generated client"""
    
    return TestSuite([
        # Resource operation tests
        *generate_resource_tests(client_structure.resources, language),
        
        # Model validation tests  
        *generate_model_tests(client_structure.models, language),
        
        # Error handling tests
        *generate_error_tests(client_structure.exceptions, language),
        
        # Authentication tests
        *generate_auth_tests(client_structure.auth_handlers, language),
        
        # Integration tests
        *generate_integration_tests(client_structure, language)
    ])
```

### Documentation Generation
Automatic documentation generation for generated clients:

```python
def generate_documentation(client_structure: ClientStructure) -> Documentation:
    """Generate complete documentation for the client"""
    
    return Documentation(
        readme=generate_readme_with_examples(client_structure),
        api_reference=generate_api_reference(client_structure),
        usage_examples=generate_usage_examples(client_structure),
        error_handling_guide=generate_error_guide(client_structure)
    )
```

### Advanced Authentication Support
Extended authentication scheme support:

```python
def generate_authentication_handlers(auth_schemes: List[AuthScheme], language: str) -> AuthCode:
    """Generate advanced authentication handling code"""
    
    handlers = []
    for scheme in auth_schemes:
        if scheme.type == "oauth2":
            # OAuth2 flow handling
            handlers.append(generate_oauth2_handler(scheme, language))
        elif scheme.type == "openIdConnect":
            # OpenID Connect integration
            handlers.append(generate_oidc_handler(scheme, language))
        elif scheme.type == "mutualTLS":
            # Mutual TLS authentication
            handlers.append(generate_mtls_handler(scheme, language))
    
    return AuthCode(handlers=handlers, token_refresh=generate_token_refresh_logic(language))
```

### Advanced OpenAPI Schema Support

#### Discriminated Unions
Full support for oneOf/anyOf with discriminator fields:

```python
# Generated discriminated union support
class Animal(BaseModel):
    type: Literal["dog", "cat"]  # Discriminator field
    name: str

class Dog(Animal):
    type: Literal["dog"] = "dog"
    breed: str
    
class Cat(Animal):
    type: Literal["cat"] = "cat"
    indoor: bool

# Union type with discriminator
AnimalUnion = Annotated[Union[Dog, Cat], Field(discriminator="type")]
```

#### Complex Schema Patterns
Support for advanced OpenAPI schema patterns:
- Nested allOf/oneOf/anyOf combinations
- Conditional schemas with if/then/else
- Complex property dependencies
- Schema composition and inheritance

### Performance Optimization Features

#### Connection Pooling
Advanced HTTP client configuration:

```python
class AdvancedAPIClient:
    """API client with advanced connection management"""
    
    def __init__(self, pool_connections=10, pool_maxsize=20):
        self.session = httpx.Client(
            limits=httpx.Limits(
                max_keepalive_connections=pool_connections,
                max_connections=pool_maxsize
            )
        )
```

#### Retry Logic with Backoff
Configurable retry strategies:

```python
@dataclass
class RetryConfig:
    max_attempts: int = 3
    backoff_factor: float = 0.5
    retry_on_status: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])
    retry_on_exceptions: List[Type[Exception]] = field(default_factory=lambda: [RequestTimeout, ConnectionError])
```

#### Response Caching
Intelligent response caching:

```python
class CachedAPIClient(APIClient):
    """API client with intelligent response caching"""
    
    def __init__(self, cache_config: CacheConfig):
        super().__init__()
        self.cache = setup_cache(cache_config)
        
    def _make_cached_request(self, method: str, path: str, **kwargs):
        """Make request with caching support"""
        # Intelligent caching logic based on HTTP semantics
        pass
```

## Cross-Language Extensions

### Package Output Type
Generate standalone, publishable packages:

```bash
ipe generate api.yaml --output-type package --package-name my-api-sdk
```

**Generated Structure:**
```
my-api-sdk/
├── pyproject.toml          # Package metadata & dependencies
├── README.md               # Usage documentation and examples
├── LICENSE                 # Package license
├── src/my_api_sdk/
│   ├── __init__.py         # Public API exports
│   ├── client.py           # Main API client class
│   └── models.py           # Data models
└── examples/               # Usage examples
    └── basic_usage.py
```

### Docker Extension
Docker containerization support:

```dockerfile
# Generated Dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "-m", "my_api_client.cli"]
```

### Configuration Extension
Advanced configuration management:

```python
# Generated configuration
class APIConfig(BaseSettings):
    base_url: str
    api_key: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3
    
    class Config:
        env_prefix = "API_"
        env_file = ".env"
```

## Development Workflow Features

### Watch Mode
Auto-regeneration when OpenAPI spec changes:

```bash
ipe generate api.yaml --output ./src/clients/ --watch
```

### Validation Command
Standalone specification validation:

```bash
ipe validate api.yaml
```

### Generator Discovery
List available generators and their capabilities:

```bash
ipe generators
```

### Diagnostic Tool
System diagnostics and troubleshooting:

```bash
ipe doctor
```

## Quality Assurance Extensions

Each extension includes:
- Comprehensive test coverage
- Full documentation with examples
- Consistent coding standards
- Regular compatibility updates
- Performance benchmarking

## Implementation Timeline

### Phase 1: Core Extensions (v0.2.0+)
- Auto-pagination
- Basic testing extension
- Package output type

### Phase 2: Framework Integrations (v0.3.0+)
- React/Vue/FastAPI integrations
- CLI wrapper generation
- Documentation generation

### Phase 3: Advanced Features (v0.4.0+)
- Template hooks system
- Advanced authentication
- Performance optimizations
- Complex schema support

This comprehensive extension system provides rich functionality while maintaining simplicity and quality control through built-in, well-tested extensions.