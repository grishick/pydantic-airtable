# CRUD Operations

Complete guide to Create, Read, Update, and Delete operations.

---

## Overview

All CRUD operations are available as methods on your model class:

| Operation | Method | Returns |
|-----------|--------|---------|
| Create | `Model.create(**data)` | Model instance |
| Read (single) | `Model.get(id)` | Model instance |
| Read (all) | `Model.all()` | List of instances |
| Read (filter) | `Model.find_by(**filters)` | List of instances |
| Read (first) | `Model.first(**filters)` | Instance or None |
| Update | `instance.save()` | Updated instance |
| Delete | `instance.delete()` | Deletion response |

---

## Create Operations

### Create Single Record

```python
from pydantic_airtable import airtable_model, configure_from_env
from pydantic import BaseModel

configure_from_env()

@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str
    age: int = None

# Create a record
user = User.create(
    name="Alice Johnson",
    email="alice@example.com",
    age=28
)

print(f"Created: {user.name}")
print(f"ID: {user.id}")
print(f"Created at: {user.created_time}")
```

### Create with Defaults

```python
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    status: str = "pending"
    priority: int = 1

# Uses default values for status and priority
task = Task.create(title="Review documentation")
print(f"Status: {task.status}")  # "pending"
print(f"Priority: {task.priority}")  # 1
```

### Create with Optional Fields

```python
# Optional fields can be omitted
user = User.create(
    name="Bob Smith",
    email="bob@example.com"
    # age is Optional, so it's None
)
```

### Bulk Create

Create multiple records efficiently:

```python
users_data = [
    {"name": "Alice", "email": "alice@example.com", "age": 28},
    {"name": "Bob", "email": "bob@example.com", "age": 32},
    {"name": "Carol", "email": "carol@example.com", "age": 25},
]

users = User.bulk_create(users_data)
print(f"Created {len(users)} users")

for user in users:
    print(f"  - {user.name} ({user.id})")
```

!!! tip "Performance"
    `bulk_create()` is more efficient than creating records one by one, especially for large datasets.

---

## Read Operations

### Get by ID

Retrieve a specific record by its AirTable ID:

```python
# Get record by ID
user = User.get("recXXXXXXXXXXXXXX")
print(f"Found: {user.name}")
```

If the record doesn't exist:

```python
from pydantic_airtable import RecordNotFoundError

try:
    user = User.get("recInvalidId")
except RecordNotFoundError:
    print("User not found!")
```

### Get All Records

Retrieve all records from the table:

```python
# Get all users
users = User.all()
print(f"Total users: {len(users)}")

for user in users:
    print(f"  - {user.name}: {user.email}")
```

### Find by Field Values

Query records by field values:

```python
# Find by single field
active_users = User.find_by(is_active=True)

# Find by multiple fields (AND)
senior_active = User.find_by(is_active=True, age=30)

# Find by string value
alice = User.find_by(name="Alice Johnson")
```

### Get First Match

Get the first record matching criteria:

```python
# Returns single instance or None
user = User.first(email="alice@example.com")

if user:
    print(f"Found: {user.name}")
else:
    print("No user found")
```

### Advanced Filtering

For complex queries, use the `filterByFormula` parameter:

```python
# Using AirTable formula
results = User.all(filterByFormula="{age} > 25")

# Complex formula
results = User.all(
    filterByFormula="AND({is_active}, {age} >= 18)"
)
```

### Pagination and Sorting

```python
# With sorting
users = User.all(
    sort=[{"field": "name", "direction": "asc"}]
)

# With field selection
users = User.all(
    fields=["name", "email"]  # Only fetch these fields
)

# With max records
users = User.all(maxRecords=10)
```

---

## Update Operations

### Update and Save

Modify an instance and save changes:

```python
# Get the record
user = User.get("recXXXXXXXXXXXXXX")

# Modify fields
user.name = "Alice Smith"  # Changed last name
user.age = 29

# Save changes
user.save()
print("User updated!")
```

### Conditional Updates

```python
user = User.first(email="alice@example.com")

if user:
    if user.age < 30:
        user.age += 1
        user.save()
        print(f"Birthday! Now {user.age}")
```

### Update Multiple Fields

```python
user = User.get("recXXXXXXXXXXXXXX")

# Update multiple fields
user.name = "Alice Johnson-Smith"
user.email = "alice.js@example.com"
user.is_active = False

# Single save call
user.save()
```

