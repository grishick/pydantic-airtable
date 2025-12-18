# Changelog

All notable changes to Pydantic Airtable are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-12-18

### Initial Release

First public release of Pydantic Airtable — the most intuitive way to integrate Pydantic models with Airtable.

### Added

- **Core Features**
  - `@airtable_model` decorator for Pydantic model integration
  - `AirtableModel` base class with full CRUD operations
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
  - `AirtableConfig` dataclass
  - `configure_from_env()` for environment-based setup
  - `set_global_config()` and `get_global_config()`
  - Per-model configuration support
  - Multiple base support

- **Table Management**
  - `create_table()` - Create tables from models
  - `sync_table()` - Synchronize model schemas
  - `AirtableManager` for direct API access

- **Field Types**
  - All standard Airtable field types
  - Automatic field type detection for email, phone, URL, etc.
  - Enum support for SELECT fields
  - List support for MULTI_SELECT fields
  - Custom field name mapping
  - Read-only field support

- ** Field Type Detection**

  | Pattern | Detected Type |
  |---------|---------------|
  | email, mail, contact | EMAIL |
  | phone, tel, mobile, cell | PHONE |
  | url, link, website | URL |
  | description, note, bio | LONG_TEXT |
  | price, cost, amount | CURRENCY |
  | percent, rate, ratio | PERCENT |

- **Examples**
  - Simple Usage — Basic CRUD operations
  - Table Management — Schema creation and evolution
  - Agentic Researcher — AI-powered research assistant with OpenAI integration

- **Documentation**
  - Comprehensive MkDocs documentation
  - API reference
  - User guide
  - Examples

---

## Upcoming

### Planned for Future Releases

- [ ] Async support
- [ ] Linked records handling
- [ ] Attachment field support
- [ ] Webhook integration
- [ ] Rate limit handling improvements
- [ ] Record versioning
- [ ] Soft delete support
- [ ] Cache layer

---

## Version History

| Version | Date | Status |
|---------|------|--------|
| 1.0.0 | 2025-12-18 | Initial Release |
