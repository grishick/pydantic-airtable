# Manager API Reference

API documentation for the AirtableManager class.

---

## AirtableManager

Unified manager for all Airtable operations.

```python
class AirtableManager:
    def __init__(self, config: AirtableConfig)
```

### Constructor

| Parameter | Type | Description |
|-----------|------|-------------|
| `config` | `AirtableConfig` | Airtable configuration |

### Example

```python
from pydantic_airtable import AirtableManager, AirtableConfig

config = AirtableConfig(
    access_token="pat_xxx",
    base_id="appXXX"
)

manager = AirtableManager(config)
```

---

## Record Operations

### get_records

Get records from a table.

```python
def get_records(
    self,
    table_name: Optional[str] = None,
    base_id: Optional[str] = None,
    **params
) -> Dict[str, Any]
```

**Parameters:**
- `table_name`: Table name (uses config default if None)
- `base_id`: Base ID (uses config default if None)
- `**params`: Airtable API parameters
  - `filterByFormula`: Filter formula
  - `maxRecords`: Maximum records
  - `sort`: Sort configuration
  - `fields`: Fields to return
  - `view`: View name

**Returns:** API response with `records` list

**Example:**
```python
response = manager.get_records("Users")
for record in response['records']:
    print(record['fields']['name'])

# With parameters
response = manager.get_records(
    "Tasks",
    filterByFormula="{status} = 'Active'",
    maxRecords=10,
    sort=[{"field": "created_time", "direction": "desc"}]
)
```

---

### create_record

Create a new record.

