# Custom Fields

Learn how to override automatic field detection and configure custom field behavior.

---

## Overview

While Pydantic Airtable provides field type detection, you may need to:

- Override detected types
- Use custom field names in Airtable
- Configure field options
- Mark fields as read-only

---

## The airtable_field Function

Use `airtable_field()` to customize field behavior:

```python
from pydantic_airtable import airtable_field, AirtableFieldType

field_name: str = airtable_field(
    field_type=AirtableFieldType.LONG_TEXT,  # Override type
    field_name="Field Name in Airtable",      # Custom Airtable name
    read_only=False,                          # Whether field is read-only
    choices=["Option 1", "Option 2"],         # For SELECT/MULTI_SELECT
    default=None,                             # Default value (Pydantic)
    description="Field description"           # Pydantic field description
)
```

---

## Override Field Type

### Basic Override

```python
from pydantic_airtable import airtable_model, airtable_field, AirtableFieldType
from pydantic import BaseModel

@airtable_model(table_name="Products")
class Product(BaseModel):
    name: str
    
    # 'notes' would be detected as LONG_TEXT, but we want single line
    notes: str = airtable_field(
        field_type=AirtableFieldType.SINGLE_LINE_TEXT
    )
    
    # 'data' is generic, explicitly set to LONG_TEXT
    data: str = airtable_field(
        field_type=AirtableFieldType.LONG_TEXT
    )
```

### All Available Types

```python
from pydantic_airtable import AirtableFieldType

# Text types
AirtableFieldType.SINGLE_LINE_TEXT  # Single line text
AirtableFieldType.LONG_TEXT         # Multi-line text
AirtableFieldType.EMAIL             # Email with validation
AirtableFieldType.URL               # URL with validation
AirtableFieldType.PHONE             # Phone number

# Number types
AirtableFieldType.NUMBER            # Generic number
AirtableFieldType.CURRENCY          # Currency with symbol
AirtableFieldType.PERCENT           # Percentage

# Date/Time types
AirtableFieldType.DATE              # Date only
AirtableFieldType.DATETIME          # Date and time

# Selection types
AirtableFieldType.SELECT            # Single select
AirtableFieldType.MULTI_SELECT      # Multiple select
AirtableFieldType.CHECKBOX          # Boolean checkbox

# Other types
AirtableFieldType.ATTACHMENT        # File attachments
AirtableFieldType.FORMULA           # Computed field
AirtableFieldType.ROLLUP            # Rollup from linked records
AirtableFieldType.LOOKUP            # Lookup from linked records
```

---

## Custom Field Names

Map Python field names to different Airtable field names:

```python
@airtable_model(table_name="Users")
class User(BaseModel):
    # Python: user_name → Airtable: "Full Name"
    user_name: str = airtable_field(
        field_name="Full Name"
    )
    
    # Python: contact_email → Airtable: "Email Address"
    contact_email: str = airtable_field(
        field_name="Email Address"
    )
    
    # Python: created → Airtable: "Created Date"
    created: datetime = airtable_field(
        field_name="Created Date"
    )
```

### When to Use Custom Names

- Airtable fields have spaces: `"First Name"`, `"Phone Number"`
- Airtable fields have special characters: `"Cost ($)"`, `"Completion %"`
- Legacy tables with non-Pythonic names
- Integration with existing Airtable bases

---

## Select Fields with Choices

### Single Select

```python
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    
    # Define available choices
    status: str = airtable_field(
        field_type=AirtableFieldType.SELECT,
        choices=["To Do", "In Progress", "Review", "Done"],
        default="To Do"
    )
    
    priority: str = airtable_field(
        field_type=AirtableFieldType.SELECT,
        choices=["Low", "Medium", "High", "Urgent"],
        default="Medium"
    )
```

### Multi Select

```python
from typing import List

@airtable_model(table_name="Projects")
class Project(BaseModel):
    name: str
    
    # Multiple selections allowed
    tags: List[str] = airtable_field(
        field_type=AirtableFieldType.MULTI_SELECT,
        choices=["Frontend", "Backend", "Database", "DevOps", "Design"],
        default=[]
    )
    
    team_members: List[str] = airtable_field(
        field_type=AirtableFieldType.MULTI_SELECT,
        choices=["Alice", "Bob", "Carol", "Dave"],
        default=[]
    )
```

### Using Enums (Alternative)

```python
from enum import Enum

class Status(str, Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"

@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    status: Status = Status.TODO  # Automatically becomes SELECT
```

---

## Read-Only Fields

Mark fields that shouldn't be sent during create/update:

```python
@airtable_model(table_name="Records")
class Record(BaseModel):
    name: str
    
    # Auto-number field (Airtable generates this)
    record_number: int = airtable_field(
        read_only=True,
        default=0
    )
    
    # Formula field (computed by Airtable)
    calculated_value: str = airtable_field(
        field_type=AirtableFieldType.FORMULA,
        read_only=True,
        default=""
    )
    
    # Last modified (updated by Airtable)
    last_modified: datetime = airtable_field(
        read_only=True,
        default=None
    )
```

