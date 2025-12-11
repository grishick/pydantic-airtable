# Configuration

Learn how to configure Pydantic AirTable for different use cases and environments.

---

## Configuration Methods

Pydantic AirTable offers multiple ways to configure your connection:

1. **Environment Variables** - Best for production
2. **`.env` Files** - Best for development
3. **Explicit Configuration** - Best for multiple bases
4. **Per-Model Configuration** - Best for complex setups

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AIRTABLE_ACCESS_TOKEN` | Personal Access Token | `pat_abc123...` |
| `AIRTABLE_BASE_ID` | AirTable Base ID | `appXXXXXXXXXXXX` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AIRTABLE_TABLE_NAME` | Default table name | Model class name |

### Using Environment Variables

```python
from pydantic_airtable import configure_from_env

# Load from environment
configure_from_env()
```

---

## .env File Configuration

Create a `.env` file in your project root:

```env
# Required
AIRTABLE_ACCESS_TOKEN=pat_your_personal_access_token
AIRTABLE_BASE_ID=appYourBaseId

# Optional
AIRTABLE_TABLE_NAME=DefaultTable
```

The library automatically loads `.env` files using `python-dotenv`:

```python
from pydantic_airtable import configure_from_env

# Automatically loads .env file
configure_from_env()
```

!!! warning "Security"
    Add `.env` to your `.gitignore` to prevent committing secrets:
    ```
    .env
    .env.local
    .env.*.local
    ```

---

## Explicit Configuration

For more control, create configuration objects directly:

```python
from pydantic_airtable import AirTableConfig, set_global_config

# Create configuration
config = AirTableConfig(
    access_token="pat_your_token",
    base_id="appYourBaseId",
    table_name="DefaultTable"  # Optional
)

# Set as global default
set_global_config(config)
```

### Configuration with Overrides

Mix environment variables with explicit overrides:

```python
from pydantic_airtable import configure_from_env

# Load from env, but override specific values
configure_from_env(
    base_id="appDifferentBase"  # Override just the base
)
```

---

## Per-Model Configuration

### Using the Decorator

Specify configuration directly in the model decorator:

```python
from pydantic_airtable import airtable_model
from pydantic import BaseModel

@airtable_model(
    table_name="Users",
    access_token="pat_your_token",
    base_id="appYourBaseId"
)
class User(BaseModel):
    name: str
    email: str
```

### Using a Config Object

Pass a configuration object to the decorator:

```python
from pydantic_airtable import airtable_model, AirTableConfig
from pydantic import BaseModel

user_config = AirTableConfig(
    access_token="pat_user_token",
    base_id="app_user_base"
)

@airtable_model(config=user_config, table_name="Users")
class User(BaseModel):
    name: str
    email: str
```

---

## Multiple Bases

### Different Bases per Model

```python
from pydantic_airtable import airtable_model, AirTableConfig
from pydantic import BaseModel

# CRM Base
crm_config = AirTableConfig(
    access_token="pat_your_token",
    base_id="appCRMBase"
)

# Inventory Base  
inventory_config = AirTableConfig(
    access_token="pat_your_token",
    base_id="appInventoryBase"
)

@airtable_model(config=crm_config, table_name="Customers")
class Customer(BaseModel):
    name: str
    email: str

@airtable_model(config=inventory_config, table_name="Products")
class Product(BaseModel):
    name: str
    price: float
```

### Switching Bases Dynamically

```python
from pydantic_airtable import AirTableConfig

base_config = AirTableConfig(
    access_token="pat_your_token",
    base_id="appBaseOne"
)

# Create a new config for a different table
other_table_config = base_config.with_table("OtherTable")
```

---

## Configuration Priority

When multiple configuration sources exist, they're applied in this order (highest priority first):

1. **Per-model configuration** (decorator parameters)
2. **Explicit overrides** (passed to `configure_from_env()`)
3. **Environment variables**
4. **Global configuration** (set via `set_global_config()`)

```python
# Example: Environment has AIRTABLE_BASE_ID=appEnvBase

# This uses appEnvBase (from environment)
configure_from_env()

# This uses appOverrideBase (override wins)
configure_from_env(base_id="appOverrideBase")

# This model uses appModelBase (per-model wins)
@airtable_model(table_name="Users", base_id="appModelBase")
class User(BaseModel):
    name: str
```

---

## Accessing Current Configuration

### Get Global Config

```python
from pydantic_airtable import get_global_config

config = get_global_config()
print(f"Base ID: {config.base_id}")
print(f"Table: {config.table_name}")
```

### Get Model Config

```python
# Access a model's configuration
config = User._get_config()
print(f"User model base: {config.base_id}")
```

---

## Configuration Validation

The library validates configuration on creation:

```python
from pydantic_airtable import AirTableConfig, ConfigurationError

try:
    config = AirTableConfig(
        access_token="invalid_token",  # Doesn't start with 'pat_'
        base_id="appValidBase"
    )
except ConfigurationError as e:
    print(f"Invalid config: {e}")
    # Output: Invalid access token format. Personal Access Tokens must start with 'pat_'
```

### Validation Rules

| Field | Rule |
|-------|------|
| `access_token` | Must start with `pat_` |
| `base_id` | Must start with `app` |
| `table_name` | Optional, uses model name if not provided |

---

## Environment-Specific Configuration

### Development vs Production

```python
import os
from pydantic_airtable import AirTableConfig, set_global_config

environment = os.getenv("ENVIRONMENT", "development")

if environment == "production":
    config = AirTableConfig(
        access_token=os.getenv("PROD_AIRTABLE_TOKEN"),
        base_id=os.getenv("PROD_AIRTABLE_BASE")
    )
elif environment == "staging":
    config = AirTableConfig(
        access_token=os.getenv("STAGING_AIRTABLE_TOKEN"),
        base_id=os.getenv("STAGING_AIRTABLE_BASE")
    )
else:
    config = AirTableConfig(
        access_token=os.getenv("DEV_AIRTABLE_TOKEN"),
        base_id=os.getenv("DEV_AIRTABLE_BASE")
    )

set_global_config(config)
```

### Using Multiple .env Files

```bash
# .env.development
AIRTABLE_ACCESS_TOKEN=pat_dev_token
AIRTABLE_BASE_ID=appDevBase

# .env.production
AIRTABLE_ACCESS_TOKEN=pat_prod_token
AIRTABLE_BASE_ID=appProdBase
```

```python
import os
from dotenv import load_dotenv
from pydantic_airtable import configure_from_env

# Load environment-specific .env
env = os.getenv("ENVIRONMENT", "development")
load_dotenv(f".env.{env}")

configure_from_env()
```

---

## Best Practices

!!! success "Do"
    - Use environment variables in production
    - Use `.env` files for local development
    - Never commit credentials to version control
    - Use per-model config for multi-base setups
    - Validate configuration early in your application

!!! failure "Don't"
    - Hard-code credentials in source code
    - Share Personal Access Tokens between environments
    - Use overly broad PAT scopes

---

## Next Steps

- [Models](../guide/models.md) - Learn how to define models
- [Field Types](../guide/field-types.md) - Understand field type detection
- [Multiple Bases](../advanced/multiple-bases.md) - Advanced multi-base patterns
