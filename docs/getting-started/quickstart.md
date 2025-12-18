# Quick Start

Get up and running with Pydantic Airtable in under 5 minutes.

---

## Prerequisites

Before starting, ensure you have:

- [x] Python 3.8+ installed
- [x] Pydantic Airtable [installed](installation.md)
- [x] Airtable [credentials configured](installation.md#getting-airtable-credentials)

---

## Your First Model

### Step 1: Configure the Library

```python
from pydantic_airtable import configure_from_env

# Load configuration from .env file or environment variables
configure_from_env()
```

This reads your `AIRTABLE_ACCESS_TOKEN` and `AIRTABLE_BASE_ID` from the environment.

### Step 2: Define Your Model

```python
from pydantic_airtable import airtable_model
from pydantic import BaseModel
from typing import Optional

@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    is_active: bool = True
```

The `@airtable_model` decorator transforms your Pydantic model into an Airtable-connected model with full CRUD capabilities.

### Step 3: Create the Table

```python
# Create the table in Airtable (if it doesn't exist)
User.create_table()
print("✅ Users table created!")
```

### Step 4: Create Records

```python
# Create a single record
alice = User.create(
    name="Alice Johnson",
    email="alice@example.com",
    age=28
)
print(f"Created: {alice.name} (ID: {alice.id})")
```

### Step 5: Query Records

```python
# Get all records
all_users = User.all()
print(f"Total users: {len(all_users)}")

# Find specific records
active_users = User.find_by(is_active=True)
print(f"Active users: {len(active_users)}")

# Get first match
user = User.first(name="Alice Johnson")
if user:
    print(f"Found: {user.email}")
```

### Step 6: Update Records

```python
# Update and save
alice.age = 29
alice.save()
print("✅ User updated!")
```

### Step 7: Delete Records

```python
# Delete a record
alice.delete()
print("✅ User deleted!")
```

---

## Complete Example

Here's a complete working example:

```python
"""
Complete Pydantic Airtable Quick Start Example
"""
from pydantic_airtable import airtable_model, configure_from_env
from pydantic import BaseModel
from typing import Optional

# Step 1: Configure
configure_from_env()

# Step 2: Define model
@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    is_active: bool = True

def main():
    # Step 3: Create table (idempotent)
    try:
        User.create_table()
        print("✅ Table created!")
    except Exception as e:
        print(f"Table may already exist: {e}")

    # Step 4: Create a user
    user = User.create(
        name="Alice Johnson",
        email="alice@example.com",
        age=28
    )
    print(f"✅ Created: {user.name} (ID: {user.id})")

    # Step 5: Query users
    all_users = User.all()
    print(f"📊 Total users: {len(all_users)}")

    # Find by criteria
    found = User.find_by(is_active=True)
    print(f"🔍 Active users: {len(found)}")

    # Step 6: Update user
    user.age = 29
    user.save()
    print(f"✅ Updated age to: {user.age}")

    # Step 7: Delete user (cleanup)
    user.delete()
    print("✅ User deleted!")

if __name__ == "__main__":
    main()
```

Save this as `quickstart.py` and run:

```bash
python quickstart.py
```

---

## Understanding the Output

When you run the example, you'll see output like:

```
✅ Table created!
✅ Created: Alice Johnson (ID: recXXXXXXXXXXXXXX)
📊 Total users: 1
🔍 Active users: 1
✅ Updated age to: 29
✅ User deleted!
```

Each record gets a unique Airtable ID (starting with `rec`) that you can use to reference it later.

---

## Smart Field Detection in Action

Notice how we didn't specify any Airtable field types? The library automatically detected them:

| Python Field | Airtable Type | Why? |
|--------------|---------------|------|
| `name: str` | SINGLE_LINE_TEXT | Default for strings |
| `email: str` | EMAIL | Field name contains "email" |
| `age: Optional[int]` | NUMBER | Integer type |
| `is_active: bool` | CHECKBOX | Boolean type |

!!! tip "Override Detection"
    You can override auto-detection when needed. See [Custom Fields](../advanced/custom-fields.md) for details.

---

## Common Patterns

### Creating Multiple Records

```python
# Batch creation
users_data = [
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Carol", "email": "carol@example.com"},
    {"name": "Dave", "email": "dave@example.com"},
]
users = User.bulk_create(users_data)
print(f"Created {len(users)} users!")
```

### Filtering Records

```python
# Simple equality
active_users = User.find_by(is_active=True)

# Multiple conditions (AND)
active_adults = User.find_by(is_active=True, age=28)

# Get single record by ID
user = User.get("recXXXXXXXXXXXXXX")
```

### Working with Optional Fields

```python
# Fields with None are handled gracefully
user = User.create(
    name="Eve",
    email="eve@example.com"
    # age is None, is_active defaults to True
)
```

---

## Error Handling

Always handle potential errors:

```python
from pydantic_airtable import APIError, ConfigurationError, RecordNotFoundError

try:
    user = User.get("recInvalidId")
except RecordNotFoundError:
    print("User not found!")
except APIError as e:
    print(f"Airtable API error: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

---

## Next Steps

Now that you've created your first model:

1. **[Configuration](configuration.md)** - Learn all configuration options
2. **[Field Types](../guide/field-types.md)** - Understand smart field detection
3. **[CRUD Operations](../guide/crud-operations.md)** - Deep dive into all operations
4. **[Examples](../examples/index.md)** - See more complex examples
