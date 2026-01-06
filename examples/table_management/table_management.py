"""
Table and Base Management Example

This example demonstrates how to create Airtable bases and tables
directly from Pydantic models, and manage table schemas using the
streamlined pydantic-airtable API.

Features demonstrated:
- Field type detection
- Automatic table creation from models
- LINKED_RECORD fields for relating tables (Tasks -> Projects)
- CRUD operations with complex models
- Table schema management
"""

import sys
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel
from dotenv import load_dotenv

# Add parent directory to path for local development
sys.path.insert(0, "../../")

from pydantic_airtable import (
    airtable_model, 
    configure_from_env, 
    airtable_field,
    AirtableFieldType,
    AirtableManager,
    AirtableConfig,
    APIError
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


# Global variable to store Projects table ID for linked record field
# This will be set after the Projects table is created
_projects_table_id: Optional[str] = None


def get_projects_table_id() -> Optional[str]:
    """Get the Projects table ID (set after table creation)"""
    return _projects_table_id


# Example 1: Simple Task Model with Field Type Detection and Project Link
@airtable_model(table_name="Tasks")
class Task(BaseModel):
    """Task model with automatic field type detection and project link"""
    
    title: str                                  # -> SINGLE_LINE_TEXT
    description: Optional[str] = None           # -> LONG_TEXT (detected from name)
    status: TaskStatus = TaskStatus.PENDING     # -> SELECT (enum auto-detected)
    priority: Priority = Priority.MEDIUM        # -> SELECT (enum auto-detected)
    completed: bool = False                     # -> CHECKBOX
    due_date: Optional[datetime] = None         # -> DATETIME
    created_at: Optional[datetime] = None       # -> DATETIME
    
    # Manual override for specific field configuration
    tags: Optional[str] = airtable_field(
        field_type=AirtableFieldType.MULTI_SELECT,
        choices=["urgent", "important", "work", "personal", "review"],
        default=None
    )
    
    # LINKED_RECORD field - links tasks to projects
    # Note: linked_table_id must be set after Projects table is created
    # This field stores a list of record IDs from the Projects table
    project_ids: Optional[List[str]] = airtable_field(
        field_type=AirtableFieldType.LINKED_RECORD,
        field_name="Projects",  # Display name in Airtable
        default=None
    )


# Example 2: Employee Model with Field Type Detection
@airtable_model(table_name="Employees")
class Employee(BaseModel):
    """Employee model demonstrating field type detection"""
    
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
        field_type=AirtableFieldType.CURRENCY,
        default=None
    )
    completion_rate: Optional[float] = airtable_field(
        field_type=AirtableFieldType.PERCENT,
        default=None
    )
    status: str = airtable_field(
        field_type=AirtableFieldType.SELECT,
        choices=["Planning", "Active", "On Hold", "Completed"],
        default="Planning"
    )
    team_size: Optional[int] = None      # -> NUMBER
    start_date: Optional[datetime] = None # -> DATETIME
    end_date: Optional[datetime] = None   # -> DATETIME
    
    # Note: When Tasks has a LINKED_RECORD to Projects, Airtable automatically
    # creates an inverse "Tasks" field in the Projects table. This field is
    # automatically ignored by pydantic-airtable (extra='ignore' in model config).
    # If you want to access it, you can add a field like:
    #
    # task_ids: Optional[List[str]] = airtable_field(
    #     field_type=AirtableFieldType.LINKED_RECORD,
    #     field_name="Tasks",
    #     read_only=True,
    #     default=None,
    #     alias="Tasks"
    # )


