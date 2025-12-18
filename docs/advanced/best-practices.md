# Best Practices

Production-ready patterns and recommendations for Pydantic Airtable applications.

---

## Configuration

### Environment Variables

```python
# ✅ Good: Use environment variables
from pydantic_airtable import configure_from_env
configure_from_env()

# ❌ Bad: Hard-coded credentials
config = AirtableConfig(
    access_token="pat_xxxxx",  # Never do this!
    base_id="appXXXX"
)
```

### Validate Early

```python
# ✅ Good: Validate configuration at startup
def initialize_app():
    try:
        configure_from_env()
        # Test connection
        _ = User.all(maxRecords=1)
        print("✅ Airtable connection verified")
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except APIError as e:
        print(f"❌ API error: {e}")
        sys.exit(1)
```

### Separate Environments

```python
# ✅ Good: Different bases per environment
import os

env = os.getenv("ENVIRONMENT", "development")

base_ids = {
    "development": "appDevBase",
    "staging": "appStagingBase",
    "production": "appProdBase"
}

config = AirtableConfig(
    access_token=os.getenv("AIRTABLE_ACCESS_TOKEN"),
    base_id=base_ids[env]
)
```

---

## Model Design

### Use Descriptive Names

```python
# ✅ Good: Descriptive field names enable smart detection
class Contact(BaseModel):
    full_name: str           # Clear purpose
    email_address: str       # Detected as EMAIL
    phone_number: str        # Detected as PHONE
    company_website: str     # Detected as URL

# ❌ Bad: Generic names
class Contact(BaseModel):
    field1: str
    field2: str
    data: str
```

### Define Types Explicitly When Needed

```python
# ✅ Good: Explicit when auto-detection isn't right
class Product(BaseModel):
    name: str
    
    # 'code' would be SINGLE_LINE_TEXT, we want to be explicit
    code: str = airtable_field(
        field_type=AirtableFieldType.SINGLE_LINE_TEXT,
        description="Product code"
    )
    
    # Status needs specific choices
    status: str = airtable_field(
        field_type=AirtableFieldType.SELECT,
        choices=["Draft", "Active", "Discontinued"]
    )
```

### Use Enums for Fixed Values

```python
# ✅ Good: Enums for fixed choices
class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Task(BaseModel):
    title: str
    priority: Priority = Priority.MEDIUM

# ❌ Bad: String with no validation
class Task(BaseModel):
    title: str
    priority: str = "medium"  # No validation, typos possible
```

### Add Pydantic Validation

```python
# ✅ Good: Validate before sending to Airtable
from pydantic import field_validator, Field

class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str
    age: Optional[int] = Field(default=None, ge=0, le=150)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()
```

---

## Query Optimization

### Use Server-Side Filtering

```python
# ✅ Good: Filter on the server
active_users = User.find_by(is_active=True)

# ❌ Bad: Fetch all, filter in Python
all_users = User.all()
active_users = [u for u in all_users if u.is_active]
```

### Limit Returned Fields

```python
# ✅ Good: Only fetch needed fields
users = User.all(fields=["name", "email"])

# ❌ Bad: Fetch everything when you only need names
users = User.all()
names = [u.name for u in users]
```

### Use Pagination for Large Datasets

```python
# ✅ Good: Limit results
recent_users = User.all(
    maxRecords=100,
    sort=[{"field": "created_time", "direction": "desc"}]
)

# ❌ Bad: Fetch unlimited results
all_users = User.all()  # Could be thousands
```

---

## Error Handling

### Handle Specific Exceptions

```python
# ✅ Good: Specific exception handling
from pydantic_airtable import APIError, RecordNotFoundError
from pydantic import ValidationError

try:
    user = User.get(user_id)
except RecordNotFoundError:
    return None
except APIError as e:
    logger.error(f"API error: {e}")
    raise
except ValidationError as e:
    logger.error(f"Validation error: {e}")
    raise

# ❌ Bad: Catch-all exception
try:
    user = User.get(user_id)
except Exception:
    return None  # Hides real errors
```

### Implement Retry Logic

```python
# ✅ Good: Retry transient failures
import time

def get_user_with_retry(user_id: str, max_retries: int = 3) -> User:
    for attempt in range(max_retries):
        try:
            return User.get(user_id)
        except APIError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

### Log Errors with Context

```python
# ✅ Good: Contextual logging
import logging

logger = logging.getLogger(__name__)

def create_user(data: dict) -> Optional[User]:
    try:
        return User.create(**data)
    except APIError as e:
        logger.error(
            "Failed to create user",
            extra={
                "email": data.get("email"),
                "error": str(e)
            }
        )
        return None
```

---

## Batch Operations

### Use Bulk Methods

```python
# ✅ Good: Bulk create
users = User.bulk_create([
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
])

# ❌ Bad: Individual creates in a loop
for data in users_data:
    User.create(**data)  # Slow, many API calls
```

### Process in Batches

```python
# ✅ Good: Process large datasets in batches
def process_large_dataset(data: list, batch_size: int = 100):
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        User.bulk_create(batch)
        time.sleep(0.5)  # Respect rate limits
