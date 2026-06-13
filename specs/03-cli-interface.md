# CLI Interface Specification

## Configuration Priority

See [04-configuration-system.md](04-configuration-system.md) for the full configuration resolution chain. In short: `CLI arguments > ipe.json > smart defaults`.

## Core Commands (MVP)

```bash
ipe generate [SPEC] [--output PATH] [OPTIONS]   # Main generation command
ipe init                                         # Interactive project setup
ipe version                                      # Version info
```

## Generate Command

### Usage Flows

Ipê supports three usage flows so developers can pick the right level of configuration for their situation.

#### Ad-hoc (no ipe.json needed)
Everything supplied on the command line. No config file required.

```bash
ipe generate api.yaml --output ./src/clients/ --target python
```

#### Project-configured (with ipe.json)
Everything lives in the config file. Just run `generate`.

```bash
ipe generate
```

This reads `spec_path`, `output_dir`, `target`, `module_name`, and all target-specific settings from `ipe.json`.

#### Mixed (config + CLI overrides)
Use the config file as a baseline and override specific values via CLI arguments.

```bash
# Uses ipe.json for target settings, CLI for spec and output
ipe generate other-api.yaml --output ./other/

# Uses ipe.json for everything except the spec
ipe generate https://staging.example.com/openapi.yaml
```

### Options Reference

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `SPEC` | OpenAPI spec file or URL | From `ipe.json` `spec_path` | Only if not in config |
| `--output PATH` / `-o` | Output directory | From `ipe.json` `output_dir` | Only if not in config |
| `--target TEXT` / `-t` | Language target | `python` (or from config) | No |
| `--module-name TEXT` / `-m` | Module name | Auto-detected (or from config) | No |
| `--config PATH` | Configuration file | `./ipe.json` | No |

### Resolution Examples

| Scenario | SPEC | --output | --target | Result |
|----------|------|----------|----------|--------|
| Full CLI | `api.yaml` | `./src/clients/` | `python` | All from CLI |
| Full config | _(omitted)_ | _(omitted)_ | _(omitted)_ | All from `ipe.json` |
| Mixed | `other.yaml` | `./other/` | _(omitted)_ | Spec/output from CLI, target from config or default |
| Minimal CLI, no config | `api.yaml` | `./src/clients/` | _(omitted)_ | Target defaults to `python` |

If `SPEC` and `--output` are both omitted and no `ipe.json` is found, Ipê exits with a helpful error:

```
Missing required arguments: SPEC and --output

Either provide them on the command line:
  ipe generate api.yaml --output ./src/clients/

Or create a configuration file:
  ipe init
```

### Spec Source Support
- **Local files**: `./api.yaml`, `../specs/openapi.json`
- **URLs**: `https://api.example.com/openapi.yaml`
- **Both YAML and JSON**: Auto-detection based on content

Remote specs are fetched over **HTTPS only** (an `http://` URL, or a redirect to one, is rejected) and are capped at **25 MB** to bound memory; a larger response fails with a clear error.

## Generated Output

See [05-code-generation.md](05-code-generation.md#generated-output-structure) for the full generated file structure and grouping rules.

```bash
# Generate into existing project (ad-hoc)
ipe generate api.yaml --output ./myapp/clients/

# From URL with custom module name
ipe generate https://api.example.com/openapi.json \
  --output ./src/integrations/ \
  --module-name external_api

# From project config
ipe generate
```

## Other Commands

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

## User Experience Design

### Beautiful CLI Output
```
Ipê - OpenAPI Code Generator

  Validating OpenAPI specification...
  Found 25 endpoints, 12 models
  Generating Python client...

  Creating models...        ################ 12/12
  Building resources...     ################ 5/5
  Building client class...  ################ 25/25
  Writing files...          ################ 100%

  Generated successfully!
     Output: ./myapp/clients/my_api_client/
     Files: 12 created
     Time: 0.8s

  Next steps:
     Import: from myapp.clients.my_api_client import APIClient
     Usage: client = APIClient(base_url="https://api.example.com")
```

### Error Messages (Helpful & Actionable)
```
  OpenAPI specification is invalid

  Error at line 42, column 15:
   Path: $.paths./users.get.responses.200
   Issue: Missing required field 'description'

  Suggestion:
   Add a description for the 200 response:

   responses:
     '200':
       description: 'List of users'
       content: ...
```

### URL Fetch Feedback
```
  Fetching OpenAPI specification from URL...
     GET https://api.example.com/openapi.yaml
     Downloaded successfully (24.5 KB)
```

### Config Resolution Feedback
When running with a mix of CLI args and config values, Ipê shows exactly where each value came from:

```
  Configuration:
     Spec:       other-api.yaml          (CLI)
     Output:     ./other/                (CLI)
     Target:     python                  (ipe.json)
     Module:     other_api               (auto-detected)
```

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Command completed successfully |
| 1 | General Error | Unspecified error occurred |
| 2 | Invalid Usage | Missing required arguments (SPEC/output not in CLI or config) |
| 3 | Validation Error | OpenAPI specification is invalid |
| 4 | Generation Error | Code generation failed |
| 5 | Network Error | Failed to fetch spec from URL |
| 6 | Config Error | Configuration file is invalid or unreadable |

## Integration Examples

### GitHub Actions
```yaml
# Ad-hoc: no config file needed in the repo
- name: Generate API Client
  run: |
    pip install ipe
    ipe generate https://api.example.com/openapi.yaml \
      --output ./src/clients/ \
      --target python

# Project-configured: uses ipe.json checked into the repo
- name: Generate API Client
  run: |
    pip install ipe
    ipe generate
```

### Makefile Integration
```makefile
.PHONY: generate-client
generate-client:
	ipe generate

.PHONY: generate-staging
generate-staging:
	ipe generate https://staging.example.com/openapi.yaml --output ./src/staging-clients/
```

### Pre-commit Hook
```bash
#!/bin/bash
# Regenerate client if spec changed
if git diff --cached --name-only | grep -q "openapi.yaml"; then
  ipe generate
  git add src/clients/
fi
```
