# Models API Reference

API documentation for the model system.

---

## airtable_model

Decorator to configure a Pydantic model for Airtable integration.

```python
def airtable_model(
    *,
    table_name: Optional[str] = None,
    config: Optional[AirtableConfig] = None,
    access_token: Optional[str] = None,
    base_id: Optional[str] = None
) -> Callable[[Type[BaseModel]], Type[AirtableModel]]
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `table_name` | `str` | Airtable table name. Uses class name if not provided. |
| `config` | `AirtableConfig` | Configuration object. Creates from other params if not provided. |
| `access_token` | `str` | Airtable Personal Access Token. |
| `base_id` | `str` | Airtable Base ID. |

### Returns

A decorator that transforms a `BaseModel` into an `AirtableModel`.

### Example

```python
from pydantic_airtable import airtable_model
from pydantic import BaseModel

# Basic usage
@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str

# With explicit credentials
@airtable_model(
    table_name="Tasks",
    access_token="pat_xxx",
    base_id="appXXX"
)
class Task(BaseModel):
    title: str

# With config object
config = AirtableConfig(access_token="pat_xxx", base_id="appXXX")

@airtable_model(config=config, table_name="Projects")
class Project(BaseModel):
    name: str
```

---

## AirtableModel

Base class providing Airtable operations. Added automatically by the `@airtable_model` decorator.

### Automatic Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `Optional[str]` | Airtable record ID (e.g., `recXXXXXXXXXXXXXX`) |
| `created_time` | `Optional[datetime]` | Record creation timestamp |

### Class Methods

#### create

Create a new record in Airtable.

```python
@classmethod
def create(cls, **data) -> 'AirtableModel'
```

**Parameters:**
- `**data`: Field values for the new record

**Returns:** Created model instance with `id` populated

**Example:**
```python
user = User.create(name="Alice", email="alice@example.com")
print(user.id)  # recXXXXXXXXXXXXXX
```

---

#### get

Retrieve a record by ID.

```python
@classmethod
def get(cls, record_id: str) -> 'AirtableModel'
```

**Parameters:**
- `record_id`: Airtable record ID

**Returns:** Model instance

**Raises:** `RecordNotFoundError` if record doesn't exist

**Example:**
```python
user = User.get("recXXXXXXXXXXXXXX")
```

---

#### all

Get all records from the table.

```python
@classmethod
def all(cls, **filters) -> List['AirtableModel']
```

**Parameters:**
- `**filters`: Query parameters passed to Airtable API
  - `filterByFormula`: Airtable formula string
  - `maxRecords`: Maximum records to return
  - `sort`: Sort configuration
  - `fields`: Fields to return

**Returns:** List of model instances

**Example:**
```python
# All records
users = User.all()

# With formula filter
active = User.all(filterByFormula="{is_active}")

# With sorting
sorted_users = User.all(
    sort=[{"field": "name", "direction": "asc"}]
)

# Limited results
top_10 = User.all(maxRecords=10)
```

---

#### find_by

Find records by field values.

```python
@classmethod
def find_by(cls, **filters) -> List['AirtableModel']
```

**Parameters:**
- `**filters`: Field name to value mappings

**Returns:** List of matching model instances

**Example:**
```python
# Single field
active_users = User.find_by(is_active=True)

# Multiple fields (AND)
admins = User.find_by(is_active=True, role="admin")
```

---

#### first

Get the first record matching filters.

```python
@classmethod
def first(cls, **filters) -> Optional['AirtableModel']
```

**Parameters:**
- `**filters`: Field name to value mappings

**Returns:** First matching model instance or `None`

**Example:**
```python
user = User.first(email="alice@example.com")
if user:
    print(user.name)
```

---

#### bulk_create

Create multiple records.

```python
@classmethod
def bulk_create(cls, data_list: List[Dict[str, Any]]) -> List['AirtableModel']
```

**Parameters:**
- `data_list`: List of field value dictionaries

**Returns:** List of created model instances

**Example:**
```python
users = User.bulk_create([
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
])
```

---

#### create_table

Create Airtable table from model definition.

```python
@classmethod
def create_table(cls, table_name: Optional[str] = None) -> Dict[str, Any]
```

**Parameters:**
- `table_name`: Override table name (uses model's table name if not provided)

**Returns:** Created table information including `id` and `fields`

**Example:**
```python
result = User.create_table()
print(f"Created: {result['id']}")
```

---

#### sync_table

Synchronize table schema with model.

```python
@classmethod
def sync_table(
    cls,
    table_name: Optional[str] = None,
    create_missing_fields: bool = True,
    update_field_types: bool = False
) -> Dict[str, Any]
```

**Parameters:**
- `table_name`: Override table name
- `create_missing_fields`: Add fields that exist in model but not table
- `update_field_types`: Update existing field types (use with caution)

**Returns:** Sync results with `fields_created`, `fields_updated`, `fields_skipped`

**Example:**
```python
result = User.sync_table(create_missing_fields=True)
print(f"Added: {result['fields_created']}")
```

---

### Instance Methods

#### save

Save changes to the record.

```python
def save(self) -> 'AirtableModel'
```

**Returns:** Updated model instance

**Raises:** `ValueError` if record has no ID

**Example:**
```python
user.name = "Alice Smith"
user.save()
```

---

#### delete

Delete the record.

```python
def delete(self) -> Dict[str, Any]
```

**Returns:** Deletion response

**Raises:** `ValueError` if record has no ID

**Example:**
```python
user.delete()
```

---

## Model Configuration

### Pydantic Config

Standard Pydantic configuration is supported:

```python
from pydantic import ConfigDict

@airtable_model(table_name="Users")
class User(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    name: str
    email: str
```

### Default Configuration

The `AirtableModel` base class sets these defaults:

```python
model_config = ConfigDict(
    extra='ignore',           # Ignore unknown fields from Airtable
    validate_assignment=True, # Validate on assignment
    use_enum_values=True      # Use enum values, not names
)
```

!!! note "Why `extra='ignore'`?"
    Airtable can have fields that aren't defined in your model, such as:
    
    - Auto-generated inverse LINKED_RECORD fields
    - Formula fields
    - Rollup/Lookup fields
    - Fields added by other users
    
    Using `extra='ignore'` allows these fields to exist in Airtable without
    causing validation errors in your Python code.

---

## Type Hints

```python
from pydantic_airtable import AirtableModel
from typing import List, Optional

# Type hints for return values
def get_user(id: str) -> User:
    return User.get(id)

def get_all_users() -> List[User]:
    return User.all()

def find_user(email: str) -> Optional[User]:
    return User.first(email=email)
```
