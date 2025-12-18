# Installation

This guide covers installing Pydantic Airtable and setting up your development environment.

---

## Requirements

- **Python 3.8** or higher
- **pip** package manager
- An **Airtable account** with API access

---

## Installation Methods

### Using pip (Recommended)

```bash
pip install pydantic-airtable
```

### From requirements.txt

Add to your `requirements.txt`:

```text
pydantic-airtable>=1.0.0
```

Then install:

```bash
pip install -r requirements.txt
```

### Development Installation

For contributing or local development:

```bash
# Clone the repository
git clone https://github.com/pydantic-airtable/pydantic-airtable.git
cd pydantic-airtable

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -r requirements-dev.txt
```

---

## Dependencies

Pydantic Airtable automatically installs these dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| `pydantic` | >=2.0.0 | Data validation and serialization |
| `requests` | >=2.28.0 | HTTP client for Airtable API |
| `python-dateutil` | >=2.8.0 | Date/time parsing utilities |
| `python-dotenv` | >=1.0.0 | Environment variable loading |

---

## Verifying Installation

After installation, verify everything works:

```python
# Test import
import pydantic_airtable
print(f"✅ Pydantic Airtable v{pydantic_airtable.__version__} installed successfully!")

# Test core components
from pydantic_airtable import (
    airtable_model,
    configure_from_env,
    AirtableConfig,
    AirtableFieldType
)
print("✅ All core components imported successfully!")
```

Run this as a script:

```bash
python -c "
import pydantic_airtable
print(f'✅ Pydantic Airtable v{pydantic_airtable.__version__} installed!')
from pydantic_airtable import airtable_model, configure_from_env
print('✅ All components ready!')
"
```

---

## Getting Airtable Credentials

### Personal Access Token (PAT)

1. Go to [Airtable Developer Hub](https://airtable.com/developers/web/api/authentication)
2. Click **"Create new token"**
3. Give it a descriptive name (e.g., "pydantic-airtable-dev")
4. Select the required scopes:
    - `data.records:read` - Read records
    - `data.records:write` - Create, update, delete records
    - `schema.bases:read` - Read base schema
    - `schema.bases:write` - Create tables
5. Select the bases you want to access
6. Copy your token (starts with `pat_`)

!!! warning "Token Security"
    Never commit your Personal Access Token to version control. Always use environment variables or `.env` files.

### Base ID

Find your Base ID in the Airtable URL:

```
https://airtable.com/appXXXXXXXXXXXXXX/...
                     ^^^^^^^^^^^^^^^^^^
                     This is your Base ID
```

Or from the [Airtable API documentation](https://airtable.com/developers/web/api/introduction) for your base.

---

## Environment Setup

### Option 1: .env File (Recommended)

Create a `.env` file in your project root:

```env
# Required
AIRTABLE_ACCESS_TOKEN=pat_your_personal_access_token_here
AIRTABLE_BASE_ID=appYourBaseIdHere

# Optional
AIRTABLE_TABLE_NAME=DefaultTableName
```

!!! tip "Git Ignore"
    Add `.env` to your `.gitignore` file to prevent accidentally committing credentials:
    ```
    # .gitignore
    .env
    .env.local
    .env.*.local
    ```

### Option 2: Environment Variables

Set variables directly in your shell:

=== "Linux/macOS"

    ```bash
    export AIRTABLE_ACCESS_TOKEN="pat_your_token"
    export AIRTABLE_BASE_ID="appYourBaseId"
    ```

=== "Windows (PowerShell)"

    ```powershell
    $env:AIRTABLE_ACCESS_TOKEN = "pat_your_token"
    $env:AIRTABLE_BASE_ID = "appYourBaseId"
    ```

=== "Windows (CMD)"

    ```cmd
    set AIRTABLE_ACCESS_TOKEN=pat_your_token
    set AIRTABLE_BASE_ID=appYourBaseId
    ```

---

## Troubleshooting

### Common Installation Issues

??? failure "ModuleNotFoundError: No module named 'pydantic'"
    **Solution**: Ensure you have Pydantic v2 installed:
    ```bash
    pip install --upgrade pydantic>=2.0.0
    ```

??? failure "ImportError: cannot import name 'BaseModel'"
    **Solution**: You may have Pydantic v1 installed. Upgrade to v2:
    ```bash
    pip uninstall pydantic
    pip install pydantic>=2.0.0
    ```

??? failure "ConfigurationError: Airtable Personal Access Token is required"
    **Solution**: Set your environment variables or create a `.env` file:
    ```bash
    export AIRTABLE_ACCESS_TOKEN="pat_your_token"
    export AIRTABLE_BASE_ID="appYourBaseId"
    ```

??? failure "Invalid access token format"
    **Solution**: Personal Access Tokens must start with `pat_`. Make sure you're using a PAT, not a legacy API key.

---

## Next Steps

Now that you have Pydantic Airtable installed:

1. **[Quick Start](quickstart.md)** - Create your first model and interact with Airtable
2. **[Configuration](configuration.md)** - Learn about all configuration options
3. **[Examples](../examples/index.md)** - See real-world usage examples
