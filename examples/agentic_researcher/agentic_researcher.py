"""
Agentic Researcher Example

This example demonstrates how to build an AI research assistant that:
1. Defines research tasks, steps, and results using Pydantic models
2. Creates AirTable bases and tables to store research data
3. Executes research steps using OpenAI
4. Stores all findings in structured AirTable records
5. Provides Q&A capabilities based on research results

Setup:
1. Copy .env.example to .env in this directory (or project root)
2. Fill in your API keys in the .env file
3. Run: python agentic_researcher.py --demo

Environment Variables (set in .env file):
- OPENAI_API_KEY: Your OpenAI API key (required)
- AIRTABLE_ACCESS_TOKEN: Your AirTable Personal Access Token (required)
- AIRTABLE_BASE_ID: Optional existing base ID (will create new base if not provided)

Dependencies:
- openai>=2.8.1 (latest version with improved reliability)
- pydantic>=2.0.0 (for data validation)
- requests>=2.28.0 (for AirTable API)
- python-dotenv>=1.0.0 (for .env file loading)
"""

import os
import json
import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from enum import Enum

import openai
from pydantic import Field, field_validator
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    
    # Look for .env file in current directory, parent directory, and project root
    env_paths = [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent.parent / ".env",
        Path.cwd() / ".env"
    ]
    
    env_loaded = False
    for env_path in env_paths:
        if env_path.exists():
            try:
                load_dotenv(env_path)
                print(f"📁 Loaded environment from: {env_path}")
                env_loaded = True
                break
            except Exception as e:
                print(f"⚠️  Could not load {env_path}: {e}")
                continue
    
    if not env_loaded:
        # Try loading from default location
        load_dotenv()
        
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Falling back to environment variables only.")

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from pydantic_airtable import AirTableModel, AirTableConfig, AirTableField, BaseManager, TableManager
from pydantic_airtable.fields import AirTableFieldType
from .prompt_loader import PromptLoader
from .research_tools import ResearchTools


# Enums for structured data
class TaskStatus(str, Enum):
    """Research task status"""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress" 
    COMPLETED = "Completed"
    FAILED = "Failed"


class StepStatus(str, Enum):
    """Research step status"""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    SKIPPED = "Skipped"


