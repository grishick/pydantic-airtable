# Field Types

Complete guide to AirTable field types and smart detection.

---

## Smart Detection Overview

Pydantic AirTable automatically detects the appropriate AirTable field type based on:

1. **Field name patterns** - Keywords in the field name
2. **Python type** - The type annotation
3. **Explicit override** - Using `airtable_field()`

---

## Detection Priority

When determining field type, the library checks in this order:

1. **Explicit type** - `airtable_field(field_type=...)` always wins
2. **Field metadata** - Existing type in field's `json_schema_extra`
3. **Field name patterns** - Smart detection from naming
4. **Python type** - Default mapping from type annotation

---

## Field Name Patterns

### Email Fields

Field names matching these patterns become **EMAIL** fields:

- `email`
- `e_mail`
- `mail`
- `contact`

```python
class User(BaseModel):
    email: str              # → EMAIL
    contact_email: str      # → EMAIL
    user_mail: str          # → EMAIL
```

### URL Fields

Field names matching these patterns become **URL** fields:

- `url`
- `link`
- `website`
- `site`
- `href`

```python
class Company(BaseModel):
    website: str            # → URL
    linkedin_url: str       # → URL
    portfolio_link: str     # → URL
```

### Phone Fields

Field names matching these patterns become **PHONE** fields:

- `phone`
- `tel`
- `mobile`
- `cell`

```python
class Contact(BaseModel):
    phone: str              # → PHONE
    mobile_number: str      # → PHONE
    work_tel: str           # → PHONE
```

### Long Text Fields

Field names matching these patterns become **LONG_TEXT** (multiline) fields:

- `description`
- `comment`
- `note`
- `bio`
- `summary`
- `content`
- `body`
- `message`
- `detail`

```python
class Article(BaseModel):
    description: str        # → LONG_TEXT
    content: str            # → LONG_TEXT
    author_bio: str         # → LONG_TEXT
    notes: str              # → LONG_TEXT
```

### Currency Fields

Number fields with these name patterns become **CURRENCY** fields:

- `price`
- `cost`
- `amount`
- `fee`
- `salary`
- `wage`
- `revenue`
- `budget`
- `payment`

```python
class Product(BaseModel):
    price: float            # → CURRENCY
    shipping_cost: float    # → CURRENCY
    total_amount: float     # → CURRENCY
```

### Percentage Fields

Number fields with these name patterns become **PERCENT** fields:

- `percent`
- `percentage`
- `rate`
- `ratio`

```python
class Metrics(BaseModel):
    completion_rate: float  # → PERCENT
    success_percentage: float  # → PERCENT
    conversion_ratio: float # → PERCENT
```

---

## Python Type Mappings

### Basic Types

| Python Type | AirTable Type |
|-------------|---------------|
| `str` | SINGLE_LINE_TEXT |
| `int` | NUMBER |
| `float` | NUMBER |
| `bool` | CHECKBOX |

### Date/Time Types

| Python Type | AirTable Type |
|-------------|---------------|
| `datetime` | DATETIME |
| `date` | DATE |

### Complex Types

| Python Type | AirTable Type |
|-------------|---------------|
| `Enum` | SELECT |
| `List[str]` | MULTI_SELECT |

---

## All AirTable Field Types

The library supports these AirTable field types:

```python
from pydantic_airtable import AirTableFieldType

class AirTableFieldType(str, Enum):
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
    ATTACHMENT = "multipleAttachments"
    FORMULA = "formula"
    ROLLUP = "rollup"
    COUNT = "count"
    LOOKUP = "lookup"
    CREATED_TIME = "createdTime"
    MODIFIED_TIME = "lastModifiedTime"
    CREATED_BY = "createdBy"
    MODIFIED_BY = "lastModifiedBy"
    AUTO_NUMBER = "autoNumber"
```

---

## Overriding Detection

Use `airtable_field()` to override automatic detection:

### Explicit Field Type

```python
from pydantic_airtable import airtable_field, AirTableFieldType

@airtable_model(table_name="Products")
class Product(BaseModel):
    name: str
    
    # Override: 'code' would normally be SINGLE_LINE_TEXT
    code: str = airtable_field(
        field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    # Override: 'notes' detected as LONG_TEXT, but we want single line
    notes: str = airtable_field(
        field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
```

### Custom Field Name

Map Python field name to different AirTable field name:

