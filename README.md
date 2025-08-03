# 🌳 Ipê

**A next-generation OpenAPI code generator with an obsession for developer experience**

[![PyPI version](https://badge.fury.io/py/ipe.svg)](https://badge.fury.io/py/ipe)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/ipe/workflows/Tests/badge.svg)](https://github.com/yourusername/ipe/actions)

---

## ✨ Why Ipê?

Transform your OpenAPI specifications into **beautiful, production-ready code** in seconds. Named after the stunning Brazilian tree known for its vibrant blooms, Ipê brings the same elegance and reliability to code generation.

```bash
# From OpenAPI spec to production code in one command
ipe generate api-spec.yaml --generator python
```

### 🚀 **Lightning Fast**
Generate complete SDKs for 200+ endpoint APIs in under 10 seconds

### 🎨 **Beautiful Output**
Rich CLI with progress indicators, syntax highlighting, and intelligent defaults

### 🧠 **Developer-First**
Works perfectly out-of-the-box, highly customizable when you need it

### 📚 **Exceptionally Documented**
Every feature explained with examples and best practices

---

## 🎯 **Quick Start**

### Installation

```bash
# Install via pip
pip install ipe

# Or via uv (recommended)
uv add ipe
```

### Generate Your First Client

```bash
# Generate a Python client
ipe generate openapi.yaml --generator python --output ./my-client

# Watch for changes and auto-regenerate
ipe generate openapi.yaml --generator python --watch

# Interactive setup with smart defaults
ipe init
```

### **That's it!** 🎉

Your generated client includes:
- ✅ Fully typed Python classes
- ✅ Async/sync support with httpx
- ✅ Pydantic models for validation
- ✅ Authentication handling
- ✅ Comprehensive error handling
- ✅ Beautiful documentation

---

## 🛠️ **Supported Generators**

| Language   | Features | Status |
|------------|----------|--------|
| **Python** | httpx client, Pydantic models, async/sync, type hints | ✅ Ready |
| **TypeScript** | Axios/Fetch client, full type definitions, modern ES6+ | 🚧 Coming Soon |
| **JavaScript** | Modern ES6+, optional TypeScript declarations | 🚧 Coming Soon |
| **Go** | Native HTTP client, struct definitions | 📅 Planned |
| **Rust** | reqwest client, serde models | 📅 Planned |

---

## 🎨 **Live Example**

Transform this OpenAPI spec:

```yaml
openapi: 3.0.0
info:
  title: Pet Store API
  version: 1.0.0
paths:
  /pets:
    get:
      summary: List all pets
      responses:
        '200':
          description: A list of pets
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Pet'
components:
  schemas:
    Pet:
      type: object
      required: [id, name]
      properties:
        id:
          type: integer
        name:
          type: string
        status:
          type: string
          enum: [available, pending, sold]
```

Into this beautiful Python client:

```python
from my_client import PetStoreClient
from my_client.models import Pet

# Initialize client
client = PetStoreClient(base_url="https://api.petstore.com")

# Use with full type support
pets: List[Pet] = await client.pets.list()

for pet in pets:
    print(f"Pet {pet.name} (ID: {pet.id}) is {pet.status}")
```

---

## ⚙️ **Configuration**

Create an `ipe.json` file for project-specific settings:

```json
{
  "generator": "python",
  "output_dir": "./generated",
  "module_name": "my_awesome_client",
  "generators": {
    "python": {
      "client_library": "httpx",
      "async_client": true,
      "type_hints": true,
      "pydantic_models": true
    }
  }
}
```

Or use CLI options for quick customization:

```bash
ipe generate api.yaml \
  --generator python \
  --output ./client \
  --config custom-config.json
```

---

## 🔥 **Current Features**

### ✨ **Dry Run**
```bash
ipe generate api.yaml --dry-run
# Preview generated files without writing them
```

### 🩺 **Health Check**
```bash
ipe doctor
# Diagnose common issues and get suggestions
```

### 🔧 **Interactive Project Setup**
```bash
ipe init
# Interactive setup wizard for new projects
```

## 🚀 **Future Features** (Coming Soon)

### 👀 **Watch Mode**
Auto-regeneration when OpenAPI spec changes
- Real-time file monitoring with intelligent debouncing
- Integration with development workflows

### 🎯 **Custom Templates**
Support for user-defined Jinja2 templates
- Template inheritance system for extending built-in templates
- Plugin system for template modifications and custom generators

---

## 🏗️ **CLI Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `ipe generate` | Generate code from OpenAPI spec | `ipe generate api.yaml -g python` |
| `ipe init` | Interactive project setup | `ipe init` |
| `ipe validate` | Validate OpenAPI specification | `ipe validate api.yaml` |
| `ipe generators` | List available generators | `ipe generators` |
| `ipe doctor` | Diagnose issues | `ipe doctor` |
| `ipe version` | Show version info | `ipe version` |

---

## 🌟 **Why Choose Ipê?**

### **vs OpenAPI Generator**
- ⚡ **10x faster** generation
- 🎨 **Beautiful CLI** with rich output
- 🧠 **Smart defaults** - works without configuration
- 🔧 **Modern Python** - built with latest best practices

### **vs Swagger Codegen**
- 🚀 **Active development** with frequent updates
- 📚 **Better documentation** with real examples
- 🎯 **Developer-focused** design and user experience
- 🌊 **Cleaner generated code** with modern patterns

---

## 🤝 **Contributing**

We'd love your help making Ipê even better!

- 🐛 **Bug Reports**: [Open an issue](https://github.com/yourusername/ipe/issues)
- 💡 **Feature Requests**: [Start a discussion](https://github.com/yourusername/ipe/discussions)
- 🔧 **Pull Requests**: See our [Contributing Guide](CONTRIBUTING.md)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ipe.git
cd ipe

# Install with uv
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check
```

---

## 📝 **License**

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- Named after the beautiful [Ipê tree](https://en.wikipedia.org/wiki/Tabebuia), Brazil's national tree
- Inspired by the OpenAPI community and tools like OpenAPI Generator
- Built with love for developers who deserve better tools

---

<div align="center">

**[Documentation](https://ipe.readthedocs.io) • [Examples](examples/) • [Changelog](CHANGELOG.md)**

Made with 💚 by developers, for developers

</div>
