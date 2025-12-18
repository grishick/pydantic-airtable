# API Reference

Complete API documentation for Pydantic Airtable.

---

## Overview

Pydantic Airtable provides a clean API for integrating Pydantic models with Airtable:

| Module | Description |
|--------|-------------|
| [Models](models.md) | Model decorator and base class |
| [Configuration](config.md) | Configuration classes and functions |
| [Fields](fields.md) | Field types and utilities |
| [Manager](manager.md) | Airtable manager for direct operations |
| [Exceptions](exceptions.md) | Exception classes |

---

## Quick Reference

### Core Imports

```python
from pydantic_airtable import (
    # Model decorator
    airtable_model,
    
    # Configuration
    AirtableConfig,
    configure_from_env,
    set_global_config,
    get_global_config,
    
    # Field utilities
    airtable_field,
    AirtableFieldType,
    
    # Manager
    AirtableManager,
    
    # Exceptions
    AirtableError,
    APIError,
    RecordNotFoundError,
    ConfigurationError,
    ValidationError,
)
```

### Basic Usage

```python
from pydantic_airtable import airtable_model, configure_from_env
from pydantic import BaseModel

configure_from_env()

@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str

# CRUD operations
user = User.create(name="Alice", email="alice@example.com")
users = User.all()
user = User.get("recXXX")
user.save()
user.delete()
```

---

## Module Details

### airtable_model

Decorator to enable Airtable integration:

```python
@airtable_model(
    table_name: str,              # Airtable table name
    config: AirtableConfig = None, # Configuration object
    access_token: str = None,     # Direct token
    base_id: str = None           # Direct base ID
)
```

### AirtableConfig

Configuration dataclass:

```python
config = AirtableConfig(
    access_token: str,    # Personal Access Token
    base_id: str,         # Base ID
    table_name: str = None # Optional default table
)
```

### airtable_field

Field customization function:

```python
field = airtable_field(
    field_type: AirtableFieldType = None,  # Override type
    field_name: str = None,                # Custom Airtable name
    read_only: bool = False,               # Read-only field
    choices: list = None,                  # For SELECT fields
    **pydantic_kwargs                      # Pydantic Field args
)
```

### AirtableFieldType

Enum of available field types:

```python
class AirtableFieldType(str, Enum):
    SINGLE_LINE_TEXT = "singleLineText"
    LONG_TEXT = "multilineText"
    NUMBER = "number"
    CURRENCY = "currency"
    PERCENT = "percent"
    DATE = "date"
    DATETIME = "dateTime"
    CHECKBOX = "checkbox"
    SELECT = "singleSelect"
    MULTI_SELECT = "multipleSelects"
    EMAIL = "email"
    URL = "url"
    PHONE = "phoneNumber"
    # ... more types
```

---

## Model Methods

### Class Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `create(**data)` | Create new record | Model instance |
| `get(id)` | Get record by ID | Model instance |
| `all(**params)` | Get all records | List[Model] |
| `find_by(**filters)` | Find by field values | List[Model] |
| `first(**filters)` | Get first match | Model or None |
| `bulk_create(data_list)` | Create multiple | List[Model] |
| `create_table()` | Create Airtable table | dict |
| `sync_table(**opts)` | Sync schema | dict |

### Instance Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `save()` | Save changes | Model instance |
| `delete()` | Delete record | dict |

### Automatic Fields

Every model includes:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `Optional[str]` | Airtable record ID |
| `created_time` | `Optional[datetime]` | Creation timestamp |

---

## Configuration Functions

| Function | Description |
|----------|-------------|
| `configure_from_env(**overrides)` | Load config from environment |
| `set_global_config(config)` | Set global configuration |
| `get_global_config()` | Get global configuration |

---

## Exceptions

| Exception | When Raised |
|-----------|-------------|
| `AirtableError` | Base exception |
| `ConfigurationError` | Configuration issues |
| `APIError` | Airtable API errors |
| `RecordNotFoundError` | Record doesn't exist |
| `ValidationError` | Pydantic validation fails |

---

## Manager Methods

The `AirtableManager` provides direct API access:

| Method | Description |
|--------|-------------|
| `create_record(fields, table)` | Create record |
| `get_record(id, table)` | Get record |
| `update_record(id, fields, table)` | Update record |
| `delete_record(id, table)` | Delete record |
| `get_records(table, **params)` | List records |
| `create_table(name, fields)` | Create table |
| `get_table_schema(table)` | Get schema |
| `create_table_from_model(cls)` | Create from model |
| `sync_model_to_table(cls, table)` | Sync model schema |

---

## See Also

- [Models Reference](models.md)
- [Configuration Reference](config.md)
- [Fields Reference](fields.md)
- [Manager Reference](manager.md)
- [Exceptions Reference](exceptions.md)
