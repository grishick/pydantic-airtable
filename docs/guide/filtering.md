# Filtering & Queries

Learn how to efficiently query and filter records in Airtable.

---

## Basic Filtering

### Find by Field Value

Use `find_by()` to query records by field values:

```python
# Single field filter
active_users = User.find_by(is_active=True)

# Multiple field filter (AND)
active_admins = User.find_by(is_active=True, role="admin")
```

### Get First Match

Use `first()` to get a single record:

```python
# Returns instance or None
user = User.first(email="alice@example.com")

if user:
    print(f"Found: {user.name}")
```

### Get All Records

```python
# All records
all_users = User.all()

# With limit
top_10 = User.all(maxRecords=10)
```

---

## Filter Types

### String Equality

```python
# Exact match
users = User.find_by(name="Alice Johnson")
```

### Boolean Fields

```python
# True value
active = User.find_by(is_active=True)

# False value
inactive = User.find_by(is_active=False)
```

### Numeric Fields

```python
# Exact number
adults = User.find_by(age=18)
```

### Multiple Conditions

All conditions are combined with AND:

```python
# is_active=True AND role="admin" AND age=30
results = User.find_by(
    is_active=True,
    role="admin",
    age=30
)
```

---

## Advanced Filtering with Formulas

For complex queries, use Airtable formulas:

### Using filterByFormula

```python
# Greater than
results = User.all(filterByFormula="{age} > 25")

# Less than or equal
results = User.all(filterByFormula="{age} <= 30")

# Not equal
results = User.all(filterByFormula="{status} != 'inactive'")
```

### String Operations

```python
# Contains
results = User.all(
    filterByFormula="FIND('gmail', {email}) > 0"
)

# Starts with
results = User.all(
    filterByFormula="LEFT({name}, 1) = 'A'"
)

# Case-insensitive match
results = User.all(
    filterByFormula="LOWER({email}) = 'alice@example.com'"
)
```

### Logical Operators

```python
# AND
results = User.all(
    filterByFormula="AND({is_active}, {age} >= 18)"
)

# OR
results = User.all(
    filterByFormula="OR({role} = 'admin', {role} = 'moderator')"
)

# NOT
results = User.all(
    filterByFormula="NOT({is_archived})"
)

# Complex combination
results = User.all(
    filterByFormula="AND(OR({role}='admin', {role}='moderator'), {is_active})"
)
```

### Date Comparisons

```python
from datetime import datetime

# Records from today
today = datetime.now().strftime("%Y-%m-%d")
results = Task.all(
    filterByFormula=f"IS_SAME({{due_date}}, '{today}', 'day')"
)

# Records before a date
results = Task.all(
    filterByFormula="IS_BEFORE({due_date}, '2024-12-31')"
)

# Records in date range
results = Task.all(
    filterByFormula="AND(IS_AFTER({created_at}, '2024-01-01'), IS_BEFORE({created_at}, '2024-06-01'))"
)
```

### Empty/Non-Empty Checks

```python
# Field is empty
results = User.all(
    filterByFormula="{phone} = BLANK()"
)

# Field is not empty
results = User.all(
    filterByFormula="{phone} != BLANK()"
)

# Check for empty string
results = User.all(
    filterByFormula="LEN({notes}) > 0"
)
```

---

## Sorting Results

### Single Field Sort

```python
# Ascending (A-Z, 0-9)
users = User.all(
    sort=[{"field": "name", "direction": "asc"}]
)

# Descending (Z-A, 9-0)
users = User.all(
    sort=[{"field": "created_time", "direction": "desc"}]
)
```

### Multiple Field Sort

```python
# Sort by priority (desc), then name (asc)
tasks = Task.all(
    sort=[
        {"field": "priority", "direction": "desc"},
        {"field": "title", "direction": "asc"}
    ]
)
```

---

## Field Selection

### Retrieve Specific Fields

```python
# Only get name and email
users = User.all(
    fields=["name", "email"]
)
# Other fields will be None/default
```

---

## Pagination

### Using maxRecords

```python
# Get first 10 records
users = User.all(maxRecords=10)
```

### Manual Pagination

For large datasets, implement pagination:

```python
def get_all_users_paginated(page_size: int = 100):
    """Fetch all users with pagination"""
    all_users = []
    offset = None
    
    while True:
        params = {"pageSize": page_size}
        if offset:
            params["offset"] = offset
        
        # Note: This requires access to raw API response
        # The library handles pagination internally in most cases
        users = User.all(**params)
        all_users.extend(users)
        
        if len(users) < page_size:
            break
    
    return all_users
```

