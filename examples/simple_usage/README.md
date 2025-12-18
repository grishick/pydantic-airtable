# 🚀 Simple Usage Example

This example demonstrates the core features of pydantic-airtable with a clean, intuitive API.

## ✨ What Makes This Simple

```python
from pydantic_airtable import airtable_model, configure_from_env
from pydantic import BaseModel

configure_from_env()  # Auto-loads from .env

@airtable_model(table_name="Users")
class User(BaseModel):
    name: str                    # Auto-detects as SINGLE_LINE_TEXT
    email: str                   # Auto-detects as EMAIL  
    age: Optional[int] = None    # Auto-detects as NUMBER
    is_active: bool = True       # Auto-detects as CHECKBOX
```

Just **8 lines of code** to get a fully functional Airtable integration!

## 🏃 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```env
   AIRTABLE_ACCESS_TOKEN=pat_your_personal_access_token
   AIRTABLE_BASE_ID=app_your_base_id
   ```

3. **Get your credentials:**
   - **Personal Access Token**: Visit [Airtable Developer Hub](https://airtable.com/developers/web/api/authentication)
   - **Base ID**: Found in your Airtable base URL or API documentation

4. **Run the example:**
   ```bash
   python simple_usage.py
   ```

   **Note**: If the "Users" table doesn't exist in your base, the script will offer to create it automatically!

## 📋 What the Example Demonstrates

1. **Environment-based configuration** from `.env` files
2. **Field type detection** - no manual type specification needed
3. **Automatic table creation** if the table doesn't exist
4. **Clean CRUD operations** with intuitive methods
5. **Simple filtering** with `find_by()` and `first()`
6. **Batch operations** with `bulk_create()`
7. **Table management** with `sync_table()`

## 🔧 Model Structure

```python
@airtable_model(table_name="Users")
class User(BaseModel):
    name: str                    # -> singleLineText
    email: str                   # -> email (detected from field name!)
    age: Optional[int] = None    # -> number
    is_active: bool = True       # -> checkbox
    bio: Optional[str] = airtable_field(
        field_type=AirtableFieldType.LONG_TEXT  # explicit override
    )
```

## 🧠 Field Type Detection

The system automatically detects Airtable field types:

| Python Declaration | Detected Type | Reason |
|--------------------|---------------|--------|
| `email: str` | EMAIL | Field name contains "email" |
| `phone: str` | PHONE | Field name contains "phone" |  
| `website: str` | URL | Field name contains "website" |
| `description: str` | LONG_TEXT | Field name suggests long text |
| `price: float` | CURRENCY | Field name suggests money |
| `completion_rate: float` | PERCENT | Field name suggests percentage |
| `is_active: bool` | CHECKBOX | Boolean type |
| `created_at: datetime` | DATETIME | DateTime type |
| `Priority: Enum` | SELECT | Enum type |

## 🛠️ Automatic Table Management

The example includes table management:

1. **Table Detection**: Automatically checks if the "Users" table exists
2. **Interactive Creation**: Creates tables from model definitions if needed
3. **Schema Generation**: Maps Python types to appropriate Airtable field types
4. **Field Mapping**: Handles the conversion between Python and Airtable field names

### Example Flow

```
🔍 Ensuring Users table exists...
🔧 Creating Users table from model...
✅ Users table created successfully!

==================================================
🚀 Starting CRUD operations...
1️⃣ Creating a new user...
✅ Created user: Alice Johnson (ID: recXXXXX)
```

This eliminates the need to manually create tables in Airtable before running the script!

## 💡 Key Learning Points

- **Field Type Mapping**: Python types automatically map to Airtable field types
- **Environment Configuration**: Simple setup through `.env` files
- **Automatic Table Creation**: The script can create missing tables from Pydantic models
- **Clean CRUD Operations**: Intuitive methods that work as expected
- **Intelligent Field Detection**: Minimal configuration required
- **Error Handling**: Helpful error messages with clear solutions

## 🔒 Security Notes

- ⚠️ **Never commit `.env` files to version control** - they contain sensitive credentials
- ✅ **Use Personal Access Tokens (PATs)** - the modern Airtable authentication method
- ✅ **Limit PAT permissions** to only required scopes and bases
- 📁 **The `.gitignore` already excludes `.env` files** for your security

## 🚀 Advanced Usage

### Custom Field Configuration

```python
from pydantic_airtable import airtable_field, AirtableFieldType

@airtable_model(table_name="Projects")
class Project(BaseModel):
    name: str  # Auto-detected
    
    # Override auto-detection
    status: str = airtable_field(
        field_type=AirtableFieldType.SELECT,
        choices=["Planning", "In Progress", "Done"]
    )
    
    # Custom Airtable field name
    description: str = airtable_field(
        field_name="Project Description"
    )
```

### Multiple Base Configuration

```python
# Per-model configuration
@airtable_model(
    table_name="Tasks",
    access_token="pat_task_token",
    base_id="app_task_base"
)
class Task(BaseModel):
    title: str
    completed: bool = False
```

## 🎯 Common Use Cases

### Task Management
```python
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    title: str
    completed: bool = False
    priority: str = "Medium"
    due_date: Optional[datetime] = None

# Usage
Task.create_table()
task = Task.create(title="Finish documentation", priority="High")
incomplete_tasks = Task.find_by(completed=False)
```

### Contact Management
```python
@airtable_model(table_name="Contacts") 
class Contact(BaseModel):
    name: str
    email: str          # Auto-detects as EMAIL
    phone: str          # Auto-detects as PHONE
    company: Optional[str] = None
    notes: Optional[str] = None  # Auto-detects as LONG_TEXT

# Usage
contact = Contact.create(
    name="John Doe",
    email="john@example.com", 
    phone="555-0123"
)
```

## 📊 Performance Tips

- Use `bulk_create()` for creating multiple records efficiently
- Use `find_by()` for filtered queries instead of filtering all results
- Set up indexes in Airtable for frequently queried fields
- Cache model instances when you need to access them multiple times

## 🚀 Next Steps

After running this example, try these advanced examples:

- **[Table Management](../table_management/)**: Advanced schema management and field operations
- **[Agentic Researcher](../agentic_researcher/)**: AI-powered research system using OpenAI integration

## 🎉 Summary

This simple example shows how pydantic-airtable makes Airtable integration:

- **Intuitive**: Just like working with regular Pydantic models
- **Automatic**: Field type detection reduces configuration
- **Flexible**: Easy to override defaults when needed  
- **Reliable**: Built-in error handling and validation
- **Secure**: Environment-based configuration keeps credentials safe

Experience the future of Airtable integration! 🌟