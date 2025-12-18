# Agentic Researcher Example

An advanced AI-powered research assistant integrating OpenAI and Airtable.

---

## Overview

This example demonstrates a production-ready application featuring:

- **OpenAI GPT-4 Integration** - AI-powered research planning and execution
- **Real Web Search** - DuckDuckGo search for current information
- **Structured Data Management** - Research tasks, steps, and results in Airtable
- **Interactive CLI** - Command-line interface for research workflows
- **Customizable Prompts** - External YAML-based prompt templates

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Agentic Researcher                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │   OpenAI     │    │   Research   │    │  Airtable  │ │
│  │   GPT-4o     │◄──►│   Engine     │◄──►│   Models   │ │
│  └──────────────┘    └──────────────┘    └────────────┘ │
│         │                   │                   │        │
│         │                   │                   │        │
│         ▼                   ▼                   ▼        │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │   Prompts    │    │  Web Search  │    │   Tables   │ │
│  │   (YAML)     │    │ (DuckDuckGo) │    │ Tasks/     │ │
│  └──────────────┘    └──────────────┘    │ Steps/     │ │
│                                          │ Results    │ │
│                                          └────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Data Models

### ResearchTask

```python
class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"

class ResearchPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

@airtable_model(table_name="Research Tasks")
class ResearchTask(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: ResearchPriority = ResearchPriority.MEDIUM
    
    requester_email: Optional[str] = None
    deadline: Optional[datetime] = None
    keywords: Optional[str] = None
    
    total_steps: int = 0
    completed_steps: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
```

### ResearchStep

```python
class StepType(str, Enum):
    LITERATURE_SEARCH = "Literature Search"
    DATA_ANALYSIS = "Data Analysis"
    EXPERT_CONSULTATION = "Expert Consultation"
    CASE_STUDY = "Case Study"
    MARKET_RESEARCH = "Market Research"
    TECHNICAL_ANALYSIS = "Technical Analysis"
    SYNTHESIS = "Synthesis"
    VALIDATION = "Validation"

@airtable_model(table_name="Research Steps")
class ResearchStep(BaseModel):
    task_id: str
    step_number: int
    title: str
    description: str
    
    step_type: StepType
    status: StepStatus = StepStatus.PENDING
    research_query: Optional[str] = None
    data_sources: Optional[str] = None
    
    estimated_hours: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
```

### ResearchResult

```python
@airtable_model(table_name="Research Results")
class ResearchResult(BaseModel):
    task_id: str
    step_id: Optional[str] = None
    title: str
    
    content: str
    summary: Optional[str] = None
    key_insights: Optional[str] = None
    
    confidence_score: Optional[float] = None
    sources: Optional[str] = None
    
    tags: Optional[str] = None
    is_final_summary: bool = False
    follow_up_questions: Optional[str] = None
```

---

## Research Workflow

### 1. Task Creation

```python
task = await researcher.create_research_task(
    title="Impact of AI on Software Development",
    description="Analyze how AI tools affect developer productivity",
    priority=ResearchPriority.HIGH
)
```

### 2. Step Planning (AI-Powered)

The AI generates research steps:

```
Step 1: Literature Search
  - Query: "AI developer productivity research 2024"
  - Sources: Academic databases, industry reports

Step 2: Market Research
  - Query: "AI coding assistant market share"
  - Sources: Market reports, news articles

Step 3: Case Studies
  - Query: "Companies using AI development tools"
  - Sources: Case studies, interviews

Step 4: Technical Analysis
  - Query: "AI code generation capabilities"
  - Sources: Tool documentation, benchmarks

Step 5: Synthesis
  - Combine findings into actionable insights
```

### 3. Step Execution

Each step:
1. Conducts web search based on query
2. AI analyzes search results
3. Generates structured findings
4. Stores results in Airtable

### 4. Final Summary

AI synthesizes all findings into:
- Executive summary
- Key insights
- Recommendations
- Areas for further research

---

## Running the Example

### Prerequisites

```bash
# Required
pip install openai>=2.13.0

# Environment variables
export OPENAI_API_KEY="sk-your-key"
export AIRTABLE_ACCESS_TOKEN="pat_your_token"
export AIRTABLE_BASE_ID="appYourBase"  # Optional - creates new if not set
```

### Interactive Mode