### Common Read-Only Fields

- Auto-number fields
- Formula fields
- Rollup fields
- Lookup fields
- Created time (use built-in `created_time`)
- Last modified time
- Created by / Modified by

---

## Field Options

### Currency Options

```python
@airtable_model(table_name="Products")
class Product(BaseModel):
    name: str
    
    # USD with 2 decimal places
    price_usd: float = airtable_field(
        field_type=AirtableFieldType.CURRENCY,
        json_schema_extra={
            "precision": 2,
            "symbol": "$"
        }
    )
    
    # Euro with 2 decimal places
    price_eur: float = airtable_field(
        field_type=AirtableFieldType.CURRENCY,
        json_schema_extra={
            "precision": 2,
            "symbol": "€"
        }
    )
```

### Percentage Options

```python
@airtable_model(table_name="Metrics")
class Metrics(BaseModel):
    name: str
    
    # Percentage with 1 decimal place
    completion: float = airtable_field(
        field_type=AirtableFieldType.PERCENT,
        json_schema_extra={
            "precision": 1
        }
    )
```

### Number Precision

```python
@airtable_model(table_name="Measurements")
class Measurement(BaseModel):
    name: str
    
    # Integer (no decimals)
    count: int = airtable_field(
        field_type=AirtableFieldType.NUMBER,
        json_schema_extra={
            "precision": 0
        }
    )
    
    # 4 decimal places
    precise_value: float = airtable_field(
        field_type=AirtableFieldType.NUMBER,
        json_schema_extra={
            "precision": 4
        }
    )
```

---

## Combining with Pydantic Validation

`airtable_field()` accepts all Pydantic Field() parameters:

```python
from pydantic import field_validator

@airtable_model(table_name="Users")
class User(BaseModel):
    # With Pydantic constraints
    name: str = airtable_field(
        min_length=1,
        max_length=100,
        description="User's full name"
    )
    
    # With pattern validation
    email: str = airtable_field(
        pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$',
        description="Valid email address"
    )
    
    # With numeric constraints
    age: int = airtable_field(
        ge=0,
        le=150,
        default=None,
        description="Age in years"
    )
    
    # Custom validator still works
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
```

---

## Complex Example

Here's a comprehensive example combining multiple customizations:

```python
from pydantic_airtable import airtable_model, airtable_field, AirtableFieldType
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

@airtable_model(table_name="Tasks")
class Task(BaseModel):
    # Standard fields with type detection
    title: str
    description: Optional[str] = None  # → LONG_TEXT (detected)
    
    # Custom Airtable field name
    assignee_email: str = airtable_field(
        field_name="Assigned To",
        field_type=AirtableFieldType.EMAIL
    )
    
    # Select with explicit choices
    status: str = airtable_field(
        field_name="Task Status",
        field_type=AirtableFieldType.SELECT,
        choices=["Backlog", "To Do", "In Progress", "Review", "Done"],
        default="Backlog"
    )
    
    # Enum-based select (auto-detected)
    priority: Priority = Priority.MEDIUM
    
    # Multi-select tags
    tags: List[str] = airtable_field(
        field_type=AirtableFieldType.MULTI_SELECT,
        choices=["Bug", "Feature", "Documentation", "Refactor"],
        default=[]
    )
    
    # Currency field
    estimated_cost: Optional[float] = airtable_field(
        field_name="Estimated Cost ($)",
        field_type=AirtableFieldType.CURRENCY,
        json_schema_extra={"precision": 2, "symbol": "$"},
        default=None
    )
    
    # Read-only computed field
    task_number: int = airtable_field(
        field_name="Task #",
        read_only=True,
        default=0
    )
    
    # Pydantic validation
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

---

## Troubleshooting

### Field Not Saving

```python
# Problem: Field value not saving to Airtable
notes: str = airtable_field(read_only=True)  # read_only prevents saving

# Solution: Remove read_only or set to False
notes: str = airtable_field(read_only=False)
```

### Wrong Type in Airtable

```python
# Problem: Field created with wrong type
status: str  # Created as SINGLE_LINE_TEXT, wanted SELECT

# Solution: Explicitly specify type
status: str = airtable_field(
    field_type=AirtableFieldType.SELECT,
    choices=["Active", "Inactive"]
)
```

### Field Name Mismatch

```python
# Problem: Python field doesn't match Airtable field
first_name: str  # Airtable has "First Name"

# Solution: Use field_name parameter
first_name: str = airtable_field(field_name="First Name")
```

---

## Next Steps

- [Multiple Bases](multiple-bases.md) - Work with multiple configurations
- [Error Handling](error-handling.md) - Handle field-related errors
- [Field Types](../guide/field-types.md) - Complete field type reference

