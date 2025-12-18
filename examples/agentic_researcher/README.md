# Agentic Researcher Example

This example demonstrates an AI-powered research assistant that combines OpenAI's language models with Airtable's database capabilities to conduct structured research workflows.

## 🎯 What This Example Shows

- **Real Web Search**: Conducts actual web searches using DuckDuckGo for current information
- **AI-Powered Analysis**: GPT-4o analyzes real research data instead of generating content
- **Multiple Research Types**: Literature search, market research, news analysis, technical research
- **Structured Data Management**: Research tasks, steps, and results in Airtable
- **Automatic Infrastructure**: Creates bases and tables automatically
- **Interactive Q&A**: Answer questions using real research findings as context
- **Full Lifecycle Management**: From data gathering to final summarization
- **Customizable Prompts**: All AI prompts stored in external YAML files for easy customization

## 🏃 Quick Start

### Prerequisites
```bash
# Install latest OpenAI library
pip install openai>=2.13.0

# Set environment variables
export OPENAI_API_KEY="sk-your-openai-api-key"
export AIRTABLE_ACCESS_TOKEN="pat_your_personal_access_token"
# AIRTABLE_BASE_ID is optional - will create new base if not provided
```

### Run the Example
```bash
# First time setup
cp .env.example .env
# Edit .env file with your API keys

# Then run:
python agentic_researcher.py --demo      # Automated demo
python agentic_researcher.py --interactive  # Interactive mode
```

## 📋 What It Does

### 1. Automated Research Workflow
1. **Task Creation**: User provides research topic
2. **Step Planning**: AI breaks down research into actionable steps
3. **Step Execution**: AI conducts each research step systematically
4. **Result Storage**: All findings stored in structured Airtable records
5. **Summarization**: Final comprehensive summary generation
6. **Q&A System**: Answer questions using research context

### 2. Infrastructure Management
- **Automatic Base Creation**: Creates Airtable base if none provided
- **Table Generation**: Creates three interconnected tables from Pydantic models
- **Schema Management**: Handles field types, enums, and relationships automatically

### 3. AI Integration
- **Latest OpenAI API**: Uses OpenAI SDK
- **Structured Prompts**: Sophisticated prompt engineering for research tasks
- **JSON Response Parsing**: Handles structured AI responses reliably
- **Error Recovery**: Graceful fallbacks for API failures

## 🏗️ Data Architecture

### Three Core Models

#### ResearchTask
```python
class ResearchTask(AirtableModel):
    # Core Information
    title: str
    description: str
    status: TaskStatus          # Pending, In Progress, Completed, Failed
    priority: ResearchPriority  # Low, Medium, High, Urgent
    
    # Metadata
    requester_email: Optional[str]
    deadline: Optional[datetime]
    keywords: Optional[str]
    
    # Progress Tracking
    total_steps: int
    completed_steps: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
```

#### ResearchStep
```python
class ResearchStep(AirtableModel):
    # Identification
    task_id: str
    step_number: int
    title: str
    description: str
    
    # Configuration
    step_type: StepType         # Literature Search, Data Analysis, etc.
    status: StepStatus          # Pending, In Progress, Completed, etc.
    research_query: Optional[str]
    data_sources: Optional[str]
    
    # Execution Tracking
    estimated_hours: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
```

#### ResearchResult
```python
class ResearchResult(AirtableModel):
    # Identification
    task_id: str
    step_id: Optional[str]
    title: str
    
    # Content
    content: str                # Detailed findings
    summary: Optional[str]      # Brief summary
    key_insights: Optional[str] # Bullet points
    
    # Quality Metrics
    confidence_score: Optional[float]  # 0-10 rating
    sources: Optional[str]             # JSON format
    
    # Metadata
    tags: Optional[str]
    is_final_summary: bool
    follow_up_questions: Optional[str]
```

## 🤖 AI Research Engine

### Step Planning
```python
async def define_research_steps(self, task: ResearchTask) -> List[ResearchStep]:
    """AI creates 5-10 specific research steps based on the task"""
    # Uses sophisticated prompts to break down complex research
    # Returns structured steps with types, queries, and data sources
```