def demonstrate_table_creation():
    """
    Demonstrate automatic table creation from models.
    
    Creates tables in the correct order to handle LINKED_RECORD dependencies:
    1. Projects table (no dependencies)
    2. Employees table (no dependencies)
    3. Tasks table (depends on Projects for LINKED_RECORD field)
    """
    global _projects_table_id
    
    print("\n" + "="*60)
    print("🏗️  TABLE CREATION DEMONSTRATION")
    print("="*60)
    
    print("\n💡 Creating tables in order to handle LINKED_RECORD dependencies...")
    print("   Projects → Employees → Tasks (Tasks links to Projects)")
    
    failed_tables = []
    
    # Step 1: Create Projects table first (Tasks will link to it)
    print(f"\n📋 Step 1: Creating Projects table...")
    projects_table_id = _create_or_get_table(Project, "Projects", failed_tables)
    
    if projects_table_id:
        _projects_table_id = projects_table_id
        print(f"   📎 Stored Projects table ID for LINKED_RECORD: {projects_table_id}")
        
        # Update Task model's linked_table_id for the project_ids field
        _update_task_linked_table_id(projects_table_id)
    
    # Step 2: Create Employees table (no dependencies)
    print(f"\n📋 Step 2: Creating Employees table...")
    _create_or_get_table(Employee, "Employees", failed_tables)
    
    # Step 3: Create Tasks table (with LINKED_RECORD to Projects)
    print(f"\n📋 Step 3: Creating Tasks table (with link to Projects)...")
    _create_or_get_table(Task, "Tasks", failed_tables)
    
    # Return success status
    if failed_tables:
        print(f"\n⚠️  Failed to set up tables: {', '.join(failed_tables)}")
        return False
    else:
        print(f"\n✅ All tables set up successfully!")
        return True


def _create_or_get_table(model_class, table_name: str, failed_tables: list) -> Optional[str]:
    """
    Create a table or get existing table ID.
    
    Checks the base schema to see if table exists (more efficient than
    fetching records). Creates the table if it doesn't exist.
    
    Returns:
        Table ID if successful, None otherwise
    """
    import time
    
    try:
        # Check base schema to see if table already exists
        config = AirtableConfig.from_env()
        manager = AirtableManager(config)
        schema = manager.get_base_schema()
        
        # Look for table in schema
        for table in schema.get('tables', []):
            if table['name'] == table_name:
                table_id = table['id']
                record_count = len(table.get('fields', []))
                print(f"✅ {table_name} table already exists")
                print(f"   Table ID: {table_id} ({record_count} fields)")
                return table_id
        
        # Table not found in schema - create it
        print(f"ℹ️  {table_name} table does not exist yet")
        print(f"🔧 Creating {table_name} table from model definition...")
        
        result = model_class.create_table()
        table_id = result.get('id', None)
        print(f"✅ Created {table_name} table successfully!")
        print(f"   Table ID: {table_id}")
        
        # Wait a moment for table to be ready
        time.sleep(1)
        
        return table_id
        
    except APIError as e:
        print(f"❌ API error while checking/creating {table_name} table: {e}")
        print(f"   Status code: {e.status_code}")
        failed_tables.append(table_name)
        return None
    
    except Exception as e:
        print(f"❌ Unexpected error for {table_name} table: {e}")
        print(f"   Error type: {type(e).__name__}")
        failed_tables.append(table_name)
        return None


def _update_task_linked_table_id(projects_table_id: str):
    """
    Update the Task model's project_ids field with the Projects table ID.
    
    This is necessary because the LINKED_RECORD field needs to know which
    table to link to, and that table ID is only available after creation.
    """
    # Access the field info and update the linked_table_id
    field_info = Task.model_fields.get('project_ids')
    if field_info and field_info.json_schema_extra:
        if isinstance(field_info.json_schema_extra, dict):
            field_info.json_schema_extra['linked_table_id'] = projects_table_id
            print(f"   ✅ Updated Task.project_ids with linked_table_id")