### Save Returns Updated Instance

```python
user.name = "New Name"
updated_user = user.save()

# Both references are updated
print(user.name)         # "New Name"
print(updated_user.name) # "New Name"
```

---

## Delete Operations

### Delete Single Record

```python
# Get and delete
user = User.get("recXXXXXXXXXXXXXX")
result = user.delete()
print(f"Deleted: {result}")
```

### Delete After Query

```python
# Find and delete
user = User.first(email="alice@example.com")
if user:
    user.delete()
    print("User deleted")
```

### Delete Multiple Records

```python
# Delete all inactive users
inactive_users = User.find_by(is_active=False)

for user in inactive_users:
    user.delete()
    print(f"Deleted: {user.name}")
```

### Safe Delete Pattern

```python
def safe_delete_user(user_id: str) -> bool:
    """Delete user if exists, return success status"""
    try:
        user = User.get(user_id)
        user.delete()
        return True
    except RecordNotFoundError:
        return False

# Usage
if safe_delete_user("recXXXXXXXXXXXXXX"):
    print("User deleted")
else:
    print("User not found")
```

---

## Error Handling

### Common Exceptions

```python
from pydantic_airtable import (
    APIError,
    RecordNotFoundError,
    ValidationError,
    ConfigurationError
)

try:
    user = User.get("recInvalidId")
except RecordNotFoundError:
    print("Record not found")
except APIError as e:
    print(f"AirTable API error: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Validation Errors

```python
from pydantic import ValidationError

try:
    # This will fail Pydantic validation
    user = User.create(name="", email="invalid")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Retry Pattern

```python
import time
from pydantic_airtable import APIError

def create_with_retry(data: dict, max_retries: int = 3):
    """Create record with retry logic"""
    for attempt in range(max_retries):
        try:
            return User.create(**data)
        except APIError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## Working with Records

### Check if Record Exists

```python
def user_exists(email: str) -> bool:
    """Check if user with email exists"""
    return User.first(email=email) is not None
```

### Get or Create Pattern

```python
def get_or_create_user(name: str, email: str) -> tuple[User, bool]:
    """Get existing user or create new one"""
    existing = User.first(email=email)
    if existing:
        return existing, False
    
    new_user = User.create(name=name, email=email)
    return new_user, True

# Usage
user, created = get_or_create_user("Alice", "alice@example.com")
if created:
    print("New user created")
else:
    print("Existing user found")
```

### Update or Create Pattern

```python
def update_or_create_user(email: str, **data) -> User:
    """Update existing user or create new one"""
    existing = User.first(email=email)
    
    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        existing.save()
        return existing
    
    return User.create(email=email, **data)
```

---

## Transaction-Like Patterns

AirTable doesn't support transactions, but you can implement patterns:

### Create with Cleanup

```python
def create_user_with_profile(user_data: dict, profile_data: dict):
    """Create user and profile, cleanup on failure"""
    user = None
    try:
        user = User.create(**user_data)
        profile_data['user_id'] = user.id
        profile = Profile.create(**profile_data)
        return user, profile
    except Exception as e:
        # Cleanup on failure
        if user:
            user.delete()
        raise
```

### Batch Updates with Rollback Data

```python
def batch_update_with_backup(users: list[User], updates: dict):
    """Update users with ability to see previous values"""
    results = []
    
    for user in users:
        # Store original values
        original = user.model_dump()
        
        # Apply updates
        for key, value in updates.items():
            setattr(user, key, value)
        
        user.save()
        results.append({
            'id': user.id,
            'original': original,
            'updated': user.model_dump()
        })
    
    return results
```

---

## Best Practices

!!! success "Performance Tips"
    - Use `bulk_create()` for multiple records
    - Use `find_by()` instead of filtering `all()` results
    - Limit fields with `fields=[]` parameter when you don't need all data
    - Use `maxRecords` to limit result sets

!!! success "Reliability Tips"
    - Always handle `RecordNotFoundError` for `get()` calls
    - Use `first()` instead of `find_by()[0]` for single results
    - Implement retry logic for production systems
    - Validate data before creating records

---

## Next Steps

- [Filtering & Queries](filtering.md) - Advanced query techniques
- [Batch Operations](batch-operations.md) - Working with multiple records
- [Error Handling](../advanced/error-handling.md) - Comprehensive error handling

