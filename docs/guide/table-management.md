# Table Management

Learn how to create and manage Airtable tables from your Pydantic models.

---

## Overview

Pydantic Airtable can automatically create and manage Airtable tables based on your model definitions. This enables an "infrastructure as code" approach where your Python models define your database schema.

---

## Creating Tables

### Basic Table Creation

Create a table from your model definition:

```python
from pydantic_airtable import airtable_model, configure_from_env
from pydantic import BaseModel

configure_from_env()

@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

# Create the table in Airtable
result = User.create_table()
print(f"Created table: {result['id']}")
```

### Custom Table Name

```python
# Create with different name
result = User.create_table(table_name="Customers")
print(f"Created: {result['name']}")
```

### Table Creation Response

The `create_table()` method returns table information:

```python
result = User.create_table()
# {
#     'id': 'tblXXXXXXXXXXXXXX',
#     'name': 'Users',
#     'fields': [
#         {'id': 'fldXXX', 'name': 'name', 'type': 'singleLineText'},
#         {'id': 'fldYYY', 'name': 'email', 'type': 'email'},
#         {'id': 'fldZZZ', 'name': 'age', 'type': 'number'}
#     ]
# }
```

---

## Automatic Field Mapping

When creating tables, Python types are mapped to Airtable field types:

```python
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

@airtable_model(table_name="Tasks")
class Task(BaseModel):
    # Basic types
    title: str                      # → singleLineText
    description: str                # → multilineText (detected from name)
    count: int                      # → number
    price: float                    # → currency (detected from name)
    is_complete: bool               # → checkbox
    
    # Date/time types
    due_date: Optional[datetime]    # → dateTime
    
    # Enum types
    priority: Priority              # → singleSelect with choices
    
    # List types
    tags: List[str]                 # → multipleSelects

# Creates table with all proper field types
Task.create_table()
```

---

## Schema Synchronization

### Sync Model to Existing Table

Update an existing table to match your model:

```python
sync_result = User.sync_table(
    create_missing_fields=True,
    update_field_types=False
)

print(f"Fields created: {sync_result['fields_created']}")
print(f"Fields updated: {sync_result['fields_updated']}")
print(f"Fields skipped: {sync_result['fields_skipped']}")
```

### Sync Options

| Option | Default | Description |
|--------|---------|-------------|
| `create_missing_fields` | `True` | Add fields that exist in model but not in table |
| `update_field_types` | `False` | Update field types (use with caution) |

### Safe Sync Pattern

```python
# Check what would change before syncing
sync_result = User.sync_table(
    create_missing_fields=False  # Don't make changes
)

if sync_result['fields_created']:
    print(f"Would create: {sync_result['fields_created']}")
    
    # Now actually sync
    User.sync_table(create_missing_fields=True)
```

---

## Schema Evolution

### Adding New Fields

When you add fields to your model, sync to add them to the table:

```python
# Original model
@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str

# Create table
User.create_table()

# Later, add new fields
@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None     # New field
    is_verified: bool = False       # New field

# Sync to add new fields
result = User.sync_table(create_missing_fields=True)
print(f"Added: {result['fields_created']}")
# Added: ['phone', 'is_verified']
```

### Handling Field Changes

!!! warning "Field Type Changes"
    Changing field types in Airtable can cause data loss. The library doesn't automatically change types unless explicitly requested.

```python
# Dangerous: changing field types
result = User.sync_table(
    update_field_types=True  # This could cause data loss
)
```

---

## Using AirtableManager

For more control, use the `AirtableManager` directly:

```python
from pydantic_airtable import AirtableManager, AirtableConfig

config = AirtableConfig(
    access_token="pat_xxx",
    base_id="appXXX"
)

manager = AirtableManager(config)
```

### Create Table with Custom Fields

```python
fields = [
    {
        "name": "Name",
        "type": "singleLineText"
    },
    {
        "name": "Status",
        "type": "singleSelect",
        "options": {
            "choices": [
                {"name": "Active"},
                {"name": "Inactive"}
            ]
        }
    },
    {
        "name": "Score",
        "type": "number",
        "options": {
            "precision": 2
        }
    }
]

result = manager.create_table("CustomTable", fields)
```

### Get Table Schema

```python
schema = manager.get_table_schema("Users")

for field in schema['fields']:
    print(f"{field['name']}: {field['type']}")
```

### Get Base Schema

```python
base_schema = manager.get_base_schema()

for table in base_schema['tables']:
    print(f"Table: {table['name']}")
    for field in table['fields']:
        print(f"  - {field['name']}: {field['type']}")
```