---

## Query Builder Pattern

Create reusable query builders:

```python
class UserQuery:
    """Fluent query builder for User model"""
    
    def __init__(self):
        self._filters = []
        self._sort = []
        self._limit = None
    
    def active(self):
        self._filters.append("{is_active}")
        return self
    
    def role(self, role: str):
        self._filters.append(f"{{role}} = '{role}'")
        return self
    
    def age_above(self, age: int):
        self._filters.append(f"{{age}} > {age}")
        return self
    
    def order_by(self, field: str, desc: bool = False):
        direction = "desc" if desc else "asc"
        self._sort.append({"field": field, "direction": direction})
        return self
    
    def limit(self, n: int):
        self._limit = n
        return self
    
    def execute(self):
        params = {}
        
        if self._filters:
            formula = "AND(" + ", ".join(self._filters) + ")"
            params["filterByFormula"] = formula
        
        if self._sort:
            params["sort"] = self._sort
        
        if self._limit:
            params["maxRecords"] = self._limit
        
        return User.all(**params)

# Usage
users = (UserQuery()
    .active()
    .role("admin")
    .age_above(25)
    .order_by("name")
    .limit(10)
    .execute())
```

---

## Common Query Patterns

### Find or None

```python
def find_user_by_email(email: str) -> Optional[User]:
    """Find user by email, return None if not found"""
    return User.first(email=email)
```

### Find or Raise

```python
from pydantic_airtable import RecordNotFoundError

def get_user_by_email(email: str) -> User:
    """Find user by email, raise if not found"""
    user = User.first(email=email)
    if not user:
        raise RecordNotFoundError(f"User with email {email} not found")
    return user
```

### Find with Default

```python
def get_user_or_default(email: str) -> User:
    """Find user by email, return default if not found"""
    user = User.first(email=email)
    if not user:
        return User(name="Unknown", email=email)
    return user
```

### Count Records

```python
def count_active_users() -> int:
    """Count active users"""
    return len(User.find_by(is_active=True))
```

### Check Existence

```python
def user_exists(email: str) -> bool:
    """Check if user with email exists"""
    return User.first(email=email) is not None
```

---

## Performance Tips

!!! tip "Query Optimization"
    
    **Use `find_by()` over filtering `all()`:**
    ```python
    # ❌ Fetches all, then filters in Python
    users = [u for u in User.all() if u.is_active]
    
    # ✅ Filters server-side
    users = User.find_by(is_active=True)
    ```

!!! tip "Limit Fields"
    
    **Only fetch fields you need:**
    ```python
    # ❌ Fetches all fields
    users = User.all()
    names = [u.name for u in users]
    
    # ✅ Only fetches name field
    users = User.all(fields=["name"])
    names = [u.name for u in users]
    ```

!!! tip "Use maxRecords"
    
    **Limit results when you don't need all:**
    ```python
    # ❌ Fetches all, takes first
    user = User.all()[0] if User.all() else None
    
    # ✅ Uses first() or maxRecords
    user = User.first()
    ```

---

## Airtable Formula Reference

Common functions for `filterByFormula`:

| Function | Description | Example |
|----------|-------------|---------|
| `AND()` | Logical AND | `AND({a}, {b})` |
| `OR()` | Logical OR | `OR({a}, {b})` |
| `NOT()` | Logical NOT | `NOT({a})` |
| `IF()` | Conditional | `IF({a}, 'yes', 'no')` |
| `FIND()` | Find substring | `FIND('text', {field})` |
| `LEN()` | String length | `LEN({field})` |
| `LOWER()` | Lowercase | `LOWER({field})` |
| `UPPER()` | Uppercase | `UPPER({field})` |
| `BLANK()` | Empty value | `{field} = BLANK()` |
| `IS_SAME()` | Date comparison | `IS_SAME({date}, TODAY())` |
| `IS_BEFORE()` | Date before | `IS_BEFORE({date}, '2024-01-01')` |
| `IS_AFTER()` | Date after | `IS_AFTER({date}, '2024-01-01')` |
| `TODAY()` | Current date | `{date} = TODAY()` |
| `NOW()` | Current datetime | `{datetime} < NOW()` |

---

## Next Steps

- [Batch Operations](batch-operations.md) - Work with multiple records
- [CRUD Operations](crud-operations.md) - Complete CRUD reference
- [Best Practices](../advanced/best-practices.md) - Production patterns

