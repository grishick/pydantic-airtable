# Exceptions API Reference

API documentation for exception classes.

---

## Exception Hierarchy

```
AirTableError (base)
├── ConfigurationError
├── APIError
├── RecordNotFoundError
└── ValidationError (from Pydantic)
```

---

## AirTableError

Base exception for all library errors.

```python
class AirTableError(Exception):
    """Base exception for AirTable errors"""
    pass
```

### Usage

Catch all library exceptions:

```python
from pydantic_airtable import AirTableError

try:
    user = User.create(name="Alice")
except AirTableError as e:
    print(f"AirTable error: {e}")
```

---

## ConfigurationError

Raised for configuration-related issues.

```python
class ConfigurationError(AirTableError):
    """Configuration error"""
    pass
```

### Common Causes

- Missing `AIRTABLE_ACCESS_TOKEN`
- Missing `AIRTABLE_BASE_ID`
- Invalid token format (doesn't start with `pat_`)
- Invalid base ID format (doesn't start with `app`)
- No global configuration set

### Examples

```python
from pydantic_airtable import ConfigurationError, configure_from_env

try:
    configure_from_env()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # Example messages:
    # - "AirTable Personal Access Token is required"
    # - "AirTable Base ID is required"
    # - "Invalid access token format. Personal Access Tokens must start with 'pat_'"
```

### Handling

```python
from pydantic_airtable import ConfigurationError, AirTableConfig

def get_config():
    try:
        return AirTableConfig(
            access_token=os.getenv("AIRTABLE_ACCESS_TOKEN", ""),
            base_id=os.getenv("AIRTABLE_BASE_ID", "")
        )
    except ConfigurationError as e:
        print("Please set AIRTABLE_ACCESS_TOKEN and AIRTABLE_BASE_ID")
        print(f"Error: {e}")
        sys.exit(1)
```

---

## APIError

Raised for AirTable API errors.

```python
class APIError(AirTableError):
    """AirTable API error"""
    pass
```

### Common Causes

- Rate limiting (429)
- Permission denied (403)
- Table not found (404)
- Invalid field values (422)
- Network issues
- Server errors (500)

### Examples

```python
from pydantic_airtable import APIError

try:
    user = User.create(name="Alice", email="invalid-email")
except APIError as e:
    print(f"API error: {e}")
    # Example messages:
    # - "INVALID_VALUE_FOR_COLUMN: Invalid value for column"
    # - "TABLE_NOT_FOUND: Table 'Users' not found"
    # - "RATE_LIMIT_EXCEEDED: Too many requests"
```

### Handling

```python
from pydantic_airtable import APIError
import time

def create_with_retry(data, max_retries=3):
    for attempt in range(max_retries):
        try:
            return User.create(**data)
        except APIError as e:
            error_str = str(e).lower()
            
            if "rate_limit" in error_str:
                # Wait and retry for rate limits
                time.sleep(2 ** attempt)
                continue
            elif "not_found" in error_str:
                # Don't retry for not found
                raise
            elif attempt == max_retries - 1:
                raise
            else:
                time.sleep(1)
```

---

## RecordNotFoundError

Raised when a record doesn't exist.

```python
class RecordNotFoundError(AirTableError):
    """Record not found error"""
    pass
```

### When Raised

- `Model.get(invalid_id)` when record doesn't exist
- Accessing deleted record

### Examples

```python
from pydantic_airtable import RecordNotFoundError

try:
    user = User.get("recInvalidId")
except RecordNotFoundError as e:
    print(f"User not found: {e}")
```

### Handling

```python
from pydantic_airtable import RecordNotFoundError

def get_user_or_none(user_id: str):
    """Get user or return None"""
    try:
        return User.get(user_id)
    except RecordNotFoundError:
        return None

def get_user_or_create(user_id: str, default_data: dict):
    """Get user or create new one"""
    try:
        return User.get(user_id)
    except RecordNotFoundError:
        return User.create(**default_data)
```

---

## ValidationError

Pydantic's validation error, raised when data fails validation.

```python
from pydantic import ValidationError
```

### When Raised

- Invalid field values during `create()`
- Invalid values during assignment with `validate_assignment=True`
- Type conversion failures

### Examples

```python
from pydantic import ValidationError

try:
    user = User.create(name="", email="not-an-email")
except ValidationError as e:
    print("Validation errors:")
    for error in e.errors():
        print(f"  - {error['loc']}: {error['msg']}")
```

### Error Structure

```python
# ValidationError.errors() returns:
[
    {
        'type': 'string_too_short',
        'loc': ('name',),
        'msg': 'String should have at least 1 character',
        'input': '',
        'ctx': {'min_length': 1}
    },
    {
        'type': 'value_error',
        'loc': ('email',),
        'msg': 'value is not a valid email address',
        'input': 'not-an-email'
    }
]
```

---

## Error Handling Patterns

### Comprehensive Handler

```python
from pydantic_airtable import (
    AirTableError,
    APIError,
    ConfigurationError,
    RecordNotFoundError
)
from pydantic import ValidationError

def safe_create_user(data: dict):
    """Create user with comprehensive error handling"""
    try:
        return User.create(**data)
    
    except ValidationError as e:
        # Data validation failed
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        print(f"Validation errors: {', '.join(errors)}")
        return None
    
    except ConfigurationError as e:
        # Configuration issue
        print(f"Configuration error: {e}")
        print("Check your AIRTABLE_ACCESS_TOKEN and AIRTABLE_BASE_ID")
        return None
    
    except RecordNotFoundError as e:
        # Shouldn't happen on create, but handle anyway
        print(f"Record not found: {e}")
        return None
    
    except APIError as e:
        # AirTable API error
        print(f"AirTable API error: {e}")
        return None
    
    except AirTableError as e:
        # Catch-all for library errors
        print(f"AirTable error: {e}")
        return None
```

### Result Type Pattern

```python
from dataclasses import dataclass
from typing import Optional, TypeVar, Generic

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    success: bool
    value: Optional[T] = None
    error: Optional[str] = None
    error_type: Optional[str] = None

def create_user_safe(data: dict) -> Result[User]:
    try:
        user = User.create(**data)
        return Result(success=True, value=user)
    except ValidationError as e:
        return Result(
            success=False,
            error=str(e),
            error_type="validation"
        )
    except APIError as e:
        return Result(
            success=False,
            error=str(e),
            error_type="api"
        )
    except Exception as e:
        return Result(
            success=False,
            error=str(e),
            error_type="unknown"
        )

# Usage
result = create_user_safe({"name": "Alice", "email": "alice@example.com"})
if result.success:
    print(f"Created: {result.value.id}")
else:
    print(f"Error ({result.error_type}): {result.error}")
```

### Logging Pattern

```python
import logging

logger = logging.getLogger(__name__)

def logged_operation(operation_name: str):
    """Decorator for logging operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                logger.info(f"{operation_name} succeeded")
                return result
            except ValidationError as e:
                logger.warning(f"{operation_name} validation error: {e}")
                raise
            except APIError as e:
                logger.error(f"{operation_name} API error: {e}")
                raise
            except Exception as e:
                logger.exception(f"{operation_name} unexpected error")
                raise
        return wrapper
    return decorator

@logged_operation("create_user")
def create_user(name: str, email: str) -> User:
    return User.create(name=name, email=email)
```

---

## Importing Exceptions

```python
# Import all exceptions
from pydantic_airtable import (
    AirTableError,
    APIError,
    ConfigurationError,
    RecordNotFoundError,
    ValidationError  # Re-exported from pydantic_airtable
)

# Or import ValidationError from pydantic directly
from pydantic import ValidationError
```
