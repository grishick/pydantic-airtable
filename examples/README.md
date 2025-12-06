# Pydantic AirTable Examples

This directory contains comprehensive examples demonstrating the capabilities of the Pydantic AirTable library, from basic CRUD operations to sophisticated AI-powered applications.

## 📁 Example Structure

Each example is organized in its own subdirectory with:
- **Main script** - The executable example
- **README.md** - Detailed documentation and usage instructions
- **Self-contained** - Can be run independently

## 🚀 Examples Overview

### 1. [Simple Usage](simple_usage/)
**Foundation patterns for basic operations**

- ✅ **Difficulty**: Beginner
- ✅ **Prerequisites**: AirTable PAT only
- ✅ **Time**: 5 minutes

**What you'll learn:**
- Basic model definition with automatic field type mapping
- CRUD operations (Create, Read, Update, Delete)
- Simple querying and filtering
- Batch operations for efficiency

```bash
cd simple_usage
python simple_usage.py
```

### 2. [Agent Tasks](agent_tasks/)
**Sophisticated business logic with state management**

- 🔶 **Difficulty**: Intermediate
- ✅ **Prerequisites**: AirTable PAT only
- ✅ **Time**: 10 minutes

**What you'll learn:**
- Complex data models with enums and relationships
- Business logic methods built into models
- Task lifecycle management and state transitions
- Performance metrics and analytics
- Advanced querying patterns

```bash
cd agent_tasks
python agent_tasks.py
```

### 3. [Table Management](table_management/)
**Schema creation and database management**

- 🔶 **Difficulty**: Intermediate
- ✅ **Prerequisites**: AirTable PAT with base creation permissions
- ✅ **Time**: 15 minutes

**What you'll learn:**
- Creating AirTable bases and tables programmatically
- Automatic schema generation from Pydantic models
- Schema validation and synchronization
- Model evolution and migration patterns
- Infrastructure as Code principles

```bash
cd table_management
python table_management.py
```

### 4. [Agentic Researcher](agentic_researcher/) 🤖
**AI-powered research assistant with full workflow automation**

- 🔴 **Difficulty**: Advanced
- ⚠️ **Prerequisites**: OpenAI API key + AirTable PAT
- ⚠️ **Time**: 30+ minutes

**What you'll learn:**
- AI workflow orchestration with OpenAI GPT-4o
- Complex multi-model data relationships
- Automatic infrastructure provisioning
- Context-aware AI interactions
- Production-ready error handling and resilience

```bash
cd agentic_researcher
python agentic_researcher.py --demo
python agentic_researcher.py --interactive
```

## 🎯 Learning Path

### For Beginners
1. **Start with [Simple Usage](simple_usage/)** - Learn the basics
2. **Try [Agent Tasks](agent_tasks/)** - Understand business logic patterns
3. **Explore [Table Management](table_management/)** - Master schema management

### For Advanced Users
1. **Review [Table Management](table_management/)** - Understand infrastructure patterns
2. **Dive into [Agentic Researcher](agentic_researcher/)** - See AI integration in action
3. **Build your own** - Combine patterns for your use case

## 🔧 Prerequisites

### Required for All Examples
- **Python 3.8+**
- **AirTable Personal Access Token (PAT)**
  - Get from: [AirTable Developer Hub](https://airtable.com/developers/web/api/authentication)
  - Set: `export AIRTABLE_ACCESS_TOKEN="pat_your_token"`

### Additional for AI Examples
- **OpenAI API Key** (for Agentic Researcher)
  - Get from: [OpenAI Platform](https://platform.openai.com/api-keys)
  - Set: `export OPENAI_API_KEY="sk-your_key"`

### Optional
- **AirTable Base ID** (will create new base if not provided)
  - Set: `export AIRTABLE_BASE_ID="app_your_base"`

## 📊 Feature Comparison

| Feature | Simple Usage | Agent Tasks | Table Management | Agentic Researcher |
|---------|-------------|-------------|------------------|-------------------|
| **CRUD Operations** | ✅ Basic | ✅ Advanced | ✅ Advanced | ✅ Advanced |
| **Business Logic** | ❌ | ✅ Rich | ✅ Schema-focused | ✅ AI-powered |
| **Enums & Types** | ✅ Basic | ✅ Extensive | ✅ Comprehensive | ✅ Comprehensive |
| **Schema Management** | ❌ | ❌ | ✅ Full | ✅ Automatic |
| **Base Creation** | ❌ | ❌ | ✅ Yes | ✅ Automatic |
| **AI Integration** | ❌ | ❌ | ❌ | ✅ Full |
| **Error Handling** | ✅ Basic | ✅ Good | ✅ Comprehensive | ✅ Production |
| **Analytics** | ❌ | ✅ Metrics | ✅ Schema | ✅ Research |

## 🚀 Quick Start Commands

```bash
# Set up environment (required for all examples)
export AIRTABLE_ACCESS_TOKEN="pat_your_personal_access_token"

# Optional: Use existing base
export AIRTABLE_BASE_ID="app_your_base_id"

# For AI examples: Add OpenAI key
export OPENAI_API_KEY="sk-your_openai_key"

# Run any example
cd [example_name]
python [example_name].py
```

## 🎨 Customization Ideas

### Extend Simple Usage
- Add more field types (URL, phone, attachment)
- Implement custom validation rules
- Add relationship fields between models

### Enhance Agent Tasks
- Add task dependencies and workflows
- Implement priority queues
- Add notification systems

### Advanced Table Management
- Multi-environment deployments (dev/staging/prod)
- Schema versioning and rollback
- Automated testing for schema changes

### Agentic Researcher Extensions
- Multiple research methodologies
- Integration with external APIs
- Custom AI models and prompts
- Research collaboration features

## 🔍 Troubleshooting

### Common Issues

**"ConfigurationError: Personal Access Token not provided"**
```bash
export AIRTABLE_ACCESS_TOKEN="pat_your_token"
```

**"Permission denied" when creating bases/tables**
- Ensure your PAT has base creation permissions
- Some operations require workspace admin privileges

**OpenAI API errors in Agentic Researcher**
- Verify your OpenAI API key is valid
- Check your OpenAI account has sufficient credits
- The library includes retry logic for transient failures

### Getting Help

1. **Check the README** in each example directory
2. **Review error messages** - they often contain helpful guidance
3. **Start simple** - begin with Simple Usage before advanced examples
4. **Check permissions** - ensure your PAT has necessary access levels

## 📚 Additional Resources

- **[Main README](../README.md)** - Library overview and installation
- **[Installation Guide](../INSTALLATION.md)** - Detailed setup instructions
- **[Authentication Migration](../AUTHENTICATION_MIGRATION.md)** - PAT migration guide
- **[AirTable API Docs](https://airtable.com/developers/web/api/introduction)** - Official API reference
- **[OpenAI API Docs](https://platform.openai.com/docs)** - AI integration reference

---

**Start with Simple Usage and work your way up to building sophisticated AI-powered applications with structured data management!** 🚀