```python
def create_record(
    self,
    fields: Dict[str, Any],
    table_name: Optional[str] = None,
    base_id: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `fields`: Field values
- `table_name`: Table name
- `base_id`: Base ID

**Returns:** Created record data

**Example:**
```python
record = manager.create_record(
    {"name": "Alice", "email": "alice@example.com"},
    "Users"
)
print(record['id'])
```

---

### get_record

Get a specific record by ID.

```python
def get_record(
    self,
    record_id: str,
    table_name: Optional[str] = None,
    base_id: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `record_id`: Airtable record ID
- `table_name`: Table name
- `base_id`: Base ID

**Returns:** Record data

**Example:**
```python
record = manager.get_record("recXXX", "Users")
print(record['fields'])
```

---

### update_record

Update an existing record.

```python
def update_record(
    self,
    record_id: str,
    fields: Dict[str, Any],
    table_name: Optional[str] = None,
    base_id: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `record_id`: Record ID to update
- `fields`: Field values to update
- `table_name`: Table name
- `base_id`: Base ID

**Returns:** Updated record data

**Example:**
```python
record = manager.update_record(
    "recXXX",
    {"name": "Alice Smith"},
    "Users"
)
```

---

### delete_record

Delete a record.

```python
def delete_record(
    self,
    record_id: str,
    table_name: Optional[str] = None,
    base_id: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `record_id`: Record ID to delete
- `table_name`: Table name
- `base_id`: Base ID

**Returns:** Deletion confirmation

**Example:**
```python
result = manager.delete_record("recXXX", "Users")
```

---

## Table Operations

### create_table

Create a new table.

```python
def create_table(
    self,
    name: str,
    fields: List[Dict[str, Any]],
    base_id: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `name`: Table name
- `fields`: List of field definitions
- `base_id`: Base ID

**Returns:** Created table information

**Example:**
```python
table = manager.create_table("Users", [
    {"name": "Name", "type": "singleLineText"},
    {"name": "Email", "type": "email"},
    {
        "name": "Status",
        "type": "singleSelect",
        "options": {
            "choices": [
                {"name": "Active"},
                {"name": "Inactive"}
            ]
        }
    }
])
print(table['id'])
```

---

### get_table_schema

Get schema for a table.

```python
def get_table_schema(
    self,
    table_name: str,
    base_id: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `table_name`: Table name
- `base_id`: Base ID

**Returns:** Table schema with fields

**Raises:** `APIError` if table not found

**Example:**
```python
schema = manager.get_table_schema("Users")
for field in schema['fields']:
    print(f"{field['name']}: {field['type']}")
```

---

### update_table

Update table properties.

```python
def update_table(
    self,
    table_id: str,
    updates: Dict[str, Any],
    base_id: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `table_id`: Table ID
- `updates`: Update data
- `base_id`: Base ID

**Returns:** Updated table information

---

### delete_table

Delete a table.

```python
def delete_table(
    self,
    table_id: str,
    base_id: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `table_id`: Table ID
- `base_id`: Base ID

**Returns:** Deletion confirmation

---

## Base Operations

### list_bases

List all accessible bases.

```python
def list_bases(self) -> List[Dict[str, Any]]
```

**Returns:** List of base information

**Example:**
```python
bases = manager.list_bases()
for base in bases:
    print(f"{base['name']}: {base['id']}")
```

---

### get_base_schema

Get schema for a base.

```python
def get_base_schema(
    self,
    base_id: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `base_id`: Base ID (uses config default if None)

**Returns:** Base schema with tables

**Example:**
```python
schema = manager.get_base_schema()
for table in schema['tables']:
    print(f"Table: {table['name']}")
```

---

### create_base

Create a new base.

```python
def create_base(
    self,
    name: str,
    tables: List[Dict[str, Any]]
) -> Dict[str, Any]
```

**Parameters:**
- `name`: Base name
- `tables`: List of table definitions

**Returns:** Created base information

**Example:**
```python
base = manager.create_base("My Project", [
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
            {"name": "Title", "type": "singleLineText"}
        ]
    }
])
```

---

### delete_base

Delete a base.

```python
def delete_base(self, base_id: str) -> Dict[str, Any]
```

**Parameters:**
- `base_id`: Base ID to delete

**Returns:** Deletion confirmation

---

## Model Integration

### create_table_from_model

Create a table from a Pydantic model.

```python
def create_table_from_model(
    self,
    model_class: Type,
    table_name: Optional[str] = None,
    base_id: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `model_class`: Pydantic model class
- `table_name`: Override table name
- `base_id`: Base ID

**Returns:** Created table information

**Example:**
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int

table = manager.create_table_from_model(User, "Users")
```

---

### sync_model_to_table

Synchronize model schema to existing table.

```python
def sync_model_to_table(
    self,
    model_class: Type,
    table_name: Optional[str] = None,
    base_id: Optional[str] = None,
    create_missing_fields: bool = True,
    update_field_types: bool = False
) -> Dict[str, Any]
```

**Parameters:**
- `model_class`: Pydantic model class
- `table_name`: Table name
- `base_id`: Base ID
- `create_missing_fields`: Add missing fields
- `update_field_types`: Update field types

**Returns:** Sync results

**Example:**
```python
result = manager.sync_model_to_table(
    User,
    "Users",
    create_missing_fields=True
)
print(f"Created: {result['fields_created']}")
```

---

## Usage Examples

### Full CRUD Example

```python
from pydantic_airtable import AirtableManager, AirtableConfig

config = AirtableConfig(
    access_token="pat_xxx",
    base_id="appXXX"
)
manager = AirtableManager(config)

# Create
record = manager.create_record(
    {"name": "Alice", "email": "alice@example.com"},
    "Users"
)
record_id = record['id']

# Read
record = manager.get_record(record_id, "Users")
print(record['fields'])

# Update
manager.update_record(
    record_id,
    {"name": "Alice Smith"},
    "Users"
)

# Delete
manager.delete_record(record_id, "Users")
```

### Schema Management

```python
# Create table
manager.create_table("Products", [
    {"name": "Name", "type": "singleLineText"},
    {"name": "Price", "type": "currency", "options": {"precision": 2}},
    {"name": "In Stock", "type": "checkbox"}
])

# Get schema
schema = manager.get_table_schema("Products")

# List all tables
base_schema = manager.get_base_schema()
for table in base_schema['tables']:
    print(table['name'])
```