```

### Handle Partial Failures

```python
# ✅ Good: Track successes and failures
def bulk_create_safe(data_list: list) -> dict:
    created = []
    failed = []
    
    for data in data_list:
        try:
            user = User.create(**data)
            created.append(user)
        except Exception as e:
            failed.append({"data": data, "error": str(e)})
    
    return {"created": created, "failed": failed}
```

---

## Table Management

### Create Tables Programmatically

```python
# ✅ Good: Tables as code
def setup_database():
    """Create all tables from models"""
    models = [User, Task, Project, Comment]
    
    for model in models:
        try:
            model.create_table()
            print(f"✅ Created {model.__name__}")
        except APIError as e:
            if "already exists" in str(e).lower():
                print(f"ℹ️ {model.__name__} already exists")
            else:
                raise
```

### Schema Migrations

```python
# ✅ Good: Track schema versions
def migrate_to_v2():
    """Add new fields for v2"""
    # New model with additional fields
    @airtable_model(table_name="Users")
    class UserV2(BaseModel):
        name: str
        email: str
        phone: Optional[str] = None  # New in v2
    
    result = UserV2.sync_table(create_missing_fields=True)
    print(f"Added fields: {result['fields_created']}")
```

---

## Security

### Protect Credentials

```python
# ✅ Good: Use .env files
# .env (never committed)
AIRTABLE_ACCESS_TOKEN=pat_xxxxx
AIRTABLE_BASE_ID=appXXXX

# .gitignore
.env
.env.*
```

### Minimal Permissions

```python
# ✅ Good: Use minimal PAT scopes
# - Only grant access to needed bases
# - Only grant read if write not needed
# - Rotate tokens periodically
```

### Don't Log Sensitive Data

```python
# ✅ Good: Redact sensitive info
def log_user_operation(user: User, operation: str):
    logger.info(f"{operation}: user_id={user.id}")

# ❌ Bad: Logging sensitive data
def log_user_operation(user: User, operation: str):
    logger.info(f"{operation}: {user.model_dump()}")  # Logs email, etc.
```

---

## Testing

### Use Test Bases

```python
# ✅ Good: Separate test base
@pytest.fixture
def test_config():
    return AirtableConfig(
        access_token=os.getenv("TEST_AIRTABLE_TOKEN"),
        base_id=os.getenv("TEST_AIRTABLE_BASE")
    )
```

### Clean Up Test Data

```python
# ✅ Good: Clean up after tests
@pytest.fixture
def test_user(test_model):
    user = test_model.create(name="Test", email="test@example.com")
    yield user
    user.delete()  # Cleanup
```

### Mock When Appropriate

```python
# ✅ Good: Mock for unit tests
from unittest.mock import patch

def test_user_logic():
    with patch.object(User, 'create') as mock_create:
        mock_create.return_value = User(
            id="rec123",
            name="Test",
            email="test@example.com"
        )
        # Test business logic without hitting API
```

---

## Performance

### Cache When Appropriate

```python
# ✅ Good: Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=100)
def get_user_by_email(email: str) -> Optional[User]:
    return User.first(email=email)

# Remember to invalidate cache on updates
def update_user(user: User):
    user.save()
    get_user_by_email.cache_clear()
```

### Avoid N+1 Queries

```python
# ✅ Good: Fetch related data efficiently
tasks = Task.all()
user_ids = {t.assignee_id for t in tasks if t.assignee_id}
users = {u.id: u for u in User.all() if u.id in user_ids}

for task in tasks:
    user = users.get(task.assignee_id)

# ❌ Bad: Query per task
for task in tasks:
    user = User.get(task.assignee_id)  # N+1 queries
```

---

## Documentation

### Document Models

```python
# ✅ Good: Document your models
@airtable_model(table_name="Users")
class User(BaseModel):
    """
    User account model.
    
    Represents a user in the system with their contact information
    and account status.
    
    Attributes:
        name: User's full name
        email: Primary email address (unique)
        is_active: Whether the account is active
    """
    name: str = Field(description="User's full name")
    email: str = Field(description="Primary email address")
    is_active: bool = Field(default=True, description="Account active status")
```

### Document Operations

```python
# ✅ Good: Document service functions
def deactivate_user(user_id: str) -> User:
    """
    Deactivate a user account.
    
    Args:
        user_id: Airtable record ID of the user
        
    Returns:
        Updated User instance
        
    Raises:
        RecordNotFoundError: If user doesn't exist
        APIError: If Airtable API call fails
    """
    user = User.get(user_id)
    user.is_active = False
    return user.save()
```

---

## Summary Checklist

- [ ] Use environment variables for credentials
- [ ] Validate configuration at startup
- [ ] Use descriptive field names
- [ ] Add Pydantic validation
- [ ] Use server-side filtering
- [ ] Handle specific exceptions
- [ ] Implement retry logic
- [ ] Use bulk operations
- [ ] Separate test environments
- [ ] Clean up test data
- [ ] Document models and operations

---

## Next Steps

- [Error Handling](error-handling.md) - Detailed error handling patterns
- [Multiple Bases](multiple-bases.md) - Multi-environment setups
- [Configuration](../getting-started/configuration.md) - Configuration options

