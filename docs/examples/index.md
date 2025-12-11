# Examples Overview

Explore practical examples demonstrating Pydantic AirTable capabilities.

---

## Available Examples

| Example | Difficulty | Description |
|---------|------------|-------------|
| [Simple Usage](simple-usage.md) | Beginner | Basic CRUD operations and smart field detection |
| [Table Management](table-management.md) | Intermediate | Schema creation and synchronization |
| [Agentic Researcher](agentic-researcher.md) | Advanced | AI-powered research assistant with OpenAI |

---

## Quick Links

### Getting Started

Start with the [Simple Usage](simple-usage.md) example to learn:

- How to define models with the `@airtable_model` decorator
- Smart field type detection
- Basic CRUD operations
- Environment-based configuration

### Schema Management

The [Table Management](table-management.md) example covers:

- Creating tables from Pydantic models
- Field type customization
- Schema synchronization
- Handling model evolution

### AI Integration

The [Agentic Researcher](agentic-researcher.md) shows:

- Complex multi-model applications
- OpenAI GPT-4 integration
- Real-time web search
- Structured research workflows

---

## Running Examples

### Prerequisites

All examples require:

1. **Python 3.8+**
2. **AirTable credentials**:
    - Personal Access Token (PAT)
    - Base ID

### Setup

1. Clone the repository:
```bash
git clone https://github.com/pydantic-airtable/pydantic-airtable.git
cd pydantic-airtable
```

2. Install dependencies:
```bash
pip install -e .
```

3. Create `.env` file:
```env
AIRTABLE_ACCESS_TOKEN=pat_your_token
AIRTABLE_BASE_ID=appYourBaseId
```

### Run

```bash
cd examples/simple_usage
python simple_usage.py
```

---

## Example Code Snippets

### Basic Model

```python
from pydantic_airtable import airtable_model, configure_from_env
from pydantic import BaseModel

configure_from_env()

@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    completed: bool = False

# Create
task = Task.create(title="Learn Pydantic AirTable")

# Read
tasks = Task.all()

# Update
task.completed = True
task.save()

# Delete
task.delete()
```

### With Smart Detection

```python
@airtable_model(table_name="Contacts")
class Contact(BaseModel):
    name: str           # → SINGLE_LINE_TEXT
    email: str          # → EMAIL (detected)
    phone: str          # → PHONE (detected)
    website: str        # → URL (detected)
    bio: str            # → LONG_TEXT (detected)
```

### With Custom Fields

```python
from pydantic_airtable import airtable_field, AirTableFieldType

@airtable_model(table_name="Products")
class Product(BaseModel):
    name: str
    
    status: str = airtable_field(
        field_type=AirTableFieldType.SELECT,
        choices=["Draft", "Active", "Discontinued"]
    )
    
    price: float = airtable_field(
        field_name="Price (USD)",
        field_type=AirTableFieldType.CURRENCY
    )
```

---

## Learning Path

**Recommended order:**

1. **[Simple Usage](simple-usage.md)** - Foundation concepts
2. **[Table Management](table-management.md)** - Schema management
3. **[Agentic Researcher](agentic-researcher.md)** - Real-world application

Each example builds on concepts from previous ones.

---

## Next Steps

After exploring examples:

- Read the [User Guide](../guide/models.md) for detailed documentation
- Check [Advanced Topics](../advanced/custom-fields.md) for complex scenarios
- Review [API Reference](../api/index.md) for complete API documentation
