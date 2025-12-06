"""
AI Agent Task Management Example

This example demonstrates how to use pydantic-airtable to manage AI agent tasks,
tracking task definitions, outputs, status, and execution metadata in AirTable.
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import Field, validator

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from pydantic_airtable import AirTableModel, AirTableConfig, AirTableField
from pydantic_airtable.fields import AirTableFieldType


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class AgentTask(AirTableModel):
    """
    AI Agent Task model for tracking task execution
    """

    # Configure AirTable connection
    AirTableConfig = AirTableConfig(
        table_name="AI_Agent_Tasks"  # Will use environment variables for access token and base ID
    )

    # Task Definition Fields
    name: str = AirTableField(
        description="Task name/title",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )

    description: str = AirTableField(
        description="Detailed task description",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )

    agent_id: str = AirTableField(
        description="ID of the AI agent assigned to this task",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )

    # Task Configuration
    priority: TaskPriority = AirTableField(
        default=TaskPriority.MEDIUM,
        description="Task priority level",
        airtable_field_type=AirTableFieldType.SELECT
    )

    status: TaskStatus = AirTableField(
        default=TaskStatus.PENDING,
        description="Current task status",
        airtable_field_type=AirTableFieldType.SELECT
    )

    parameters: Optional[str] = AirTableField(
        default=None,
        description="Task parameters as JSON string",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )

    # Execution Tracking
    started_at: Optional[datetime] = AirTableField(
        default=None,
        description="When task execution started",
        airtable_field_type=AirTableFieldType.DATETIME
    )

    completed_at: Optional[datetime] = AirTableField(
        default=None,
        description="When task execution completed",
        airtable_field_type=AirTableFieldType.DATETIME
    )

    # Output and Results
    output: Optional[str] = AirTableField(
        default=None,
        description="Task output/results",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )

    error_message: Optional[str] = AirTableField(
        default=None,
        description="Error message if task failed",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )

    # Metrics
    execution_time_seconds: Optional[float] = AirTableField(
        default=None,
        description="Task execution time in seconds",
        airtable_field_type=AirTableFieldType.NUMBER
    )

    retry_count: int = AirTableField(
        default=0,
        description="Number of retry attempts",
        airtable_field_type=AirTableFieldType.NUMBER
    )

    # Relationships
    parent_task_id: Optional[str] = AirTableField(
        default=None,
        description="ID of parent task (for subtasks)",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )

    # Validation
    @validator('execution_time_seconds')
    def validate_execution_time(cls, v):
        if v is not None and v < 0:
            raise ValueError('Execution time cannot be negative')
        return v

    @validator('retry_count')
    def validate_retry_count(cls, v):
        if v < 0:
            raise ValueError('Retry count cannot be negative')
        return v

    # Business Logic Methods

    def start_execution(self) -> 'AgentTask':
        """Mark task as started"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
        return self.save()

    def complete_execution(self, output: str, execution_time: Optional[float] = None) -> 'AgentTask':
        """Mark task as completed with output"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.output = output

        if execution_time is not None:
            self.execution_time_seconds = execution_time
        elif self.started_at:
            # Calculate execution time if not provided
            duration = datetime.utcnow() - self.started_at
            self.execution_time_seconds = duration.total_seconds()

        return self.save()

    def fail_execution(self, error_message: str, execution_time: Optional[float] = None) -> 'AgentTask':
        """Mark task as failed with error message"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message

        if execution_time is not None:
            self.execution_time_seconds = execution_time
        elif self.started_at:
            duration = datetime.utcnow() - self.started_at
            self.execution_time_seconds = duration.total_seconds()

        return self.save()

    def retry_execution(self) -> 'AgentTask':
        """Reset task for retry"""
        self.retry_count += 1
        self.status = TaskStatus.PENDING
        self.started_at = None
        self.completed_at = None
        self.error_message = None
        return self.save()

    def add_subtask(self, name: str, description: str, **kwargs) -> 'AgentTask':
        """Create a subtask of this task"""
        subtask_data = {
            'name': name,
            'description': description,
            'agent_id': self.agent_id,
            'parent_task_id': self.id,
            'priority': self.priority,  # Inherit parent priority by default
            **kwargs
        }
        return AgentTask.create(**subtask_data)

    # Query Methods

    @classmethod
    def get_pending_tasks(cls, agent_id: Optional[str] = None) -> List['AgentTask']:
        """Get all pending tasks, optionally filtered by agent"""
        filters = {'status': TaskStatus.PENDING}
        if agent_id:
            filters['agent_id'] = agent_id
        return cls.find_by(**filters)

    @classmethod
    def get_in_progress_tasks(cls, agent_id: Optional[str] = None) -> List['AgentTask']:
        """Get all in-progress tasks, optionally filtered by agent"""
        filters = {'status': TaskStatus.IN_PROGRESS}
        if agent_id:
            filters['agent_id'] = agent_id
        return cls.find_by(**filters)

    @classmethod
    def get_failed_tasks(cls, agent_id: Optional[str] = None) -> List['AgentTask']:
        """Get all failed tasks, optionally filtered by agent"""
        filters = {'status': TaskStatus.FAILED}
        if agent_id:
            filters['agent_id'] = agent_id
        return cls.find_by(**filters)

    @classmethod
    def get_tasks_by_priority(cls, priority: TaskPriority, agent_id: Optional[str] = None) -> List['AgentTask']:
        """Get tasks by priority level"""
        filters = {'priority': priority}
        if agent_id:
            filters['agent_id'] = agent_id
        return cls.find_by(**filters)

    @classmethod
    def get_agent_stats(cls, agent_id: str) -> Dict[str, Any]:
        """Get task statistics for an agent"""
        agent_tasks = cls.find_by(agent_id=agent_id)

        stats = {
            'total_tasks': len(agent_tasks),
            'by_status': {},
            'by_priority': {},
            'avg_execution_time': 0.0,
            'success_rate': 0.0,
            'total_retries': 0
        }

        execution_times = []
        completed_tasks = 0
        total_retries = 0

        for task in agent_tasks:
            # Count by status
            status = task.status.value
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

            # Count by priority
            priority = task.priority.value
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1

            # Collect execution times
            if task.execution_time_seconds:
                execution_times.append(task.execution_time_seconds)

            # Count completed tasks
            if task.status == TaskStatus.COMPLETED:
                completed_tasks += 1

            # Sum retries
            total_retries += task.retry_count

        # Calculate averages
        if execution_times:
            stats['avg_execution_time'] = sum(execution_times) / len(execution_times)

        if len(agent_tasks) > 0:
            stats['success_rate'] = completed_tasks / len(agent_tasks)

        stats['total_retries'] = total_retries

        return stats


