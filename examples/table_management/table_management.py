"""
Table and Base Management Example

This example demonstrates how to create AirTable bases and tables
directly from Pydantic models, and manage table schemas.
"""

import os
from datetime import datetime
from typing import Optional, List
from enum import Enum

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from pydantic_airtable import AirTableModel, AirTableConfig, AirTableField, BaseManager, TableManager
from pydantic_airtable.fields import AirTableFieldType


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


# Example 1: Simple Task Model
class Task(AirTableModel):
    """Task model that can create its own table"""
    
    AirTableConfig = AirTableConfig(
        table_name="Tasks"
    )
    
    title: str = AirTableField(
        description="Task title",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    description: str = AirTableField(
        description="Detailed task description",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )
    
    status: TaskStatus = AirTableField(
        default=TaskStatus.PENDING,
        description="Current task status",
        airtable_field_type=AirTableFieldType.SELECT
    )
    
    priority: Priority = AirTableField(
        default=Priority.MEDIUM,
        description="Task priority level",
        airtable_field_type=AirTableFieldType.SELECT
    )
    
    due_date: Optional[datetime] = AirTableField(
        default=None,
        description="Task due date",
        airtable_field_type=AirTableFieldType.DATETIME
    )
    
    assignee_email: Optional[str] = AirTableField(
        default=None,
        description="Assignee email address",
        airtable_field_type=AirTableFieldType.EMAIL
    )
    
    estimated_hours: Optional[float] = AirTableField(
        default=None,
        description="Estimated hours to complete",
        airtable_field_type=AirTableFieldType.NUMBER
    )


# Example 2: User Model with relationships
class User(AirTableModel):
    """User model with various field types"""
    
    AirTableConfig = AirTableConfig(
        table_name="Users"
    )
    
    name: str = AirTableField(
        description="Full name",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    email: str = AirTableField(
        description="Email address",
        airtable_field_type=AirTableFieldType.EMAIL
    )
    
    phone: Optional[str] = AirTableField(
        default=None,
        description="Phone number",
        airtable_field_type=AirTableFieldType.PHONE
    )
    
    website: Optional[str] = AirTableField(
        default=None,
        description="Personal website",
        airtable_field_type=AirTableFieldType.URL
    )
    
    is_active: bool = AirTableField(
        default=True,
        description="User is active",
        airtable_field_type=AirTableFieldType.CHECKBOX
    )
    
    join_date: datetime = AirTableField(
        default_factory=datetime.now,
        description="Date joined",
        airtable_field_type=AirTableFieldType.DATE
    )


def demo_base_management():
    """Demonstrate base management operations"""
    
    print("🏗️  Base Management Demo")
    print("=" * 40)
    
    access_token = os.getenv("AIRTABLE_ACCESS_TOKEN") or os.getenv("AIRTABLE_API_KEY")
    if not access_token:
        print("⚠️  No access token found. Set AIRTABLE_ACCESS_TOKEN environment variable.")
        return
    
    base_manager = BaseManager(access_token)
    
    try:
        # List existing bases
        print("\\n📋 Listing existing bases...")
        bases = base_manager.list_bases()
        print(f"Found {len(bases)} bases:")
        for base in bases[:3]:  # Show first 3
            print(f"  - {base['name']} (ID: {base['id']})")
        
        # Create a new base (if you have permissions)
        print("\\n🆕 Creating new base...")
        
        # Define table schemas for the new base
        task_table_config = {
            "name": "Tasks",
            "description": "Project tasks and assignments",
            "fields": [
                {"name": "Title", "type": "singleLineText"},
                {"name": "Status", "type": "singleSelect", "options": {"choices": [
                    {"name": "Pending"}, {"name": "In Progress"}, {"name": "Completed"}
                ]}},
                {"name": "Priority", "type": "singleSelect", "options": {"choices": [
                    {"name": "Low"}, {"name": "Medium"}, {"name": "High"}, {"name": "Urgent"}
                ]}},
                {"name": "Due Date", "type": "dateTime"},
                {"name": "Assignee", "type": "email"}
            ]
        }
        
        user_table_config = {
            "name": "Users", 
            "description": "User information and contacts",
            "fields": [
                {"name": "Name", "type": "singleLineText"},
                {"name": "Email", "type": "email"},
                {"name": "Phone", "type": "phoneNumber"},
                {"name": "Is Active", "type": "checkbox"},
                {"name": "Join Date", "type": "date"}
            ]
        }
        
        new_base = base_manager.create_base(
            name="Project Management Demo",
            tables=[task_table_config, user_table_config]
        )
        
        print(f"✅ Created base: {new_base['name']} (ID: {new_base['id']})")
        created_base_id = new_base['id']
        
        # Get schema of the new base
        print("\\n📊 Getting base schema...")
        schema = base_manager.get_base_schema(created_base_id)
        print(f"Base has {len(schema.get('tables', []))} tables:")
        for table in schema.get('tables', []):
            field_count = len(table.get('fields', []))
            print(f"  - {table['name']}: {field_count} fields")
        
        return created_base_id
        
    except Exception as e:
        print(f"❌ Base management error: {e}")
        print("Note: Creating bases requires special permissions in AirTable")
        return None


def demo_table_management():
    """Demonstrate table management operations"""
    
    print("\\n🔧 Table Management Demo")
    print("=" * 40)
    
    access_token = os.getenv("AIRTABLE_ACCESS_TOKEN") or os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    
    if not access_token or not base_id:
        print("⚠️  Need AIRTABLE_ACCESS_TOKEN and AIRTABLE_BASE_ID environment variables")
        return
    
    table_manager = TableManager(access_token, base_id)
    
    try:
        # List existing tables
        print("\\n📋 Listing existing tables...")
        tables = table_manager.list_tables()
        print(f"Found {len(tables)} tables:")
        for table in tables:
            field_count = len(table.get('fields', []))
            print(f"  - {table['name']}: {field_count} fields (ID: {table['id']})")
        
        # Create table from Pydantic model
        print("\\n🆕 Creating table from Pydantic model...")
        
        # This will create a table based on the Task model
        created_table = table_manager.create_table_from_pydantic(
            Task,
            table_name="Demo_Tasks",
            description="Tasks created from Pydantic model"
        )
        
        print(f"✅ Created table: {created_table['name']} (ID: {created_table['id']})")
        
        # Validate model against table  
        print("\\n✅ Validating Task model against created table...")
        validation = table_manager.validate_pydantic_model_against_table(Task, "Demo_Tasks")
        
        if validation['is_valid']:
            print("✅ Model matches table schema perfectly!")
        else:
            print("⚠️  Model/table validation issues:")
            if validation['missing_in_table']:
                print(f"  - Missing in table: {validation['missing_in_table']}")
            if validation['missing_in_model']:
                print(f"  - Missing in model: {validation['missing_in_model']}")
            if validation['type_mismatches']:
                print(f"  - Type mismatches: {validation['type_mismatches']}")
        
        # Create User table  
        print("\\n🆕 Creating User table...")
        user_table = table_manager.create_table_from_pydantic(
            User,
            table_name="Demo_Users",
            description="Users created from Pydantic model"
        )
        print(f"✅ Created table: {user_table['name']} (ID: {user_table['id']})")
        
        return created_table['id'], user_table['id']
        
    except Exception as e:
        print(f"❌ Table management error: {e}")
        return None, None


def demo_model_table_integration():
    """Demonstrate how models can create and manage their own tables"""
    
    print("\\n🔗 Model-Table Integration Demo")
    print("=" * 40)
    
    access_token = os.getenv("AIRTABLE_ACCESS_TOKEN") or os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    
    if not access_token or not base_id:
        print("⚠️  Need AIRTABLE_ACCESS_TOKEN and AIRTABLE_BASE_ID environment variables")
        return
    
    try:
        # Update the Task model config to use our environment
        Task.AirTableConfig.access_token = access_token
        Task.AirTableConfig.base_id = base_id
        Task.AirTableConfig.table_name = "Integrated_Tasks"
        
        # Model creates its own table
        print("\\n🆕 Task model creating its own table...")
        table_result = Task.create_table_in_airtable(
            description="Tasks table created by the model itself"
        )
        print(f"✅ Model created table: {table_result['name']}")
        
        # Now we can use the model normally
        print("\\n📝 Creating sample tasks...")
        task1 = Task.create(
            title="Set up development environment",
            description="Install all required tools and dependencies",
            priority=Priority.HIGH,
            assignee_email="dev@company.com",
            estimated_hours=4.0
        )
        
        task2 = Task.create(
            title="Write unit tests",
            description="Comprehensive test coverage for core functionality", 
            priority=Priority.MEDIUM,
            assignee_email="qa@company.com",
            estimated_hours=8.0
        )
        
        print(f"✅ Created task: {task1.title} (ID: {task1.id})")
        print(f"✅ Created task: {task2.title} (ID: {task2.id})")
        
        # Demonstrate schema validation
        print("\\n✅ Validating model schema...")
        validation = Task.validate_table_schema()
        if validation['is_valid']:
            print("✅ Model schema is perfectly synchronized with AirTable!")
        else:
            print("⚠️  Schema validation issues found")
        
        # Query the created tasks
        print("\\n📊 Querying created tasks...")
        all_tasks = Task.all()
        print(f"Found {len(all_tasks)} total tasks:")
        
        for task in all_tasks:
            print(f"  - {task.title} [{task.status.value}] (Priority: {task.priority.value})")
        
    except Exception as e:
        print(f"❌ Integration error: {e}")


def demo_schema_synchronization():
    """Demonstrate schema synchronization features"""
    
    print("\\n🔄 Schema Synchronization Demo")
    print("=" * 40)
    
    # This demonstrates how to handle evolving models
    class EvolvingTask(AirTableModel):
        """A task model that evolves over time"""
        
        AirTableConfig = AirTableConfig(
            table_name="Evolving_Tasks"
        )
        
        # Original fields
        title: str = AirTableField(airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT)
        status: TaskStatus = AirTableField(default=TaskStatus.PENDING, airtable_field_type=AirTableFieldType.SELECT)
        
        # New field added later
        complexity: Optional[int] = AirTableField(
            default=None,
            description="Task complexity rating (1-10)",
            airtable_field_type=AirTableFieldType.NUMBER
        )
        
        # Another new field
        tags: Optional[str] = AirTableField(
            default=None,
            description="Comma-separated tags",
            airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
        )
    
    access_token = os.getenv("AIRTABLE_ACCESS_TOKEN") or os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    
    if not access_token or not base_id:
        print("⚠️  Need environment variables")
        return
    
    try:
        EvolvingTask.AirTableConfig.access_token = access_token
        EvolvingTask.AirTableConfig.base_id = base_id
        
        # Create initial table with basic fields
        print("\\n🆕 Creating initial table...")
        table_result = EvolvingTask.create_table_in_airtable(
            description="Table that will evolve over time"
        )
        print(f"✅ Created table: {table_result['name']}")
        
        # Now sync the full model (which has additional fields)
        print("\\n🔄 Synchronizing evolved model...")
        sync_result = EvolvingTask.sync_table_schema(
            create_missing_fields=True,
            update_field_types=False
        )
        
        print("📊 Sync Results:")
        results = sync_result['sync_results']
        if results['fields_added']:
            print(f"  ✅ Added fields: {', '.join(results['fields_added'])}")
        if results['fields_updated']:
            print(f"  🔄 Updated fields: {', '.join(results['fields_updated'])}")
        if results['fields_unchanged']:
            print(f"  ➡️ Unchanged fields: {', '.join(results['fields_unchanged'])}")
        if results['warnings']:
            print(f"  ⚠️ Warnings: {results['warnings']}")
        
        print("\\n✅ Schema synchronization complete!")
        
    except Exception as e:
        print(f"❌ Sync error: {e}")


def main():
    """Main demo function"""
    
    print("🚀 AirTable Schema Management Demo")
    print("=" * 50)
    
    access_token = os.getenv("AIRTABLE_ACCESS_TOKEN") or os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    
    if not access_token:
        print("⚠️  Please set AIRTABLE_ACCESS_TOKEN environment variable")
        print("Get your Personal Access Token from:")
        print("https://airtable.com/developers/web/api/authentication")
        print("")
        print("export AIRTABLE_ACCESS_TOKEN='pat_your_token'")
        if not base_id:
            print("export AIRTABLE_BASE_ID='app_your_base'  # Optional for base creation")
        return
    
    print("🔑 Authentication: ✅")
    print(f"🏗️  Base ID: {'✅' if base_id else '❌ (required for table operations)'}")
    print("")
    
    # Run demos
    try:
        # Demo 1: Base management (requires special permissions)
        created_base_id = demo_base_management()
        
        # Demo 2: Table management (requires existing base)
        if base_id:
            task_table_id, user_table_id = demo_table_management()
            
            # Demo 3: Model integration
            demo_model_table_integration()
            
            # Demo 4: Schema synchronization
            demo_schema_synchronization()
        
        print("\\n🎉 All demos completed!")
        print("\\n💡 Key Features Demonstrated:")
        print("  • ✅ Create AirTable bases programmatically")
        print("  • ✅ Create tables from Pydantic models")
        print("  • ✅ Automatic field type mapping")
        print("  • ✅ Schema validation and synchronization")
        print("  • ✅ Model-driven table management")
        print("  • ✅ Support for Enums, complex types, and constraints")
        
    except Exception as e:
        print(f"\\n❌ Demo error: {e}")
        print("\\n💡 Common Issues:")
        print("  • Ensure your PAT has base/table creation permissions")
        print("  • Some operations require workspace admin privileges")
        print("  • Table creation requires an existing base")


if __name__ == "__main__":
    main()
