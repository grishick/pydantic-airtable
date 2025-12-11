# Table Management Example

Learn to create and manage AirTable schemas programmatically.

---

## Overview

This example demonstrates:

- Creating tables from Pydantic models
- Customizing field types and options
- Schema synchronization
- Handling model evolution

---

## Complete Code

```python
"""
Table Management Example for Pydantic AirTable
"""
from pydantic_airtable import (
    airtable_model,
    configure_from_env,
    airtable_field,
    AirTableFieldType,
    AirTableManager,
    AirTableConfig
)
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

configure_from_env()

# Enum definitions
class TaskStatus(str, Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    REVIEW = "Review"
    DONE = "Done"

class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

# Model definitions
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    description: Optional[str] = None  # LONG_TEXT (detected)
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    assignee_email: Optional[str] = None  # EMAIL (detected)
    due_date: Optional[datetime] = None
    is_blocked: bool = False
    
    # Custom field with explicit options
    tags: List[str] = airtable_field(
        field_type=AirTableFieldType.MULTI_SELECT,
        choices=["Bug", "Feature", "Documentation", "Refactor"],
        default=[]
    )
    
    # Custom field name in AirTable
    estimated_hours: Optional[float] = airtable_field(
        field_name="Estimated Hours",
        default=None
    )

@airtable_model(table_name="Users")
class User(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: bool = True

@airtable_model(table_name="Projects")
class Project(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = airtable_field(
        field_type=AirTableFieldType.SELECT,
        choices=["Planning", "Active", "On Hold", "Completed"],
        default="Planning"
    )
    budget: Optional[float] = airtable_field(
        field_name="Budget ($)",
        field_type=AirTableFieldType.CURRENCY,
        default=None
    )
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

def create_tables():
    """Create all tables from models"""
    models = [Task, User, Project]
    
    for model in models:
        try:
            result = model.create_table()
            print(f"✅ Created {model.__name__}: {result['id']}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"ℹ️ {model.__name__} already exists")
            else:
                print(f"❌ Error creating {model.__name__}: {e}")

def sync_schema():
    """Sync model changes to existing tables"""
    models = [Task, User, Project]
    
    for model in models:
        result = model.sync_table(
            create_missing_fields=True,
            update_field_types=False
        )
        print(f"\n{model.__name__} sync:")
        print(f"  Created: {result.get('fields_created', [])}")
        print(f"  Skipped: {result.get('fields_skipped', [])}")

def demonstrate_crud():
    """Demonstrate CRUD with managed tables"""
    
    # Create a user
    user = User.create(
        name="Alice Johnson",
        email="alice@example.com",
        department="Engineering"
    )
    print(f"\n✅ Created user: {user.name}")
    
    # Create a project
    project = Project.create(
        name="Website Redesign",
        description="Complete redesign of company website",
        budget=50000.00
    )
    print(f"✅ Created project: {project.name}")
    
    # Create tasks
    tasks = Task.bulk_create([
        {
            "title": "Design mockups",
            "description": "Create initial design mockups",
            "priority": Priority.HIGH,
            "assignee_email": "alice@example.com",
            "tags": ["Feature"],
            "estimated_hours": 8.0
        },
        {
            "title": "Review designs",
            "description": "Team review of mockups",
            "priority": Priority.MEDIUM,
            "tags": ["Feature"],
            "estimated_hours": 2.0
        }
    ])
    print(f"✅ Created {len(tasks)} tasks")
    
    # Query and update
    high_priority = Task.find_by(priority=Priority.HIGH)
    print(f"\n🔍 High priority tasks: {len(high_priority)}")
    
    for task in high_priority:
        task.status = TaskStatus.IN_PROGRESS
        task.save()
        print(f"  Updated: {task.title}")

def main():
    print("=== Table Management Demo ===\n")
    
    print("1. Creating tables...")
    create_tables()
    
    print("\n2. Syncing schema...")
    sync_schema()
    
    print("\n3. CRUD operations...")
    demonstrate_crud()
    
    print("\n✅ Demo complete!")

if __name__ == "__main__":
    main()
```

---

## Key Concepts

### Table Creation from Models

```python
# Define model
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    status: TaskStatus = TaskStatus.TODO

# Create table
result = Task.create_table()
# Returns: {'id': 'tblXXX', 'name': 'Tasks', 'fields': [...]}
```

### Field Type Mapping

| Model Definition | AirTable Field |
|------------------|----------------|
| `title: str` | singleLineText |
| `description: str` | multilineText (detected) |
| `status: TaskStatus` | singleSelect with enum values |
| `priority: Priority` | singleSelect with enum values |
| `due_date: datetime` | dateTime |
| `is_blocked: bool` | checkbox |
| `tags: List[str]` | multipleSelects |