# Example usage and helper functions

def demo_agent_task_management():
    """
    Demonstrate the AI agent task management system
    
    Make sure to set these environment variables:
    - AIRTABLE_ACCESS_TOKEN: Your AirTable Personal Access Token (PAT)
    - AIRTABLE_BASE_ID: Your AirTable base ID
    
    Note: AIRTABLE_API_KEY is deprecated. Use AIRTABLE_ACCESS_TOKEN instead.
    """

    print("🤖 AI Agent Task Management Demo")
    print("=" * 50)

    # Create some example tasks
    print("📝 Creating example tasks...")

    task1 = AgentTask.create(
        name="Process Customer Emails",
        description="Analyze and categorize incoming customer support emails",
        agent_id="agent_001",
        priority=TaskPriority.HIGH,
        parameters='{"email_folder": "support_inbox", "categories": ["bug", "feature_request", "question"]}'
    )

    task2 = AgentTask.create(
        name="Generate Weekly Report",
        description="Compile performance metrics and generate weekly summary report",
        agent_id="agent_002",
        priority=TaskPriority.MEDIUM,
        parameters='{"report_type": "weekly", "include_charts": true}'
    )

    task3 = AgentTask.create(
        name="Data Quality Check",
        description="Validate data integrity across all datasets",
        agent_id="agent_001",
        priority=TaskPriority.LOW
    )

    print(f"✅ Created task: {task1.name} (ID: {task1.id})")
    print(f"✅ Created task: {task2.name} (ID: {task2.id})")
    print(f"✅ Created task: {task3.name} (ID: {task3.id})")

    # Demonstrate task execution lifecycle
    print("\\n🚀 Simulating task execution...")

    # Start first task
    task1.start_execution()
    print(f"▶️ Started: {task1.name}")

    # Complete first task
    task1.complete_execution(
        output="Processed 45 emails: 12 bugs, 18 feature requests, 15 questions",
        execution_time=23.5
    )
    print(f"✅ Completed: {task1.name} in {task1.execution_time_seconds}s")

    # Start and fail second task
    task2.start_execution()
    print(f"▶️ Started: {task2.name}")

    task2.fail_execution("Database connection timeout during report generation")
    print(f"❌ Failed: {task2.name} - {task2.error_message}")

    # Retry the failed task
    task2.retry_execution()
    print(f"🔄 Retried: {task2.name} (retry count: {task2.retry_count})")

    # Query and display task statistics
    print("\\n📊 Task Statistics:")
    print("-" * 30)

    # Get pending tasks
    pending_tasks = AgentTask.get_pending_tasks()
    print(f"Pending tasks: {len(pending_tasks)}")

    # Get agent statistics
    agent_stats = AgentTask.get_agent_stats("agent_001")
    print(f"Agent 001 stats: {agent_stats}")

    # Get high priority tasks
    high_priority_tasks = AgentTask.get_tasks_by_priority(TaskPriority.HIGH)
    print(f"High priority tasks: {len(high_priority_tasks)}")

    print("\\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    # Run the demo if environment variables are set
    access_token = os.getenv("AIRTABLE_ACCESS_TOKEN") or os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    
    if access_token and base_id:
        if os.getenv("AIRTABLE_API_KEY") and not os.getenv("AIRTABLE_ACCESS_TOKEN"):
            print("⚠️  AIRTABLE_API_KEY is deprecated. Please use AIRTABLE_ACCESS_TOKEN instead.")
            print("See: https://airtable.com/developers/web/api/authentication")
        demo_agent_task_management()
    else:
        print("⚠️  Set AIRTABLE_ACCESS_TOKEN and AIRTABLE_BASE_ID environment variables to run the demo")
        print("Example usage:")
        print("export AIRTABLE_ACCESS_TOKEN='pat....'  # Use Personal Access Token, not API key")
        print("export AIRTABLE_BASE_ID='app....'")
        print("python examples/agent_tasks.py")
        print("")
        print("Note: API keys are deprecated. Get your PAT from:")
        print("https://airtable.com/developers/web/api/authentication")
