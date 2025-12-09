# 📚 Pydantic AirTable Examples

This directory contains comprehensive examples demonstrating the capabilities of pydantic-airtable.

## 🚀 Quick Start Examples

### [Simple Usage](./simple_usage/)
**Perfect for beginners** - Shows the core features in just 8 lines of code!

```python
@airtable_model(table_name="Users")
class User(BaseModel):
    name: str        # Auto-detects as SINGLE_LINE_TEXT
    email: str       # Auto-detects as EMAIL
    age: Optional[int] = None  # Auto-detects as NUMBER
```

**What you'll learn:**
- Smart field type detection
- Automatic table creation
- Basic CRUD operations
- Environment-based configuration

**Run it:**
```bash
cd simple_usage
pip install -r requirements.txt
python simple_usage.py
```

---

## 🏗️ Advanced Examples

### [Table Management](./table_management/)
**Advanced schema management** - Learn to manage complex table structures and relationships.

**What you'll learn:**
- Creating tables from Pydantic models
- Field type customization and overrides
- Base and table schema management
- Synchronizing model changes to AirTable
- Handling complex data types (Enums, nested structures)

**Features demonstrated:**
- Multiple model types (Task, User, Project)
- Custom field configurations
- Table synchronization
- Base-level operations

**Run it:**
```bash
cd table_management
pip install -r requirements.txt
python table_management.py
```

---

### [Agentic Researcher](./agentic_researcher/)
**AI-powered research system** - A complete application integrating OpenAI, web search, and AirTable.

**What you'll learn:**
- Complex multi-model applications
- AI integration with OpenAI GPT-4
- Real-time web search integration
- Interactive command-line interfaces
- YAML-based prompt management
- Async operations and error handling

**Features:**
- 🤖 AI-powered research task planning
- 🔍 Real web search using DuckDuckGo
- 📊 Progress tracking and analytics
- ❓ Interactive Q&A about research
- 📋 Comprehensive result management

**Run it:**
```bash
cd agentic_researcher
pip install -r requirements.txt
python agentic_researcher.py
```

---

## 🛠️ Setup Instructions

### 1. Prerequisites
All examples require:
```bash
# Python 3.8+
python --version

# AirTable credentials
# Get your Personal Access Token: https://airtable.com/developers/web/api/authentication
```

### 2. Environment Setup
Create a `.env` file in each example directory:
```env
AIRTABLE_ACCESS_TOKEN=pat_your_personal_access_token
AIRTABLE_BASE_ID=app_your_base_id
```

For the Agentic Researcher, also add:
```env
OPENAI_API_KEY=sk_your_openai_api_key
```

### 3. Installation
Each example has its own `requirements.txt`:
```bash
cd [example-directory]
pip install -r requirements.txt
```

## 📖 Learning Path

**Recommended order for learning:**

1. **[Simple Usage](./simple_usage/)** - Start here to understand the basics
2. **[Table Management](./table_management/)** - Learn advanced schema management
3. **[Agentic Researcher](./agentic_researcher/)** - See a real-world application

## 🎯 Common Use Cases by Example

| Use Case | Example | Key Features |
|----------|---------|-------------|
| **User Management** | Simple Usage | Basic CRUD, field detection |
| **Task Tracking** | Table Management | Status enums, priorities, dates |
| **CRM System** | Table Management | Contact info, relationships |
| **Content Management** | Table Management | Rich text, attachments |
| **AI Applications** | Agentic Researcher | OpenAI integration, complex workflows |
| **Research Tools** | Agentic Researcher | Web scraping, data analysis |
| **Automation Systems** | Agentic Researcher | Multi-step processes, progress tracking |

## 💡 Tips for Success

### Field Type Detection
The library automatically detects field types from naming patterns:
- `email` → EMAIL
- `phone` → PHONE  
- `website` → URL
- `description` → LONG_TEXT
- `price` → CURRENCY
- `rate` → PERCENT

### Performance Optimization
- Use `bulk_create()` for multiple records
- Use `find_by()` for filtered queries
- Cache model instances when possible
- Set up AirTable indexes for frequent queries

### Error Handling
```python
try:
    user = User.create(name="Alice", email="alice@example.com")
except APIError as e:
    print(f"AirTable API error: {e}")
except ValidationError as e:
    print(f"Data validation error: {e}")
```

### Testing
```python
# Setup test configuration
configure_from_env(
    access_token="pat_test_token",
    base_id="app_test_base"
)

# Test your models
def test_user_creation():
    user = User.create(name="Test", email="test@example.com")
    assert user.id is not None
    user.delete()  # Cleanup
```

## 🔧 Troubleshooting

### Common Issues

**Missing credentials:**
```bash
# Check your .env file
cat .env

# Verify environment variables are loaded
python -c "import os; print(os.getenv('AIRTABLE_ACCESS_TOKEN'))"
```

**Table not found:**
```python
# Create table from model
User.create_table()

# Or check if it exists
try:
    users = User.all()
    print("Table exists")
except APIError:
    print("Table needs to be created")
```

**Import errors:**
```bash
# Install package in development mode
pip install -e ../../

# Check dependencies
pip list | grep pydantic
```

### Getting Help

1. **Check the logs** - All examples include detailed error messages
2. **Review the model definitions** - Ensure field types are correct
3. **Verify AirTable permissions** - Your PAT needs appropriate scopes
4. **Test with simple examples first** - Start with Simple Usage

## 🚀 Next Steps

After running these examples:

1. **Explore the source code** - Understand how each feature works
2. **Modify the examples** - Try adding your own fields and models
3. **Build your own application** - Use the examples as templates
4. **Share your creations** - Contribute back to the community!

## 📚 Additional Resources

- **[Main Documentation](../README.md)** - Complete API reference
- **[AirTable API Docs](https://airtable.com/developers/web/api/introduction)** - Official AirTable documentation
- **[Pydantic Docs](https://pydantic.dev/)** - Learn more about Pydantic models

---

**Happy coding! 🎉**

*These examples showcase the power and simplicity of pydantic-airtable. From basic CRUD to AI-powered applications, see how easy it is to build with AirTable.*