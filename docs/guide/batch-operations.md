# Batch Operations

Learn how to efficiently work with multiple records at once.

---

## Overview

Batch operations allow you to create, update, or delete multiple records efficiently. This is faster and more cost-effective than individual operations.

---

## Bulk Create

### Basic Bulk Create

Create multiple records in a single operation:

```python
users_data = [
    {"name": "Alice", "email": "alice@example.com", "age": 28},
    {"name": "Bob", "email": "bob@example.com", "age": 32},
    {"name": "Carol", "email": "carol@example.com", "age": 25},
    {"name": "Dave", "email": "dave@example.com", "age": 30},
]

users = User.bulk_create(users_data)

print(f"Created {len(users)} users")
for user in users:
    print(f"  - {user.name} ({user.id})")
```

### With Default Values

```python
# Model with defaults
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    status: str = "pending"
    priority: int = 1

# Only provide required fields
tasks_data = [
    {"title": "Task 1"},
    {"title": "Task 2"},
    {"title": "Task 3"},
]

tasks = Task.bulk_create(tasks_data)
# All tasks have status="pending" and priority=1
```

### Mixed Data

```python
# Some records have optional fields, some don't
users_data = [
    {"name": "Alice", "email": "alice@example.com", "age": 28},
    {"name": "Bob", "email": "bob@example.com"},  # No age
    {"name": "Carol", "email": "carol@example.com", "age": 25, "phone": "555-0123"},
]

users = User.bulk_create(users_data)
```

---

## Batch Processing Pattern

For large datasets, process in batches:

```python
def create_users_in_batches(users_data: list[dict], batch_size: int = 10):
    """Create users in batches to avoid rate limits"""
    created_users = []
    
    for i in range(0, len(users_data), batch_size):
        batch = users_data[i:i + batch_size]
        users = User.bulk_create(batch)
        created_users.extend(users)
        print(f"Created batch {i // batch_size + 1}: {len(users)} users")
    
    return created_users

# Usage with large dataset
large_dataset = [{"name": f"User {i}", "email": f"user{i}@example.com"} 
                 for i in range(100)]

all_users = create_users_in_batches(large_dataset)
print(f"Total created: {len(all_users)}")
```

---

## Batch Update Pattern

Update multiple records:

```python
def batch_update(records: list, updates: dict):
    """Update multiple records with the same changes"""
    updated = []
    
    for record in records:
        for key, value in updates.items():
            setattr(record, key, value)
        record.save()
        updated.append(record)
    
    return updated

# Usage
inactive_users = User.find_by(last_login__lt="2024-01-01")
batch_update(inactive_users, {"is_active": False})
```

### Conditional Batch Update

```python
def batch_update_conditional(model_class, condition: dict, updates: dict):
    """Find records matching condition and update them"""
    records = model_class.find_by(**condition)
    
    for record in records:
        for key, value in updates.items():
            setattr(record, key, value)
        record.save()
    
    return records

# Deactivate all pending tasks
batch_update_conditional(
    Task,
    condition={"status": "pending"},
    updates={"status": "cancelled"}
)
```

---

## Batch Delete Pattern

Delete multiple records:

```python
def batch_delete(records: list):
    """Delete multiple records"""
    deleted_ids = []
    
    for record in records:
        record.delete()
        deleted_ids.append(record.id)
    
    return deleted_ids

# Usage
old_tasks = Task.find_by(status="completed")
deleted = batch_delete(old_tasks)
print(f"Deleted {len(deleted)} tasks")
```

### Delete by Criteria

```python
def delete_by_criteria(model_class, **criteria):
    """Delete all records matching criteria"""
    records = model_class.find_by(**criteria)
    
    count = 0
    for record in records:
        record.delete()
        count += 1
    
    return count

# Delete all inactive users
deleted_count = delete_by_criteria(User, is_active=False)
print(f"Deleted {deleted_count} inactive users")
```

---

## Import/Export Patterns

### Import from CSV

```python
import csv

def import_users_from_csv(filepath: str):
    """Import users from CSV file"""
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        users_data = list(reader)
    
    # Convert types as needed
    for user in users_data:
        if 'age' in user and user['age']:
            user['age'] = int(user['age'])
        if 'is_active' in user:
            user['is_active'] = user['is_active'].lower() == 'true'
    
    return User.bulk_create(users_data)

# Usage
users = import_users_from_csv("users.csv")
print(f"Imported {len(users)} users")
```

### Export to CSV

```python
import csv

def export_users_to_csv(filepath: str):
    """Export all users to CSV file"""
    users = User.all()
    
    if not users:
        return 0
    
    # Get field names from first user
    fieldnames = list(users[0].model_dump().keys())
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for user in users:
            writer.writerow(user.model_dump())
    
    return len(users)

# Usage
count = export_users_to_csv("users_export.csv")
print(f"Exported {count} users")
```

### Import from JSON

```python
import json

def import_from_json(model_class, filepath: str):
    """Import records from JSON file"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return model_class.bulk_create(data)

# Usage
tasks = import_from_json(Task, "tasks.json")
```

### Export to JSON