### Step Execution
```python
async def execute_research_step(self, step: ResearchStep) -> ResearchResult:
    """AI conducts individual research step"""
    # Context-aware research using previous findings
    # Generates structured results with confidence scores
    # Handles different step types (literature, analysis, synthesis)
```

### Final Summarization
```python
async def _create_final_summary(self, task: ResearchTask, step_results: List[ResearchResult]) -> ResearchResult:
    """Creates comprehensive final summary"""
    # Synthesizes all findings into executive summary
    # Provides conclusions and recommendations
    # Suggests areas for further research
```

## 🎨 Advanced Features

### Context-Aware Q&A
```python
async def answer_question(self, question: str, task_id: Optional[str] = None) -> str:
    """Answer questions using research findings as context"""
    # Uses all stored research results as knowledge base
    # Cites sources and confidence levels
    # Suggests additional research if needed
```

### Progress Tracking
```python
def get_research_summary(self, task_id: str) -> Dict[str, Any]:
    """Comprehensive research status and metrics"""
    # Task progress and completion status
    # Step-by-step execution details
    # Results count and final summary availability
```

### Business Logic Integration
```python
# Built into models
task.start_research()
task.complete_research()
step.start_step()
step.complete_step()
result.is_final_summary = True
```

## 🔄 Example Research Workflow

### 1. Task Creation
```python
task = await researcher.create_research_task(
    title="AI Impact on Software Development",
    description="Analyze productivity trends and developer tools",
    priority=ResearchPriority.HIGH
)
```

### 2. AI Planning
```
AI generates steps like:
1. Literature Search - Recent studies on AI developer tools
2. Market Analysis - Current AI coding assistant adoption
3. Case Studies - Productivity improvements in real teams
4. Technical Analysis - Tool capabilities and limitations
5. Synthesis - Overall impact assessment
```

### 3. Execution
```python
final_summary = await researcher.execute_full_research(task)
# AI executes each step, storing findings in Airtable
```

### 4. Q&A
```python
answer = await researcher.answer_question(
    "What are the key productivity benefits?", 
    task.id
)
```

## 💡 Key Learning Points

- **AI Workflow Orchestration**: Managing complex AI tasks with structured data
- **Prompt Engineering**: Sophisticated prompts for research planning and execution
- **Data Persistence**: Storing AI outputs in structured, queryable format
- **Context Management**: Using previous findings to inform subsequent research
- **Error Resilience**: Handling AI API failures gracefully

## 🚀 Production Use Cases

This pattern is perfect for:
- **Market Research**: Automated competitive analysis and trend identification
- **Academic Research**: Literature reviews and synthesis
- **Due Diligence**: Investment and business analysis
- **Content Creation**: Research-backed article and report generation
- **Knowledge Management**: Building organizational knowledge bases

## 🔧 Configuration Options

### Research Step Types
- **Literature Search**: Academic and industry publications
- **Data Analysis**: Quantitative analysis and statistics
- **Expert Consultation**: Simulated expert interviews
- **Case Studies**: Real-world implementation examples
- **Market Research**: Industry trends and competitive analysis
- **Technical Analysis**: Tool and technology evaluation
- **Synthesis**: Combining findings into insights
- **Validation**: Fact-checking and verification

### AI Model Configuration
```python
# Uses latest OpenAI capabilities
model="gpt-4o"           # Most capable model
timeout=60.0             # Reliable timeout handling
max_retries=3           # Built-in retry logic
temperature=0.7         # Balanced creativity/accuracy
```

### Customizable AI Prompts

All AI prompts are externalized in YAML files for easy customization:

```
prompts/
├── README.md                    # Complete customization guide
├── keywords_extraction.yaml     # Extract keywords from descriptions
├── research_steps_definition.yaml # Plan research methodology
├── research_execution.yaml      # Execute research steps
├── final_summary.yaml          # Synthesize findings
└── qa_answering.yaml           # Answer contextual questions
```