```python
@airtable_model(table_name="Users")
class User(BaseModel):
    # Python: 'full_name' → AirTable: 'Full Name'
    full_name: str = airtable_field(
        field_name="Full Name"
    )
    
    # Python: 'desc' → AirTable: 'Description'
    desc: str = airtable_field(
        field_name="Description",
        field_type=AirTableFieldType.LONG_TEXT
    )
```

### Select Field with Choices

```python
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    
    status: str = airtable_field(
        field_type=AirTableFieldType.SELECT,
        choices=["To Do", "In Progress", "Review", "Done"]
    )
    
    tags: List[str] = airtable_field(
        field_type=AirTableFieldType.MULTI_SELECT,
        choices=["Frontend", "Backend", "Database", "DevOps"]
    )
```

### Read-Only Fields

Mark computed or system fields as read-only:

```python
@airtable_model(table_name="Records")
class Record(BaseModel):
    name: str
    
    # Won't be sent during create/update
    record_number: int = airtable_field(
        read_only=True
    )
    
    # Computed field
    formula_result: str = airtable_field(
        field_type=AirTableFieldType.FORMULA,
        read_only=True
    )
```

---

## Field Options

Different field types support different options:

### Checkbox Options

```python
# Default: green checkmark
is_active: bool  # icon="check", color="greenBright"
```

### Currency Options

```python
price: float = airtable_field(
    field_type=AirTableFieldType.CURRENCY,
    json_schema_extra={
        "precision": 2,      # Decimal places
        "symbol": "€"        # Currency symbol
    }
)
```

### Percent Options

```python
rate: float = airtable_field(
    field_type=AirTableFieldType.PERCENT,
    json_schema_extra={
        "precision": 1       # Decimal places
    }
)
```

### Number Options

```python
count: int = airtable_field(
    field_type=AirTableFieldType.NUMBER,
    json_schema_extra={
        "precision": 0       # Integer (no decimals)
    }
)
```

---

## Working with Enums

### Basic Enum

```python
from enum import Enum

class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    priority: Priority = Priority.MEDIUM
```

### Enum with Values

AirTable displays the enum **value**, not the name:

```python
class Status(str, Enum):
    DRAFT = "📝 Draft"
    REVIEW = "👀 Under Review"
    APPROVED = "✅ Approved"
    REJECTED = "❌ Rejected"

# In AirTable, you'll see: "📝 Draft", "👀 Under Review", etc.
```

### Optional Enum

```python
class Category(str, Enum):
    TECH = "Technology"
    BUSINESS = "Business"
    PERSONAL = "Personal"

@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    category: Optional[Category] = None  # Can be unset
```

---

## Detection Examples

Here's a comprehensive example showing various detections:

```python
from pydantic_airtable import airtable_model, airtable_field, AirTableFieldType
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

@airtable_model(table_name="Contacts")
class Contact(BaseModel):
    # Auto-detected types
    name: str                      # → SINGLE_LINE_TEXT
    email: str                     # → EMAIL
    phone: str                     # → PHONE
    website: Optional[str] = None  # → URL
    bio: Optional[str] = None      # → LONG_TEXT
    age: Optional[int] = None      # → NUMBER
    salary: Optional[float] = None # → CURRENCY
    is_active: bool = True         # → CHECKBOX
    created_at: datetime           # → DATETIME
    priority: Priority             # → SELECT
    
    # Explicit overrides
    internal_code: str = airtable_field(
        field_name="Internal Code",
        field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    tags: List[str] = airtable_field(
        field_type=AirTableFieldType.MULTI_SELECT,
        choices=["VIP", "Partner", "Lead", "Customer"]
    )
```

---

## Troubleshooting

### Field Type Not Detected

If a field isn't detected as expected:

```python
# Problem: 'status' isn't detected as SELECT
status: str  # → SINGLE_LINE_TEXT

# Solution: Use explicit type
status: str = airtable_field(
    field_type=AirTableFieldType.SELECT,
    choices=["Active", "Inactive"]
)
```

### Wrong Type Detected

```python
# Problem: 'rate' detected as PERCENT but you want NUMBER
rate: float  # → PERCENT (because of 'rate' in name)

# Solution: Override
rate: float = airtable_field(
    field_type=AirTableFieldType.NUMBER
)
```

### Field Name Conflict

```python
# Problem: Python name differs from AirTable name
# AirTable has "First Name" but Python can't use spaces

first_name: str = airtable_field(
    field_name="First Name"
)
```

---

## Next Steps

- [CRUD Operations](crud-operations.md) - Use your models
- [Custom Fields](../advanced/custom-fields.md) - Advanced customization
- [Table Management](table-management.md) - Create and sync tables