def demonstrate_crud_operations() -> bool:
    """
    Demonstrate CRUD operations with the new models including LINKED_RECORD.
    
    Returns:
        True if all operations succeeded, False otherwise
    """
    success = True
    
    print("\n" + "="*60)
    print("📝 CRUD OPERATIONS DEMONSTRATION") 
    print("="*60)
    
    # Create sample project first (so we can link tasks to it)
    print("\n1️⃣ Creating sample project first (for linking tasks)...")
    
    try:
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
        print(f"   Project record ID: {project.id}")
        
    except Exception as project_error:
        print(f"❌ Failed to create project: {project_error}")
        print(f"   Error type: {type(project_error).__name__}")
        project = None
        success = False
    
    # Create sample tasks linked to the project
    print("\n2️⃣ Creating sample tasks (linked to project)...")
    
    # Debug: Show what table name we're using
    print(f"🔍 Debug: Task table name is '{Task._get_table_name()}'")
    
    try:
        # Create task linked to the project using LINKED_RECORD field
        task1 = Task.create(
            title="Design user interface",
            description="Create wireframes and mockups for the new dashboard",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH,
            due_date=datetime(2024, 12, 31),
            # Link to project using record ID (LINKED_RECORD field)
            project_ids=[project.id] if project else None
        )
        
        task2 = Task.create(
            title="Write documentation", 
            description="Complete API documentation and user guides",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            # Also link to the same project
            project_ids=[project.id] if project else None
        )
        
        print(f"✅ Created tasks: {task1.title} and {task2.title}")
        if project:
            print(f"   📎 Both tasks linked to project: {project.name}")
        
    except Exception as task_error:
        print(f"❌ Failed to create tasks: {task_error}")
        print(f"   Error type: {type(task_error).__name__}")
        print("   This might be due to:")
        print("   - Table doesn't exist (creation failed)")
        print("   - Insufficient permissions") 
        print("   - Table name mismatch")
        print("   - LINKED_RECORD field not properly configured")
        return False  # Skip rest of CRUD operations
    
    # Create sample users
    print("\n3️⃣ Creating sample users...")
    
    try:
        employee1 = Employee.create(
            name="Alice Johnson",
            email="alice@example.com",  # Auto-detected as EMAIL type
            phone="555-0123",           # Auto-detected as PHONE type 
            bio="Senior software engineer with 8 years experience",
            website="https://alice.dev",  # Auto-detected as URL type
            is_admin=True,
            salary=95000.0
        )
        
        employee2 = Employee.create(
            name="Bob Smith",
            email="bob@example.com",
            bio="Product manager focused on user experience",
            is_admin=False,
            salary=85000.0
        )
        
        print(f"✅ Created employees: {employee1.name} and {employee2.name}")
    except Exception as user_error:
        print(f"❌ Failed to create users: {user_error}")
        success = False
    
    # Demonstrate querying
    print("\n4️⃣ Demonstrating queries...")
    
    try:
        # Find high priority tasks
        high_priority_tasks = Task.find_by(priority=Priority.HIGH)
        print(f"📊 High priority tasks: {len(high_priority_tasks)}")
        
        # Show linked project info for tasks
        for task in high_priority_tasks:
            if task.project_ids:
                print(f"   📎 Task '{task.title}' linked to {len(task.project_ids)} project(s)")
        
        # Find admin employees
        admin_employees = Employee.find_by(is_admin=True)
        print(f"📊 Admin employees: {len(admin_employees)}")
        
        # Find active projects
        active_projects = Project.find_by(status="Active")
        print(f"📊 Active projects: {len(active_projects)}")
        
        # Multi-field filtering example: find high priority incomplete tasks
        # find_by supports multiple field filters combined with AND logic
        high_priority_incomplete = Task.find_by(priority=Priority.HIGH, completed=False)
        print(f"📊 High priority incomplete tasks: {len(high_priority_incomplete)}")
        
        # Another multi-field example: find in-progress tasks with specific status
        in_progress_tasks = Task.find_by(status=TaskStatus.IN_PROGRESS, completed=False)
        print(f"📊 In-progress tasks (not completed): {len(in_progress_tasks)}")
    except Exception as query_error:
        print(f"❌ Failed during queries: {query_error}")
        success = False
    
    # Demonstrate updates
    print("\n5️⃣ Demonstrating updates...")
    
    try:
        task1.status = TaskStatus.COMPLETED
        task1.completed = True
        task1.save()
        print(f"✅ Marked task '{task1.title}' as completed")
        
        if project:
            project.completion_rate = 0.50
            project.save()
            print(f"✅ Updated project completion rate to 50%")
    except Exception as update_error:
        print(f"❌ Failed during updates: {update_error}")
        success = False
    
    # Demonstrate updating linked records
    print("\n6️⃣ Demonstrating LINKED_RECORD operations...")
    
    # Create another project
    try:
        project2 = Project.create(
            name="API Integration",
            description="Build REST API integrations for third-party services",
            budget=75000.0,
            status="Planning",
            team_size=3
        )
        print(f"✅ Created second project: {project2.name}")
        
        # Update task to link to multiple projects
        if task2.project_ids:
            task2.project_ids.append(project2.id)
        else:
            task2.project_ids = [project2.id]
        task2.save()
        print(f"✅ Updated task '{task2.title}' to link to multiple projects")
        print(f"   📎 Now linked to {len(task2.project_ids)} project(s)")
        
    except Exception as e:
        print(f"⚠️  Could not demonstrate multi-project linking: {e}")
        success = False
    
    return success


