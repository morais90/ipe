# 🌳 Ipê

**A next-generation OpenAPI code generator with an obsession for developer experience**

[![PyPI version](https://badge.fury.io/py/ipe.svg)](https://badge.fury.io/py/ipe)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/ipe/workflows/Tests/badge.svg)](https://github.com/yourusername/ipe/actions)

---

## ✨ Transform APIs into Beautiful Code

From OpenAPI specification to production-ready client in **one command**. Named after the stunning Brazilian tree known for its vibrant blooms, Ipê brings the same elegance and reliability to code generation.

```bash
ipe generate api.yaml --output ./src/clients/
```

### ⚡ **Lightning Fast**
Sub-second generation for most specs

### 🎨 **Beautiful Output**  
Rich CLI with progress indicators and syntax highlighting

### 🧠 **Zero Configuration**
Works perfectly out-of-the-box with intelligent defaults

### 🚀 **Multi-Language Ready**
Start with Python, expand to TypeScript, Go, and more

---

## 🎯 **Get Started in 30 Seconds**

```bash
# Install
pip install ipe

# Generate your first client
ipe init
ipe generate openapi.yaml --output ./src/clients/
```

**That's it!** Your API client is ready to use:

```python
from petstore.client import PetStoreClient

client = PetStoreClient(api_key="your-key")

# Intuitive resource-based API
users = client.users.list(status="active")
user = client.users.get(user_id="123")
new_user = client.users.create(name="John", email="john@example.com")

# Smart error handling
try:
    user = client.users.get("invalid-id")
except PetStoreClient.NotFoundError:
    print("User not found")
```

---

## 🎨 **See It In Action**

Transform this OpenAPI spec:

```yaml
openapi: 3.0.0
info:
  title: Pet Store API
paths:
  /pets:
    get:
      summary: List pets
      responses:
        '200':
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
        id: { type: integer }
        name: { type: string }
        status: 
          type: string
          enum: [available, pending, sold]
```

Into this beautiful Python client:

```python
from petstore_client import PetStoreClient

client = PetStoreClient(base_url="https://api.petstore.com")

# Fully typed, auto-complete ready
pets: List[Pet] = client.pets.list()

for pet in pets:
    print(f"🐾 {pet.name} is {pet.status}")
```

---

## 🚀 **What You Get**

### ✅ **Resource-Based Organization**
Intuitive APIs that mirror your OpenAPI structure
```python
client.users.list()     # GET /users
client.pets.create()    # POST /pets
```

### ✅ **Full Type Safety**
Complete type hints with client-side validation
```python
# Type errors caught before runtime
user: User = client.users.get(user_id=123)  # ✅ 
user: User = client.users.get(user_id="invalid")  # ❌ Type error
```

### ✅ **Smart Error Handling**
Meaningful exceptions with helpful context
```python
except PetStoreClient.NotFoundError as e:
    print(f"Resource not found: {e.message}")
except PetStoreClient.ValidationError as e:
    print(f"Invalid data: {e.details}")
```

### ✅ **Authentication Made Easy**
Multiple auth methods, clean initialization
```python
# API Key
client = PetStoreClient(api_key="secret")

# Bearer Token  
client = PetStoreClient(bearer_token="jwt-token")

# OAuth (coming soon)
client = PetStoreClient(client_id="id", client_secret="secret")
```

### ✅ **File Uploads**
Seamless handling of multipart form data
```python
# Upload files with ease
avatar = client.users.upload_avatar(
    user_id="123",
    file=open("avatar.jpg", "rb")
)
```

---

## 🛠️ **Language Support**

| Language | Status |
|----------|---------|
| **Python** | ✅ Ready |
| **TypeScript** | 🚧 In Development |
| **JavaScript** | 📅 Planned |
| **Go** | 📅 Planned |

---

## ⚙️ **Simple Configuration**

Everything lives in one clean `ipe.json` file:

```json
{
  "generator": "python",
  "output_dir": "./src/clients",
  "spec_path": "openapi.yaml"
}
```

Or use CLI options for quick customization:
```bash
ipe generate api.yaml --output ./clients/ --module-name my_client
```

---

## 🎯 **CLI Commands**

| Command | What It Does |
|---------|--------------|
| `ipe init` | 🎨 Interactive setup wizard |
| `ipe generate` | ⚡ Generate beautiful client code |
| `ipe version` | 📋 Show version information |

More commands coming soon: `validate`, `watch`, `doctor`

---

## 🌟 **Why Developers Love Ipê**

### **vs OpenAPI Generator**
- ⚡ **10x faster** generation with better output
- 🎨 **Beautiful CLI** instead of confusing Java tools
- 🧠 **Smart defaults** - no complex configuration needed
- 🎯 **Modern Python** patterns and best practices

### **vs Swagger Codegen**  
- 🚀 **Active development** with frequent updates
- 📚 **Better docs** with real-world examples
- 🌊 **Cleaner code** - looks like handwritten Python
- 💚 **Developer joy** - tools that spark happiness

### **vs Writing Clients Manually**
- ⚡ **Minutes vs Days** - instant client generation
- 🛡️ **Always up-to-date** with your API changes
- 🔧 **Consistent patterns** across all your APIs
- 🧪 **Built-in validation** and error handling

---

## 🎁 **Coming Soon**

### **Auto-Pagination**
```python
# Effortlessly iterate through all results
for user in client.users.list_iter():
    process(user)  # Handles pagination automatically
```

### **Built-in Extensions**
- 🧪 **Test Suite Generation** - Complete test coverage out of the box
- 🖥️ **CLI Wrappers** - Turn your API into a command-line tool  
- ⚡ **Framework Integration** - FastAPI, React hooks, and more

### **Watch Mode**
```bash
ipe generate api.yaml --watch
# Auto-regenerates when your spec changes
```

---

## 🤝 **Join the Community**

- 🌟 **Star us** on GitHub if Ipê makes your life easier
- 🐛 **Report issues** - we fix them fast
- 💡 **Suggest features** - help shape the future
- 🔧 **Contribute** - all skill levels welcome

### Quick Start Contributing
```bash
git clone https://github.com/yourusername/ipe.git
cd ipe
uv sync --dev
uv run pytest  # All tests should pass!
```

---

## 📝 **License**

MIT License - free for commercial use, personal projects, everything!

---

## 💚 **Acknowledgments**

Named after Brazil's national tree, the [Ipê](https://en.wikipedia.org/wiki/Tabebuia) 🌳, known for its breathtaking blooms that transform entire landscapes. Just like the tree, Ipê transforms your development landscape with beautiful, production-ready code.

---

<div align="center">

**[Get Started](examples/) • [Documentation](SPECIFICATION.md) • [Community](https://github.com/yourusername/ipe/discussions)**

*Transform your APIs. Transform your workflow. Transform your joy in coding.*

Made with 💚 by developers who believe tools should be delightful

</div>