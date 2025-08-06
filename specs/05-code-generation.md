# Code Generation Specification

## Overview

Ipê generates resource-based API clients that provide exceptional developer experience through intuitive organization, strong type safety, and comprehensive error handling. The generation system is language-agnostic at its core, with language-specific templates handling the nuances of each target environment.

## Core Requirements for Generated Code

### 1. Resource-Based Client Organization
API operations are logically grouped by resource, creating intuitive client interfaces that mirror the API's structure and common usage patterns.

### 2. Strong Type Safety
Generated code includes comprehensive type information, client-side validation, and schema-aware request/response handling to catch errors early in the development process.

### 3. Comprehensive Error Handling
HTTP errors are mapped to language-appropriate exception hierarchies with clear, actionable error messages and proper error context.

### 4. Idiomatic Code Generation
Generated code follows the conventions, patterns, and best practices of the target language, appearing as if written by an experienced developer in that language.

### 5. Schema Validation
All request and response data is validated against the OpenAPI schema, ensuring API contract compliance and providing immediate feedback for data inconsistencies.

### 6. Forward Compatibility
Generated clients handle unknown fields gracefully and are designed to work with evolving APIs without breaking existing code.

## Developer Experience Goals

The generated clients should provide an intuitive, discoverable API that feels natural in the target language:

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

**TypeScript Example:**
```typescript
import { PetStoreClient } from './petstore-client';

const client = new PetStoreClient({ apiKey: 'your-key' });

// Resource-based organization with full typing
const users: User[] = await client.users.list({ status: 'active', limit: 50 });
const user: User = await client.users.get({ userId: '123' });
const newUser: User = await client.users.create({ name: 'John', email: 'john@example.com' });

// Comprehensive error handling
try {
    const user = await client.users.get({ userId: 'invalid-id' });
} catch (error) {
    if (error instanceof PetStoreClient.NotFoundError) {
        console.log('User not found');
    } else if (error instanceof PetStoreClient.ValidationError) {
        console.log(`Invalid data: ${error.detail}`);
    }
}
```

## Generation Process

### 1. Resource Organization
Operations are grouped into logical resources based on OpenAPI tags or path analysis:

```python
def organize_operations_by_resource(operations: List[StandardOperation]) -> Dict[str, List]:
    """Group operations into resources for intuitive client organization"""
    
    resources = {}
    
    for operation in operations:
        # Determine resource from tags or path analysis
        resource_name = extract_resource_name(operation)
        
        # Determine method name based on HTTP method and patterns
        method_name = determine_method_name(operation)
        
        if resource_name not in resources:
            resources[resource_name] = []
            
        resources[resource_name].append({
            "method_name": method_name,
            "operation": operation
        })
    
    return resources

def extract_resource_name(operation: StandardOperation) -> str:
    """Extract resource name using intelligent heuristics"""
    
    # Prefer explicit tags
    if operation.tags:
        return normalize_name(operation.tags[0])
    
    # Extract from path structure
    path_segments = [segment for segment in operation.path.split("/") 
                    if segment and not segment.startswith("{")]
    if path_segments:
        return normalize_name(path_segments[0])
    
    return "default"

def determine_method_name(operation: StandardOperation) -> str:
    """Determine method name based on HTTP method and path patterns"""
    
    # Standard CRUD patterns
    if operation.method == "GET":
        return "get" if has_path_parameter(operation) else "list"
    elif operation.method == "POST":
        return "create"
    elif operation.method in ["PUT", "PATCH"]:
        return "update"
    elif operation.method == "DELETE":
        return "delete"
    else:
        # Use operation ID or generate from context
        return normalize_name(operation.operation_id or "perform_operation")
```

### 2. Type System Integration

Each language template provides sophisticated type mapping from OpenAPI schemas:

```python
def map_openapi_type_to_language(schema: Dict[str, Any], language: str) -> str:
    """Convert OpenAPI schema to appropriate language type"""
    
    type_mappers = {
        "python": PythonTypeMapper(),
        "typescript": TypeScriptTypeMapper(), 
        "go": GoTypeMapper(),
        "rust": RustTypeMapper()
    }
    
    return type_mappers[language].convert_schema(schema)

class TypeMapper(ABC):
    """Base type mapper interface"""
    
    @abstractmethod
    def convert_schema(self, schema: Dict[str, Any]) -> str:
        """Convert OpenAPI schema to language-specific type"""
        pass
    
    @abstractmethod
    def handle_array_type(self, items_schema: Dict[str, Any]) -> str:
        pass
    
    @abstractmethod
    def handle_nullable_type(self, base_type: str) -> str:
        pass
    
    @abstractmethod
    def handle_complex_type(self, schema: Dict[str, Any]) -> str:
        pass
```

### 3. Error Handling Generation

Each language template defines appropriate error handling patterns:

