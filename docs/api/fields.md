# Fields API Reference

API documentation for field types and utilities.

---

## AirtableFieldType

Enum of available Airtable field types.

```python
class AirtableFieldType(str, Enum):
    SINGLE_LINE_TEXT = "singleLineText"
    LONG_TEXT = "multilineText"
    NUMBER = "number"
    CURRENCY = "currency"
    PERCENT = "percent"
    DATE = "date"
    DATETIME = "dateTime"
    DURATION = "duration"
    RATING = "rating"
    CHECKBOX = "checkbox"
    
    # Relational fields
    LINKED_RECORD = "multipleRecordLinks"
    LOOKUP = "lookup"
    ROLLUP = "rollup"
    COUNT = "count"
    
    # Special fields
    BARCODE = "barcode"
    BUTTON = "button"
    USER = "multipleCollaborators"
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
- `DURATION` - Time duration (stored in seconds)
- `RATING` - Star rating (1-5 or 1-10)
- `LINKED_RECORD` - Links to records in another table
- `USER` - Collaborator/user references
- `BUTTON` - Triggers automations (read-only)
- `BARCODE` - Stores barcode text

#### Selection Fields
- `SELECT` - Single select dropdown
- `MULTI_SELECT` - Multiple select
- `CHECKBOX` - Boolean checkbox

#### System Fields
- `CREATED_TIME` - Record creation time
- `MODIFIED_TIME` - Last modification time
- `CREATED_BY` - Creator user
- `MODIFIED_BY` - Last modifier user
- `AUTO_NUMBER` - Auto-incrementing number (**Note**: Cannot be created via API, see below)

!!! warning "AUTO_NUMBER API Limitation"
    The Airtable public API does not support creating `AUTO_NUMBER` fields programmatically. To use auto-number fields:
    
    1. Create a `NUMBER` field via `create_table()` or `sync_table()`
    2. Open your Airtable base in the browser
    3. Click on the field header → "Customize field type"
    4. Select "Auto number" to convert the field
    
    The converted field will then be read-only and auto-increment for each new record.

#### Computed Fields
- `FORMULA` - Computed formula
- `ROLLUP` - Rollup from linked records
- `LOOKUP` - Lookup from linked records
- `COUNT` - Count of linked records

#### Other Fields
- `ATTACHMENT` - File attachments

---

## airtable_field

Function to create a Pydantic field with Airtable metadata.

```python
def airtable_field(
    *,
    field_type: Optional[AirtableFieldType] = None,
    field_name: Optional[str] = None,
    read_only: bool = False,
    choices: Optional[list] = None,
    **field_kwargs
) -> Any
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `field_type` | `AirtableFieldType` | `None` | Explicit Airtable field type |
| `field_name` | `str` | `None` | Custom name in Airtable |
| `read_only` | `bool` | `False` | Exclude from create/update |
| `choices` | `list` | `None` | Options for SELECT fields |
| `**field_kwargs` | - | - | Pydantic Field() arguments |

### Returns

Pydantic `Field` with Airtable metadata in `json_schema_extra`.

### Examples

#### Override Type

```python
from pydantic_airtable import airtable_field, AirtableFieldType

@airtable_model(table_name="Products")
class Product(BaseModel):
    # Override auto-detection
    code: str = airtable_field(
        field_type=AirtableFieldType.SINGLE_LINE_TEXT
    )
```

#### Custom Field Name

```python
@airtable_model(table_name="Users")
class User(BaseModel):
    # Python: user_name → Airtable: "Full Name"
    user_name: str = airtable_field(
        field_name="Full Name"
    )
```

#### Select with Choices

```python
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    status: str = airtable_field(
        field_type=AirtableFieldType.SELECT,
        choices=["To Do", "In Progress", "Done"]
    )
```

#### Read-Only Field

```python
@airtable_model(table_name="Records")
class Record(BaseModel):
    # Won't be sent to Airtable on create/update
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
        field_type=AirtableFieldType.CURRENCY,
        ge=0,
        description="Product price in USD"
    )
```

---

## FieldTypeResolver

Internal class for field type detection.

```python
class FieldTypeResolver:
    @classmethod
    def resolve_field_type(
        cls,
        field_name: str,
        python_type: Type,
        field_info: Optional[FieldInfo] = None,
        explicit_type: Optional[AirtableFieldType] = None
    ) -> AirtableFieldType
```

### Detection Priority

1. Explicit type specification
2. Field info metadata
3. Field type detection from field name
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

| Python Type | Airtable Type |
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

## AirtableField (Legacy)

Alternative function for field creation. Use `airtable_field` instead.

```python
def AirtableField(
    airtable_field_name: Optional[str] = None,
    airtable_field_type: Optional[AirtableFieldType] = None,
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

### Duration

```python
{
    "durationFormat": "h:mm"  # Options: h:mm, h:mm:ss, h:mm:ss.S, h:mm:ss.SS, h:mm:ss.SSS
}
```

### Rating

```python
{
    "max": 5,              # Maximum rating (1-10)
    "icon": "star",        # Options: star, heart, thumbs-up, flag, dot
    "color": "yellowBright"
}
```

### Linked Record

```python
{
    "linked_table_id": "tblXXXXXXX",  # Required: ID of table to link to
    "single_record": False,           # Optional: prefer single record link
    "inverse_link_field_id": "fldXXX" # Optional: inverse link field
}
```

### User

```python
{
    "should_notify": False  # Whether to notify users when assigned
}
```

### Button

```python
{
    "label": "Click"  # Button label text
}
```

### Barcode

No additional options required.

---

## Usage Examples

### Complete Model

```python
from pydantic_airtable import (
    airtable_model,
    airtable_field,
    AirtableFieldType
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
        field_type=AirtableFieldType.MULTI_SELECT,
        choices=["VIP", "Partner", "Lead"],
        default=[]
    )
    
    # Custom name
    annual_value: float = airtable_field(
        field_name="Annual Value ($)",
        field_type=AirtableFieldType.CURRENCY
    )
    
    # Read-only
    record_number: int = airtable_field(
        read_only=True,
        default=0
    )
```
