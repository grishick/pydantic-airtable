# Installation Guide

## 📦 **Installing Pydantic AirTable**

### **Prerequisites**
- Python 3.8 or higher
- pip package manager

### **Basic Installation**

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install individual packages
pip install pydantic>=2.0.0 requests>=2.28.0 python-dateutil>=2.8.0 openai>=2.8.1
```

### **Development Installation**

```bash
# Clone the repository
git clone <repository-url>
cd pydantic-at

# Install in development mode
pip install -e .

# Install with test dependencies
pip install -r requirements.txt
```

## 🔑 **API Keys and Configuration**

### **AirTable Setup**

1. **Get Personal Access Token (PAT)**:
   - Go to [AirTable Developer Hub](https://airtable.com/developers/web/api/authentication)
   - Create a Personal Access Token
   - Your token will start with `pat_`

2. **Set Environment Variable**:
   ```bash
   export AIRTABLE_ACCESS_TOKEN="pat_your_personal_access_token"
   export AIRTABLE_BASE_ID="app_your_base_id"  # Optional
   ```

### **OpenAI Setup (for Agentic Researcher)**

1. **Get API Key**:
   - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create a new API key
   - Your key will start with `sk-`

2. **Set Environment Variable**:
   ```bash
   export OPENAI_API_KEY="sk-your-openai-api-key"
   ```

## 🔍 **Version Compatibility**

### **OpenAI Library**
- **Latest Version**: 2.8.1 (November 2024)
- **Key Features**:
  - Enhanced error handling
  - Improved timeout management
  - Better retry logic
  - Support for latest models (gpt-4o, gpt-4-turbo)

### **Pydantic Library**
- **Version**: 2.0+
- **Features Used**:
  - Field validation
  - Type hints
  - Model serialization
  - Custom validators

### **AirTable API**
- **Version**: REST API v0
- **Authentication**: Personal Access Tokens (PATs)
- **Features**: Base/table creation, CRUD operations, schema management

## 🧪 **Testing Installation**

### **Quick Test**
```bash
python -c "
import pydantic_airtable
from pydantic_airtable import AirTableModel, AirTableConfig
print('✅ Pydantic AirTable imported successfully')
print(f'📦 Version: {pydantic_airtable.__version__}')
"
```

### **OpenAI Test** (if using Agentic Researcher)
```bash
python -c "
import openai
print('✅ OpenAI library imported successfully')
print(f'📦 Version: {openai.__version__}')
"
```

### **Run Examples**
```bash
# Basic usage
python examples/simple_usage.py

# With AirTable credentials
export AIRTABLE_ACCESS_TOKEN="pat_your_token"
export AIRTABLE_BASE_ID="app_your_base"
python examples/table_management.py

# With OpenAI + AirTable credentials
export OPENAI_API_KEY="sk-your_key"
python examples/agentic_researcher.py --demo
```

## 🚨 **Common Installation Issues**

### **Issue**: `ModuleNotFoundError: No module named 'pydantic'`
**Solution**:
```bash
pip install --upgrade pydantic>=2.0.0
```

### **Issue**: `ImportError: cannot import name 'OpenAI' from 'openai'`
**Solution**: Update to latest OpenAI library
```bash
pip install --upgrade openai>=2.8.1
```

### **Issue**: `ConfigurationError: AirTable Personal Access Token not provided`
**Solution**: Set environment variables
```bash
export AIRTABLE_ACCESS_TOKEN="pat_your_token"
```

### **Issue**: OpenAI rate limiting errors
**Solution**: The library includes built-in retry logic, but ensure you have sufficient OpenAI credits

## 🔄 **Upgrading**

### **From v0.1.x to v0.2.x**
```bash
pip install --upgrade openai>=2.8.1
```

No breaking changes - all v0.1.x code continues to work. New features:
- Table/base creation
- Schema management
- Agentic Researcher

### **OpenAI Library Migration**
If upgrading from older OpenAI versions:

**Old (pre-1.0)**:
```python
import openai
openai.api_key = "sk-..."
response = openai.ChatCompletion.create(...)
```

**New (1.0+)**:
```python
from openai import OpenAI
client = OpenAI(api_key="sk-...")
response = client.chat.completions.create(...)
```

Our library uses the **new pattern** and requires OpenAI 2.8.1+.

## 📚 **Next Steps**

1. **Quick Start**: Run `python examples/simple_usage.py`
2. **Schema Management**: Try `python examples/table_management.py`
3. **AI Research**: Explore `python examples/agentic_researcher.py --interactive`
4. **Documentation**: Read the full [README.md](README.md)
5. **API Reference**: Check the [AirTable API docs](https://airtable.com/developers/web/api/introduction)

## 💡 **Tips for Success**

- **Use PATs**: Always use Personal Access Tokens, not deprecated API keys
- **Set Timeouts**: The library includes reasonable timeouts for API calls
- **Monitor Usage**: Track your OpenAI and AirTable API usage
- **Start Simple**: Begin with basic examples before trying advanced features
- **Check Permissions**: Ensure your PAT has necessary base/table creation permissions

---

**Need Help?** Check the examples, read error messages carefully, and ensure all environment variables are set correctly.

