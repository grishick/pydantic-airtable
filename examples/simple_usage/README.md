# Simple Usage Example

This example demonstrates basic CRUD operations with the Pydantic AirTable library.

## 🎯 What This Example Shows

- **Basic Model Definition**: Creating a simple User model with various field types
- **CRUD Operations**: Create, read, update, delete operations
- **Querying**: Finding records by field values
- **Batch Operations**: Creating multiple records efficiently

## 🏃 Quick Start

1. **Set Environment Variables**:
   ```bash
   export AIRTABLE_ACCESS_TOKEN="pat_your_personal_access_token"
   export AIRTABLE_BASE_ID="app_your_base_id"
   ```

2. **Run the Example**:
   ```bash
   python simple_usage.py
   ```

## 📋 What It Does

1. **Creates a User model** with fields like name, email, age, and active status
2. **Creates individual users** and shows their AirTable IDs
3. **Demonstrates querying** - finding active users, getting first user, etc.
4. **Shows batch operations** - creating multiple users at once
5. **Displays final statistics** - total user count and details

## 🔧 Model Structure

```python
class User(AirTableModel):
    name: str                    # -> singleLineText
    email: str                   # -> email
    age: Optional[int]           # -> number
    is_active: bool             # -> checkbox
```

## 💡 Key Learning Points

- **Automatic Type Mapping**: Python types automatically map to AirTable field types
- **Environment Variables**: Configuration through environment variables
- **Error Handling**: Graceful handling of missing credentials
- **Pydantic Validation**: Built-in validation for all field types

## 🚀 Next Steps

After running this example:
- Try modifying the User model with additional fields
- Experiment with different field types (dates, URLs, phone numbers)
- Add custom validation using Pydantic validators
- Explore the generated AirTable base to see your data

## 📚 Related Examples

- **[Agent Tasks](../agent_tasks/)**: More complex business logic with enums and status tracking
- **[Table Management](../table_management/)**: Creating tables and bases programmatically
- **[Agentic Researcher](../agentic_researcher/)**: AI-powered research with OpenAI integration