def demonstrate_table_management() -> bool:
    """
    Demonstrate advanced table management features.
    
    This function shows how schema synchronization works by:
    1. Listing current tables and their fields
    2. Defining extended models with new fields
    3. Synchronizing the extended models to add new fields to Airtable
    
    Returns:
        True if all operations succeeded, False otherwise
    """
    success = True
    
    print("\n" + "="*60)
    print("⚙️  TABLE MANAGEMENT DEMONSTRATION")
    print("="*60)
    
    # Get the manager
    config = AirtableConfig.from_env()
    manager = AirtableManager(config)
    
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
        success = False
    
    # Demonstrate table synchronization with EXTENDED models
    # This shows how sync can add new fields to existing tables
    print("\n2️⃣ Demonstrating schema evolution with extended models...")
    print("   We'll define extended versions of our models with new fields,")
    print("   then sync them to add those fields to the Airtable tables.")
    
    # Define extended Task model with new fields
    @airtable_model(table_name="Tasks")
    class TaskExtended(BaseModel):
        """Extended Task model with additional fields for schema sync demo"""
        # Original fields
        title: str
        description: Optional[str] = None
        status: TaskStatus = TaskStatus.PENDING
        priority: Priority = Priority.MEDIUM
        completed: bool = False
        due_date: Optional[datetime] = None
        created_at: Optional[datetime] = None
        tags: Optional[str] = airtable_field(
            field_type=AirtableFieldType.MULTI_SELECT,
            choices=["urgent", "important", "work", "personal", "review"],
            default=None
        )
        project_ids: Optional[List[str]] = airtable_field(
            field_type=AirtableFieldType.LINKED_RECORD,
            field_name="Projects",
            default=None
        )
        # NEW FIELDS for sync demonstration
        estimated_hours: Optional[float] = airtable_field(
            field_type=AirtableFieldType.NUMBER,
            default=None
        )
        assigned_to: Optional[str] = None  # Will be detected as SINGLE_LINE_TEXT
        notes: Optional[str] = None        # Will be detected as LONG_TEXT
    
    # Define extended Employee model with new fields
    @airtable_model(table_name="Employees")
    class EmployeeExtended(BaseModel):
        """Extended Employee model with additional fields for schema sync demo"""
        # Original fields
        name: str
        email: str
        phone: Optional[str] = None
        bio: Optional[str] = None
        website: Optional[str] = None
        is_admin: bool = False
        salary: Optional[float] = None
        # NEW FIELDS for sync demonstration
        department: Optional[str] = None   # Will be SINGLE_LINE_TEXT
        hire_date: Optional[datetime] = None  # Will be DATETIME
        is_active: bool = True             # Will be CHECKBOX
    
    # Define extended Project model with new fields  
    @airtable_model(table_name="Projects")
    class ProjectExtended(BaseModel):
        """Extended Project model with additional fields for schema sync demo"""
        # Original fields
        name: str
        description: str
        budget: Optional[float] = airtable_field(
            field_type=AirtableFieldType.CURRENCY,
            default=None
        )
        completion_rate: Optional[float] = airtable_field(
            field_type=AirtableFieldType.PERCENT,
            default=None
        )
        status: str = airtable_field(
            field_type=AirtableFieldType.SELECT,
            choices=["Planning", "Active", "On Hold", "Completed"],
            default="Planning"
        )
        team_size: Optional[int] = None
        start_date: Optional[datetime] = None
        end_date: Optional[datetime] = None
        # NEW FIELDS for sync demonstration
        project_code: Optional[str] = None    # Will be SINGLE_LINE_TEXT
        risk_level: Optional[str] = airtable_field(
            field_type=AirtableFieldType.SELECT,
            choices=["Low", "Medium", "High", "Critical"],
            default=None
        )
        notes: Optional[str] = None           # Will be detected as LONG_TEXT
    
    print("\n   📋 Extended models defined with new fields:")
    print("      • TaskExtended: +estimated_hours, +assigned_to, +notes")
    print("      • EmployeeExtended: +department, +hire_date, +is_active")
    print("      • ProjectExtended: +project_code, +risk_level, +notes")
    
    # Sync extended models
    extended_models = [
        ("Tasks", TaskExtended),
        ("Employees", EmployeeExtended),
        ("Projects", ProjectExtended)
    ]
    
    print("\n3️⃣ Synchronizing extended models to add new fields...")
    
    for table_name, model_class in extended_models:
        print(f"\n🔄 Synchronizing {table_name} table with extended model...")
        
        try:
            sync_result = model_class.sync_table(
                create_missing_fields=True,
                update_field_types=False
            )
            
            fields_created = sync_result.get('fields_created', [])
            fields_updated = sync_result.get('fields_updated', [])
            fields_skipped = sync_result.get('fields_skipped', [])
            
            print(f"✅ Sync completed for {table_name}:")
            print(f"   📝 Fields created: {len(fields_created)}")
            if fields_created:
                for field in fields_created:
                    print(f"      • {field}")
            print(f"   🔄 Fields updated: {len(fields_updated)}")
            print(f"   ⏭️  Fields skipped: {len(fields_skipped)}")
            
        except Exception as e:
            print(f"❌ Sync failed for {table_name}: {e}")
            success = False
    
    # Show final schema
    print("\n4️⃣ Verifying updated table schemas...")
    try:
        updated_schema = manager.get_base_schema()
        for table in updated_schema.get('tables', []):
            if table['name'] in ['Tasks', 'Employees', 'Projects']:
                fields = table.get('fields', [])
                print(f"\n   📋 {table['name']}: {len(fields)} fields")
                for field in fields[:10]:  # Show first 10 fields
                    print(f"      • {field['name']} ({field['type']})")
                if len(fields) > 10:
                    print(f"      ... and {len(fields) - 10} more fields")
    except Exception as e:
        print(f"⚠️  Could not verify schemas: {e}")
    
    return success