```python
import json

def export_to_json(model_class, filepath: str):
    """Export all records to JSON file"""
    records = model_class.all()
    
    data = [record.model_dump() for record in records]
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    return len(data)

# Usage
export_to_json(User, "users.json")
```

---

## Sync Patterns

### Upsert Pattern

Create or update based on unique field:

```python
def upsert_users(users_data: list[dict], unique_field: str = "email"):
    """Create or update users based on unique field"""
    created = []
    updated = []
    
    for data in users_data:
        unique_value = data[unique_field]
        existing = User.first(**{unique_field: unique_value})
        
        if existing:
            # Update existing
            for key, value in data.items():
                setattr(existing, key, value)
            existing.save()
            updated.append(existing)
        else:
            # Create new
            user = User.create(**data)
            created.append(user)
    
    return {"created": created, "updated": updated}

# Usage
result = upsert_users([
    {"name": "Alice Updated", "email": "alice@example.com"},
    {"name": "New User", "email": "new@example.com"},
])
print(f"Created: {len(result['created'])}, Updated: {len(result['updated'])}")
```

### Sync from External Source

```python
def sync_from_external(external_data: list[dict], id_field: str = "external_id"):
    """Sync records from external data source"""
    results = {
        "created": 0,
        "updated": 0,
        "unchanged": 0,
        "deleted": 0
    }
    
    # Get all existing records
    existing = {getattr(r, id_field): r for r in Record.all()}
    external_ids = {d[id_field] for d in external_data}
    
    # Process external data
    for data in external_data:
        ext_id = data[id_field]
        
        if ext_id in existing:
            record = existing[ext_id]
            changed = False
            
            for key, value in data.items():
                if getattr(record, key, None) != value:
                    setattr(record, key, value)
                    changed = True
            
            if changed:
                record.save()
                results["updated"] += 1
            else:
                results["unchanged"] += 1
        else:
            Record.create(**data)
            results["created"] += 1
    
    # Delete records not in external data
    for ext_id, record in existing.items():
        if ext_id not in external_ids:
            record.delete()
            results["deleted"] += 1
    
    return results
```

---

## Progress Tracking

### With Progress Callback

```python
def bulk_create_with_progress(data: list[dict], callback=None):
    """Bulk create with progress callback"""
    total = len(data)
    created = []
    
    for i, item in enumerate(data):
        user = User.create(**item)
        created.append(user)
        
        if callback:
            callback(i + 1, total, user)
    
    return created

# Usage with progress
def print_progress(current, total, user):
    percent = (current / total) * 100
    print(f"[{percent:.1f}%] Created {user.name}")

users = bulk_create_with_progress(users_data, callback=print_progress)
```

### With tqdm Progress Bar

```python
from tqdm import tqdm

def bulk_create_with_tqdm(data: list[dict]):
    """Bulk create with tqdm progress bar"""
    created = []
    
    for item in tqdm(data, desc="Creating users"):
        user = User.create(**item)
        created.append(user)
    
    return created
```

---

## Error Handling in Batches

### Continue on Error

```python
def bulk_create_safe(data: list[dict]):
    """Bulk create, continue on errors"""
    created = []
    errors = []
    
    for i, item in enumerate(data):
        try:
            user = User.create(**item)
            created.append(user)
        except Exception as e:
            errors.append({"index": i, "data": item, "error": str(e)})
    
    return {"created": created, "errors": errors}

# Usage
result = bulk_create_safe(users_data)
print(f"Created: {len(result['created'])}")
print(f"Errors: {len(result['errors'])}")
```

### Stop on Error

```python
def bulk_create_strict(data: list[dict]):
    """Bulk create, stop and rollback on error"""
    created = []
    
    try:
        for item in data:
            user = User.create(**item)
            created.append(user)
    except Exception as e:
        # Rollback: delete created records
        for user in created:
            user.delete()
        raise RuntimeError(f"Batch failed: {e}. Rolled back {len(created)} records.")
    
    return created
```

---

## Performance Considerations

!!! tip "Batch Size"
    AirTable API supports up to 10 records per request. The library handles this automatically, but be aware of rate limits.

!!! tip "Rate Limits"
    AirTable has rate limits (5 requests per second per base). For large batches, add delays:
    
    ```python
    import time
    
    def bulk_create_rate_limited(data, delay=0.2):
        created = []
        for item in data:
            user = User.create(**item)
            created.append(user)
            time.sleep(delay)  # Respect rate limits
        return created
    ```

!!! tip "Memory Usage"
    For very large datasets, process in chunks to avoid memory issues:
    
    ```python
    def process_large_dataset(filepath: str, chunk_size: int = 1000):
        """Process large file in chunks"""
        import pandas as pd
        
        for chunk in pd.read_csv(filepath, chunksize=chunk_size):
            data = chunk.to_dict('records')
            User.bulk_create(data)
    ```

---

## Next Steps

- [CRUD Operations](crud-operations.md) - Individual record operations
- [Filtering & Queries](filtering.md) - Query your batch-created records
- [Best Practices](../advanced/best-practices.md) - Production patterns

