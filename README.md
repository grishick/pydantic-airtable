# Pydantic AirTable

A Python library for managing AirTable data using Pydantic objects, similar to how SQLAlchemy manages relational databases. This library combines the power of Pydantic's data validation with AirTable's flexible database capabilities.

## 🚀 Features

- **Pydantic Integration**: Use familiar Pydantic models with automatic validation
- **Type Safety**: Full type hints and runtime type checking
- **CRUD Operations**: Create, read, update, and delete records with simple method calls
- **Field Mapping**: Automatic mapping between Python field names and AirTable column names
- **Batch Operations**: Efficient batch create and update operations
- **Query Interface**: Intuitive querying with filtering and sorting
- **Rate Limiting**: Built-in handling of AirTable API rate limits
- **Error Handling**: Comprehensive error handling with custom exceptions
- **🆕 Base Management**: Create and manage AirTable bases programmatically
- **🆕 Table Management**: Create, update, and delete tables from Pydantic models
- **🆕 Schema Sync**: Synchronize Pydantic models with existing AirTable schemas
- **🆕 Auto-Schema Generation**: Automatically generate AirTable schemas from Python types

## 📦 Installation

```bash
pip install -r requirements.txt
```

**📚 Detailed Installation Guide**: See [INSTALLATION.md](INSTALLATION.md) for complete setup instructions, troubleshooting, and version compatibility information.

## 🔧 Setup

### 1. Get AirTable Credentials

