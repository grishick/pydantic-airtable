# Pydantic AirTable

**The most intuitive way to integrate Pydantic models with AirTable**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-green.svg)](https://pydantic.dev/)
[![AirTable API](https://img.shields.io/badge/airtable-API%20v0-orange.svg)](https://airtable.com/developers/web/api/introduction)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Transform Your AirTable Integration

Turn your Pydantic models into fully-functional AirTable integrations with just **8 lines of code**:

```python
from pydantic_airtable import airtable_model, configure_from_env
from pydantic import BaseModel

configure_from_env()  # Auto-loads from .env

@airtable_model(table_name="Users")
class User(BaseModel):
    name: str                    # Auto-detects as SINGLE_LINE_TEXT
    email: str                   # Auto-detects as EMAIL  
    age: Optional[int] = None    # Auto-detects as NUMBER
    is_active: bool = True       # Auto-detects as CHECKBOX

# That's it! Now you have full CRUD operations
user = User.create(name="Alice", email="alice@example.com", age=28)
users = User.all()
alice = User.find_by(name="Alice")
```

---

## 🌟 Key Features

<div class="grid cards" markdown>

-   :brain: **Smart Detection**

    ---

    Auto-detects field types from naming patterns. `email: str` automatically becomes an EMAIL field.

-   :zap: **Zero Config**

    ---

    Works with just environment variables. Set your token and base ID, and you're ready to go.

-   :hammer_and_wrench: **Table Creation**

    ---

    Creates AirTable tables directly from your model definitions with `User.create_table()`.

-   :rocket: **Intuitive CRUD**

    ---

    Simple, predictable methods: `User.create()`, `User.all()`, `user.save()`, `user.delete()`.

-   :mag: **Advanced Filtering**

    ---

    Clean query syntax with `User.find_by(is_active=True)` and formula support.

-   :package: **Batch Operations**

    ---

    Efficient bulk operations with `User.bulk_create([...])` for multiple records.

</div>

---

## 🚀 Quick Start

### 1. Install the package

```bash
pip install pydantic-airtable
```

### 2. Set up your credentials

Create a `.env` file:

```env
AIRTABLE_ACCESS_TOKEN=pat_your_personal_access_token
AIRTABLE_BASE_ID=app_your_base_id
```

### 3. Define your model

```python
from pydantic_airtable import airtable_model, configure_from_env
from pydantic import BaseModel
from typing import Optional

configure_from_env()

@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
```

### 4. Start using it!

```python
# Create a table (if it doesn't exist)
User.create_table()

# Create a record
user = User.create(name="Alice", email="alice@example.com", age=28)

# Query records
all_users = User.all()
active_users = User.find_by(is_active=True)

# Update a record
user.age = 29
user.save()
```

---

## 📚 Documentation Sections

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started/installation.md) | Installation, setup, and your first model |
| [User Guide](guide/models.md) | Detailed guides for all features |
| [Advanced](advanced/custom-fields.md) | Custom configurations and best practices |
| [Examples](examples/index.md) | Real-world example applications |
| [API Reference](api/index.md) | Complete API documentation |

---

## 🧠 Smart Field Detection

The library automatically detects AirTable field types based on your field names:

| Python Code | Detected Type | Reason |
|-------------|---------------|--------|
| `email: str` | EMAIL | Field name contains "email" |
| `phone: str` | PHONE | Field name contains "phone" |
| `website: str` | URL | Field name contains "website" |
| `description: str` | LONG_TEXT | Field name suggests long text |
| `price: float` | CURRENCY | Field name suggests money |
| `completion_rate: float` | PERCENT | Field name suggests percentage |
| `is_active: bool` | CHECKBOX | Boolean type |
| `created_at: datetime` | DATETIME | DateTime type |
| `Priority: Enum` | SELECT | Enum type |
| `tags: List[str]` | MULTI_SELECT | List type |

---

## 💡 Why Pydantic AirTable?

- **Type Safety**: Full Pydantic validation with AirTable persistence
- **Intuitive API**: Works exactly like you'd expect
- **Smart Defaults**: Minimal configuration required
- **Production Ready**: Error handling, retries, and batch operations
- **Well Documented**: Comprehensive guides and examples

---

## 🔗 Links

- [GitHub Repository](https://github.com/pydantic-airtable/pydantic-airtable)
- [PyPI Package](https://pypi.org/project/pydantic-airtable/)
- [AirTable API Documentation](https://airtable.com/developers/web/api/introduction)
- [Pydantic Documentation](https://pydantic.dev/)

---

**Made with ❤️ for the Python community**
