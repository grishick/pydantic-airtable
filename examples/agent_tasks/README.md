# AI Agent Task Management Example

This example demonstrates how to manage AI agent tasks with sophisticated status tracking, metrics, and business logic.

## 🎯 What This Example Shows

- **Complex Data Models**: Rich models with enums, business logic, and relationships
- **Status Management**: Task lifecycle with proper state transitions
- **Metrics Tracking**: Performance monitoring and statistics
- **Business Logic**: Built-in methods for common operations
- **Advanced Querying**: Complex filtering and data analysis

## 🏃 Quick Start

1. **Set Environment Variables**:
   ```bash
   export AIRTABLE_ACCESS_TOKEN="pat_your_personal_access_token"
   export AIRTABLE_BASE_ID="app_your_base_id"
   ```

2. **Run the Example**:
   ```bash
   python agent_tasks.py
   ```

## 📋 What It Does

1. **Creates sophisticated task models** with status tracking and metrics
2. **Demonstrates task lifecycle** - creation, execution, completion, failure
3. **Shows business logic methods** - start_execution(), complete_execution(), etc.
4. **Tracks performance metrics** - execution time, retry counts, success rates
5. **Generates agent statistics** - productivity analysis and reporting
6. **Handles task relationships** - parent tasks and subtasks

## 🏗️ Model Structure

### AgentTask Model
```python
class AgentTask(AirTableModel):
    # Core Task Info
    name: str
    description: str
    agent_id: str
    
    # Status & Priority
    status: TaskStatus          # Enum: Pending, In Progress, Completed, Failed
    priority: TaskPriority      # Enum: Low, Medium, High, Urgent
    
    # Execution Tracking
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time_seconds: Optional[float]
    retry_count: int
    
    # Results
    output: Optional[str]
    error_message: Optional[str]
    
    # Relationships
    parent_task_id: Optional[str]
```

## 🔄 Business Logic Features

### Task Lifecycle Management
- `start_execution()` - Mark task as started with timestamp
- `complete_execution(output, time)` - Mark as completed with results
- `fail_execution(error)` - Handle task failures
- `retry_execution()` - Reset for retry attempts

### Advanced Querying
- `get_pending_tasks(agent_id)` - Find tasks ready for execution
- `get_failed_tasks(agent_id)` - Identify tasks needing attention
- `get_agent_stats(agent_id)` - Comprehensive performance analysis

### Relationship Management
- `add_subtask()` - Create child tasks
- Parent-child task relationships
- Dependency tracking

## 📊 Analytics & Metrics

The example generates comprehensive statistics:
- **Task Counts**: By status, priority, agent
- **Performance Metrics**: Average execution time, success rates
- **Error Analysis**: Failure patterns and retry statistics
- **Productivity Insights**: Agent workload and efficiency

## 💡 Key Learning Points

- **Enum Integration**: Python enums become AirTable select fields
- **Business Logic**: Rich domain methods built into models
- **State Management**: Proper task lifecycle handling
- **Relationship Modeling**: Parent-child and dependency relationships
- **Performance Tracking**: Built-in metrics and analytics

## 🎨 Advanced Features

### Custom Validation
```python
@validator('execution_time_seconds')
def validate_execution_time(cls, v):
    if v is not None and v < 0:
        raise ValueError('Execution time cannot be negative')
    return v
```

### Dynamic Relationships
```python
def add_subtask(self, name: str, description: str, **kwargs) -> 'AgentTask':
    subtask_data = {
        'name': name,
        'description': description,
        'parent_task_id': self.id,
        **kwargs
    }
    return AgentTask.create(**subtask_data)
```

## 🚀 Production Use Cases

This pattern is perfect for:
- **AI Agent Orchestration**: Managing multiple AI agents and their tasks
- **Workflow Management**: Complex business process automation  
- **Task Queue Systems**: Distributed task processing
- **Performance Monitoring**: Agent productivity and health tracking
- **Error Recovery**: Systematic retry and failure handling

## 📚 Related Examples

- **[Simple Usage](../simple_usage/)**: Basic CRUD operations foundation
- **[Table Management](../table_management/)**: Schema creation and management
- **[Agentic Researcher](../agentic_researcher/)**: Full AI workflow implementation

