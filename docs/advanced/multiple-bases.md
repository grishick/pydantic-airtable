# Multiple Bases

Learn how to work with multiple AirTable bases in a single application.

---

## Overview

Real-world applications often need to:

- Connect to multiple AirTable bases
- Use different credentials for different data
- Support multi-tenant architectures
- Separate development/staging/production data

---

## Per-Model Configuration

### Using Decorator Parameters

Specify credentials directly in the decorator:

```python
from pydantic_airtable import airtable_model
from pydantic import BaseModel

# CRM Base
@airtable_model(
    table_name="Customers",
    access_token="pat_crm_token",
    base_id="appCRMBase"
)
class Customer(BaseModel):
    name: str
    email: str

# Inventory Base
@airtable_model(
    table_name="Products",
    access_token="pat_inventory_token",
    base_id="appInventoryBase"
)
class Product(BaseModel):
    name: str
    price: float
```

### Using Config Objects

Create reusable configuration objects:

```python
from pydantic_airtable import airtable_model, AirTableConfig
from pydantic import BaseModel

# Define configurations
crm_config = AirTableConfig(
    access_token="pat_crm_token",
    base_id="appCRMBase"
)

inventory_config = AirTableConfig(
    access_token="pat_inventory_token",
    base_id="appInventoryBase"
)

analytics_config = AirTableConfig(
    access_token="pat_analytics_token",
    base_id="appAnalyticsBase"
)

# Apply to models
@airtable_model(config=crm_config, table_name="Customers")
class Customer(BaseModel):
    name: str
    email: str

@airtable_model(config=crm_config, table_name="Deals")
class Deal(BaseModel):
    title: str
    value: float

@airtable_model(config=inventory_config, table_name="Products")
class Product(BaseModel):
    name: str
    sku: str

@airtable_model(config=analytics_config, table_name="Events")
class Event(BaseModel):
    name: str
    timestamp: datetime
```

---

## Configuration Management

### Centralized Config Module

Create a dedicated configuration module:

```python
# config.py
import os
from pydantic_airtable import AirTableConfig

class AirTableConfigs:
    """Centralized AirTable configurations"""
    
    @staticmethod
    def crm() -> AirTableConfig:
        return AirTableConfig(
            access_token=os.getenv("CRM_AIRTABLE_TOKEN"),
            base_id=os.getenv("CRM_AIRTABLE_BASE")
        )
    
    @staticmethod
    def inventory() -> AirTableConfig:
        return AirTableConfig(
            access_token=os.getenv("INVENTORY_AIRTABLE_TOKEN"),
            base_id=os.getenv("INVENTORY_AIRTABLE_BASE")
        )
    
    @staticmethod
    def analytics() -> AirTableConfig:
        return AirTableConfig(
            access_token=os.getenv("ANALYTICS_AIRTABLE_TOKEN"),
            base_id=os.getenv("ANALYTICS_AIRTABLE_BASE")
        )
```

```python
# models.py
from pydantic_airtable import airtable_model
from pydantic import BaseModel
from .config import AirTableConfigs

@airtable_model(config=AirTableConfigs.crm(), table_name="Customers")
class Customer(BaseModel):
    name: str
    email: str

@airtable_model(config=AirTableConfigs.inventory(), table_name="Products")
class Product(BaseModel):
    name: str
    price: float
```

### Environment-Based Configuration

```python
# config.py
import os
from pydantic_airtable import AirTableConfig

def get_config(base_name: str) -> AirTableConfig:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development")
    
    # Token is shared across environments
    token = os.getenv("AIRTABLE_ACCESS_TOKEN")
    
    # Base IDs are environment-specific
    base_ids = {
        "development": {
            "crm": os.getenv("DEV_CRM_BASE_ID"),
            "inventory": os.getenv("DEV_INVENTORY_BASE_ID"),
        },
        "staging": {
            "crm": os.getenv("STAGING_CRM_BASE_ID"),
            "inventory": os.getenv("STAGING_INVENTORY_BASE_ID"),
        },
        "production": {
            "crm": os.getenv("PROD_CRM_BASE_ID"),
            "inventory": os.getenv("PROD_INVENTORY_BASE_ID"),
        }
    }
    
    return AirTableConfig(
        access_token=token,
        base_id=base_ids[env][base_name]
    )
```

---

## Multi-Tenant Architecture

### Tenant-Specific Bases

```python
from pydantic_airtable import airtable_model, AirTableConfig
from pydantic import BaseModel
from typing import Type

# Tenant registry
TENANT_CONFIGS: dict[str, AirTableConfig] = {}

def register_tenant(tenant_id: str, base_id: str, token: str):
    """Register a tenant's AirTable configuration"""
    TENANT_CONFIGS[tenant_id] = AirTableConfig(
        access_token=token,
        base_id=base_id
    )

def get_tenant_model(tenant_id: str, base_model: Type) -> Type:
    """Create a tenant-specific model"""
    config = TENANT_CONFIGS.get(tenant_id)
    if not config:
        raise ValueError(f"Unknown tenant: {tenant_id}")
    
    # Create new model class with tenant config
    return airtable_model(
        config=config,
        table_name=base_model.__name__
    )(base_model)

# Base model definition (no AirTable connection)
class CustomerBase(BaseModel):
    name: str
    email: str

# Usage
register_tenant("acme", "appAcmeBase", "pat_acme_token")
register_tenant("globex", "appGlobexBase", "pat_globex_token")

# Get tenant-specific models
AcmeCustomer = get_tenant_model("acme", CustomerBase)
GlobexCustomer = get_tenant_model("globex", CustomerBase)

# Use them
acme_customers = AcmeCustomer.all()
globex_customers = GlobexCustomer.all()
```

