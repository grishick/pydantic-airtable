# Error Handling

Learn how to handle errors effectively in Pydantic AirTable applications.

---

## Exception Hierarchy

Pydantic AirTable provides a structured exception hierarchy:

```
AirTableError (base)
├── ConfigurationError
├── APIError
├── RecordNotFoundError
└── ValidationError
```

---

## Exception Types

### AirTableError

Base exception for all library errors:

```python
from pydantic_airtable import AirTableError

try:
    # Any operation
    user = User.create(name="Alice")
except AirTableError as e:
    print(f"AirTable error: {e}")
```

### ConfigurationError

Raised for configuration issues:

```python
from pydantic_airtable import ConfigurationError

try:
    configure_from_env()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # Common causes:
    # - Missing AIRTABLE_ACCESS_TOKEN
    # - Missing AIRTABLE_BASE_ID
    # - Invalid token format
    # - Invalid base ID format
```

### APIError

Raised for AirTable API errors:

```python
from pydantic_airtable import APIError

try:
    user = User.create(name="Alice")
except APIError as e:
    print(f"API error: {e}")
    # Common causes:
    # - Rate limiting
    # - Permission denied
    # - Table not found
    # - Invalid field values
    # - Network issues
```

### RecordNotFoundError

Raised when a record doesn't exist:

```python
from pydantic_airtable import RecordNotFoundError

try:
    user = User.get("recInvalidId")
except RecordNotFoundError as e:
    print(f"Record not found: {e}")
```

### ValidationError

Raised for Pydantic validation errors:

```python
from pydantic import ValidationError

try:
    user = User.create(name="", email="invalid")
except ValidationError as e:
    print(f"Validation error: {e}")
    for error in e.errors():
        print(f"  - {error['loc']}: {error['msg']}")
```

---

## Basic Error Handling

### Try-Except Pattern

```python
from pydantic_airtable import (
    APIError,
    ConfigurationError,
    RecordNotFoundError
)
from pydantic import ValidationError

def create_user_safe(name: str, email: str) -> Optional[User]:
    """Create user with comprehensive error handling"""
    try:
        return User.create(name=name, email=email)
    
    except ValidationError as e:
        print(f"Invalid data: {e}")
        return None
    
    except ConfigurationError as e:
        print(f"Configuration issue: {e}")
        return None
    
    except APIError as e:
        print(f"AirTable API error: {e}")
        return None
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### Specific Exception Handling

```python
def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user with specific error handling"""
    try:
        return User.get(user_id)
    except RecordNotFoundError:
        return None
    except APIError as e:
        # Log and re-raise for other API errors
        logger.error(f"API error fetching user {user_id}: {e}")
        raise
```

---

## Retry Logic

### Simple Retry

```python
import time

def create_with_retry(data: dict, max_retries: int = 3) -> User:
    """Create user with retry logic"""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return User.create(**data)
        except APIError as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retry {attempt + 1} after {wait_time}s...")
                time.sleep(wait_time)
    
    raise last_error
```

### Retry Decorator

```python
import functools
import time
from typing import Type

def retry_on_error(
    max_retries: int = 3,
    exceptions: tuple = (APIError,),
    backoff: float = 2.0
):
    """Decorator for retry logic"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = backoff ** attempt
                        time.sleep(wait_time)
            
            raise last_error
        return wrapper
    return decorator

# Usage
@retry_on_error(max_retries=3)
def fetch_all_users():
    return User.all()
