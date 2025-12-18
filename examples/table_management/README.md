# Table and Base Management Example

This example demonstrates the schema management capabilities of the Pydantic Airtable library, including creating bases and tables programmatically.

## 🎯 What This Example Shows

- **Base Management**: Create, list, and manage Airtable bases
- **Table Creation**: Generate tables from Pydantic models automatically
- **Schema Validation**: Ensure models match Airtable table structures
- **Schema Synchronization**: Add missing fields to existing tables
- **Model Evolution**: Handle changing requirements over time

## 🏃 Quick Start

1. **Set Environment Variables**:
   ```bash
   export AIRTABLE_ACCESS_TOKEN="pat_your_personal_access_token"
   # AIRTABLE_BASE_ID is optional - will create new base if not provided
   export AIRTABLE_BASE_ID="app_your_base_id"  # Optional
   ```

2. **Run the Example**:
   ```bash
   python table_management.py
   ```

## 📋 What It Does

### 1. Base Management Demo
- **Lists existing bases** accessible with your token
- **Creates new bases** with multiple tables
- **Retrieves base schemas** with complete field information
- **Manages base lifecycle** (create, inspect, delete)

### 2. Table Management Demo
- **Creates tables from Pydantic models** automatically
- **Validates schema compatibility** between models and tables
- **Synchronizes schemas** by adding missing fields
- **Handles model evolution** gracefully

### 3. Model-Table Integration Demo
- **Models create their own tables** with `create_table_in_airtable()`
- **Automatic field type detection** from Python types
- **Enum support** with automatic choice generation
- **Built-in validation** and error handling

### 4. Schema Synchronization Demo
- **Evolving models** that gain new fields over time
- **Non-destructive updates** that only add, never remove
- **Validation reporting** with detailed mismatch analysis
- **Safe schema migration** patterns

## 🏗️ Architecture Overview

### BaseManager
```python
base_manager = BaseManager(access_token)

# Create bases with multiple tables
new_base = base_manager.create_base(
    name="Project Management",
    tables=[task_config, user_config]
)

# List and inspect bases
bases = base_manager.list_bases()
schema = base_manager.get_base_schema(base_id)
```

### TableManager
```python
table_manager = TableManager(access_token, base_id)

# Create from Pydantic models
table_info = table_manager.create_table_from_pydantic(
    MyModel, 
    table_name="CustomName",
    description="Generated from Pydantic model"
)

# Validate and sync schemas
validation = table_manager.validate_pydantic_model_against_table(MyModel, "TableName")
sync_result = table_manager.sync_pydantic_model_to_table(MyModel, "TableName")
```

### Model Integration
```python
class Task(AirtableModel):
    title: str
    priority: Priority  # Enum -> SELECT field
    due_date: Optional[datetime]

# Model creates its own table
Task.create_table_in_airtable(description="Auto-generated")

# Validate and sync
validation = Task.validate_table_schema()
sync_result = Task.sync_table_schema(create_missing_fields=True)
```

## 🔄 Schema Evolution Workflow

### 1. Initial Model
```python
class Task(AirtableModel):
    title: str
    status: TaskStatus
```

### 2. Evolved Model
```python
class Task(AirtableModel):
    title: str
    status: TaskStatus
    # New fields added
    complexity: Optional[int]
    tags: Optional[str]
```

### 3. Synchronization
```python
# Add missing fields to existing table
sync_result = Task.sync_table_schema(
    create_missing_fields=True,
    update_field_types=False  # Safe: only add, don't modify
)
```

## 🎨 Advanced Features

### Automatic Type Detection
- **Python types** → **Airtable field types**
- **Enums** → **SELECT fields with choices**
- **Optional types** → **Nullable fields**
- **DateTime** → **Proper date/time fields**

### Field Configuration
```python
complexity: Optional[int] = AirtableField(
    default=None,
    description="Task complexity rating (1-10)",
    airtable_field_type=AirtableFieldType.NUMBER
)
```

### Validation Reporting
```python
validation = Task.validate_table_schema()
# Returns:
# {
#   "is_valid": False,
#   "missing_in_table": ["complexity", "tags"],
#   "missing_in_model": [],
#   "type_mismatches": []
# }
```

## 💡 Key Learning Points

- **Infrastructure as Code**: Define your database schema in Python
- **Type Safety**: Full validation from Python to Airtable
- **Schema Evolution**: Handle changing requirements gracefully
- **Enum Integration**: Rich data types with automatic UI generation
- **Non-Destructive Updates**: Safe schema migrations

## 🚀 Production Patterns

### Schema Versioning
```python
# Version 1: Basic model
class TaskV1(AirtableModel):
    title: str
    status: str

# Version 2: Enhanced model  
class TaskV2(AirtableModel):
    title: str
    status: TaskStatus  # Now an enum
    priority: Priority  # New field
    
# Migration
TaskV2.sync_table_schema(create_missing_fields=True)
```

### Multi-Environment Management
```python
# Development
dev_base = base_manager.create_base("MyApp-Dev", tables)

# Staging  
staging_base = base_manager.create_base("MyApp-Staging", tables)

# Production
prod_base = base_manager.create_base("MyApp-Prod", tables)
```

## 🔧 Troubleshooting

### Common Issues
- **Permission Errors**: Ensure PAT has base/table creation permissions
- **Schema Conflicts**: Use validation before making changes
- **Field Type Mismatches**: Check enum definitions and type mappings

### Best Practices
- **Always validate** before syncing schemas
- **Use descriptive names** for tables and fields
- **Test schema changes** in development first
- **Document field purposes** with descriptions

## 📚 Related Examples

- **[Simple Usage](../simple_usage/)**: Foundation CRUD operations
- **[Agentic Researcher](../agentic_researcher/)**: Full AI application with schema management

