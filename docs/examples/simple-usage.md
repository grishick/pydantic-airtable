# Simple Usage Example

A beginner-friendly example demonstrating core Pydantic Airtable features.

---

## Overview

This example shows how to:

- Configure the library from environment variables
- Define models with smart field detection
- Perform CRUD operations
- Use filtering and queries

---

## Complete Code

```python
"""
Simple Usage Example for Pydantic Airtable
"""
from pydantic_airtable import (
    airtable_model, 
    configure_from_env,
    airtable_field,
    AirtableFieldType
)
from pydantic import BaseModel
from typing import Optional

# Configure from environment
configure_from_env()

@airtable_model(table_name="Users")
class User(BaseModel):
    # Smart field detection
    name: str                    # → SINGLE_LINE_TEXT
    email: str                   # → EMAIL (detected from name)
    age: Optional[int] = None    # → NUMBER
    is_active: bool = True       # → CHECKBOX
    
    # Explicit override
    bio: Optional[str] = airtable_field(
        field_type=AirtableFieldType.LONG_TEXT,
        default=None
    )

def main():
    # Create table if needed
    try:
        User.create_table()
        print("✅ Table created")
    except Exception as e:
        print(f"ℹ️ Table may exist: {e}")
    
    # Create a user
    alice = User.create(
        name="Alice Johnson",
        email="alice@example.com",
        age=28
    )
    print(f"✅ Created: {alice.name} ({alice.id})")
    
    # Query users
    all_users = User.all()
    print(f"📊 Total users: {len(all_users)}")
    
    # Find by criteria
    active_users = User.find_by(is_active=True)
    print(f"🔍 Active users: {len(active_users)}")
    
    # Get first match
    found = User.first(email="alice@example.com")
    if found:
        print(f"✅ Found: {found.name}")
    
    # Update
    alice.age = 29
    alice.save()
    print(f"✅ Updated age to: {alice.age}")
    
    # Bulk create
    users = User.bulk_create([
        {"name": "Bob", "email": "bob@example.com"},
        {"name": "Carol", "email": "carol@example.com"},
    ])
    print(f"✅ Bulk created: {len(users)} users")
    
    # Cleanup
    for user in User.all():
        user.delete()
    print("✅ Cleanup complete")

if __name__ == "__main__":
    main()
```

---

## Step-by-Step Breakdown

### 1. Configuration

```python
from pydantic_airtable import configure_from_env

configure_from_env()
```

This loads credentials from:
- `.env` file in current directory
- Environment variables `AIRTABLE_ACCESS_TOKEN` and `AIRTABLE_BASE_ID`

### 2. Model Definition

```python
@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    is_active: bool = True
```

The decorator:
- Links the model to the "Users" table
- Adds `id` and `created_time` fields automatically
- Enables CRUD methods

### 3. Smart Detection

| Field | Python Type | Detected Airtable Type |
|-------|-------------|------------------------|
| `name` | `str` | SINGLE_LINE_TEXT |
| `email` | `str` | EMAIL (name pattern) |
| `age` | `Optional[int]` | NUMBER |
| `is_active` | `bool` | CHECKBOX |

### 4. Creating Records

```python
# Single record
user = User.create(name="Alice", email="alice@example.com")

# Bulk create
users = User.bulk_create([
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Carol", "email": "carol@example.com"},
])
```

### 5. Querying Records

```python
# Get all
all_users = User.all()

# Filter by field values
active = User.find_by(is_active=True)

# Get first match
user = User.first(email="alice@example.com")

# Get by ID
user = User.get("recXXXXXXXXXXXXXX")
```

### 6. Updating Records

```python
user.name = "Alice Smith"
user.age = 30
user.save()
```

### 7. Deleting Records

```python
user.delete()
```

---

## Running the Example

### Prerequisites

1. Python 3.8+
2. Airtable account with API access

### Setup

```bash
# Navigate to example
cd examples/simple_usage

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
AIRTABLE_ACCESS_TOKEN=pat_your_token
AIRTABLE_BASE_ID=appYourBaseId
EOF

# Run
python simple_usage.py
```

### Expected Output

```
✅ Table created
✅ Created: Alice Johnson (recXXXXXXXXXXXXXX)
📊 Total users: 1
🔍 Active users: 1
✅ Found: Alice Johnson
✅ Updated age to: 29
✅ Bulk created: 2 users
✅ Cleanup complete
```

---

## Variations

### With Enums

```python
from enum import Enum

class Role(str, Enum):
    USER = "User"
    ADMIN = "Admin"
    MODERATOR = "Moderator"

@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str
    role: Role = Role.USER  # Creates SELECT field
```

### With More Field Types

```python
from datetime import datetime

@airtable_model(table_name="Contacts")
class Contact(BaseModel):
    name: str
    email: str              # EMAIL
    phone: str              # PHONE
    website: str            # URL
    bio: str                # LONG_TEXT
    salary: float           # CURRENCY
    completion: float       # PERCENT (if named 'rate', 'ratio', etc.)
    joined_at: datetime     # DATETIME
    is_verified: bool       # CHECKBOX
```

### With Custom Configuration

```python
from pydantic_airtable import AirtableConfig

config = AirtableConfig(
    access_token="pat_xxx",
    base_id="appXXX"
)

@airtable_model(config=config, table_name="Users")
class User(BaseModel):
    name: str
    email: str
```

---

## Common Patterns

### Error Handling

```python
from pydantic_airtable import APIError, RecordNotFoundError

try:
    user = User.get("recInvalidId")
except RecordNotFoundError:
    print("User not found")
except APIError as e:
    print(f"API error: {e}")
```

### Find or Create

```python
def get_or_create_user(email: str, name: str) -> User:
    existing = User.first(email=email)
    if existing:
        return existing
    return User.create(name=name, email=email)
```

### Conditional Updates

```python
def activate_user(email: str) -> bool:
    user = User.first(email=email)
    if user and not user.is_active:
        user.is_active = True
        user.save()
        return True
    return False
```

---

## Next Steps

- [Table Management](table-management.md) - Learn schema management
- [Field Types](../guide/field-types.md) - All field type options
- [CRUD Operations](../guide/crud-operations.md) - Detailed CRUD guide
