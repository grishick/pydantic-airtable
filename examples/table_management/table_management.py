"""
Table and Base Management Example

This example demonstrates how to create AirTable bases and tables
directly from Pydantic models, and manage table schemas using the
streamlined pydantic-airtable API.
"""

import sys
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel
from dotenv import load_dotenv

# Add parent directory to path for local development
sys.path.insert(0, "../../")

from pydantic_airtable import (
    airtable_model, 
    configure_from_env, 
    airtable_field,
    AirTableFieldType,
    AirTableManager,
    AirTableConfig
)

# Load environment variables
load_dotenv()

# Configure from environment
configure_from_env()

# Define Enums for better type safety
class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


# Example 1: Simple Task Model with Smart Field Detection
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    """Task model with automatic field type detection"""
    
    title: str                                  # -> SINGLE_LINE_TEXT
    description: Optional[str] = None           # -> LONG_TEXT (detected from name)
    status: TaskStatus = TaskStatus.PENDING     # -> SELECT (enum auto-detected)
    priority: Priority = Priority.MEDIUM        # -> SELECT (enum auto-detected)
    completed: bool = False                     # -> CHECKBOX
    due_date: Optional[datetime] = None         # -> DATETIME
    created_at: Optional[datetime] = None       # -> DATETIME
    
    # Manual override for specific field configuration
    tags: Optional[str] = airtable_field(
        field_type=AirTableFieldType.MULTI_SELECT,
        choices=["urgent", "important", "work", "personal", "review"],
        default=None
    )


# Example 2: User Model with Smart Email/Phone Detection
@airtable_model(table_name="Users")
class User(BaseModel):
    """User model demonstrating smart field detection"""
    
    name: str                    # -> SINGLE_LINE_TEXT
    email: str                   # -> EMAIL (detected from field name!)
    phone: Optional[str] = None  # -> PHONE (detected from field name!)
    bio: Optional[str] = None    # -> LONG_TEXT (detected from field name!)
    website: Optional[str] = None # -> URL (detected from field name!)
    is_admin: bool = False       # -> CHECKBOX
    salary: Optional[float] = None # -> NUMBER


# Example 3: Project Model with Custom Field Configuration
@airtable_model(table_name="Projects")
class Project(BaseModel):
    """Project model with mixed auto-detection and manual configuration"""
    
    name: str                    # Auto-detected
    description: str             # Auto-detected as LONG_TEXT
    budget: Optional[float] = airtable_field(
        field_type=AirTableFieldType.CURRENCY,
        default=None
    )
    completion_rate: Optional[float] = airtable_field(
        field_type=AirTableFieldType.PERCENT,
        default=None
    )
    status: str = airtable_field(
        field_type=AirTableFieldType.SELECT,
        choices=["Planning", "Active", "On Hold", "Completed"],
        default="Planning"
    )
    team_size: Optional[int] = None      # -> NUMBER
    start_date: Optional[datetime] = None # -> DATETIME
    end_date: Optional[datetime] = None   # -> DATETIME


def demonstrate_table_creation():
    """Demonstrate automatic table creation from models"""
    
    print("\n" + "="*60)
    print("🏗️  TABLE CREATION DEMONSTRATION")
    print("="*60)
    
    models_to_create = [
        ("Tasks", Task),
        ("Users", User), 
        ("Projects", Project)
    ]
    
    failed_tables = []
    
    for table_name, model_class in models_to_create:
        print(f"\n📋 Creating {table_name} table...")
        
        try:
            # Try to access existing table
            existing_records = model_class.all()
            print(f"✅ {table_name} table already exists with {len(existing_records)} records")
            
        except Exception as check_error:
            # Table doesn't exist, create it
            print(f"⚠️  Table check failed: {check_error}")
            print(f"🔧 Attempting to create {table_name} table...")
            
            try:
                result = model_class.create_table()
                print(f"✅ Created {table_name} table successfully!")
                print(f"   Table ID: {result.get('id', 'Unknown')}")
                
                # Wait a moment for table to be ready
                import time
                time.sleep(1)
                
                # Verify we can access it
                try:
                    test_records = model_class.all()
                    print(f"✅ Verified table access - found {len(test_records)} records")
                except Exception as verify_error:
                    print(f"⚠️  Table created but access verification failed: {verify_error}")
                
            except Exception as e:
                print(f"❌ Failed to create {table_name} table: {e}")
                print(f"   Error type: {type(e).__name__}")
                failed_tables.append(table_name)
    
    # Return success status
    if failed_tables:
        print(f"\n⚠️  Failed to set up tables: {', '.join(failed_tables)}")
        return False
    else:
        print(f"\n✅ All tables set up successfully!")
        return True