```

---

## Error Recovery

### Fallback Values

```python
def get_user_or_default(user_id: str) -> User:
    """Get user or return default"""
    try:
        return User.get(user_id)
    except RecordNotFoundError:
        return User(name="Unknown", email="unknown@example.com")
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Simple circuit breaker for API calls"""
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "half-open"
            else:
                raise APIError("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result
        
        except APIError as e:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = "open"
            
            raise

# Usage
breaker = CircuitBreaker()

def safe_fetch_users():
    return breaker.call(User.all)
```

---

## Logging Errors

### Basic Logging

```python
import logging

logger = logging.getLogger(__name__)

def create_user_logged(name: str, email: str) -> Optional[User]:
    """Create user with logging"""
    try:
        user = User.create(name=name, email=email)
        logger.info(f"Created user: {user.id}")
        return user
    
    except ValidationError as e:
        logger.warning(f"Validation failed for user {email}: {e}")
        return None
    
    except APIError as e:
        logger.error(f"API error creating user {email}: {e}")
        return None
    
    except Exception as e:
        logger.exception(f"Unexpected error creating user {email}")
        return None
```

### Structured Logging

```python
import json
import logging

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_error(self, operation: str, error: Exception, **context):
        log_data = {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            **context
        }
        self.logger.error(json.dumps(log_data))

# Usage
slogger = StructuredLogger(__name__)

try:
    user = User.create(name="Alice", email="alice@example.com")
except Exception as e:
    slogger.log_error(
        "create_user",
        e,
        user_email="alice@example.com"
    )
```

---

## Custom Exceptions

### Application-Specific Exceptions

```python
class UserServiceError(Exception):
    """Base exception for user service"""
    pass

class UserNotFoundError(UserServiceError):
    """User not found in system"""
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"User not found: {identifier}")

class UserCreationError(UserServiceError):
    """Failed to create user"""
    def __init__(self, email: str, reason: str):
        self.email = email
        self.reason = reason
        super().__init__(f"Failed to create user {email}: {reason}")

# Usage
def get_user(email: str) -> User:
    user = User.first(email=email)
    if not user:
        raise UserNotFoundError(email)
    return user

def create_user(name: str, email: str) -> User:
    try:
        return User.create(name=name, email=email)
    except ValidationError as e:
        raise UserCreationError(email, f"Invalid data: {e}")
    except APIError as e:
        raise UserCreationError(email, f"API error: {e}")
```

---

## Error Handling Patterns

### Result Type Pattern

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    """Result type for operations that can fail"""
    success: bool
    value: Optional[T] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, value: T) -> 'Result[T]':
        return cls(success=True, value=value)
    
    @classmethod
    def fail(cls, error: str) -> 'Result[T]':
        return cls(success=False, error=error)

def create_user_result(name: str, email: str) -> Result[User]:
    """Create user returning Result type"""
    try:
        user = User.create(name=name, email=email)
        return Result.ok(user)
    except ValidationError as e:
        return Result.fail(f"Validation error: {e}")
    except APIError as e:
        return Result.fail(f"API error: {e}")

# Usage
result = create_user_result("Alice", "alice@example.com")

if result.success:
    print(f"Created: {result.value.id}")
else:
    print(f"Failed: {result.error}")
```

### Error Aggregation

```python
@dataclass
class BatchResult:
    """Result of batch operation"""
    successful: list
    failed: list[tuple[dict, str]]  # (data, error_message)
    
    @property
    def success_count(self) -> int:
        return len(self.successful)
    
    @property
    def failure_count(self) -> int:
        return len(self.failed)
    
    @property
    def all_successful(self) -> bool:
        return len(self.failed) == 0

def bulk_create_with_errors(data_list: list[dict]) -> BatchResult:
    """Bulk create capturing all errors"""
    successful = []
    failed = []
    
    for data in data_list:
        try:
            user = User.create(**data)
            successful.append(user)
        except Exception as e:
            failed.append((data, str(e)))
    
    return BatchResult(successful=successful, failed=failed)

# Usage
result = bulk_create_with_errors(users_data)
print(f"Created: {result.success_count}")
print(f"Failed: {result.failure_count}")

for data, error in result.failed:
    print(f"  - {data['email']}: {error}")
```

---

## Best Practices

!!! success "Do"
    - Catch specific exceptions, not bare `Exception`
    - Log errors with context
    - Implement retry logic for transient failures
    - Use custom exceptions for business logic
    - Provide meaningful error messages

!!! failure "Don't"
    - Silently swallow exceptions
    - Expose internal errors to users
    - Retry indefinitely
    - Ignore validation errors

---

## Next Steps

- [Best Practices](best-practices.md) - Production patterns
- [CRUD Operations](../guide/crud-operations.md) - Operations that may error
- [Configuration](../getting-started/configuration.md) - Prevent configuration errors