1. Create an AirTable account and base
2. **Generate a Personal Access Token (PAT)** from [AirTable Developer Hub](https://airtable.com/developers/web/api/authentication)
   - ⚠️ **Important**: AirTable has deprecated API keys. You must use Personal Access Tokens (PATs)
   - PATs start with `pat_` and provide better security and granular permissions
3. Get your Base ID from the AirTable API documentation for your base

### 2. Set Environment Variables

```bash
export AIRTABLE_ACCESS_TOKEN="pat_your_personal_access_token"
export AIRTABLE_BASE_ID="app_your_base_id"
```

**Important**: AirTable has [deprecated API keys](https://airtable.com/developers/web/api/authentication) in favor of Personal Access Tokens (PATs). Always use PATs which start with `pat_`.

For backward compatibility, `AIRTABLE_API_KEY` is still supported but will show deprecation warnings.

Alternatively, you can pass these values directly when creating `AirTableConfig`.

## 📚 Usage

### Basic Model Definition

```python
from datetime import datetime
from typing import Optional
from pydantic_airtable import AirTableModel, AirTableConfig, AirTableField
from pydantic_airtable.fields import AirTableFieldType

class User(AirTableModel):
    # Configure AirTable connection
    AirTableConfig = AirTableConfig(
        table_name="Users"  # AirTable table name
    )
    
    # Define fields with Pydantic validation
    name: str = AirTableField(
        description="User's full name",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    email: str = AirTableField(
        description="User's email address",
        airtable_field_type=AirTableFieldType.EMAIL
    )
    
    age: Optional[int] = AirTableField(
        default=None,
        description="User's age",
        airtable_field_type=AirTableFieldType.NUMBER
    )
    
    is_active: bool = AirTableField(
        default=True,
        description="Whether user is active",
        airtable_field_type=AirTableFieldType.CHECKBOX
    )
```

### CRUD Operations

```python
# Create a new record
user = User.create(
    name="John Doe",
    email="john@example.com",
    age=30
)
print(f"Created user with ID: {user.id}")

# Get a record by ID
user = User.get("rec123456789")
print(f"Retrieved user: {user.name}")

# Update a record
user.age = 31
user.save()

# Delete a record
user.delete()
```

### Querying Records

```python
# Get all records
all_users = User.all()

# Filter by field values
active_users = User.find_by(is_active=True)
john_users = User.find_by(name="John Doe")

# Get first matching record
first_user = User.first(is_active=True)

# Advanced filtering with AirTable formulas
young_users = User.filter(
    filter_by_formula="AND({Age} < 25, {Is Active} = TRUE())",
    max_records=10,
    sort=[{"field": "Age", "direction": "asc"}]
)
```

### Batch Operations

```python
# Batch create multiple records
users_data = [
    {"name": "Alice Smith", "email": "alice@example.com", "age": 25},
    {"name": "Bob Johnson", "email": "bob@example.com", "age": 35},
    {"name": "Carol Wilson", "email": "carol@example.com", "age": 28},
]

created_users = User.bulk_create(users_data)
print(f"Created {len(created_users)} users")
```

### 🆕 Table and Base Management

#### Creating Tables from Pydantic Models

```python
from pydantic_airtable import BaseManager, TableManager
from enum import Enum

class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium" 
    HIGH = "High"

class Task(AirTableModel):
    AirTableConfig = AirTableConfig(table_name="Tasks")
    
    title: str = AirTableField(airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT)
    priority: Priority = AirTableField(airtable_field_type=AirTableFieldType.SELECT)
    due_date: Optional[datetime] = AirTableField(airtable_field_type=AirTableFieldType.DATETIME)

# Method 1: Model creates its own table
table_info = Task.create_table_in_airtable(
    description="Tasks table created from Pydantic model"
)
print(f"Created table: {table_info['name']}")

# Method 2: Using TableManager directly
table_manager = TableManager(access_token, base_id)
table_info = table_manager.create_table_from_pydantic(
    Task, 
    table_name="MyTasks",
    description="Custom task table"
)
```

#### Creating AirTable Bases

```python
base_manager = BaseManager(access_token)

# Create a new base with tables
new_base = base_manager.create_base(
    name="Project Management",
    tables=[
        {
            "name": "Tasks",
            "fields": [
                {"name": "Title", "type": "singleLineText"},
                {"name": "Status", "type": "singleSelect", "options": {"choices": [
                    {"name": "Pending"}, {"name": "In Progress"}, {"name": "Completed"}
                ]}},
                {"name": "Due Date", "type": "dateTime"}
            ]
        }
    ]
)
print(f"Created base: {new_base['name']} (ID: {new_base['id']})")

# List all accessible bases
bases = base_manager.list_bases()
for base in bases:
    print(f"Base: {base['name']} (ID: {base['id']})")
```

#### Schema Synchronization

```python
# Validate model matches table
validation = Task.validate_table_schema()
if validation['is_valid']:
    print("✅ Model matches table schema!")
else:
    print("⚠️ Schema mismatches found")

# Sync model with table (add missing fields)
sync_result = Task.sync_table_schema(
    create_missing_fields=True,
    update_field_types=False
)
print(f"Added fields: {sync_result['sync_results']['fields_added']}")
```

### 🤖 Agentic Researcher Example

The library includes a comprehensive AI research assistant that demonstrates advanced schema management:

```python
from examples.agentic_researcher import AgenticResearcher
import asyncio

# Initialize with OpenAI and AirTable credentials
researcher = AgenticResearcher(
    openai_api_key="your_openai_key",
    airtable_access_token="pat_your_token"
    # Will create new base automatically
)

# Create and execute research
async def main():
    # Create research task
    task = await researcher.create_research_task(
        title="AI Impact on Software Development",
        description="Analyze current trends and productivity impacts",
        priority=ResearchPriority.HIGH
    )
    
    # Execute full research workflow
    final_summary = await researcher.execute_full_research(task)
    
    # Ask questions about findings
    answer = await researcher.answer_question(
        "What are the key benefits identified?", 
        task.id
    )
    
asyncio.run(main())
```

**Features:**
- **📊 Structured Data Models**: ResearchTask, ResearchStep, ResearchResult
- **🏗️ Auto-Schema Creation**: Creates AirTable base and tables automatically
- **🤖 AI-Powered Research**: Uses OpenAI for research planning and execution
- **📝 Complete Workflow**: Task creation → Step planning → Execution → Summarization
- **❓ Q&A System**: Answer questions using research context
- **🔄 Progress Tracking**: Real-time status updates in AirTable

**Run the example:**
```bash
# Install latest OpenAI library
pip install openai>=2.8.1

# Set environment variables
export OPENAI_API_KEY="your_key"
export AIRTABLE_ACCESS_TOKEN="pat_your_token"

# Automated demo
python examples/agentic_researcher/agentic_researcher.py --demo

# Interactive mode
python examples/agentic_researcher/agentic_researcher.py --interactive
```

**Note**: Requires OpenAI API key and uses latest OpenAI Python library (2.8.1) with `gpt-4o` model for optimal performance.
```

## 🤖 AI Agent Task Management Example

The library includes a comprehensive example for managing AI agent tasks. Here's a quick overview:

```python
from datetime import datetime
from examples.agent_tasks import AgentTask, TaskStatus, TaskPriority

# Create a task
task = AgentTask.create(
    name="Process Customer Emails",
    description="Analyze and categorize incoming customer support emails",
    agent_id="agent_001",
    priority=TaskPriority.HIGH
)

# Execute task lifecycle
task.start_execution()
# ... do work ...
task.complete_execution("Processed 45 emails successfully", execution_time=23.5)

# Query tasks
pending_tasks = AgentTask.get_pending_tasks(agent_id="agent_001")
failed_tasks = AgentTask.get_failed_tasks()
agent_stats = AgentTask.get_agent_stats("agent_001")
```

## 🛠 Advanced Features

### Custom Field Names

Map Python field names to different AirTable column names:

```python
class Product(AirTableModel):
    AirTableConfig = AirTableConfig(table_name="Products")
    
    product_name: str = AirTableField(
        airtable_field_name="Product Name",  # Different column name in AirTable
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
```

### Read-Only Fields

Mark fields as read-only to exclude them from create/update operations:

```python
class Record(AirTableModel):
    AirTableConfig = AirTableConfig(table_name="Records")
    
    auto_number: int = AirTableField(
        read_only=True,  # Won't be sent in create/update requests
        airtable_field_type=AirTableFieldType.AUTO_NUMBER
    )
```

### Field Type Auto-Detection

The library automatically detects AirTable field types based on Python types:

```python
class AutoDetected(AirTableModel):
    AirTableConfig = AirTableConfig(table_name="Auto")
    
    # These will be auto-detected:
    text_field: str          # -> SINGLE_LINE_TEXT
    number_field: int        # -> NUMBER
    float_field: float       # -> NUMBER
    checkbox_field: bool     # -> CHECKBOX
    datetime_field: datetime # -> DATETIME
```

## 🔍 Field Types

Supported AirTable field types with automatic mapping:

- `SINGLE_LINE_TEXT` - Short text (from `str`)
- `LONG_TEXT` - Multi-line text (explicit)
- `NUMBER` - Numeric values (from `int`, `float`)
- `CHECKBOX` - Boolean values (from `bool`)
- `DATE` - Date values (from `date`)
- `DATETIME` - Date and time values (from `datetime`)
- `EMAIL` - Email addresses (explicit)
- `URL` - Web URLs (explicit) 
- `PHONE` - Phone numbers (explicit)
- `SELECT` - Single select dropdown (from `Enum`)
- `MULTI_SELECT` - Multiple select (explicit)
- `AUTO_NUMBER` - Auto-incrementing numbers
- `CREATED_TIME` - Record creation timestamp
- `MODIFIED_TIME` - Record modification timestamp
- And more...

### 🔄 Automatic Type Detection

The library automatically maps Python types to AirTable field types:

```python
class AutoMappedModel(AirTableModel):
    # These types are automatically detected:
    text_field: str                    # -> SINGLE_LINE_TEXT
    number_field: int                  # -> NUMBER  
    decimal_field: float               # -> NUMBER
    flag_field: bool                   # -> CHECKBOX
    date_field: date                   # -> DATE
    timestamp_field: datetime          # -> DATETIME
    priority: MyEnum                   # -> SELECT (with enum choices)
    
    # These require explicit field types:
    email: str = AirTableField(airtable_field_type=AirTableFieldType.EMAIL)
    website: str = AirTableField(airtable_field_type=AirTableFieldType.URL)
    phone: str = AirTableField(airtable_field_type=AirTableFieldType.PHONE)
```

## 🚨 Error Handling

The library provides specific exceptions for different error conditions:

```python
from pydantic_airtable.exceptions import (
    AirTableError,
    RecordNotFoundError,
    ValidationError,
    APIError,
    ConfigurationError
)

try:
    user = User.get("invalid_id")
except RecordNotFoundError:
    print("User not found")
except APIError as e:
    print(f"API Error: {e.message} (Status: {e.status_code})")
```

## ⚡ Performance Tips

1. **Batch Operations**: Use `bulk_create()` for creating multiple records
2. **Field Selection**: Specify `fields` parameter in queries to reduce data transfer
3. **Pagination**: Use `max_records` and `page_size` for large datasets
4. **Rate Limits**: The library handles rate limiting automatically with exponential backoff
5. **🆕 Schema Validation**: Use `validate_table_schema()` to catch mismatches early
6. **🆕 Incremental Sync**: Use `sync_table_schema()` to add fields without recreating tables

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Run the example demos (require environment variables):

```bash
# Basic CRUD operations
python examples/simple_usage/simple_usage.py

# AI agent task management
python examples/agent_tasks/agent_tasks.py

# 🆕 Table and base management
python examples/table_management/table_management.py

# 🤖 Agentic Researcher (requires OpenAI API key)
python examples/agentic_researcher/agentic_researcher.py --demo
python examples/agentic_researcher/agentic_researcher.py --interactive
```

**📚 Detailed Examples**: See [examples/README.md](examples/README.md) for comprehensive documentation of each example with learning paths and troubleshooting guides.

## 📝 Configuration Options

### AirTableConfig Parameters

- `access_token`: AirTable Personal Access Token (PAT) - **REQUIRED** (or use `AIRTABLE_ACCESS_TOKEN` env var)
- `base_id`: AirTable Base ID (or use `AIRTABLE_BASE_ID` env var)  
- `table_name`: Name of the table in AirTable
- `api_key`: **DEPRECATED** - Use `access_token` instead. Will show deprecation warnings.

### AirTableField Parameters

- `airtable_field_name`: Custom field name in AirTable
- `airtable_field_type`: Specific AirTable field type
- `read_only`: Exclude from create/update operations
- All standard Pydantic Field parameters are supported

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋 Support

For questions, bug reports, or feature requests, please open an issue on the GitHub repository.

## 🔗 Related Projects

- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation using Python type hints
- [AirTable API](https://airtable.com/developers/web/api/introduction) - AirTable REST API documentation

## 🎯 What's New in v0.2.0

### 🆕 **Schema Management** 
- **Create AirTable tables** directly from Pydantic models
- **Automatic field type detection** from Python types
- **Enum support** for select fields with automatic choice generation
- **Schema validation** to ensure model-table compatibility

### 🏗️ **Base Management**
- **Create AirTable bases** programmatically 
- **List and manage** existing bases
- **Get base schemas** with full table and field information

### 🔄 **Schema Synchronization**
- **Sync models with tables** - add missing fields automatically
- **Validate schemas** to catch mismatches before runtime
- **Non-destructive updates** - only add fields, never remove data

### 🎛️ **Advanced Table Operations**
- **Update table schemas** with new fields
- **Delete tables** when needed
- **Full CRUD operations** on table structure

### 🔧 **Developer Experience**
- **Model-driven approach** - tables create themselves from models
- **Type-safe operations** with full Pydantic validation
- **Comprehensive error handling** with helpful messages
- **Backward compatibility** with existing v0.1.x code

### 📚 **New Examples**
- **`table_management.py`** - Complete schema management workflow
- **Base creation** examples with multiple tables
- **Schema sync** demonstrations
- **Model evolution** patterns

## 📁 **Complete Example Library**

The library now includes three comprehensive examples:

| Example | Description | Key Features |
|---------|-------------|--------------|
| **[`simple_usage/`](examples/simple_usage/)** | Basic CRUD operations | Model creation, querying, batch operations |
| **[`agent_tasks/`](examples/agent_tasks/)** | AI agent task management | Status tracking, metrics, business logic |
| **[`table_management/`](examples/table_management/)** | Schema management | Table creation, validation, synchronization |
| **[`agentic_researcher/`](examples/agentic_researcher/)** 🤖 | AI research assistant | Full AI workflow, base creation, Q&A system |

All based on AirTable's official APIs:
- [Create Table](https://airtable.com/developers/web/api/create-table)
- [Update Table](https://airtable.com/developers/web/api/update-table)  
- [Create Base](https://airtable.com/developers/web/api/create-base)
- [Get Base Schema](https://airtable.com/developers/web/api/get-base-schema)
- [List Bases](https://airtable.com/developers/web/api/list-bases)

---

**Made with ❤️ for seamless AirTable integration with Python**