```bash
cd examples/agentic_researcher
pip install -r requirements.txt
python agentic_researcher.py --interactive
```

```
🔬 Agentic Researcher - Interactive Mode

Commands:
  new     - Create new research task
  list    - List all tasks
  run     - Execute research for a task
  ask     - Ask questions about research
  summary - View research summary
  quit    - Exit

> new
Enter research topic: Impact of AI on Healthcare
Enter description: Analyze AI applications in diagnostics and treatment

✅ Created task: rec123456
```

### Demo Mode

```bash
python agentic_researcher.py --demo
```

Runs automated demonstration of full research workflow.

---

## Customizable Prompts

All AI prompts are in external YAML files:

```
prompts/
├── keywords_extraction.yaml
├── research_steps_definition.yaml
├── research_execution.yaml
├── final_summary.yaml
└── qa_answering.yaml
```

### Example: research_execution.yaml

```yaml
system_template: |
  You are a {step_type_lower} specialist conducting research.
  Provide thorough, well-sourced analysis.

user_template: |
  Research Task: {task_title}
  Description: {task_description}
  
  Current Step: {step_title}
  Step Type: {step_type}
  Query: {research_query}
  
  Research Data:
  {research_data}
  
  Please analyze and provide:
  1. Key findings
  2. Supporting evidence
  3. Confidence assessment
  4. Recommended next steps
```

### Customization

Edit YAML files to:
- Change AI tone and style
- Add domain-specific instructions
- Modify output format
- Include additional context

---

## Key Features

### Real Web Search

```python
# Automatic search based on step type
research_data = await tools.conduct_research(
    step_type="Literature Search",
    query="machine learning trends 2024"
)

# Returns actual search results:
# - Title, URL, snippet for each result
# - Formatted for AI analysis
```

### Context-Aware Q&A

```python
answer = await researcher.answer_question(
    "What are the main productivity benefits?",
    task_id="rec123456"
)
# Uses all research results as context
```

### Progress Tracking

```python
summary = researcher.get_research_summary(task_id)
# {
#     "task": {...},
#     "progress": "3/5 steps completed",
#     "steps": [...],
#     "results_count": 3,
#     "has_final_summary": False
# }
```

---

## Code Highlights

### Research Engine

```python
class AgenticResearcher:
    async def execute_full_research(self, task: ResearchTask):
        """Execute complete research workflow"""
        
        # 1. Start task
        task.start_research()
        
        # 2. Define steps (AI-powered)
        steps = await self.define_research_steps(task)
        
        # 3. Execute each step
        results = []
        for step in steps:
            result = await self.execute_research_step(step, task)
            results.append(result)
        
        # 4. Create final summary
        final = await self._create_final_summary(task, results)
        
        # 5. Complete task
        task.complete_research()
        
        return final
```

### Prompt Loading

```python
class PromptLoader:
    @staticmethod
    def load_prompt(name: str) -> dict:
        """Load prompt template from YAML file"""
        path = Path(__file__).parent / "prompts" / f"{name}.yaml"
        with open(path) as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def format_prompt(template: str, **kwargs) -> str:
        """Format template with variables"""
        return template.format(**kwargs)
```

---

## Production Considerations

### Error Handling

```python
async def execute_with_retry(self, step):
    for attempt in range(3):
        try:
            return await self.execute_research_step(step)
        except OpenAIError as e:
            if attempt == 2:
                raise
            await asyncio.sleep(2 ** attempt)
```

### Rate Limiting

```python
# Built-in delays for web search
await asyncio.sleep(1)  # Between searches

# OpenAI retry logic
client = OpenAI(max_retries=3, timeout=60.0)
```

### Cost Management

```python
# Use efficient models
model = "gpt-4o"  # Good balance of capability/cost

# Limit response tokens
response = await client.chat.completions.create(
    model=model,
    messages=messages,
    max_tokens=2000  # Limit output
)
```

---

## Use Cases

This pattern is ideal for:

- **Market Research** - Competitive analysis, trend identification
- **Academic Research** - Literature reviews, paper synthesis
- **Due Diligence** - Investment and business analysis
- **Content Creation** - Research-backed articles
- **Knowledge Management** - Building organizational knowledge bases

---

## Next Steps

- [Simple Usage](simple-usage.md) - Start with basics
- [Table Management](table-management.md) - Schema management
- [Best Practices](../advanced/best-practices.md) - Production patterns
