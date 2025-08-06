# CLI Interface Specification

## Core Commands (MVP)

### Essential Commands
```bash
ipe generate SPEC --output PATH [OPTIONS]    # Main generation command
ipe init                                     # Interactive project setup  
ipe version                                  # Version info
```

## Generate Command

### Basic Usage
```bash
# From local file
ipe generate api.yaml --output ./src/clients/

# From URL
ipe generate https://api.example.com/openapi.json --output ./src/clients/
```

### Full Options
```bash
ipe generate SPEC --output PATH \
  --generator python \           # Target language (default: python)
  --module-name my_api_client \  # Module name (auto-detected from spec)
  --config ./ipe.json            # Config file path (optional)
```

### Spec Source Support
- **Local files**: `./api.yaml`, `../specs/openapi.json`
- **URLs**: `https://api.example.com/openapi.yaml`
- **Both YAML and JSON**: Auto-detection based on content

## Primary Use Case: Embedded Module Generation

```bash
# Generate into existing project
ipe generate api.yaml --output ./myapp/clients/

# From URL with custom module name
ipe generate https://api.example.com/openapi.json \
  --output ./src/integrations/ \
  --module-name external_api
```

**Generated Structure:**
```
myapp/clients/my_api_client/
├── __init__.py             # Client exports
├── client.py               # Main API client class
├── models/                 # Data models
│   ├── __init__.py
│   ├── user.py
│   └── pet.py
├── auth.py                 # Authentication handling
└── exceptions.py           # Custom exception classes
```

## User Experience Design

### Beautiful CLI Output
```
🌳 Ipê - OpenAPI Code Generator

✅ Validating OpenAPI specification...
📋 Found 25 endpoints, 12 models
🎯 Generating Python client...

  ⚡ Creating models...        ████████████████ 12/12
  🔧 Building client class...  ████████████████ 25/25
  📝 Writing files...         ████████████████ 100%

🎉 Generated successfully!
   📁 Output: ./myapp/clients/my_api_client/
   📊 Files: 8 created
   ⏱️  Time: 0.8s

💡 Next steps:
   • Import: from myapp.clients.my_api_client import APIClient
   • Usage: client = APIClient(base_url="https://api.example.com")
```

### Error Messages (Helpful & Actionable)
```
❌ OpenAPI specification is invalid

📍 Error at line 42, column 15:
   Path: $.paths./users.get.responses.200
   Issue: Missing required field 'description'

💡 Suggestion:
   Add a description for the 200 response:

   responses:
     '200':
       description: 'List of users'
       content: ...
```

### URL Fetch Feedback
```
🌐 Fetching OpenAPI specification from URL...
   📡 GET https://api.example.com/openapi.yaml
   ✅ Downloaded successfully (24.5 KB)
```

## Command Details

### `ipe generate SPEC --output PATH [OPTIONS]`
Main generation command with automatic validation:
- Accepts local files or URLs
- Auto-detects YAML/JSON format  
- Validates spec before generation
- Creates module structure in target directory
- Provides progress feedback

**Required Arguments:**
- `SPEC`: Path to OpenAPI file or URL
- `--output PATH`: Target directory

**Optional Arguments:**
- `--generator TEXT`: Language generator (default: `python`)
- `--module-name TEXT`: Generated module name (auto-detected from spec title)
- `--config PATH`: Configuration file path

### `ipe init`
Interactive project setup:
- Prompts for OpenAPI spec location (file or URL)
- Suggests output directory based on project structure
- Creates `ipe.json` with defaults
- Tests spec validation and provides immediate feedback

### `ipe version`
Simple version display:
- Shows current version
- Python compatibility info

## CLI Options Reference

### Generate Command
| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `SPEC` | OpenAPI spec file or URL | - | **Yes** |
| `--output PATH` | Output directory | - | **Yes** |
| `--generator TEXT` | Target generator | `python` | No |
| `--module-name TEXT` | Module name | Auto-detected | No |
| `--config PATH` | Configuration file | `./ipe.json` | No |

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Command completed successfully |
| 1 | General Error | Unspecified error occurred |
| 2 | Invalid Usage | Missing required arguments |
| 3 | Validation Error | OpenAPI specification is invalid |
| 4 | Generation Error | Code generation failed |
| 5 | Network Error | Failed to fetch spec from URL |

## Integration Examples

### GitHub Actions
```yaml
- name: Generate API Client
  run: |
    pip install ipe
    ipe generate https://api.example.com/openapi.yaml --output ./src/clients/
```

### Makefile Integration
```makefile
.PHONY: generate-client
generate-client:
	ipe generate api.yaml --output ./src/clients/
```

This streamlined CLI focuses on delivering the essential module generation functionality with excellent developer experience.