**Key Benefits:**
- **No Code Changes**: Modify prompts without touching Python code
- **Version Control**: Track prompt changes over time
- **A/B Testing**: Easy to experiment with different approaches
- **Role Specialization**: Customize AI behavior for different research types

**Example Customization:**
```yaml
# research_execution.yaml
system_template: "You are a {step_type_lower} specialist with 10+ years experience..."
user_template: |
  Research Project: {task_title}
  Methodology: {step_type}
  Your task: {step_description}
  
  Please provide analysis with:
  - Industry-specific insights
  - Data-driven conclusions
  - Actionable recommendations
```

See `prompts/README.md` for complete documentation and template variables.

## 🌐 Real Research Capabilities

### Web Search Integration
The system conducts **actual web searches** using DuckDuckGo to gather current information:

```python
# Automatic research type detection
research_data = await tools.conduct_research(
    step_type="Literature Search",    # Searches academic sources
    query="machine learning trends 2024"
)

# Different research types use different search strategies:
# - Literature Search: scholar.google.com, pubmed, arxiv, researchgate
# - Market Research: market reports, industry analysis + recent news
# - Technical Analysis: documentation, specifications, technical sources
# - News Search: recent articles and developments
```

### Real Data Analysis
Instead of generating content, the AI **analyzes real search results**:

```yaml
# The AI receives actual search data like this:
RESEARCH RESULTS FOR: machine learning trends 2024
Sources Found: 10
Timestamp: 2024-12-06T10:30:15

SOURCE SUMMARIES:
1. Machine Learning Trends 2024: Industry Report
   URL: https://research.example.com/ml-trends-2024
   Summary: Comprehensive analysis of ML adoption across industries...

2. Recent Advances in Deep Learning Applications
   URL: https://scholar.google.com/paper/12345
   Summary: Academic paper on latest deep learning breakthroughs...
```

### Fallback Mechanisms
- **Rate Limiting**: Automatic delays between searches to respect API limits
- **Error Handling**: Graceful fallback when search APIs are unavailable
- **Research Framework**: Structured research approach when live data isn't accessible
- **Source Verification**: AI cites specific sources found during research

### Research Types Supported
| Type | Search Strategy | Sources |
|------|----------------|---------|
| **Literature Search** | Academic databases | Google Scholar, PubMed, arXiv |
| **Market Research** | Market reports + news | Industry sites, recent news |
| **Technical Analysis** | Documentation | Technical specs, docs |
| **Expert Consultation** | Expert opinions | Interviews, quotes, analysis |
| **Case Study** | Real examples | Implementation cases |
| **News Analysis** | Current events | Recent articles |

## 🎯 Interactive Features

### CLI Interface
```bash
python agentic_researcher.py --interactive
```

**Features:**
- Create research tasks interactively
- Execute research with real-time progress
- Ask questions about findings
- View research summaries and statistics

### Automated Demo
```bash
python agentic_researcher.py --demo
```

**Demonstrates:**
- Complete research workflow
- AI planning and execution
- Q&A system capabilities
- Airtable integration

## 📊 Research Analytics

The system provides comprehensive analytics:
- **Task Progress**: Real-time completion tracking
- **Step Analysis**: Execution time and success rates
- **Confidence Metrics**: AI confidence in findings
- **Source Tracking**: Research source attribution
- **Quality Assessment**: Built-in validation and scoring

## 🔗 Integration Points

### Airtable Integration
- **Automatic base/table creation**
- **Real-time progress updates**
- **Rich data relationships**
- **Query and reporting capabilities**

### OpenAI Integration
- **Latest API patterns**
- **Structured response handling**
- **Error recovery and retries**
- **Cost-effective prompt design**

## 📚 Related Examples

- **[Simple Usage](../simple_usage/)**: Foundation patterns
- **[Table Management](../table_management/)**: Schema creation and evolution

---

**This example represents the pinnacle of the library's capabilities**, combining AI, structured data, and workflow management into a production-ready research assistant.
