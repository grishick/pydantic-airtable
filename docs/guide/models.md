# Models

Learn how to define and use Pydantic models with AirTable integration.

---

## Basic Model Definition

The `@airtable_model` decorator transforms any Pydantic `BaseModel` into an AirTable-connected model:

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
    is_active: bool = True
```

---

## Model Decorator Parameters

The `@airtable_model` decorator accepts these parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `table_name` | `str` | AirTable table name (required) |
| `config` | `AirTableConfig` | Configuration object |
| `access_token` | `str` | Direct token specification |
| `base_id` | `str` | Direct base ID specification |

### Examples

```python
# Minimal - uses global config
@airtable_model(table_name="Users")
class User(BaseModel):
    name: str

# With explicit credentials
@airtable_model(
    table_name="Projects",
    access_token="pat_xxx",
    base_id="appXXX"
)
class Project(BaseModel):
    name: str

# With config object
config = AirTableConfig(access_token="pat_xxx", base_id="appXXX")

@airtable_model(config=config, table_name="Tasks")
class Task(BaseModel):
    title: str
```

---

## Automatic Fields

Every model automatically includes these fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `Optional[str]` | AirTable record ID (e.g., `recXXXXXXXXXXXXXX`) |
| `created_time` | `Optional[datetime]` | Record creation timestamp |

```python
@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str

# After creation
user = User.create(name="Alice", email="alice@example.com")
print(user.id)           # recXXXXXXXXXXXXXX
print(user.created_time) # 2024-01-15T10:30:00.000Z
```

---

## Field Types

### Supported Python Types

| Python Type | AirTable Type | Notes |
|-------------|---------------|-------|
| `str` | SINGLE_LINE_TEXT | Default for strings |
| `int` | NUMBER | Integer values |
| `float` | NUMBER | Decimal values |
| `bool` | CHECKBOX | True/False |
| `datetime` | DATETIME | Date and time |
| `date` | DATE | Date only |
| `Enum` | SELECT | Single selection |
| `List[str]` | MULTI_SELECT | Multiple selections |

### Smart Detection

Field names trigger automatic type detection:

```python
@airtable_model(table_name="Contacts")
class Contact(BaseModel):
    name: str           # → SINGLE_LINE_TEXT
    email: str          # → EMAIL (detected!)
    phone: str          # → PHONE (detected!)
    website: str        # → URL (detected!)
    bio: str            # → LONG_TEXT (detected!)
    salary: float       # → CURRENCY (detected!)
    completion: float   # → PERCENT (detected!)
```

See [Field Types](field-types.md) for complete detection rules.

---

## Optional Fields

Use `Optional` for nullable fields:

```python
from typing import Optional

@airtable_model(table_name="Users")
class User(BaseModel):
    name: str                          # Required
    email: str                         # Required
    phone: Optional[str] = None        # Optional
    age: Optional[int] = None          # Optional
    bio: Optional[str] = None          # Optional
```

---

## Default Values

Set default values as you would with Pydantic:

```python
from datetime import datetime

@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    status: str = "pending"
    priority: int = 1
    is_urgent: bool = False
    created_at: datetime = datetime.now()
```

---

## Enum Fields

Use Python enums for SELECT fields:

```python
from enum import Enum

class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class Status(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING
```

When you create the table, enum values become SELECT options automatically.

---

## Complex Models

### Nested Information

For related data, use string fields with JSON or structured text:

```python
import json
from typing import Optional

@airtable_model(table_name="Projects")
class Project(BaseModel):
    name: str
    description: Optional[str] = None
    metadata: Optional[str] = None  # Store JSON as string
    
    def set_metadata(self, data: dict):
        """Store dict as JSON string"""
        self.metadata = json.dumps(data)
    
    def get_metadata(self) -> dict:
        """Parse JSON string to dict"""
        return json.loads(self.metadata) if self.metadata else {}
```

### Multiple Models

Define multiple models for different tables:

```python
@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str
    department_id: Optional[str] = None

@airtable_model(table_name="Departments")
class Department(BaseModel):
    name: str
    manager: Optional[str] = None

@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    assignee_id: Optional[str] = None  # Reference to User
    department_id: Optional[str] = None  # Reference to Department
```

---

## Model Validation

Pydantic validation works normally:

```python
from pydantic import BaseModel, EmailStr, Field, field_validator

@airtable_model(table_name="Users")
class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str
    age: Optional[int] = Field(default=None, ge=0, le=150)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()
```

```python
# Validation happens before AirTable operations
try:
    user = User.create(name="", email="invalid")
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## Model Configuration

### Pydantic Config

Standard Pydantic configuration works:

```python
from pydantic import ConfigDict

@airtable_model(table_name="Users")
class User(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    name: str
    email: str
```

### Extra Fields

By default, extra fields are forbidden:

```python
@airtable_model(table_name="Users")
class User(BaseModel):
    name: str

# This raises an error
user = User.create(name="Alice", unknown_field="value")
# ValidationError: Extra inputs are not permitted
```

---

## Model Methods Summary

### Class Methods

| Method | Description |
|--------|-------------|
| `create(**data)` | Create a new record |
| `get(record_id)` | Get record by ID |
| `all(**filters)` | Get all records |
| `find_by(**filters)` | Find by field values |
| `first(**filters)` | Get first match |
| `bulk_create(data_list)` | Create multiple records |
| `create_table()` | Create AirTable table |
| `sync_table(**options)` | Sync schema to table |

### Instance Methods

| Method | Description |
|--------|-------------|
| `save()` | Save changes to record |
| `delete()` | Delete the record |

See [CRUD Operations](crud-operations.md) for detailed usage.

---

## Best Practices

!!! success "Do"
    - Use descriptive field names for smart detection
    - Define enums for fixed choice fields
    - Use `Optional` for truly optional fields
    - Add Pydantic validators for data integrity

!!! failure "Don't"
    - Use generic names like `field1`, `data`
    - Mix different data types in the same field
    - Store complex nested objects (use separate tables)

---

## Next Steps

- [Field Types](field-types.md) - Complete field type reference
- [CRUD Operations](crud-operations.md) - Create, read, update, delete
- [Custom Fields](../advanced/custom-fields.md) - Override auto-detection

