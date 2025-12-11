# Configuration API Reference

API documentation for configuration classes and functions.

---

## AirTableConfig

Configuration dataclass for AirTable connections.

```python
@dataclass
class AirTableConfig:
    access_token: str
    base_id: str
    table_name: Optional[str] = None
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `access_token` | `str` | Yes | Personal Access Token (must start with `pat_`) |
| `base_id` | `str` | Yes | Base ID (must start with `app`) |
| `table_name` | `str` | No | Default table name |

### Constructor

```python
config = AirTableConfig(
    access_token="pat_xxx",
    base_id="appXXX",
    table_name="Users"  # Optional
)
```

### Validation

The constructor validates:

- `access_token` must start with `pat_`
- `base_id` must start with `app`

Raises `ConfigurationError` if validation fails.

### Methods

#### from_env

Create configuration from environment variables.

```python
@classmethod
def from_env(
    cls,
    access_token: Optional[str] = None,
    base_id: Optional[str] = None,
    table_name: Optional[str] = None,
    env_prefix: str = "AIRTABLE_"
) -> 'AirTableConfig'
```

**Parameters:**
- `access_token`: Override for token (uses env if not provided)
- `base_id`: Override for base ID (uses env if not provided)
- `table_name`: Override for table name (uses env if not provided)
- `env_prefix`: Environment variable prefix (default: `"AIRTABLE_"`)

**Environment Variables:**
- `AIRTABLE_ACCESS_TOKEN`
- `AIRTABLE_BASE_ID`
- `AIRTABLE_TABLE_NAME` (optional)

**Example:**
```python
# From environment only
config = AirTableConfig.from_env()

# With overrides
config = AirTableConfig.from_env(
    base_id="appDifferentBase"
)

# Custom prefix
config = AirTableConfig.from_env(env_prefix="MY_APP_")
# Uses MY_APP_ACCESS_TOKEN, MY_APP_BASE_ID, etc.
```

---

#### with_table

Create a new config with a different table name.

```python
def with_table(self, table_name: str) -> 'AirTableConfig'
```

**Parameters:**
- `table_name`: New table name

**Returns:** New `AirTableConfig` instance

**Example:**
```python
base_config = AirTableConfig(
    access_token="pat_xxx",
    base_id="appXXX"
)

users_config = base_config.with_table("Users")
tasks_config = base_config.with_table("Tasks")
```

---

#### validate_table_name

Validate and return table name.

```python
def validate_table_name(self, table_name: Optional[str] = None) -> str
```

**Parameters:**
- `table_name`: Table name to validate (uses config default if None)

**Returns:** Validated table name

**Raises:** `ConfigurationError` if no table name available

---

## Configuration Functions

### configure_from_env

Load configuration from environment and set as global.

```python
def configure_from_env(**overrides) -> AirTableConfig
```

**Parameters:**
- `**overrides`: Override specific configuration values
  - `access_token`: Override token
  - `base_id`: Override base ID
  - `table_name`: Override table name

**Returns:** Created `AirTableConfig` (also set as global)

**Example:**
```python
from pydantic_airtable import configure_from_env

# Basic usage
configure_from_env()

# With overrides
configure_from_env(
    base_id="appOverrideBase"
)
```

---

### set_global_config

Set global configuration.

```python
def set_global_config(config: AirTableConfig) -> None
```

**Parameters:**
- `config`: Configuration to set as global

**Example:**
```python
from pydantic_airtable import AirTableConfig, set_global_config

config = AirTableConfig(
    access_token="pat_xxx",
    base_id="appXXX"
)
set_global_config(config)
```

---

### get_global_config

Get current global configuration.

```python
def get_global_config() -> AirTableConfig
```

**Returns:** Global `AirTableConfig` instance

**Raises:** `ConfigurationError` if no global config set

**Example:**
```python
from pydantic_airtable import get_global_config

config = get_global_config()
print(f"Base: {config.base_id}")
```

---

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `AIRTABLE_ACCESS_TOKEN` | Personal Access Token | `pat_abc123...` |
| `AIRTABLE_BASE_ID` | AirTable Base ID | `appXXXXXXXXXXXX` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `AIRTABLE_TABLE_NAME` | Default table name | Model class name |

### .env File

```env
# .env
AIRTABLE_ACCESS_TOKEN=pat_your_token_here
AIRTABLE_BASE_ID=appYourBaseIdHere
AIRTABLE_TABLE_NAME=DefaultTable
```

---

## Configuration Priority

When multiple sources exist, priority (highest first):

1. Per-model configuration (decorator parameters)
2. Explicit overrides (`configure_from_env(**overrides)`)
3. Environment variables
4. Global configuration (`set_global_config()`)

**Example:**
```python
# Environment: AIRTABLE_BASE_ID=appEnvBase

# Uses appEnvBase
configure_from_env()

# Uses appOverride (override wins)
configure_from_env(base_id="appOverride")

# Uses appModelBase (per-model wins)
@airtable_model(table_name="Users", base_id="appModelBase")
class User(BaseModel):
    name: str
```

---

## Usage Examples

### Basic Setup

```python
from pydantic_airtable import configure_from_env

# Load from .env file
configure_from_env()
```

### Multi-Environment

```python
import os
from pydantic_airtable import AirTableConfig, set_global_config

env = os.getenv("ENVIRONMENT", "development")

configs = {
    "development": AirTableConfig(
        access_token=os.getenv("DEV_TOKEN"),
        base_id=os.getenv("DEV_BASE")
    ),
    "production": AirTableConfig(
        access_token=os.getenv("PROD_TOKEN"),
        base_id=os.getenv("PROD_BASE")
    )
}

set_global_config(configs[env])
```

### Multiple Bases

```python
from pydantic_airtable import AirTableConfig, airtable_model
from pydantic import BaseModel

crm_config = AirTableConfig(
    access_token="pat_xxx",
    base_id="appCRMBase"
)

inventory_config = AirTableConfig(
    access_token="pat_xxx",
    base_id="appInventoryBase"
)

@airtable_model(config=crm_config, table_name="Customers")
class Customer(BaseModel):
    name: str

@airtable_model(config=inventory_config, table_name="Products")
class Product(BaseModel):
    name: str
```