class ResearchPriority(str, Enum):
    """Research priority levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class StepType(str, Enum):
    """Types of research steps"""
    LITERATURE_SEARCH = "Literature Search"
    DATA_ANALYSIS = "Data Analysis" 
    EXPERT_CONSULTATION = "Expert Consultation"
    CASE_STUDY = "Case Study"
    MARKET_RESEARCH = "Market Research"
    TECHNICAL_ANALYSIS = "Technical Analysis"
    SYNTHESIS = "Synthesis"
    VALIDATION = "Validation"


# Pydantic Models for Research Data

class ResearchTask(AirTableModel):
    """Main research task model"""
    
    # Note: AirTableConfig will be set dynamically by AgenticResearcher
    AirTableConfig: Optional['AirTableConfig'] = None
    
    title: str = AirTableField(
        description="Research task title",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    description: str = AirTableField(
        description="Detailed research request",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )
    
    status: TaskStatus = AirTableField(
        default=TaskStatus.PENDING,
        description="Current task status",
        airtable_field_type=AirTableFieldType.SELECT
    )
    
    priority: ResearchPriority = AirTableField(
        default=ResearchPriority.MEDIUM,
        description="Task priority",
        airtable_field_type=AirTableFieldType.SELECT
    )
    
    requester_email: Optional[str] = AirTableField(
        default=None,
        description="Email of person requesting research",
        airtable_field_type=AirTableFieldType.EMAIL
    )
    
    deadline: Optional[datetime] = AirTableField(
        default=None,
        description="Research deadline",
        airtable_field_type=AirTableFieldType.DATETIME
    )
    
    started_at: Optional[datetime] = AirTableField(
        default=None,
        description="When research started",
        airtable_field_type=AirTableFieldType.DATETIME
    )
    
    completed_at: Optional[datetime] = AirTableField(
        default=None,
        description="When research completed",
        airtable_field_type=AirTableFieldType.DATETIME
    )
    
    total_steps: int = AirTableField(
        default=0,
        description="Total number of research steps",
        airtable_field_type=AirTableFieldType.NUMBER
    )
    
    completed_steps: int = AirTableField(
        default=0,
        description="Number of completed steps",
        airtable_field_type=AirTableFieldType.NUMBER
    )
    
    research_budget_hours: Optional[float] = AirTableField(
        default=None,
        description="Estimated research hours",
        airtable_field_type=AirTableFieldType.NUMBER
    )
    
    keywords: Optional[str] = AirTableField(
        default=None,
        description="Research keywords (comma-separated)",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    # Business logic methods
    def start_research(self) -> 'ResearchTask':
        """Mark research as started"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now(timezone.utc)
        return self.save()
    
    def complete_research(self) -> 'ResearchTask':
        """Mark research as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        return self.save()
    
    def update_progress(self, completed_steps: int, total_steps: int) -> 'ResearchTask':
        """Update research progress"""
        self.completed_steps = completed_steps
        self.total_steps = total_steps
        return self.save()


class ResearchStep(AirTableModel):
    """Individual research step model"""
    
    # Note: AirTableConfig will be set dynamically by AgenticResearcher
    AirTableConfig: Optional['AirTableConfig'] = None
    
    task_id: str = AirTableField(
        description="ID of parent research task",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    step_number: int = AirTableField(
        description="Step sequence number",
        airtable_field_type=AirTableFieldType.NUMBER
    )
    
    title: str = AirTableField(
        description="Step title",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    description: str = AirTableField(
        description="Detailed step description",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )
    
    step_type: StepType = AirTableField(
        description="Type of research step",
        airtable_field_type=AirTableFieldType.SELECT
    )
    
    status: StepStatus = AirTableField(
        default=StepStatus.PENDING,
        description="Step status",
        airtable_field_type=AirTableFieldType.SELECT
    )
    
    estimated_hours: Optional[float] = AirTableField(
        default=None,
        description="Estimated hours for this step",
        airtable_field_type=AirTableFieldType.NUMBER
    )
    
    started_at: Optional[datetime] = AirTableField(
        default=None,
        description="When step started",
        airtable_field_type=AirTableFieldType.DATETIME
    )
    
    completed_at: Optional[datetime] = AirTableField(
        default=None,
        description="When step completed", 
        airtable_field_type=AirTableFieldType.DATETIME
    )
    
    research_query: Optional[str] = AirTableField(
        default=None,
        description="Specific research query for this step",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )
    
    data_sources: Optional[str] = AirTableField(
        default=None,
        description="Data sources to use (comma-separated)",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    dependencies: Optional[str] = AirTableField(
        default=None,
        description="Step IDs this step depends on",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    # Business logic methods
    def start_step(self) -> 'ResearchStep':
        """Mark step as started"""
        self.status = StepStatus.IN_PROGRESS
        self.started_at = datetime.now(timezone.utc)
        return self.save()
    
    def complete_step(self) -> 'ResearchStep':
        """Mark step as completed"""
        self.status = StepStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        return self.save()
    
    def fail_step(self, reason: str) -> 'ResearchStep':
        """Mark step as failed"""
        self.status = StepStatus.FAILED
        return self.save()


class ResearchResult(AirTableModel):
    """Research results and findings model"""
    
    # Note: AirTableConfig will be set dynamically by AgenticResearcher
    AirTableConfig: Optional['AirTableConfig'] = None
    
    task_id: str = AirTableField(
        description="ID of parent research task",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    step_id: Optional[str] = AirTableField(
        default=None,
        description="ID of research step (if from specific step)",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    title: str = AirTableField(
        description="Result title",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    content: str = AirTableField(
        description="Research findings content",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )
    
    summary: Optional[str] = AirTableField(
        default=None,
        description="Brief summary of findings",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )
    
    confidence_score: Optional[float] = AirTableField(
        default=None,
        description="Confidence in findings (0-10)",
        airtable_field_type=AirTableFieldType.NUMBER
    )
    
    sources: Optional[str] = AirTableField(
        default=None,
        description="Sources cited (JSON format)",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )
    
    key_insights: Optional[str] = AirTableField(
        default=None,
        description="Key insights from this result",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )
    
    follow_up_questions: Optional[str] = AirTableField(
        default=None,
        description="Questions for further research",
        airtable_field_type=AirTableFieldType.LONG_TEXT
    )
    
    tags: Optional[str] = AirTableField(
        default=None,
        description="Result tags (comma-separated)",
        airtable_field_type=AirTableFieldType.SINGLE_LINE_TEXT
    )
    
    is_final_summary: bool = AirTableField(
        default=False,
        description="Is this the final research summary",
        airtable_field_type=AirTableFieldType.CHECKBOX
    )
    
    @field_validator('confidence_score')
    def validate_confidence_score(cls, v):
        if v is not None and (v < 0 or v > 10):
            raise ValueError('Confidence score must be between 0 and 10')
        return v


class AgenticResearcher:
    """
    AI-powered research assistant that manages the complete research lifecycle
    """
    
    def __init__(self, openai_api_key: str, airtable_access_token: str, base_id: Optional[str] = None):
        """
        Initialize the Agentic Researcher
        
        Args:
            openai_api_key: OpenAI API key
            airtable_access_token: AirTable Personal Access Token
            base_id: Optional existing base ID (will create new base if not provided)
        """
        # Configure OpenAI client with environment-based settings
        timeout = float(os.getenv("OPENAI_TIMEOUT", "60.0"))
        max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
        
        self.openai_client = openai.OpenAI(
            api_key=openai_api_key,
            timeout=timeout,
            max_retries=max_retries
        )
        self.airtable_token = airtable_access_token
        self.base_id = base_id
        self.base_manager = BaseManager(airtable_access_token)
        
        # Initialize prompt loader
        self.prompt_loader = PromptLoader()
        
        # Initialize research tools
        self.research_tools = ResearchTools()
        
        # Initialize base and tables
        self._setup_base_and_tables()
    
    def _setup_base_and_tables(self):
        """Setup AirTable base and tables"""
        try:
            if not self.base_id:
                print("🏗️  No base ID provided - will try to create new base...")
                
                # First, let's check what bases we can access
                try:
                    existing_bases = self.base_manager.list_bases()
                    print(f"📋 Found {len(existing_bases)} existing bases accessible to your token")
                    
                    if existing_bases:
                        print("\\nAvailable bases:")
                        for i, base in enumerate(existing_bases, 1):
                            print(f"  {i}. {base.get('name', 'Unnamed')} (ID: {base.get('id', 'Unknown')})")
                        
                        # For demo mode, automatically use the first base
                        if len(existing_bases) > 0:
                            selected_base = existing_bases[0]
                            self.base_id = selected_base['id']
                            print(f"\\n🎯 Auto-selecting first base for demo: {selected_base['name']}")
                            print(f"✅ Using base: {selected_base['name']} (ID: {self.base_id})")
                        
                except Exception as e:
                    print(f"⚠️  Could not list existing bases: {e}")
                
                # If still no base, try to create one
                if not self.base_id:
                    print("🆕 Attempting to create new base...")
                    
                    try:
                        # Create new base with minimal table
                        new_base = self.base_manager.create_base(
                            name=f"AI Research Base - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                            tables=[
                                {
                                    "name": "Research_Tasks",
                                    "description": "Main research tasks and their metadata",
                                    "fields": [
                                        {
                                            "name": "Title",
                                            "type": "singleLineText"
                                        }
                                    ]
                                }
                            ]
                        )
                        self.base_id = new_base['id']
                        print(f"✅ Successfully created base: {new_base['name']} (ID: {self.base_id})")
                        
                    except Exception as base_error:
                        print(f"❌ Failed to create base: {base_error}")
                        print("")
                        print("🔧 QUICK SOLUTION:")
                        print("1. Go to https://airtable.com")
                        print("2. Click 'Create a base' (any template is fine)")
                        print("3. Copy the base ID from the URL (starts with 'app')")
                        print("4. Add this line to your .env file:")
                        print("   AIRTABLE_BASE_ID=app_your_base_id")
                        print("5. Run the demo again")
                        print("")
                        print("💡 The demo will create the research tables automatically in your base")
                        raise Exception("Please provide an existing AIRTABLE_BASE_ID in .env file")
            
            # Update model configurations
            ResearchTask.AirTableConfig = AirTableConfig(
                access_token=self.airtable_token,
                base_id=self.base_id,
                table_name="Research_Tasks"
            )
            
            ResearchStep.AirTableConfig = AirTableConfig(
                access_token=self.airtable_token,
                base_id=self.base_id,
                table_name="Research_Steps"
            )
            
            ResearchResult.AirTableConfig = AirTableConfig(
                access_token=self.airtable_token,
                base_id=self.base_id,
                table_name="Research_Results"
            )
            
            # Create tables from Pydantic models
            print("📋 Setting up research tables...")
            
            try:
                ResearchTask.create_table_in_airtable(
                    description="Research tasks and project metadata"
                )
                print("✅ Created Research_Tasks table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️  Research_Tasks table already exists")
                else:
                    raise
            
            try:
                ResearchStep.create_table_in_airtable(
                    description="Individual research steps and actions"
                )
                print("✅ Created Research_Steps table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️  Research_Steps table already exists")
                else:
                    raise
            
            try:
                ResearchResult.create_table_in_airtable(
                    description="Research findings, results, and summaries"
                )
                print("✅ Created Research_Results table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️  Research_Results table already exists")
                else:
                    raise
            
            print(f"🎯 Research environment ready! Base ID: {self.base_id}")
            
        except Exception as e:
            print(f"❌ Error setting up base and tables: {e}")
            raise
    
    async def _call_openai(self, messages: List[Dict[str, str]], max_tokens: int = 2000) -> str:
        """Make OpenAI API call with error handling"""
        try:
            # Use configurable model from environment
            model = os.getenv("OPENAI_MODEL", "gpt-4o")
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️  OpenAI API error: {e}")
            return f"Error calling OpenAI API: {str(e)}"
    
    async def create_research_task(
        self, 
        title: str, 
        description: str,
        requester_email: Optional[str] = None,
        priority: ResearchPriority = ResearchPriority.MEDIUM,
        deadline: Optional[datetime] = None,
        research_budget_hours: Optional[float] = None
    ) -> ResearchTask:
        """
        Create a new research task
        
        Args:
            title: Research task title
            description: Detailed research request
            requester_email: Email of requester
            priority: Task priority
            deadline: Optional deadline
            research_budget_hours: Estimated hours for research
            
        Returns:
            Created ResearchTask instance
        """
        print(f"📝 Creating research task: {title}")
        
        # Extract keywords using AI
        system_msg, user_msg = self.prompt_loader.format_keywords_extraction(description)
        
        keywords_response = await self._call_openai([
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ])
        
        keywords = keywords_response.strip() if keywords_response else None
        
        # Create the task
        task = ResearchTask.create(
            title=title,
            description=description,
            requester_email=requester_email,
            priority=priority,
            deadline=deadline,
            research_budget_hours=research_budget_hours,
            keywords=keywords
        )
        
        print(f"✅ Created task: {task.title} (ID: {task.id})")
        if keywords:
            print(f"🔍 Keywords: {keywords}")
        
        return task
    
    async def define_research_steps(self, task: ResearchTask) -> List[ResearchStep]:
        """
        Define research steps for a given task using AI
        
        Args:
            task: ResearchTask to create steps for
            
        Returns:
            List of created ResearchStep instances
        """
        print(f"🔬 Defining research steps for: {task.title}")
        
        system_msg, user_msg = self.prompt_loader.format_research_steps_definition(
            task_title=task.title,
            task_description=task.description,
            task_keywords=task.keywords or 'None provided',
            task_priority=task.priority.value,
            budget_hours=str(task.research_budget_hours or 'No limit specified')
        )
        
        response = await self._call_openai([
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ], max_tokens=3000)
        
        try:
            # Parse JSON response
            steps_data = json.loads(response)
            steps = []
            
            for i, step_info in enumerate(steps_data.get("steps", []), 1):
                step = ResearchStep.create(
                    task_id=task.id,
                    step_number=i,
                    title=step_info.get("title", f"Research Step {i}"),
                    description=step_info.get("description", ""),
                    step_type=StepType(step_info.get("step_type", StepType.LITERATURE_SEARCH.value)),
                    estimated_hours=step_info.get("estimated_hours"),
                    research_query=step_info.get("research_query"),
                    data_sources=step_info.get("data_sources")
                )
                steps.append(step)
                print(f"  ✅ Step {i}: {step.title} ({step.step_type.value})")
            
            # Update task with step count
            task.update_progress(0, len(steps))
            
            print(f"🎯 Created {len(steps)} research steps")
            return steps
            
        except json.JSONDecodeError:
            print("⚠️  Could not parse AI response as JSON, creating basic steps...")
            # Fallback: create basic steps
            basic_steps = [
                {
                    "title": "Initial Literature Review",
                    "description": f"Conduct comprehensive literature review on: {task.description}",
                    "step_type": StepType.LITERATURE_SEARCH,
                    "estimated_hours": 3.0,
                    "research_query": task.description,
                    "data_sources": "academic databases, Google Scholar, industry reports"
                },
                {
                    "title": "Key Findings Analysis",
                    "description": "Analyze and synthesize key findings from literature review",
                    "step_type": StepType.DATA_ANALYSIS,
                    "estimated_hours": 2.0,
                    "research_query": "What are the key findings and trends?",
                    "data_sources": "literature review results"
                },
                {
                    "title": "Final Summary",
                    "description": "Create comprehensive summary of research findings",
                    "step_type": StepType.SYNTHESIS,
                    "estimated_hours": 1.0,
                    "research_query": "What are the main conclusions?",
                    "data_sources": "all previous steps"
                }
            ]
            
            steps = []
            for i, step_info in enumerate(basic_steps, 1):
                step = ResearchStep.create(
                    task_id=task.id,
                    step_number=i,
                    **step_info
                )
                steps.append(step)
            
            task.update_progress(0, len(steps))
            return steps
    
    async def execute_research_step(self, step: ResearchStep) -> ResearchResult:
        """
        Execute a single research step using real data gathering and AI analysis
        
        Args:
            step: ResearchStep to execute
            
        Returns:
            ResearchResult with findings based on real research data
        """
        print(f"🔍 Executing step {step.step_number}: {step.title}")
        print(f"🌐 Gathering real data for: {step.research_query}")
        
        # Start the step
        step.start_step()
        
        try:
            # Get task context
            task = ResearchTask.get(step.task_id)
            
            # Get previous results for context
            previous_results = ResearchResult.find_by(task_id=task.id)
            context = ""
            if previous_results:
                context = "\\n\\nPrevious findings:\\n" + "\\n".join([
                    f"- {result.title}: {result.summary or result.content[:200]}..."
                    for result in previous_results
                ])
            
            # CONDUCT REAL RESEARCH using research tools
            research_data = await self.research_tools.conduct_research(
                step_type=step.step_type.value,
                query=step.research_query or step.title,
                max_results=10
            )
            
            # Format research data for AI analysis
            formatted_research_data = self.research_tools.format_research_for_ai(research_data)
            
            print(f"📊 Found {research_data.get('total_sources', 0)} sources")
            
            # Get AI analysis of the real research data
            system_msg, user_msg = self.prompt_loader.format_research_execution(
                step_type_lower=step.step_type.value.lower(),
                step_number=step.step_number,
                total_steps=task.total_steps,
                task_title=task.title,
                task_description=task.description,
                step_title=step.title,
                step_description=step.description,
                step_type=step.step_type.value,
                research_query=step.research_query,
                research_data=formatted_research_data,
                context=context
            )
            
            response = await self._call_openai([
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ], max_tokens=5000)
            
            try:
                result_data = json.loads(response)
                
                # Include raw research sources in the result
                sources_info = {
                    'raw_research_data': research_data,
                    'ai_cited_sources': result_data.get("sources_cited", []),
                    'total_sources_found': research_data.get('total_sources', 0),
                    'research_timestamp': research_data.get('timestamp', ''),
                    'search_query': research_data.get('query', '')
                }
                
                # Create research result with real data
                result = ResearchResult.create(
                    task_id=task.id,
                    step_id=step.id,
                    title=f"{step.title} - Research Findings",
                    content=result_data.get("content", "No detailed findings available"),
                    summary=result_data.get("summary"),
                    key_insights=result_data.get("key_insights"),
                    confidence_score=result_data.get("confidence_score", 7.0),
                    follow_up_questions=result_data.get("follow_up_questions"),
                    tags=result_data.get("tags"),
                    sources=json.dumps(sources_info)
                )
                
                # Complete the step
                step.complete_step()
                
                # Update task progress
                completed_steps = len(ResearchStep.find_by(task_id=task.id, status=StepStatus.COMPLETED))
                task.update_progress(completed_steps, task.total_steps)
                
                confidence = result_data.get("confidence_score", 7.0)
                print(f"  ✅ Completed step with confidence score: {confidence}/10")
                print(f"  📚 Based on {research_data.get('total_sources', 0)} real sources")
                return result
                
            except json.JSONDecodeError:
                print("⚠️ Could not parse AI analysis as JSON, creating fallback result...")
                
                # Create fallback result with research data summary
                research_summary = f"Research conducted on '{step.research_query}' found {research_data.get('total_sources', 0)} sources. " + formatted_research_data[:500]
                
                result = ResearchResult.create(
                    task_id=task.id,
                    step_id=step.id,
                    title=f"{step.title} - Research Data",
                    content=research_summary,
                    summary=f"Gathered {research_data.get('total_sources', 0)} sources on {step.research_query}",
                    confidence_score=6.0,
                    sources=json.dumps({'raw_research_data': research_data})
                )
                
                step.complete_step()
                completed_steps = len(ResearchStep.find_by(task_id=task.id, status=StepStatus.COMPLETED))
                task.update_progress(completed_steps, task.total_steps)
                
                return result
                
        except Exception as e:
            print(f"  ❌ Step failed: {e}")
            step.fail_step(str(e))
            raise
    
    async def execute_full_research(self, task: ResearchTask) -> ResearchResult:
        """
        Execute complete research workflow
        
        Args:
            task: ResearchTask to execute
            
        Returns:
            Final ResearchResult summary
        """
        print(f"🚀 Starting full research execution for: {task.title}")
        
        # Start the research task
        task.start_research()
        
        try:
            # Define research steps
            steps = await self.define_research_steps(task)
            
            # Execute each step
            step_results = []
            for step in steps:
                result = await self.execute_research_step(step)
                step_results.append(result)
                
                # Brief pause between steps
                await asyncio.sleep(1)
            
            # Create final summary
            print("📊 Creating final research summary...")
            final_summary = await self._create_final_summary(task, step_results)
            
            # Complete the task
            task.complete_research()
            
            print(f"🎉 Research completed! Final summary ID: {final_summary.id}")
            return final_summary
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.save()
            print(f"❌ Research failed: {e}")
            raise
    
    async def _create_final_summary(self, task: ResearchTask, step_results: List[ResearchResult]) -> ResearchResult:
        """Create final research summary from all step results"""
        
        # Compile all findings
        all_findings = "\\n\\n".join([
            f"**{result.title}**\\n{result.content}\\n\\nKey Insights:\\n{result.key_insights or 'None'}"
            for result in step_results
        ])
        
        system_msg, user_msg = self.prompt_loader.format_final_summary(
            task_title=task.title,
            task_description=task.description,
            all_findings=all_findings
        )
        
        response = await self._call_openai([
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ], max_tokens=4000)
        
        try:
            summary_data = json.loads(response)
            
            # Create comprehensive content
            content = f"""
            EXECUTIVE SUMMARY
            {summary_data.get('executive_summary', '')}
            
            KEY FINDINGS
            {summary_data.get('key_findings', '')}
            
            DETAILED ANALYSIS
            {summary_data.get('detailed_analysis', '')}
            
            CONCLUSIONS & RECOMMENDATIONS
            {summary_data.get('conclusions', '')}
            
            FURTHER RESEARCH
            {summary_data.get('further_research', '')}
            """
            
            final_result = ResearchResult.create(
                task_id=task.id,
                title=f"FINAL SUMMARY: {task.title}",
                content=content.strip(),
                summary=summary_data.get('executive_summary'),
                key_insights=summary_data.get('key_findings'),
                confidence_score=summary_data.get('confidence_score', 8.0),
                is_final_summary=True,
                tags="final_summary, research_complete"
            )
            
            return final_result
            
        except json.JSONDecodeError:
            # Fallback summary
            return ResearchResult.create(
                task_id=task.id,
                title=f"FINAL SUMMARY: {task.title}",
                content=response,
                summary="Final research summary generated by AI",
                is_final_summary=True,
                confidence_score=7.0
            )
    
    async def answer_question(self, question: str, task_id: Optional[str] = None) -> str:
        """
        Answer questions about research using stored results as context
        
        Args:
            question: User's question
            task_id: Optional specific task ID to focus on
            
        Returns:
            AI-generated answer based on research context
        """
        print(f"❓ Answering question: {question}")
        
        # Get relevant research context
        if task_id:
            # Focus on specific task
            task = ResearchTask.get(task_id)
            results = ResearchResult.find_by(task_id=task_id)
            context_intro = f"Research Task: {task.title}\\n"
        else:
            # Use all available research
            tasks = ResearchTask.all()
            results = ResearchResult.all()
            context_intro = f"Based on {len(tasks)} research tasks:\\n"
        
        if not results:
            return "No research data available to answer your question."
        
        # Build context from research results
        research_context = context_intro
        for result in results:
            research_context += f"""
            
            Research: {result.title}
            Summary: {result.summary or 'No summary available'}
            Key Insights: {result.key_insights or 'None specified'}
            Confidence: {result.confidence_score or 'Not specified'}/10
            """
        
        qa_prompt = self.prompt_loader.format_qa_answering(research_context, question)
        
        response = await self._call_openai([
            {"role": "system", "content": "You are a research assistant providing accurate answers based on available research data."},
            {"role": "user", "content": qa_prompt}
        ], max_tokens=2000)
        
        return response
    
    def get_research_summary(self, task_id: str) -> Dict[str, Any]:
        """Get comprehensive summary of a research task"""
        try:
            task = ResearchTask.get(task_id)
            steps = ResearchStep.find_by(task_id=task_id)
            results = ResearchResult.find_by(task_id=task_id)
            
            final_summary = ResearchResult.first(task_id=task_id, is_final_summary=True)
            
            return {
                "task": {
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "progress": f"{task.completed_steps}/{task.total_steps}",
                    "started_at": task.started_at,
                    "completed_at": task.completed_at
                },
                "steps": [
                    {
                        "number": step.step_number,
                        "title": step.title,
                        "type": step.step_type.value,
                        "status": step.status.value,
                        "estimated_hours": step.estimated_hours
                    }
                    for step in sorted(steps, key=lambda x: x.step_number)
                ],
                "results_count": len(results),
                "final_summary": {
                    "available": final_summary is not None,
                    "title": final_summary.title if final_summary else None,
                    "confidence": final_summary.confidence_score if final_summary else None
                }
            }
            
        except Exception as e:
            return {"error": str(e)}


# Example usage and demo
async def demo_agentic_researcher():
    """Demonstrate the Agentic Researcher in action"""
    
    print("🧠 Agentic Researcher Demo")
    print("=" * 50)
    
    # Check for .env file
    env_file_locations = [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent.parent / ".env"
    ]
    
    env_file_found = False
    for env_path in env_file_locations:
        if env_path.exists():
            print(f"📁 Using .env file: {env_path}")
            env_file_found = True
            break
    
    if not env_file_found:
        print("📁 No .env file found, using environment variables")
    
    # Check environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    airtable_token = os.getenv("AIRTABLE_ACCESS_TOKEN") or os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")  # Optional
    
    if not openai_key:
        print("❌ OPENAI_API_KEY not found")
        print("💡 Create a .env file with your API keys:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your OpenAI API key")
        print("   3. Add your AirTable PAT")
        return
    
    if not airtable_token:
        print("❌ AIRTABLE_ACCESS_TOKEN not found")  
        print("💡 Add your AirTable Personal Access Token to .env file")
        return
    
    print("✅ API keys loaded successfully")
    print(f"🔑 OpenAI key: {openai_key[:10]}...{openai_key[-4:]}")
    print(f"🔑 AirTable token: {airtable_token[:10]}...{airtable_token[-4:]}")
    print(f"🏗️  Base ID: {'Provided' if base_id else 'Will create new base'}")
    
    try:
        # Initialize the researcher
        print("\\n🤖 Initializing Agentic Researcher...")
        researcher = AgenticResearcher(
            openai_api_key=openai_key,
            airtable_access_token=airtable_token,
            base_id=base_id
        )
        
        # Example research task
        research_topic = "The impact of AI on software development productivity in 2024"
        
        # Create research task
        task = await researcher.create_research_task(
            title=f"Research: {research_topic}",
            description=f"Comprehensive analysis of {research_topic}, including current trends, key findings from recent studies, practical implications, and future outlook.",
            priority=ResearchPriority.HIGH,
            research_budget_hours=8.0,
            requester_email="researcher@company.com"
        )
        
        print(f"\\n📋 Research Task Created:")
        print(f"  Title: {task.title}")
        print(f"  Priority: {task.priority.value}")
        print(f"  Keywords: {task.keywords}")
        
        # Execute full research
        print("\\n🔬 Executing research workflow...")
        final_summary = await researcher.execute_full_research(task)
        
        print(f"\\n📊 Research Completed!")
        print(f"Task Status: {task.status.value}")
        print(f"Progress: {task.completed_steps}/{task.total_steps} steps")
        
        # Show final summary
        print(f"\\n📝 Final Summary:")
        print(f"Title: {final_summary.title}")
        print(f"Confidence: {final_summary.confidence_score}/10")
        print(f"Summary: {final_summary.summary}")
        
        # Demo Q&A system
        print("\\n❓ Testing Q&A System...")
        
        sample_questions = [
            "What are the main benefits of AI in software development?",
            "What challenges were identified in the research?",
            "What are the key recommendations from this research?"
        ]
        
        for question in sample_questions:
            print(f"\\nQ: {question}")
            answer = await researcher.answer_question(question, task.id)
            print(f"A: {answer[:300]}...")
        
        # Show research summary
        try:
            summary = researcher.get_research_summary(task.id)
            print(f"\\n📈 Research Overview:")
            if 'error' in summary:
                print(f"  ⚠️  Error getting summary: {summary['error']}")
            else:
                print(f"  Status: {summary['task']['status']}")
                print(f"  Progress: {summary['task']['progress']}")
                print(f"  Steps completed: {len([s for s in summary['steps'] if s['status'] == 'Completed'])}")
                print(f"  Results generated: {summary['results_count']}")
                print(f"  Final summary: {'✅' if summary['final_summary']['available'] else '❌'}")
        except Exception as e:
            print(f"\\n📈 Research Overview: ⚠️  Could not generate summary: {e}")
        
        print(f"\\n🎉 Demo completed successfully!")
        print(f"\\n🔗 AirTable Base: {researcher.base_id}")
        print("\\n💡 Next steps:")
        print("  • View your research data in AirTable")
        print("  • Ask more questions about the research")
        print("  • Create additional research tasks")
        print("  • Extend the research with more specific queries")
        
    except Exception as e:
        print(f"\\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


# Interactive CLI interface
async def interactive_researcher():
    """Interactive command-line interface for the Agentic Researcher"""
    
    print("🤖 Interactive Agentic Researcher")
    print("=" * 50)
    
    # Check for .env file
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"📁 Loading configuration from: {env_file}")
    else:
        print("📁 No .env file found - copy .env.example to .env and add your API keys")
    
    # Setup
    openai_key = os.getenv("OPENAI_API_KEY")
    airtable_token = os.getenv("AIRTABLE_ACCESS_TOKEN") or os.getenv("AIRTABLE_API_KEY")
    
    if not openai_key or not airtable_token:
        print("❌ Missing required API keys in .env file:")
        print("   OPENAI_API_KEY - Your OpenAI API key")
        print("   AIRTABLE_ACCESS_TOKEN - Your AirTable Personal Access Token")
        print("")
        print("💡 Setup instructions:")
        print("   1. Copy .env.example to .env")
        print("   2. Edit .env and add your actual API keys")
        print("   3. Run the example again")
        return
    
    try:
        researcher = AgenticResearcher(
            openai_api_key=openai_key,
            airtable_access_token=airtable_token,
            base_id=os.getenv("AIRTABLE_BASE_ID")
        )
        
        print("\\n✅ Researcher initialized!")
        print(f"🔗 AirTable Base: {researcher.base_id}")
        
        current_task = None
        
        # Auto-select single existing task for better UX
        try:
            existing_tasks = ResearchTask.all()
            if len(existing_tasks) == 1:
                current_task = existing_tasks[0]
                print(f"\\n🔍 Auto-selected the only existing task: {current_task.title}")
            elif len(existing_tasks) > 1:
                print(f"\\n📚 Found {len(existing_tasks)} existing research tasks. Use Option 6 to select one.")
        except Exception as e:
            print(f"\\n⚠️  Note: Could not check for existing tasks: {e}")
        
        while True:
            print("\\n" + "="*50)
            print("🤖 Agentic Researcher - What would you like to do?")
            if current_task:
                print(f"📌 Current task: {current_task.title} ({current_task.status.value})")
            else:
                print("📌 No task selected")
            print("1. 🔬 Create new research task")
            print("2. 📊 Execute research task")
            print("3. ❓ Ask questions about research")
            print("4. 📋 View research summary")
            print("5. 📚 List all research tasks")
            print("6. 🔍 Select existing research task")
            print("7. 📄 View detailed research results")
            print("8. 🚪 Exit")
            
            choice = input("\\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                print("\\n📝 Create New Research Task")
                title = input("Research title: ").strip()
                if not title:
                    print("❌ Title is required")
                    continue
                
                description = input("Research description: ").strip()
                if not description:
                    description = title
                
                email = input("Your email (optional): ").strip() or None
                
                task = await researcher.create_research_task(
                    title=title,
                    description=description,
                    requester_email=email,
                    priority=ResearchPriority.HIGH
                )
                
                current_task = task
                print(f"✅ Created task: {task.title} (ID: {task.id})")
                
            elif choice == "2":
                if not current_task:
                    print("❌ No research task selected.")
                    # Check if there are existing tasks to select from
                    existing_tasks = ResearchTask.all()
                    if existing_tasks:
                        print(f"\\n📋 Found {len(existing_tasks)} existing tasks. Please select one:")
                        for i, task in enumerate(existing_tasks, 1):
                            status_emoji = "✅" if task.status == TaskStatus.COMPLETED else "⏳" if task.status == TaskStatus.IN_PROGRESS else "⭕"
                            print(f"{i}. {status_emoji} {task.title} (ID: {task.id[:8]}...)")
                        
                        try:
                            selection = input("\\nEnter task number to select and execute (or press Enter to go back): ").strip()
                            if not selection:
                                continue
                            
                            if selection.isdigit():
                                task_idx = int(selection) - 1
                                if 0 <= task_idx < len(existing_tasks):
                                    current_task = existing_tasks[task_idx]
                                    print(f"✅ Selected task: {current_task.title}")
                                    # Continue to execute the task below
                                else:
                                    print("❌ Invalid task number")
                                    continue
                            else:
                                print("❌ Please enter a valid task number")
                                continue
                                
                        except ValueError:
                            print("❌ Invalid input")
                            continue
                    else:
                        print("Create a new research task first (Option 1).")
                        continue
                
                print(f"\\n🚀 Executing research: {current_task.title}")
                print("This may take several minutes...")
                
                try:
                    final_summary = await researcher.execute_full_research(current_task)
                    print("\\n🎉 Research completed!")
                    print(f"Final summary: {final_summary.title}")
                except Exception as e:
                    print(f"❌ Research failed: {e}")
                
            elif choice == "3":
                if not current_task:
                    print("❌ No research task selected.")
                    # Check if there are existing tasks to select from
                    existing_tasks = ResearchTask.all()
                    if existing_tasks:
                        print(f"\\n📋 Found {len(existing_tasks)} existing tasks. Please select one:")
                        for i, task in enumerate(existing_tasks, 1):
                            status_emoji = "✅" if task.status == TaskStatus.COMPLETED else "⏳" if task.status == TaskStatus.IN_PROGRESS else "⭕"
                            print(f"{i}. {status_emoji} {task.title} (ID: {task.id[:8]}...)")
                        
                        try:
                            selection = input("\\nEnter task number to select (or press Enter to go back): ").strip()
                            if not selection:
                                continue
                            
                            if selection.isdigit():
                                task_idx = int(selection) - 1
                                if 0 <= task_idx < len(existing_tasks):
                                    current_task = existing_tasks[task_idx]
                                    print(f"✅ Selected task: {current_task.title}")
                                    # Continue to ask questions about the task below
                                else:
                                    print("❌ Invalid task number")
                                    continue
                            else:
                                print("❌ Please enter a valid task number")
                                continue
                                
                        except ValueError:
                            print("❌ Invalid input")
                            continue
                    else:
                        print("Create a new research task first (Option 1).")
                        continue
                
                print("\\n❓ Ask Questions About Research")
                question = input("Your question: ").strip()
                if question:
                    answer = await researcher.answer_question(question, current_task.id)
                    print(f"\\n🤖 Answer:\\n{answer}")
                
            elif choice == "4":
                if not current_task:
                    print("❌ No research task selected.")
                    # Check if there are existing tasks to select from
                    existing_tasks = ResearchTask.all()
                    if existing_tasks:
                        print(f"\\n📋 Found {len(existing_tasks)} existing tasks. Please select one:")
                        for i, task in enumerate(existing_tasks, 1):
                            status_emoji = "✅" if task.status == TaskStatus.COMPLETED else "⏳" if task.status == TaskStatus.IN_PROGRESS else "⭕"
                            print(f"{i}. {status_emoji} {task.title} (ID: {task.id[:8]}...)")
                        
                        try:
                            selection = input("\\nEnter task number to select (or press Enter to go back): ").strip()
                            if not selection:
                                continue
                            
                            if selection.isdigit():
                                task_idx = int(selection) - 1
                                if 0 <= task_idx < len(existing_tasks):
                                    current_task = existing_tasks[task_idx]
                                    print(f"✅ Selected task: {current_task.title}")
                                    # Continue to show summary below
                                else:
                                    print("❌ Invalid task number")
                                    continue
                            else:
                                print("❌ Please enter a valid task number")
                                continue
                                
                        except ValueError:
                            print("❌ Invalid input")
                            continue
                    else:
                        print("Create a new research task first (Option 1).")
                        continue
                
                summary = researcher.get_research_summary(current_task.id)
                print(f"\\n📊 Research Summary for: {summary['task']['title']}")
                print(f"Status: {summary['task']['status']}")
                print(f"Progress: {summary['task']['progress']}")
                print(f"Steps: {len(summary['steps'])}")
                print(f"Results: {summary['results_count']}")
                
            elif choice == "5":
                print("\\n📚 List All Research Tasks")
                tasks = ResearchTask.all()
                if not tasks:
                    print("❌ No research tasks found.")
                else:
                    print(f"\\n📋 Found {len(tasks)} research tasks:\\n")
                    for i, task in enumerate(tasks, 1):
                        status_emoji = "✅" if task.status == TaskStatus.COMPLETED else "⏳" if task.status == TaskStatus.IN_PROGRESS else "⭕"
                        print(f"{i}. {status_emoji} {task.title}")
                        print(f"   ID: {task.id}")
                        print(f"   Status: {task.status.value}")
                        print(f"   Progress: {task.completed_steps}/{task.total_steps}")
                        print(f"   Started: {task.started_at if task.started_at else 'Not started'}")
                        print()
                        
            elif choice == "6":
                print("\\n🔍 Select Existing Research Task")
                tasks = ResearchTask.all()
                if not tasks:
                    print("❌ No research tasks found. Create one first.")
                    continue
                
                print("\\nAvailable tasks:")
                for i, task in enumerate(tasks, 1):
                    status_emoji = "✅" if task.status == TaskStatus.COMPLETED else "⏳" if task.status == TaskStatus.IN_PROGRESS else "⭕"
                    print(f"{i}. {status_emoji} {task.title} (ID: {task.id[:8]}...)")
                
                try:
                    selection = input("\\nEnter task number or task ID: ").strip()
                    
                    if selection.isdigit():
                        # User entered task number
                        task_idx = int(selection) - 1
                        if 0 <= task_idx < len(tasks):
                            current_task = tasks[task_idx]
                            print(f"✅ Selected task: {current_task.title}")
                        else:
                            print("❌ Invalid task number")
                    else:
                        # User entered task ID
                        selected_task = None
                        for task in tasks:
                            if task.id.startswith(selection) or task.id == selection:
                                selected_task = task
                                break
                        
                        if selected_task:
                            current_task = selected_task
                            print(f"✅ Selected task: {current_task.title}")
                        else:
                            print("❌ Task not found")
                            
                except ValueError:
                    print("❌ Invalid input")
                    
            elif choice == "7":
                if not current_task:
                    print("❌ No research task selected.")
                    # Check if there are existing tasks to select from
                    existing_tasks = ResearchTask.all()
                    if existing_tasks:
                        print(f"\\n📋 Found {len(existing_tasks)} existing tasks. Please select one:")
                        for i, task in enumerate(existing_tasks, 1):
                            status_emoji = "✅" if task.status == TaskStatus.COMPLETED else "⏳" if task.status == TaskStatus.IN_PROGRESS else "⭕"
                            print(f"{i}. {status_emoji} {task.title} (ID: {task.id[:8]}...)")
                        
                        try:
                            selection = input("\\nEnter task number to select (or press Enter to go back): ").strip()
                            if not selection:
                                continue
                            
                            if selection.isdigit():
                                task_idx = int(selection) - 1
                                if 0 <= task_idx < len(existing_tasks):
                                    current_task = existing_tasks[task_idx]
                                    print(f"✅ Selected task: {current_task.title}")
                                    # Continue to show detailed results below
                                else:
                                    print("❌ Invalid task number")
                                    continue
                            else:
                                print("❌ Please enter a valid task number")
                                continue
                                
                        except ValueError:
                            print("❌ Invalid input")
                            continue
                    else:
                        print("Create a new research task first (Option 1).")
                        continue
                
                print(f"\\n📄 Detailed Research Results for: {current_task.title}")
                print("=" * 60)
                
                # Get comprehensive data
                steps = ResearchStep.find_by(task_id=current_task.id)
                results = ResearchResult.find_by(task_id=current_task.id)
                final_summary = ResearchResult.first(task_id=current_task.id, is_final_summary=True)
                
                # Task details
                print(f"\\n📊 Task Overview:")
                print(f"  Title: {current_task.title}")
                print(f"  Description: {current_task.description}")
                print(f"  Status: {current_task.status.value}")
                print(f"  Priority: {current_task.priority.value}")
                print(f"  Progress: {current_task.completed_steps}/{current_task.total_steps}")
                print(f"  Started: {current_task.started_at if current_task.started_at else 'Not started'}")
                if current_task.completed_at:
                    print(f"  Completed: {current_task.completed_at}")
                
                # Research steps
                if steps:
                    print(f"\\n🔬 Research Steps ({len(steps)}):")
                    for step in sorted(steps, key=lambda x: x.step_number):
                        status_emoji = "✅" if step.status == StepStatus.COMPLETED else "⏳" if step.status == StepStatus.IN_PROGRESS else "⭕"
                        print(f"  {step.step_number}. {status_emoji} {step.title}")
                        print(f"      Type: {step.step_type.value}")
                        print(f"      Status: {step.status.value}")
                        if step.estimated_hours:
                            print(f"      Estimated: {step.estimated_hours}h")
                
                # Research results
                if results:
                    non_summary_results = [r for r in results if not r.is_final_summary]
                    if non_summary_results:
                        print(f"\\n📝 Research Results ({len(non_summary_results)}):")
                        for result in non_summary_results:
                            print(f"  • {result.title}")
                            print(f"    Confidence: {result.confidence_score}/10")
                            if result.content and len(result.content) > 100:
                                print(f"    Content: {result.content[:100]}...")
                            else:
                                print(f"    Content: {result.content}")
                
                # Final summary
                if final_summary:
                    print(f"\\n🎯 Final Summary:")
                    print(f"  Title: {final_summary.title}")
                    print(f"  Confidence: {final_summary.confidence_score}/10")
                    if final_summary.content:
                        print(f"  Summary: {final_summary.content}")
                else:
                    print(f"\\n🎯 Final Summary: Not available")
                    
            elif choice == "8":
                print("\\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-8.")
                
    except KeyboardInterrupt:
        print("\\n\\n👋 Goodbye!")
    except Exception as e:
        print(f"\\n❌ Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agentic Researcher Demo")
    parser.add_argument("--interactive", action="store_true", help="Run interactive mode")
    parser.add_argument("--demo", action="store_true", help="Run automated demo")
    
    args = parser.parse_args()
    
    if args.interactive:
        asyncio.run(interactive_researcher())
    elif args.demo:
        asyncio.run(demo_agentic_researcher())
    else:
        print("Usage:")
        print("  python agentic_researcher.py --demo       # Run automated demo")
        print("  python agentic_researcher.py --interactive # Run interactive mode")
        print("")
        print("Setup:")
        print("  1. Copy .env.example to .env")
        print("  2. Edit .env file and add your API keys:")
        print("     - OPENAI_API_KEY (from https://platform.openai.com/api-keys)")
        print("     - AIRTABLE_ACCESS_TOKEN (from https://airtable.com/developers/web/api/authentication)")
        print("     - AIRTABLE_BASE_ID (optional - will create new base if not provided)")
        print("")
        print("Example .env file:")
        print("  OPENAI_API_KEY=sk-your-openai-key-here")
        print("  AIRTABLE_ACCESS_TOKEN=pat-your-airtable-token-here")