def demonstrate_crud_operations():
    """Demonstrate CRUD operations with the new models"""
    
    print("\n" + "="*60)
    print("📝 CRUD OPERATIONS DEMONSTRATION") 
    print("="*60)
    
    # Create sample tasks
    print("\n1️⃣ Creating sample tasks...")
    
    # Debug: Show what table name we're using
    print(f"🔍 Debug: Task table name is '{Task._get_table_name()}'")
    
    try:
        task1 = Task.create(
            title="Design user interface",
            description="Create wireframes and mockups for the new dashboard",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH,
            due_date=datetime(2024, 12, 31)
        )
        
        task2 = Task.create(
            title="Write documentation", 
            description="Complete API documentation and user guides",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM
        )
        
        print(f"✅ Created tasks: {task1.title} and {task2.title}")
        
    except Exception as task_error:
        print(f"❌ Failed to create tasks: {task_error}")
        print(f"   Error type: {type(task_error).__name__}")
        print("   This might be due to:")
        print("   - Table doesn't exist (creation failed)")
        print("   - Insufficient permissions") 
        print("   - Table name mismatch")
        return  # Skip rest of CRUD operations
    
    # Create sample users
    print("\n2️⃣ Creating sample users...")
    
    user1 = User.create(
        name="Alice Johnson",
        email="alice@example.com",  # Auto-detected as EMAIL type
        phone="555-0123",           # Auto-detected as PHONE type 
        bio="Senior software engineer with 8 years experience",
        website="https://alice.dev",  # Auto-detected as URL type
        is_admin=True,
        salary=95000.0
    )
    
    user2 = User.create(
        name="Bob Smith",
        email="bob@example.com",
        bio="Product manager focused on user experience",
        is_admin=False,
        salary=85000.0
    )
    
    print(f"✅ Created users: {user1.name} and {user2.name}")
    
    # Create sample project
    print("\n3️⃣ Creating sample project...")
    
    project = Project.create(
        name="Mobile App Redesign",
        description="Complete overhaul of the mobile application user interface and user experience",
        budget=150000.0,        # CURRENCY field
        completion_rate=0.25,   # PERCENT field  
        status="Active",        # SELECT field
        team_size=5,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 6, 30)
    )
    
    print(f"✅ Created project: {project.name}")
    
    # Demonstrate querying
    print("\n4️⃣ Demonstrating queries...")
    
    # Find high priority tasks
    high_priority_tasks = Task.find_by(priority=Priority.HIGH)
    print(f"📊 High priority tasks: {len(high_priority_tasks)}")
    
    # Find admin users
    admin_users = User.find_by(is_admin=True)
    print(f"📊 Admin users: {len(admin_users)}")
    
    # Find active projects
    active_projects = Project.find_by(status="Active")
    print(f"📊 Active projects: {len(active_projects)}")
    
    # Demonstrate updates
    print("\n5️⃣ Demonstrating updates...")
    
    task1.status = TaskStatus.COMPLETED
    task1.completed = True
    task1.save()
    print(f"✅ Marked task '{task1.title}' as completed")
    
    project.completion_rate = 0.50
    project.save()
    print(f"✅ Updated project completion rate to 50%")


