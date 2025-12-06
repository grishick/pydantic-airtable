"""
Simple usage example showing basic CRUD operations
"""

import os
from typing import Optional
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from pydantic_airtable import AirTableModel, AirTableConfig, AirTableField
from pydantic_airtable.fields import AirTableFieldType


class User(AirTableModel):
    """Simple User model for demonstration"""
    
    # Configure AirTable connection
    AirTableConfig = AirTableConfig(
        table_name="Users"  # Will use env vars for access token and base ID
    )
    
    # Define fields
    name: str = AirTableField(
        description="User's full name",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    email: str = AirTableField(
        description="User's email address",
        airtable_field_type=AirTableFieldType.EMAIL
    )
    
    age: Optional[int] = AirTableField(
        default=None,
        description="User's age",
        airtable_field_type=AirTableFieldType.NUMBER
    )
    
    is_active: bool = AirTableField(
        default=True,
        description="Whether user is active",
        airtable_field_type=AirTableFieldType.CHECKBOX
    )


def main():
    """Demonstrate basic CRUD operations"""
    
    print("🔗 Pydantic AirTable - Simple Usage Example")
    print("=" * 50)
    
    # Check for required environment variables
    access_token = os.getenv("AIRTABLE_ACCESS_TOKEN") or os.getenv("AIRTABLE_API_KEY")
    if not access_token or not os.getenv("AIRTABLE_BASE_ID"):
        print("⚠️  Please set AIRTABLE_ACCESS_TOKEN and AIRTABLE_BASE_ID environment variables")
        print("Example:")
        print("export AIRTABLE_ACCESS_TOKEN='pat....'  # Use Personal Access Token")
        print("export AIRTABLE_BASE_ID='app....'")
        print("")
        print("Note: API keys are deprecated. Get your PAT from:")
        print("https://airtable.com/developers/web/api/authentication")
        return
    
    # Warn about deprecated environment variable
    if os.getenv("AIRTABLE_API_KEY") and not os.getenv("AIRTABLE_ACCESS_TOKEN"):
        print("⚠️  AIRTABLE_API_KEY is deprecated. Please use AIRTABLE_ACCESS_TOKEN instead.")
        print("See: https://airtable.com/developers/web/api/authentication")
        print("")
    
    try:
        # 1. Create a new user
        print("\\n1️⃣ Creating a new user...")
        user = User.create(
            name="Alice Johnson",
            email="alice@example.com",
            age=28
        )
        print(f"✅ Created user: {user.name} (ID: {user.id})")
        
        # 2. Read the user back
        print("\\n2️⃣ Reading user by ID...")
        retrieved_user = User.get(user.id)
        print(f"✅ Retrieved user: {retrieved_user.name}, Email: {retrieved_user.email}")
        
        # 3. Update the user
        print("\\n3️⃣ Updating user...")
        retrieved_user.age = 29
        retrieved_user.save()
        print(f"✅ Updated user age to: {retrieved_user.age}")
        
        # 4. Create another user for querying
        print("\\n4️⃣ Creating another user...")
        user2 = User.create(
            name="Bob Smith",
            email="bob@example.com",
            age=35,
            is_active=False
        )
        print(f"✅ Created user: {user2.name} (ID: {user2.id})")
        
        # 5. Query users
        print("\\n5️⃣ Querying users...")
        
        # Get all users
        all_users = User.all()
        print(f"📊 Total users: {len(all_users)}")
        
        # Get active users
        active_users = User.find_by(is_active=True)
        print(f"📊 Active users: {len(active_users)}")
        
        # Get first inactive user
        inactive_user = User.first(is_active=False)
        if inactive_user:
            print(f"📊 First inactive user: {inactive_user.name}")
        
        # 6. Batch create users
        print("\\n6️⃣ Batch creating users...")
        users_data = [
            {"name": "Charlie Brown", "email": "charlie@example.com", "age": 22},
            {"name": "Diana Prince", "email": "diana@example.com", "age": 30},
            {"name": "Eve Davis", "email": "eve@example.com", "age": 27},
        ]
        
        created_users = User.bulk_create(users_data)
        print(f"✅ Batch created {len(created_users)} users")
        
        # 7. Final count
        print("\\n7️⃣ Final user count...")
        final_users = User.all()
        print(f"📊 Final total users: {len(final_users)}")
        
        # List all users
        print("\\n👥 All users:")
        for u in final_users:
            status = "✓" if u.is_active else "✗"
            print(f"  {status} {u.name} ({u.email}) - Age: {u.age}")
        
        print("\\n🎉 Example completed successfully!")
        print("\\n💡 Try modifying this script to:")
        print("   - Add more fields to the User model")
        print("   - Experiment with different field types")
        print("   - Use custom field names with airtable_field_name")
        print("   - Add validation using Pydantic validators")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\\n💡 Common issues:")
        print("   - Check your AirTable API key and Base ID")
        print("   - Ensure the 'Users' table exists in your AirTable base")
        print("   - Verify your API key has the correct permissions")


if __name__ == "__main__":
    main()