```python
def generate_error_hierarchy(responses: Dict[str, Response], language: str) -> List[ErrorClass]:
    """Generate language-appropriate error handling"""
    
    # Extract unique status codes
    status_codes = extract_error_status_codes(responses)
    
    # Map to semantic error classes
    error_classes = map_status_codes_to_errors(status_codes)
    
    # Generate language-specific error hierarchy
    return generate_language_errors(error_classes, language)

def map_status_codes_to_errors(status_codes: List[int]) -> List[str]:
    """Map HTTP status codes to semantic error types"""
    
    error_mapping = {
        400: "BadRequestError",
        401: "UnauthorizedError", 
        403: "ForbiddenError",
        404: "NotFoundError",
        409: "ConflictError",
        422: "ValidationError",
        429: "RateLimitError",
        500: "InternalServerError",
        502: "BadGatewayError",
        503: "ServiceUnavailableError"
    }
    
    return [error_mapping.get(code, f"HTTPError{code}") for code in status_codes]
```

### 4. Client Structure Generation

The generation process creates structured, discoverable client interfaces:

```python
def generate_client_structure(resources: Dict[str, List], language: str) -> ClientStructure:
    """Generate the overall client class structure"""
    
    return ClientStructure(
        main_client_class=generate_main_client(resources, language),
        resource_managers=generate_resource_managers(resources, language),
        model_classes=generate_model_classes(language),
        exception_hierarchy=generate_exception_classes(language),
        authentication_handlers=generate_auth_handlers(language)
    )

def generate_main_client(resources: Dict[str, List], language: str) -> MainClient:
    """Generate the primary client class with resource managers"""
    
    return MainClient(
        initialization=generate_client_init(language),
        resource_properties=[
            ResourceProperty(name=resource_name, manager_class=f"{resource_name}Manager")
            for resource_name in resources.keys()
        ],
        authentication_setup=generate_auth_setup(language),
        request_handling=generate_request_methods(language)
    )
```

## Template System Architecture

### Language Template Structure

Each language template follows a consistent structure while adapting to language-specific patterns:

```
templates/{language}/
├── plugin.py                    # Language template implementation
├── copier.yml                   # Generation configuration
└── {{module_name}}/
    ├── client.{ext}.jinja       # Main client class
    ├── models.{ext}.jinja       # Data model definitions
    ├── exceptions.{ext}.jinja   # Error handling classes
    ├── auth.{ext}.jinja         # Authentication handlers
    └── README.md.jinja          # Usage documentation
```

### Template Context Structure

Templates receive rich, normalized data from the kernel:

```python
@dataclass
class TemplateData:
    """Complete data context for template generation"""
    
    # Basic metadata
    module_name: str
    client_class_name: str
    spec_info: SpecInfo
    
    # Organized operations
    resources: Dict[str, List[ResourceOperation]]
    
    # Type definitions
    models: List[ModelDefinition]
    enums: List[EnumDefinition]
    
    # Error handling
    error_responses: List[ErrorResponse]
    exception_classes: List[ExceptionDefinition]
    
    # Authentication
    auth_schemes: List[AuthScheme]
    
    # Generation metadata
    generated_timestamp: str
    generator_version: str
    language_config: Dict[str, Any]

@dataclass
class ResourceOperation:
    """Language-agnostic operation representation"""
    method_name: str
    http_method: str
    path: str
    summary: Optional[str]
    parameters: List[Parameter]
    request_body: Optional[RequestBodySpec]
    response_type: str
    error_responses: List[ErrorResponse]
    authentication_required: bool
```

## Quality Standards

### Code Generation Standards

1. **Type Safety**: All generated code includes comprehensive type information
2. **Validation**: Request and response data validated against schemas
3. **Error Handling**: Comprehensive error mapping with clear error messages
4. **Documentation**: Generated code includes helpful docstrings and comments
5. **Performance**: Efficient request handling and data serialization
6. **Maintainability**: Clean, readable generated code that follows language conventions

### Authentication Integration

Support for essential authentication schemes:

```python
def generate_authentication_handlers(auth_schemes: List[AuthScheme], language: str) -> AuthCode:
    """Generate authentication handling code"""
    
    handlers = []
    for scheme in auth_schemes:
        if scheme.type == "apiKey":
            handlers.append(generate_api_key_handler(scheme, language))
        elif scheme.type == "http" and scheme.scheme == "bearer":
            handlers.append(generate_bearer_token_handler(scheme, language))
        elif scheme.type == "http" and scheme.scheme == "basic":
            handlers.append(generate_basic_auth_handler(scheme, language))
    
    return AuthCode(handlers=handlers, selection_logic=generate_auth_selection(language))
```

### Basic File Upload Support

Essential support for file uploads:

```python
def generate_file_upload_support(operations: List[ResourceOperation], language: str) -> FileUploadCode:
    """Generate basic file upload handling"""
    
    upload_operations = [op for op in operations if has_file_uploads(op)]
    
    return FileUploadCode(
        upload_methods=generate_upload_methods(upload_operations, language),
        content_type_detection=generate_basic_content_type_logic(language)
    )
```

This comprehensive code generation system ensures that all generated clients provide exceptional developer experience while maintaining consistency across languages and full compatibility with OpenAPI specifications.