def demonstrate_table_management():
    """Demonstrate advanced table management features"""
    
    print("\n" + "="*60)
    print("⚙️  TABLE MANAGEMENT DEMONSTRATION")
    print("="*60)
    
    # Get the manager
    config = AirTableConfig.from_env()
    manager = AirTableManager(config)
    
    print("\n1️⃣ Listing all tables in base...")
    try:
        base_schema = manager.get_base_schema()
        tables = base_schema.get('tables', [])
        
        print(f"📊 Found {len(tables)} tables in base:")
        for table in tables:
            fields_count = len(table.get('fields', []))
            print(f"   📋 {table['name']}: {fields_count} fields")
        
    except Exception as e:
        print(f"❌ Failed to list tables: {e}")
    
    # Demonstrate table synchronization
    print("\n2️⃣ Synchronizing model schemas with tables...")
    
    models_to_sync = [Task, User, Project]
    
    for model_class in models_to_sync:
        table_name = model_class._get_table_name()
        print(f"\n🔄 Synchronizing {table_name} table...")
        
        try:
            sync_result = model_class.sync_table(
                create_missing_fields=True,
                update_field_types=False
            )
            
            print(f"✅ Sync completed for {table_name}:")
            print(f"   📝 Fields created: {len(sync_result.get('fields_created', []))}")
            print(f"   🔄 Fields updated: {len(sync_result.get('fields_updated', []))}")
            print(f"   ⏭️  Fields skipped: {len(sync_result.get('fields_skipped', []))}")
            
        except Exception as e:
            print(f"❌ Sync failed for {table_name}: {e}")


def demonstrate_base_operations():
    """Demonstrate base-level operations"""
    
    print("\n" + "="*60)
    print("🗄️  BASE OPERATIONS DEMONSTRATION") 
    print("="*60)
    
    config = AirTableConfig.from_env()
    manager = AirTableManager(config)
    
    print("\n1️⃣ Listing accessible bases...")
    try:
        bases = manager.list_bases()
        print(f"📊 Found {len(bases)} accessible bases:")
        
        for base in bases[:3]:  # Show first 3 bases
            print(f"   🗄️  {base['name']} (ID: {base['id']})")
            
        if len(bases) > 3:
            print(f"   ... and {len(bases) - 3} more bases")
            
    except Exception as e:
        print(f"❌ Failed to list bases: {e}")
    
    print(f"\n2️⃣ Getting schema for current base ({config.base_id})...")
    try:
        schema = manager.get_base_schema()
        tables = schema.get('tables', [])
        
        print(f"📋 Base contains {len(tables)} tables:")
        for table in tables:
            fields = table.get('fields', [])
            print(f"   📋 {table['name']}: {len(fields)} fields")
        
    except Exception as e:
        print(f"❌ Failed to get base schema: {e}")


def main():
    """Main demonstration function"""
    
    print("🚀 Pydantic AirTable - Table Management Example")
    print("=" * 60)
    
    print("\nThis example demonstrates:")
    print("✨ Smart field type detection")
    print("🏗️  Automatic table creation from models") 
    print("📝 CRUD operations with complex models")
    print("⚙️  Table schema management")
    print("🗄️  Base-level operations")
    
    try:
        # Run all demonstrations
        table_setup_success = demonstrate_table_creation()
        
        # Only proceed with CRUD if tables were set up successfully
        if table_setup_success is not False:
            demonstrate_crud_operations()
            demonstrate_table_management()
            demonstrate_base_operations()
        else:
            print("\n⚠️  Skipping CRUD operations due to table setup failures")
            print("🔧 Please check your AirTable permissions and try again")
        
        print("\n" + "="*60)
        print("🎉 All demonstrations completed successfully!")
        print("="*60)
        
        print("\n💡 Key takeaways:")
        print("   ✅ Models automatically detect field types from names and Python types")
        print("   ✅ Tables can be created directly from model definitions")
        print("   ✅ CRUD operations work seamlessly with complex data types")
        print("   ✅ Schema synchronization keeps AirTable in sync with model changes")
        print("   ✅ Base operations provide visibility into your AirTable workspace")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        print("\n💡 Common issues:")
        print("   - Ensure .env file has AIRTABLE_ACCESS_TOKEN and AIRTABLE_BASE_ID")
        print("   - Verify your Personal Access Token has the required permissions")
        print("   - Check that your base ID is correct and accessible")


if __name__ == "__main__":
    main()