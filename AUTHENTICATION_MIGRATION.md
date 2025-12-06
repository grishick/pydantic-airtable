# AirTable Authentication Migration Guide

This document explains the migration from deprecated API keys to Personal Access Tokens (PATs) in compliance with AirTable's new authentication requirements.

## 🚨 Important: API Keys Are Deprecated

According to [AirTable's Authentication Documentation](https://airtable.com/developers/web/api/authentication), API keys have been **deprecated** in favor of **Personal Access Tokens (PATs)**.

## ✅ What's Changed in This Library

### 1. New Authentication Parameters

| Old (Deprecated) | New (Recommended) | Status |
|-----------------|-------------------|---------|
| `api_key` | `access_token` | ✅ Use this |
| `AIRTABLE_API_KEY` | `AIRTABLE_ACCESS_TOKEN` | ✅ Use this |

### 2. Updated Code Examples

**❌ Old Way (Deprecated)**:
```python
from pydantic_airtable import AirTableConfig

# This will show deprecation warnings
config = AirTableConfig(
    api_key="your_api_key",  # DEPRECATED
    base_id="app123",
    table_name="MyTable"
)
```

**✅ New Way (Recommended)**:
```python
from pydantic_airtable import AirTableConfig

# Use Personal Access Token instead
config = AirTableConfig(
    access_token="pat_your_personal_access_token",  # CORRECT
    base_id="app123", 
    table_name="MyTable"
)
```

### 3. Environment Variables

**❌ Old Environment Variable (Deprecated)**:
```bash
export AIRTABLE_API_KEY="your_api_key"  # Will show warnings
export AIRTABLE_BASE_ID="app123"
```

**✅ New Environment Variable (Recommended)**:
```bash
export AIRTABLE_ACCESS_TOKEN="pat_your_access_token"  # CORRECT
export AIRTABLE_BASE_ID="app123"
```

## 🔄 Migration Steps

### Step 1: Get Your Personal Access Token
1. Go to [AirTable Developer Hub](https://airtable.com/developers/web/api/authentication)
2. Create a new Personal Access Token (PAT)
3. Your PAT will start with `pat_`
4. Configure appropriate permissions for your bases

### Step 2: Update Your Code
Replace all instances of:
- `api_key=` → `access_token=`
- `AIRTABLE_API_KEY` → `AIRTABLE_ACCESS_TOKEN`

### Step 3: Test Your Changes
The library will show deprecation warnings if you're still using old parameters:
```
DeprecationWarning: The 'api_key' parameter is deprecated. Use 'access_token' instead.
```

## 🛡️ Backward Compatibility

This library maintains **full backward compatibility**:

✅ **Old code continues to work** (with deprecation warnings)
✅ **Old environment variables still work** (with deprecation warnings)  
✅ **Migration can be done gradually**
✅ **No breaking changes** in this version

## 🚦 Deprecation Warnings

When using deprecated parameters, you'll see warnings like:

```python
DeprecationWarning: The 'api_key' parameter is deprecated. 
Use 'access_token' instead. API keys are deprecated by AirTable 
in favor of Personal Access Tokens (PATs). 
See: https://airtable.com/developers/web/api/authentication
```

## 📋 Checklist for Migration

- [ ] **Get PAT**: Generate Personal Access Token from AirTable
- [ ] **Update Environment Variables**: Replace `AIRTABLE_API_KEY` with `AIRTABLE_ACCESS_TOKEN`
- [ ] **Update Code**: Replace `api_key` parameters with `access_token`
- [ ] **Test**: Ensure no deprecation warnings appear
- [ ] **Update CI/CD**: Update deployment scripts and environment configurations

## 🔍 Validation

You can verify your migration is complete by ensuring:

1. **No deprecation warnings** appear when running your code
2. **PAT starts with `pat_`** (not an old API key format)
3. **Environment variables use new names** (`AIRTABLE_ACCESS_TOKEN`)
4. **Code uses new parameter names** (`access_token`)

## 📚 Additional Resources

- [AirTable Authentication Documentation](https://airtable.com/developers/web/api/authentication)
- [Personal Access Token Management](https://airtable.com/developers/web/api/authentication)
- [AirTable API Reference](https://airtable.com/developers/web/api/introduction)

## 🆘 Troubleshooting

### Error: "Cannot specify both 'access_token' and 'api_key'"
- **Solution**: Use only `access_token`, remove `api_key` parameter

### Error: "access_token is required"
- **Solution**: Provide a Personal Access Token via `access_token` parameter or `AIRTABLE_ACCESS_TOKEN` environment variable

### Warning: "AIRTABLE_API_KEY environment variable is deprecated"
- **Solution**: Replace with `AIRTABLE_ACCESS_TOKEN` environment variable

### Error: "Personal Access Token not provided"
- **Solution**: Set `AIRTABLE_ACCESS_TOKEN` environment variable or pass `access_token` parameter

---

**Migration Timeline**: While backward compatibility is maintained, plan to migrate to PATs as soon as possible since AirTable may discontinue API key support entirely in the future.

