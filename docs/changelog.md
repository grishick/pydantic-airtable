# Changelog

All notable changes to Pydantic AirTable are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2024-12-10

### Added

- **Core Features**
  - `@airtable_model` decorator for Pydantic model integration
  - `AirTableModel` base class with full CRUD operations
  - Smart field type detection from Python types and field names
  - `airtable_field()` function for field customization

- **CRUD Operations**
  - `create()` - Create single records
  - `get()` - Retrieve by ID
  - `all()` - Get all records with filtering
  - `find_by()` - Query by field values
  - `first()` - Get first matching record
  - `bulk_create()` - Batch record creation
  - `save()` - Update existing records
  - `delete()` - Remove records

- **Configuration**
  - `AirTableConfig` dataclass
  - `configure_from_env()` for environment-based setup
  - `set_global_config()` and `get_global_config()`
  - Per-model configuration support
  - Multiple base support

- **Table Management**
  - `create_table()` - Create tables from models
  - `sync_table()` - Synchronize model schemas
  - `AirTableManager` for direct API access

- **Field Types**
  - All standard AirTable field types
  - Smart detection for email, phone, URL, etc.
  - Enum support for SELECT fields
  - List support for MULTI_SELECT fields
  - Custom field name mapping
  - Read-only field support

- **Documentation**
  - Comprehensive MkDocs documentation
  - API reference
  - User guide
  - Examples

### Field Detection Patterns

| Pattern | Detected Type |
|---------|---------------|
| email, mail, contact | EMAIL |
| phone, tel, mobile, cell | PHONE |
| url, link, website | URL |
| description, note, bio | LONG_TEXT |
| price, cost, amount | CURRENCY |
| percent, rate, ratio | PERCENT |

---

## [0.9.0] - 2024-11-15

### Added

- Initial beta release
- Basic model decorator
- Simple CRUD operations
- Environment configuration

### Known Issues

- Limited field type support
- No batch operations
- No table management

---

## Upcoming

### Planned for 1.1.0

- [ ] Async support
- [ ] Linked records
- [ ] Attachment handling
- [ ] Webhook support
- [ ] Rate limit handling improvements

### Planned for 1.2.0

- [ ] Record versioning
- [ ] Soft delete support
- [ ] Audit logging
- [ ] Cache layer

---

## Migration Guides

### 0.9.x to 1.0.0

**Breaking Changes:**

1. **Decorator syntax changed**
   ```python
   # Old (0.9.x)
   @airtable_model("Users")
   class User(BaseModel): ...
   
   # New (1.0.0)
   @airtable_model(table_name="Users")
   class User(BaseModel): ...
   ```

2. **Configuration function renamed**
   ```python
   # Old (0.9.x)
   configure(token="...", base_id="...")
   
   # New (1.0.0)
   configure_from_env(access_token="...", base_id="...")
   ```

3. **Field helper renamed**
   ```python
   # Old (0.9.x)
   AirTableField(type=...)
   
   # New (1.0.0)
   airtable_field(field_type=...)
   ```

---

## Version History

| Version | Date | Status |
|---------|------|--------|
| 1.0.0 | 2024-12-10 | Current |
| 0.9.0 | 2024-11-15 | Beta |