---

## Base Management

### List Bases

```python
bases = manager.list_bases()

for base in bases:
    print(f"{base['name']} ({base['id']})")
```

### Create Base with Tables

```python
tables = [
    {
        "name": "Users",
        "fields": [
            {"name": "Name", "type": "singleLineText"},
            {"name": "Email", "type": "email"}
        ]
    },
    {
        "name": "Tasks",
        "fields": [
            {"name": "Title", "type": "singleLineText"},
            {"name": "Status", "type": "singleSelect"}
        ]
    }
]

new_base = manager.create_base("My Project", tables)
print(f"Created base: {new_base['id']}")
```

---

## Field Type Options

### Checkbox Field

```python
{
    "name": "is_active",
    "type": "checkbox",
    "options": {
        "icon": "check",
        "color": "greenBright"
    }
}
```

### Select Field

```python
{
    "name": "status",
    "type": "singleSelect",
    "options": {
        "choices": [
            {"name": "Draft", "color": "blueLight"},
            {"name": "Published", "color": "greenLight"},
            {"name": "Archived", "color": "grayLight"}
        ]
    }
}
```

### Currency Field

```python
{
    "name": "price",
    "type": "currency",
    "options": {
        "precision": 2,
        "symbol": "$"
    }
}
```

### DateTime Field

```python
{
    "name": "created_at",
    "type": "dateTime",
    "options": {
        "dateFormat": {"name": "iso"},
        "timeFormat": {"name": "24hour"},
        "timeZone": "utc"
    }
}
```

---

## Table Check Pattern

Check if table exists before creating:

```python
def ensure_table_exists(model_cls):
    """Create table if it doesn't exist"""
    try:
        # Try to fetch records (table exists)
        model_cls.all(maxRecords=1)
        print(f"Table {model_cls._get_table_name()} exists")
    except Exception:
        # Table doesn't exist, create it
        model_cls.create_table()
        print(f"Created table {model_cls._get_table_name()}")

# Usage
ensure_table_exists(User)
ensure_table_exists(Task)
```

---

## Migration Patterns

### Version-Based Migration

```python
# migrations.py
def migrate_v1_to_v2():
    """Add new fields for v2"""
    
    # New model definition
    @airtable_model(table_name="Users")
    class UserV2(BaseModel):
        name: str
        email: str
        phone: Optional[str] = None  # New in v2
        role: str = "user"           # New in v2
    
    # Sync to add new fields
    result = UserV2.sync_table(create_missing_fields=True)
    print(f"Migration complete: {result}")

# Run migration
migrate_v1_to_v2()
```

### Multi-Environment Tables

```python
import os

def setup_tables(environment: str):
    """Create tables for specific environment"""
    
    suffix = f"_{environment}" if environment != "production" else ""
    
    @airtable_model(table_name=f"Users{suffix}")
    class User(BaseModel):
        name: str
        email: str
    
    User.create_table()
    print(f"Created Users{suffix}")

# Usage
setup_tables("development")  # Creates Users_development
setup_tables("staging")      # Creates Users_staging
setup_tables("production")   # Creates Users
```

---

## API Limitations

Some field types cannot be created through the Airtable API:

!!! warning "AUTO_NUMBER Fields"
    The Airtable public API does not support creating `AUTO_NUMBER` fields. To add an auto-number field:
    
    1. Define a `NUMBER` field in your model
    2. Create the table using `create_table()`
    3. Open the Airtable UI and convert the field to "Auto number"
    
    ```python
    @airtable_model(table_name="Invoices")
    class Invoice(BaseModel):
        # This will be created as NUMBER - convert to Auto number in Airtable UI
        invoice_number: int = airtable_field(
            field_type=AirtableFieldType.NUMBER,
            read_only=True,  # Mark as read-only since it will be auto-generated
            default=0
        )
        customer_name: str
        amount: float
    ```

---

## Best Practices

!!! success "Do"
    - Create tables from models for consistency
    - Use `sync_table()` for schema updates
    - Keep `update_field_types=False` unless necessary
    - Test schema changes in development first
    - Document schema changes

!!! failure "Don't"
    - Manually create tables that models use
    - Change field types without data migration
    - Delete fields without checking for data
    - Skip testing schema changes

---

## Next Steps

- [Filtering & Queries](filtering.md) - Query your tables
- [Multiple Bases](../advanced/multiple-bases.md) - Work with multiple bases
- [Best Practices](../advanced/best-practices.md) - Production patterns

