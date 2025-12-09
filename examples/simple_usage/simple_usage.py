"""
Simple usage example showing the streamlined pydantic-airtable API
"""

import sys
from typing import Optional
from pydantic import BaseModel

# Add parent directory to path for local development  
sys.path.insert(0, "../../")

from pydantic_airtable import airtable_model, configure_from_env, airtable_field, AirTableFieldType
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure AirTable connection from environment
configure_from_env()

# Define model with streamlined decorator
@airtable_model(table_name="Users")  
class User(BaseModel):
    """User model with smart field detection"""
    
    # Smart field detection - no explicit field types needed!
    name: str                    # -> SINGLE_LINE_TEXT (auto-detected)
    email: str                   # -> EMAIL (auto-detected from field name)  
    age: Optional[int] = None    # -> NUMBER (auto-detected)
    is_active: bool = True       # -> CHECKBOX (auto-detected)
    
    # Optional: Override detection with explicit field configuration
    bio: Optional[str] = airtable_field(
        field_type=AirTableFieldType.LONG_TEXT,
        default=None
    )


def main():
    """Demonstrate streamlined CRUD operations"""
    
    print("🚀 Pydantic AirTable - Simple Usage Example")
    print("=" * 50)
    
    try:
        # Automatic table creation if it doesn't exist
        print("🔍 Ensuring Users table exists...")
        try:
            # Try a simple operation first
            existing_users = User.all()
            print(f"✅ Table exists with {len(existing_users)} existing users")
        except Exception:
            # Table doesn't exist, create it
            print("🔧 Creating Users table from model...")
            User.create_table()
            print("✅ Users table created successfully!")
        
        print("\n" + "=" * 50)
        print("🚀 Starting CRUD operations...")
        
        # 1. Create a new user
        print("\n1️⃣ Creating a new user...")
        user = User.create(
            name="Alice Johnson",
            email="alice@example.com", 
            age=28,
            bio="Software engineer with 5 years experience"
        )
        print(f"✅ Created user: {user.name} (ID: {user.id})")
        
        # 2. Read the user back  
        print("\n2️⃣ Reading user by ID...")
        retrieved_user = User.get(user.id)
        print(f"✅ Retrieved user: {retrieved_user.name}, Email: {retrieved_user.email}")
        
        # 3. Update the user
        print("\n3️⃣ Updating user...")
        retrieved_user.age = 29
        retrieved_user.bio = "Senior software engineer with 6 years experience"
        retrieved_user.save()
        print(f"✅ Updated user age to: {retrieved_user.age}")
        
        # 4. Create another user
        print("\n4️⃣ Creating another user...")  
        user2 = User.create(
            name="Bob Smith",
            email="bob@example.com",
            age=35,
            is_active=False,
            bio="Product manager specializing in user experience"
        )
        print(f"✅ Created user: {user2.name} (ID: {user2.id})")
        
        # 5. Query users
        print("\n5️⃣ Querying users...")
        
        # Get all users
        all_users = User.all()
        print(f"📊 Total users: {len(all_users)}")
        
        # Get active users - simple filtering
        active_users = User.find_by(is_active=True)
        print(f"📊 Active users: {len(active_users)}")
        
        # Get first inactive user  
        inactive_user = User.first(is_active=False)
        if inactive_user:
            print(f"📊 First inactive user: {inactive_user.name}")
        
        # 6. Batch create users
        print("\n6️⃣ Batch creating users...")
        users_data = [
            {"name": "Charlie Brown", "email": "charlie@example.com", 
             "age": 22, "bio": "Junior developer"},
            {"name": "Diana Prince", "email": "diana@example.com", 
             "age": 30, "bio": "UX designer"},  
            {"name": "Eve Davis", "email": "eve@example.com", 
             "age": 27, "bio": "Data scientist"},
        ]
        
        created_users = User.bulk_create(users_data)
        print(f"✅ Batch created {len(created_users)} users")
        
        # 7. Final count
        print("\n7️⃣ Final user count...")
        final_users = User.all()
        print(f"📊 Final total users: {len(final_users)}")
        
        # List all users with their details
        print("\n👥 All users:")
        for u in final_users:
            status = "✓" if u.is_active else "✗"
            bio_preview = (u.bio[:30] + "...") if u.bio and len(u.bio) > 30 else (u.bio or "No bio")
            print(f"  {status} {u.name} ({u.email}) - Age: {u.age}")
            print(f"     Bio: {bio_preview}")
        
        print("\n🎉 Example completed successfully!")
        print("\n💡 Key features demonstrated:")
        print("   ✅ Smart field type detection")  
        print("   ✅ Simple @airtable_model decorator")
        print("   ✅ Automatic table creation")
        print("   ✅ Clean CRUD operations")
        print("   ✅ Environment-based configuration")
        
        # 8. Demonstrate table operations
        print("\n8️⃣ Table management operations...")
        sync_result = User.sync_table()
        print(f"✅ Table sync completed: {sync_result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Quick fixes:")
        print("   - Ensure .env file has AIRTABLE_ACCESS_TOKEN and AIRTABLE_BASE_ID")
        print("   - Make sure you're using a Personal Access Token (starts with 'pat')")
        print("   - Verify your token has permissions for the base")


if __name__ == "__main__":
    main()