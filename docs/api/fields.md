# Fields API Reference

API documentation for field types and utilities.

---

## AirTableFieldType

Enum of available AirTable field types.

```python
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

### Field Type Categories

#### Text Fields
- `SINGLE_LINE_TEXT` - Single line text
- `LONG_TEXT` - Multi-line text (rich text supported)
- `EMAIL` - Email with validation
- `URL` - URL with validation
- `PHONE` - Phone number

#### Number Fields
- `NUMBER` - Generic number
- `CURRENCY` - Currency with symbol
- `PERCENT` - Percentage value

#### Date/Time Fields
- `DATE` - Date only
- `DATETIME` - Date and time

#### Selection Fields
- `SELECT` - Single select dropdown
- `MULTI_SELECT` - Multiple select
- `CHECKBOX` - Boolean checkbox

#### System Fields
- `CREATED_TIME` - Record creation time
- `MODIFIED_TIME` - Last modification time
- `CREATED_BY` - Creator user
- `MODIFIED_BY` - Last modifier user
- `AUTO_NUMBER` - Auto-incrementing number

#### Computed Fields
- `FORMULA` - Computed formula
- `ROLLUP` - Rollup from linked records
- `LOOKUP` - Lookup from linked records
- `COUNT` - Count of linked records

#### Other Fields
- `ATTACHMENT` - File attachments

---

## airtable_field

Function to create a Pydantic field with AirTable metadata.

```python
def airtable_field(
    *,
    field_type: Optional[AirTableFieldType] = None,
    field_name: Optional[str] = None,
    read_only: bool = False,
    choices: Optional[list] = None,
    **field_kwargs
) -> Any
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `field_type` | `AirTableFieldType` | `None` | Explicit AirTable field type |
| `field_name` | `str` | `None` | Custom name in AirTable |
| `read_only` | `bool` | `False` | Exclude from create/update |
| `choices` | `list` | `None` | Options for SELECT fields |
| `**field_kwargs` | - | - | Pydantic Field() arguments |

### Returns

Pydantic `Field` with AirTable metadata in `json_schema_extra`.

### Examples

#### Override Type

```python
from pydantic_airtable import airtable_field, AirTableFieldType

@airtable_model(table_name="Products")
class Product(BaseModel):
    # Override auto-detection
    code: str = airtable_field(
        field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
```

#### Custom Field Name

```python
@airtable_model(table_name="Users")
class User(BaseModel):
    # Python: user_name → AirTable: "Full Name"
    user_name: str = airtable_field(
        field_name="Full Name"
    )
```

#### Select with Choices

```python
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    status: str = airtable_field(
        field_type=AirTableFieldType.SELECT,
        choices=["To Do", "In Progress", "Done"]
    )
```

#### Read-Only Field

```python
@airtable_model(table_name="Records")
class Record(BaseModel):
    # Won't be sent to AirTable on create/update
    auto_number: int = airtable_field(
        read_only=True,
        default=0
    )
```

#### With Pydantic Validation

```python
@airtable_model(table_name="Users")
class User(BaseModel):
    name: str = airtable_field(
        min_length=1,
        max_length=100,
        description="User's full name"
    )
    
    age: int = airtable_field(
        ge=0,
        le=150,
        default=None
    )
```

#### Combined Options

```python
@airtable_model(table_name="Products")
class Product(BaseModel):
    # Custom name, type, and validation
    price_usd: float = airtable_field(
        field_name="Price (USD)",
        field_type=AirTableFieldType.CURRENCY,
        ge=0,
        description="Product price in USD"
    )
```

---

## FieldTypeResolver

Internal class for smart field type detection.

```python
class FieldTypeResolver:
    @classmethod
    def resolve_field_type(
        cls,
        field_name: str,
        python_type: Type,
        field_info: Optional[FieldInfo] = None,
        explicit_type: Optional[AirTableFieldType] = None
    ) -> AirTableFieldType
```

### Detection Priority

1. Explicit type specification
2. Field info metadata
3. Smart detection from field name
4. Python type mapping
5. Default fallback (`SINGLE_LINE_TEXT`)

### Field Name Patterns

| Pattern | Detected Type |
|---------|---------------|
| `email`, `mail`, `contact` | EMAIL |
| `url`, `link`, `website`, `site`, `href` | URL |
| `phone`, `tel`, `mobile`, `cell` | PHONE |
| `description`, `comment`, `note`, `bio`, `summary`, `content`, `body`, `message`, `detail` | LONG_TEXT |
| `price`, `cost`, `amount`, `fee`, `salary`, `wage`, `revenue`, `budget`, `payment` | CURRENCY |
| `percent`, `percentage`, `rate`, `ratio` | PERCENT |

### Python Type Mapping

| Python Type | AirTable Type |
|-------------|---------------|
| `str` | SINGLE_LINE_TEXT |
| `int` | NUMBER |
| `float` | NUMBER |
| `bool` | CHECKBOX |
| `datetime` | DATETIME |
| `date` | DATE |
| `Enum` | SELECT |
| `List[str]` | MULTI_SELECT |

---

## AirTableField (Legacy)

Alternative function for field creation. Use `airtable_field` instead.

```python
def AirTableField(
    airtable_field_name: Optional[str] = None,
    airtable_field_type: Optional[AirTableFieldType] = None,
    read_only: bool = False,
    **kwargs
) -> Any
```

---

## Field Options

Different field types support different options when creating tables:

### Checkbox

```python
{
    "icon": "check",        # Icon style
    "color": "greenBright"  # Color
}
```

### Currency

```python
{
    "precision": 2,  # Decimal places
    "symbol": "$"    # Currency symbol
}
```

### Percent

```python
{
    "precision": 1  # Decimal places
}
```

### Number

```python
{
    "precision": 0  # Decimal places (0 for integer)
}
```

### Select / Multi-Select

```python
{
    "choices": [
        {"name": "Option 1"},
        {"name": "Option 2"}
    ]
}
```

### DateTime

```python
{
    "dateFormat": {"name": "iso"},
    "timeFormat": {"name": "24hour"},
    "timeZone": "utc"
}
```

---

## Usage Examples

### Complete Model

```python
from pydantic_airtable import (
    airtable_model,
    airtable_field,
    AirTableFieldType
)
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Status(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

@airtable_model(table_name="Contacts")
class Contact(BaseModel):
    # Auto-detected
    name: str
    email: str                       # → EMAIL
    phone: Optional[str] = None      # → PHONE
    website: Optional[str] = None    # → URL
    bio: Optional[str] = None        # → LONG_TEXT
    
    # Type-mapped
    age: Optional[int] = None        # → NUMBER
    is_verified: bool = False        # → CHECKBOX
    joined_at: datetime              # → DATETIME
    status: Status = Status.ACTIVE   # → SELECT
    
    # Explicit configuration
    tags: List[str] = airtable_field(
        field_type=AirTableFieldType.MULTI_SELECT,
        choices=["VIP", "Partner", "Lead"],
        default=[]
    )
    
    # Custom name
    annual_value: float = airtable_field(
        field_name="Annual Value ($)",
        field_type=AirTableFieldType.CURRENCY
    )
    
    # Read-only
    record_number: int = airtable_field(
        read_only=True,
        default=0
    )
```