### Dynamic Tenant Selection

```python
class TenantContext:
    """Context manager for tenant operations"""
    
    _current_tenant: str = None
    
    @classmethod
    def set_tenant(cls, tenant_id: str):
        cls._current_tenant = tenant_id
    
    @classmethod
    def get_tenant(cls) -> str:
        if not cls._current_tenant:
            raise ValueError("No tenant set")
        return cls._current_tenant
    
    @classmethod
    def get_config(cls) -> AirTableConfig:
        return TENANT_CONFIGS[cls.get_tenant()]

# Middleware/decorator for tenant context
def with_tenant(tenant_id: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            TenantContext.set_tenant(tenant_id)
            try:
                return func(*args, **kwargs)
            finally:
                TenantContext.set_tenant(None)
        return wrapper
    return decorator

# Usage
@with_tenant("acme")
def process_acme_data():
    config = TenantContext.get_config()
    # Use config...
```

---

## Shared Token, Different Bases

When using the same token for multiple bases:

```python
from pydantic_airtable import AirTableConfig

# Shared token
SHARED_TOKEN = os.getenv("AIRTABLE_ACCESS_TOKEN")

# Different bases
sales_config = AirTableConfig(
    access_token=SHARED_TOKEN,
    base_id="appSalesBase"
)

support_config = AirTableConfig(
    access_token=SHARED_TOKEN,
    base_id="appSupportBase"
)

marketing_config = AirTableConfig(
    access_token=SHARED_TOKEN,
    base_id="appMarketingBase"
)
```

---

## Cross-Base Operations

### Copying Data Between Bases

```python
def copy_records(source_model, target_model, transform=None):
    """Copy records from one base/table to another"""
    source_records = source_model.all()
    copied = []
    
    for record in source_records:
        data = record.model_dump(exclude={'id', 'created_time'})
        
        if transform:
            data = transform(data)
        
        new_record = target_model.create(**data)
        copied.append(new_record)
    
    return copied

# Usage: Copy from dev to staging
@airtable_model(config=dev_config, table_name="Users")
class DevUser(BaseModel):
    name: str
    email: str

@airtable_model(config=staging_config, table_name="Users")
class StagingUser(BaseModel):
    name: str
    email: str

copied = copy_records(DevUser, StagingUser)
print(f"Copied {len(copied)} users to staging")
```

### Syncing Between Bases

```python
def sync_bases(source_model, target_model, key_field: str):
    """Sync records between bases using a key field"""
    source_records = {getattr(r, key_field): r for r in source_model.all()}
    target_records = {getattr(r, key_field): r for r in target_model.all()}
    
    results = {"created": 0, "updated": 0, "deleted": 0}
    
    # Create/Update
    for key, source in source_records.items():
        data = source.model_dump(exclude={'id', 'created_time'})
        
        if key in target_records:
            target = target_records[key]
            for field, value in data.items():
                setattr(target, field, value)
            target.save()
            results["updated"] += 1
        else:
            target_model.create(**data)
            results["created"] += 1
    
    # Delete (optional)
    for key, target in target_records.items():
        if key not in source_records:
            target.delete()
            results["deleted"] += 1
    
    return results
```

---

## Testing with Multiple Bases

### Test Fixtures

```python
import pytest
from pydantic_airtable import AirTableConfig, airtable_model
from pydantic import BaseModel

@pytest.fixture
def test_config():
    """Test configuration using test base"""
    return AirTableConfig(
        access_token=os.getenv("TEST_AIRTABLE_TOKEN"),
        base_id=os.getenv("TEST_AIRTABLE_BASE")
    )

@pytest.fixture
def test_user_model(test_config):
    """User model for testing"""
    @airtable_model(config=test_config, table_name="TestUsers")
    class TestUser(BaseModel):
        name: str
        email: str
    
    return TestUser

def test_create_user(test_user_model):
    user = test_user_model.create(name="Test", email="test@example.com")
    assert user.id is not None
    user.delete()  # Cleanup
```

### Mock Configurations

```python
from unittest.mock import MagicMock, patch

def test_with_mock_config():
    """Test without hitting real AirTable"""
    mock_config = MagicMock(spec=AirTableConfig)
    mock_config.access_token = "pat_mock"
    mock_config.base_id = "appMock"
    
    with patch('pydantic_airtable.get_global_config', return_value=mock_config):
        # Test code here
        pass
```

---

## Best Practices

!!! success "Do"
    - Use environment variables for credentials
    - Create a centralized config module
    - Use descriptive config names
    - Document which models use which bases
    - Test with separate test bases

!!! failure "Don't"
    - Hard-code credentials
    - Mix production and development bases
    - Share tokens unnecessarily
    - Forget to clean up test data

---

## Next Steps

- [Error Handling](error-handling.md) - Handle configuration errors
- [Best Practices](best-practices.md) - Production patterns
- [Configuration](../getting-started/configuration.md) - Basic configuration guide