def demonstrate_base_operations() -> bool:
    """
    Demonstrate base-level operations.
    
    Returns:
        True if all operations succeeded, False otherwise
    """
    success = True
    
    print("\n" + "="*60)
    print("🗄️  BASE OPERATIONS DEMONSTRATION") 
    print("="*60)
    
    config = AirtableConfig.from_env()
    manager = AirtableManager(config)
    
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
        success = False
    
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
        success = False
    
    return success


def main():
    """Main demonstration function"""
    
    print("🚀 Pydantic Airtable - Table Management Example")
    print("=" * 60)
    
    print("\nThis example demonstrates:")
    print("✨ Field type detection")
    print("🏗️  Automatic table creation from models") 
    print("🔗 LINKED_RECORD fields for relating tables (Tasks → Projects)")
    print("📝 CRUD operations with complex models")
    print("⚙️  Table schema management")
    print("🗄️  Base-level operations")
    
    # Track overall success
    all_success = True
    
    try:
        # Run all demonstrations and track success
        table_setup_success = demonstrate_table_creation()
        if not table_setup_success:
            all_success = False
        
        # Only proceed with CRUD if tables were set up successfully
        if table_setup_success:
            crud_success = demonstrate_crud_operations()
            if not crud_success:
                all_success = False
            
            mgmt_success = demonstrate_table_management()
            if not mgmt_success:
                all_success = False
            
            base_success = demonstrate_base_operations()
            if not base_success:
                all_success = False
        else:
            print("\n⚠️  Skipping CRUD operations due to table setup failures")
            print("🔧 Please check your Airtable permissions and try again")
            all_success = False
        
        # Print appropriate summary based on success
        print("\n" + "="*60)
        if all_success:
            print("🎉 All demonstrations completed successfully!")
            print("="*60)
            
            print("\n💡 Key takeaways:")
            print("   ✅ Models automatically detect field types from names and Python types")
            print("   ✅ Tables can be created directly from model definitions")
            print("   ✅ LINKED_RECORD fields enable relationships between tables")
            print("   ✅ Tasks can be linked to Projects using record IDs")
            print("   ✅ CRUD operations work seamlessly with complex data types")
            print("   ✅ Schema synchronization keeps Airtable in sync with model changes")
            print("   ✅ Base operations provide visibility into your Airtable workspace")
        else:
            print("⚠️  Demonstrations completed with some errors")
            print("="*60)
            print("\n💡 Review the errors above and check:")
            print("   - Ensure .env file has AIRTABLE_ACCESS_TOKEN and AIRTABLE_BASE_ID")
            print("   - Verify your Personal Access Token has the required permissions")
            print("   - Check that your base ID is correct and accessible")
            print("   - For LINKED_RECORD issues, ensure Projects table exists first")
        
    except Exception as e:
        print(f"\n❌ Unexpected error during demonstration: {e}")
        print("\n💡 Common issues:")
        print("   - Ensure .env file has AIRTABLE_ACCESS_TOKEN and AIRTABLE_BASE_ID")
        print("   - Verify your Personal Access Token has the required permissions")
        print("   - Check that your base ID is correct and accessible")


if __name__ == "__main__":
    main()