### Custom Field Configuration

```python
# Explicit type
tags: List[str] = airtable_field(
    field_type=AirTableFieldType.MULTI_SELECT,
    choices=["Bug", "Feature", "Documentation"]
)

# Custom AirTable name
budget: float = airtable_field(
    field_name="Budget ($)",
    field_type=AirTableFieldType.CURRENCY
)
```

### Schema Synchronization

```python
# Add new fields to existing table
result = Task.sync_table(
    create_missing_fields=True,  # Add missing fields
    update_field_types=False     # Don't change existing types
)
```

---

## Running the Example

```bash
cd examples/table_management
pip install -r requirements.txt

# Set environment
export AIRTABLE_ACCESS_TOKEN="pat_your_token"
export AIRTABLE_BASE_ID="appYourBaseId"

python table_management.py
```

### Expected Output

```
=== Table Management Demo ===

1. Creating tables...
✅ Created Task: tblXXXXXXXXXXXXXX
✅ Created User: tblYYYYYYYYYYYYYY
✅ Created Project: tblZZZZZZZZZZZZZZ

2. Syncing schema...
Task sync:
  Created: []
  Skipped: []
User sync:
  Created: []
  Skipped: []
Project sync:
  Created: []
  Skipped: []

3. CRUD operations...
✅ Created user: Alice Johnson
✅ Created project: Website Redesign
✅ Created 2 tasks

🔍 High priority tasks: 1
  Updated: Design mockups

✅ Demo complete!
```

---

## Schema Evolution Pattern

### Adding New Fields

```python
# Original model
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    status: str

# After creating table, add new fields
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    status: str
    priority: Optional[str] = None  # New field
    due_date: Optional[datetime] = None  # New field

# Sync to add new fields
Task.sync_table(create_missing_fields=True)
```

### Migration Script

```python
def migrate_v1_to_v2():
    """
    Migration: Add priority and tags to Tasks
    """
    @airtable_model(table_name="Tasks")
    class TaskV2(BaseModel):
        title: str
        status: str
        # New in v2
        priority: str = airtable_field(
            field_type=AirTableFieldType.SELECT,
            choices=["Low", "Medium", "High"],
            default="Medium"
        )
        tags: List[str] = airtable_field(
            field_type=AirTableFieldType.MULTI_SELECT,
            choices=["Bug", "Feature"],
            default=[]
        )
    
    result = TaskV2.sync_table(create_missing_fields=True)
    
    print("Migration complete:")
    print(f"  Fields added: {result['fields_created']}")
    
    # Optionally, set default values for existing records
    tasks = TaskV2.all()
    for task in tasks:
        if not task.priority:
            task.priority = "Medium"
            task.save()
```

---

## Using AirTableManager

For advanced operations, use the manager directly:

```python
from pydantic_airtable import AirTableManager, AirTableConfig

config = AirTableConfig(
    access_token="pat_xxx",
    base_id="appXXX"
)

manager = AirTableManager(config)

# List bases
bases = manager.list_bases()
for base in bases:
    print(f"{base['name']}: {base['id']}")

# Get base schema
schema = manager.get_base_schema()
for table in schema['tables']:
    print(f"\nTable: {table['name']}")
    for field in table['fields']:
        print(f"  - {field['name']}: {field['type']}")

# Create custom table
manager.create_table("CustomTable", [
    {"name": "Name", "type": "singleLineText"},
    {"name": "Score", "type": "number", "options": {"precision": 2}}
])
```

---

## Best Practices

### 1. Version Your Schemas

```python
# Keep track of schema versions
SCHEMA_VERSION = "2.0.0"

def check_schema_version():
    """Verify schema is up to date"""
    # Store version in a Settings table
    pass
```

### 2. Test Migrations First

```python
# Use a test base for migrations
@pytest.fixture
def test_base():
    return AirTableConfig(
        access_token=os.getenv("TEST_TOKEN"),
        base_id=os.getenv("TEST_BASE")
    )

def test_migration(test_base):
    # Test migration on test base first
    pass
```

### 3. Document Schema Changes

```python
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    """
    Task model - v2.0
    
    Changes from v1.0:
    - Added priority field (SELECT)
    - Added tags field (MULTI_SELECT)
    - Renamed 'desc' to 'description'
    """
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    tags: List[str] = []
```

---

## Next Steps

- [Agentic Researcher](agentic-researcher.md) - Complex application example
- [Table Management Guide](../guide/table-management.md) - Detailed guide
- [Custom Fields](../advanced/custom-fields.md) - Field customization
