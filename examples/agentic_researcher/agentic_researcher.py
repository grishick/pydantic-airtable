"""
Agentic Researcher Example

An AI-powered research assistant that uses OpenAI's API to conduct comprehensive research
on any topic, storing all data in Airtable using the streamlined pydantic-airtable API.

Features:
- Field detection for all research models
- Automatic table creation and management
- Real web search integration using DuckDuckGo
- Comprehensive prompt management via YAML files
- Interactive and automated research modes
- Built-in question-answering system
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, field_validator

# Add parent directory to path
sys.path.insert(0, "../../")

from pydantic_airtable import (
    airtable_model,
    configure_from_env,
    AirtableManager,
    AirtableConfig
)

import openai
from dotenv import load_dotenv
from research_tools import ResearchTools
from prompt_loader import PromptLoader

# Load environment variables
load_dotenv()

# Configure Airtable from environment
configure_from_env()

# Initialize OpenAI
openai_client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30,
    max_retries=3
)

# Initialize research tools and prompt loader
research_tools = ResearchTools()
prompt_loader = PromptLoader()


# Enums for better type safety
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


class StepType(str, Enum):
    KEYWORD_EXTRACTION = "Keyword Extraction"
    LITERATURE_SEARCH = "Literature Search"
    DATA_ANALYSIS = "Data Analysis" 
    EXPERT_CONSULTATION = "Expert Consultation"
    CASE_STUDY = "Case Study"
    MARKET_RESEARCH = "Market Research"
    TECHNICAL_ANALYSIS = "Technical Analysis"
    SYNTHESIS = "Synthesis"
    VALIDATION = "Validation"


# Research Models using Streamlined API

@airtable_model(table_name="Research_Tasks")
class ResearchTask(BaseModel):
    """Main research task with field type detection"""
    
    title: str                              # -> SINGLE_LINE_TEXT
    description: str                        # -> LONG_TEXT (detected)
    status: TaskStatus = TaskStatus.PENDING # -> SELECT (enum detected)
    priority: ResearchPriority = ResearchPriority.MEDIUM  # -> SELECT
    requester_email: Optional[str] = None   # -> EMAIL (detected from name)
    deadline: Optional[datetime] = None     # -> DATETIME
    started_at: Optional[datetime] = None   # -> DATETIME
    completed_at: Optional[datetime] = None # -> DATETIME
    
    # Research-specific fields
    keywords: Optional[str] = None          # -> LONG_TEXT (for keyword list)
    research_scope: Optional[str] = None    # -> LONG_TEXT
    expected_outcome: Optional[str] = None  # -> LONG_TEXT
    
    # Progress tracking
    progress: float = 0.0                   # -> NUMBER (percentage)
    total_steps: int = 0                    # -> NUMBER
    completed_steps: int = 0                # -> NUMBER


@airtable_model(table_name="Research_Steps")  
class ResearchStep(BaseModel):
    """Individual research steps with automatic detection"""
    
    task_id: str                            # -> SINGLE_LINE_TEXT (links to ResearchTask)
    step_number: int                        # -> NUMBER
    step_type: StepType                     # -> SELECT (enum detected)
    title: str                              # -> SINGLE_LINE_TEXT
    description: str                        # -> LONG_TEXT (detected)
    
    status: TaskStatus = TaskStatus.PENDING # -> SELECT
    started_at: Optional[datetime] = None   # -> DATETIME
    completed_at: Optional[datetime] = None # -> DATETIME
    
    # Research data
    research_query: Optional[str] = None    # -> LONG_TEXT
    research_data: Optional[str] = None     # -> LONG_TEXT (for JSON data)
    findings: Optional[str] = None          # -> LONG_TEXT
    sources: Optional[str] = None           # -> LONG_TEXT (URLs, references)
    
    # Quality metrics
    confidence_score: float = 0.0           # -> NUMBER (0-1 scale)
    source_count: int = 0                   # -> NUMBER
    
    @field_validator('research_data')
    @classmethod
    def validate_research_data(cls, v):
        if v is not None and isinstance(v, (dict, list)):
            return json.dumps(v)
        return v


@airtable_model(table_name="Research_Results")
class ResearchResult(BaseModel):
    """Final research results and insights"""
    
    task_id: str                            # -> SINGLE_LINE_TEXT (links to ResearchTask)
    result_type: str = "Summary"            # -> SINGLE_LINE_TEXT
    title: str                              # -> SINGLE_LINE_TEXT
    content: str                            # -> LONG_TEXT (detected)
    
    # Result metadata
    confidence_level: float = 0.0           # -> NUMBER (0-1 scale)
    source_count: int = 0                   # -> NUMBER
    word_count: int = 0                     # -> NUMBER
    
    # Flags
    is_final_summary: bool = False          # -> CHECKBOX
    requires_review: bool = False           # -> CHECKBOX
    
    # Timestamps
    generated_at: Optional[datetime] = None # -> DATETIME
    
    # Additional data
    sources: Optional[str] = None           # -> LONG_TEXT
    key_insights: Optional[str] = None      # -> LONG_TEXT
    recommendations: Optional[str] = None   # -> LONG_TEXT


class AgenticResearcher:
    """
    AI-powered research assistant using the streamlined pydantic-airtable API
    """
    
    def __init__(self, config: Optional[AirtableConfig] = None):
        """
        Initialize the Agentic Researcher
        
        Args:
            config: Optional Airtable configuration (uses global if None)
        """
        self.config = config
        self.manager = AirtableManager(config) if config else None
        
        # Initialize tools
        self.research_tools = research_tools
        self.prompt_loader = prompt_loader
        self.openai_client = openai_client
        
    def setup_tables(self) -> Dict[str, Any]:
        """
        Setup all required Airtable tables
        
        Returns:
            Dictionary with setup results
        """
        print("🔧 Setting up Airtable tables...")
        
        results = {
            "tables_created": [],
            "tables_existing": [],
            "errors": []
        }
        
        models = [
            ("Research_Tasks", ResearchTask),
            ("Research_Steps", ResearchStep), 
            ("Research_Results", ResearchResult)
        ]
        
        # Get base schema once (more efficient than checking each table separately)
        try:
            config = AirtableConfig.from_env()
            manager = AirtableManager(config)
            schema = manager.get_base_schema()
            existing_tables = {t['name']: t['id'] for t in schema.get('tables', [])}
        except Exception as e:
            print(f"⚠️  Could not fetch base schema: {e}")
            existing_tables = {}
        
        for table_name, model_class in models:
            try:
                if table_name in existing_tables:
                    # Table already exists
                    results["tables_existing"].append(table_name)
                    print(f"✅ {table_name} table already exists (ID: {existing_tables[table_name]})")
                else:
                    # Table doesn't exist - create it
                    print(f"ℹ️  {table_name} table does not exist yet")
                    print(f"🔧 Creating {table_name} table from model definition...")
                    result = model_class.create_table()
                    results["tables_created"].append(table_name)
                    print(f"✅ Created {table_name} table (ID: {result.get('id')})")
                    
            except Exception as e:
                results["errors"].append(f"{table_name}: {str(e)}")
                print(f"❌ Failed to setup {table_name}: {e}")
        
        return results
    
    async def create_research_task(
        self, 
        title: str, 
        description: str,
        priority: ResearchPriority = ResearchPriority.MEDIUM,
        requester_email: Optional[str] = None,
        deadline: Optional[datetime] = None
    ) -> ResearchTask:
        """
        Create a new research task
        
        Args:
            title: Research task title
            description: Detailed research request
            priority: Task priority
            requester_email: Email of requester
            deadline: Research deadline
            
        Returns:
            Created ResearchTask instance
        """
        print(f"📝 Creating research task: {title}")
        
        # Extract keywords using AI
        keywords = await self._extract_keywords(description)
        
        task = ResearchTask.create(
            title=title,
            description=description,
            priority=priority,
            requester_email=requester_email,
            deadline=deadline,
            keywords=", ".join(keywords) if keywords else None,
            started_at=datetime.now()
        )
        
        print(f"✅ Created research task (ID: {task.id})")
        return task
    
    async def define_research_steps(self, task: ResearchTask) -> List[ResearchStep]:
        """
        Define research steps for a task using AI
        
        Args:
            task: Research task to define steps for
            
        Returns:
            List of created ResearchStep instances
        """
        print(f"🔍 Defining research steps for: {task.title}")
        
        # Use AI to generate research steps
        steps_data = await self._generate_research_steps(task)
        
        steps = []
        for i, step_data in enumerate(steps_data, 1):
            step = ResearchStep.create(
                task_id=task.id,
                step_number=i,
                step_type=step_data["type"],
                title=step_data["title"],
                description=step_data["description"],
                research_query=step_data.get("query")
            )
            steps.append(step)
        
        # Update task with step count
        task.total_steps = len(steps)
        task.save()
        
        print(f"✅ Defined {len(steps)} research steps")
        return steps
            
    async def execute_research_step(self, step: ResearchStep) -> ResearchStep:
        """
        Execute a single research step
        
        Args:
            step: Research step to execute
            
        Returns:
            Updated ResearchStep instance
        """
        print(f"🔬 Executing step {step.step_number}: {step.title}")
        
        step.status = TaskStatus.IN_PROGRESS
        step.started_at = datetime.now()
        step.save()
        
        try:
            # Conduct research based on step type
            research_data = await self.research_tools.conduct_research(
                query=step.research_query or step.description,
                step_type=step.step_type
            )
            
            # Analyze research data with AI
            findings = await self._analyze_research_data(step, research_data)
            
            # Update step with results
            step.research_data = json.dumps(research_data) if research_data else None
            step.findings = findings
            step.source_count = len(research_data.get('sources', [])) if research_data else 0
            step.confidence_score = research_data.get('confidence', 0.7) if research_data else 0.5
            step.status = TaskStatus.COMPLETED
            step.completed_at = datetime.now()
            step.save()
            
            print(f"✅ Completed step {step.step_number}")
            
        except Exception as e:
            step.status = TaskStatus.FAILED
            step.findings = f"Error: {str(e)}"
            step.save()
            print(f"❌ Step {step.step_number} failed: {e}")
            
        return step
    
    async def answer_question(self, task_id: str, question: str) -> str:
        """
        Answer questions about research using stored data
        
        Args:
            task_id: Research task ID
            question: Question to answer
            
        Returns:
            AI-generated answer
        """
        print(f"❓ Answering question about task {task_id}: {question}")
        
        # Get task and related data
        task = ResearchTask.get(task_id)
        steps = ResearchStep.find_by(task_id=task_id)
        results = ResearchResult.find_by(task_id=task_id)
        
        # Use AI to answer question based on research data
        answer = await self._answer_question_with_context(
            question, task, steps, results
        )
        
        # Store Q&A as result
        qa_result = ResearchResult.create(
            task_id=task_id,
            result_type="Q&A",
            title=f"Q: {question[:50]}...",
            content=f"Question: {question}\n\nAnswer: {answer}",
            generated_at=datetime.now()
        )
        
        print(f"✅ Generated answer (ID: {qa_result.id})")
        return answer
    
    async def generate_final_summary(self, task: ResearchTask) -> ResearchResult:
        """
        Generate final research summary
        
        Args:
            task: Research task to summarize
            
        Returns:
            Final summary as ResearchResult
        """
        print(f"📄 Generating final summary for: {task.title}")
        
        # Get all completed steps
        try:
            steps = ResearchStep.find_by(task_id=task.id)
            completed_steps = [s for s in steps if s.status == "Completed"]
        except Exception as e:
            print(f"⚠️ Failed to fetch research steps: {e}")
            completed_steps = []
        
        # Generate AI summary
        try:
            if completed_steps:
                summary_content = await self._generate_final_summary(task, completed_steps)
            else:
                summary_content = f"Research completed for: {task.title}\n\nNo completed research steps found."
        except Exception as e:
            print(f"⚠️ Summary generation failed: {e}")
            summary_content = f"Research completed for: {task.title}\n\nTotal steps: {len(completed_steps)}"
        
        # Create final result
        final_result = ResearchResult.create(
            task_id=task.id,
            result_type="Final Summary",
            title=f"Final Summary: {task.title}",
            content=summary_content,
            is_final_summary=True,
            generated_at=datetime.now(),
            confidence_level=0.8,
            source_count=sum(step.source_count for step in completed_steps)
        )
        
        # Update task status and progress
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.progress = 100.0
        task.save()
        
        print(f"✅ Generated final summary (ID: {final_result.id})")
        return final_result
            
    # AI Helper Methods
    
    async def _extract_keywords(self, description: str) -> List[str]:
        """Extract research keywords using AI"""
        try:
            system_message, user_message = self.prompt_loader.format_keywords_extraction(
                description=description
            )
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            # Parse keywords from response (assuming comma-separated)
            keywords = [kw.strip() for kw in content.split(',')]
            return keywords[:10]  # Limit to 10 keywords
            
        except Exception as e:
            print(f"⚠️ Keyword extraction failed: {e}")
            return []
    
    async def _generate_research_steps(self, task: ResearchTask) -> List[Dict[str, Any]]:
        """Generate research steps using AI"""
        try:
            system_message, user_message = self.prompt_loader.format_research_steps_definition(
                task_title=task.title,
                task_description=task.description,
                task_keywords=task.keywords or "",
                task_priority=str(task.priority) if task.priority else "Medium",
                budget_hours=8.0  # Default budget hours
            )
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            
            # Parse AI response into structured steps
            # This would need to be implemented based on prompt format
            steps = [
                {
                    "type": StepType.LITERATURE_SEARCH,
                    "title": "Literature Search",
                    "description": f"Search for academic and professional literature on {task.title}",
                    "query": task.keywords or task.title
                },
                {
                    "type": StepType.DATA_ANALYSIS, 
                    "title": "Data Analysis",
                    "description": f"Analyze findings and data related to {task.title}",
                    "query": task.title
                },
                {
                    "type": StepType.SYNTHESIS,
                    "title": "Synthesis",
                    "description": f"Synthesize findings into comprehensive insights",
                    "query": task.title
                }
            ]
            
            return steps
            
        except Exception as e:
            print(f"⚠️ Step generation failed: {e}")
            # Return default steps
            return [
                {
                    "type": StepType.LITERATURE_SEARCH,
                    "title": "Literature Search", 
                    "description": f"Research {task.title}",
                    "query": task.title
                }
            ]
    
    async def _analyze_research_data(self, step: ResearchStep, research_data: Dict, task: ResearchTask = None) -> str:
        """Analyze research data using AI"""
        try:
            # Get task information if not provided
            if not task:
                try:
                    task = ResearchTask.get(step.task_id)
                except Exception:
                    task = ResearchTask(title="Unknown Task", description="Task information not available")
            
            # Get total step count (estimate if needed)
            try:
                all_steps = ResearchStep.find_by(task_id=step.task_id)
                total_steps = len(all_steps)
            except Exception:
                total_steps = 5  # Fallback estimate
            
            system_message, user_message = self.prompt_loader.format_research_execution(
                step_type_lower=step.step_type.lower() if step.step_type else "research",
                step_number=step.step_number,
                total_steps=total_steps,
                task_title=task.title,
                task_description=task.description,
                step_title=step.title,
                step_description=step.description,
                step_type=step.step_type or "Research",
                research_query=step.research_query or step.description,
                context="",  # Additional context if needed
                research_data=json.dumps(research_data, indent=2)
            )
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.4
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️ Research analysis failed: {e}")
            return f"Analysis unavailable: {str(e)}"
    
    async def _generate_final_summary(self, task: ResearchTask, steps: List[ResearchStep]) -> str:
        """Generate final research summary using AI"""
        try:
            # Compile all findings
            all_findings = "\n\n".join([
                f"Step {step.step_number} - {step.title}:\n{step.findings or 'No findings'}"
                for step in steps if step.findings
            ])
            
            system_message, user_message = self.prompt_loader.format_final_summary(
                task_title=task.title,
                task_description=task.description,
                all_findings=all_findings
            )
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️ Summary generation failed: {e}")
            return f"Summary unavailable: {str(e)}"
    
    async def _answer_question_with_context(
        self, 
        question: str, 
        task: ResearchTask, 
        steps: List[ResearchStep],
        results: List[ResearchResult]
    ) -> str:
        """Answer question using research context"""
        try:
            # Compile context
            context_parts = [
                f"Task: {task.title}",
                f"Description: {task.description}"
            ]
            
            if steps:
                context_parts.append("Research Steps:")
                for step in steps:
                    if step.findings:
                        context_parts.append(f"- {step.title}: {step.findings}")
            
            if results:
                context_parts.append("Previous Results:")
                for result in results:
                    if result.content:
                        context_parts.append(f"- {result.title}: {result.content[:200]}...")
            
            context = "\n".join(context_parts)
            
            system_message, user_message = self.prompt_loader.format_qa_answering(
                question=question,
                research_context=context
            )
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️ Question answering failed: {e}")
            return f"Unable to answer: {str(e)}"


# Interactive Interface

async def interactive_mode():
    """Interactive mode for the Agentic Researcher"""
    
    print("\n🤖 Welcome to Agentic Researcher Interactive Mode!")
    print("=" * 60)
    
    researcher = AgenticResearcher()
    
    # Setup tables
    setup_result = researcher.setup_tables()
    if setup_result["errors"]:
        print(f"⚠️ Some tables had setup issues: {setup_result['errors']}")
        print("Continuing anyway...")
    
    current_task = None
    
    while True:
        try:
            # Display menu
            print(f"\n🤖 Agentic Researcher - What would you like to do?")
            if current_task:
                status_str = str(current_task.status) if current_task.status else "Unknown"
                print(f"📌 Current task: {current_task.title} ({status_str})")
            
            print("1. 🔬 Create new research task")
            print("2. 📊 Execute research task")
            print("3. ❓ Ask questions about research")
            print("4. 📋 View research summary")
            print("5. 📚 List all research tasks")
            print("6. 🔍 Select existing research task")
            print("7. 📄 View detailed research results")
            print("8. 🚪 Exit")
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                # Create new research task
                title = input("📝 Enter research title: ").strip()
                description = input("📝 Enter research description: ").strip()
                
                if title and description:
                    priority_input = input("📝 Priority (Low/Medium/High/Urgent) [Medium]: ").strip()
                    priority = ResearchPriority.MEDIUM
                    
                    try:
                        if priority_input:
                            priority = ResearchPriority(priority_input.title())
                    except ValueError:
                        print("⚠️ Invalid priority, using Medium")
                    
                    current_task = await researcher.create_research_task(
                    title=title,
                    description=description,
                        priority=priority
                )
                
                    print(f"✅ Created research task: {current_task.title}")
                else:
                    print("❌ Title and description are required")
                
            elif choice == "2":
                # Execute research task
                if not current_task:
                    print("❌ No task selected. Please create or select a task first.")
                    continue
                
                status_str = str(current_task.status) if current_task.status else ""
                if status_str == "Completed":
                    print("✅ Task already completed!")
                    continue
                
                print(f"🔬 Executing research for: {current_task.title}")
                
                # Define steps if not already done
                existing_steps = ResearchStep.find_by(task_id=current_task.id)
                if not existing_steps:
                    steps = await researcher.define_research_steps(current_task)
                else:
                    steps = existing_steps
                
                # Execute each step
                completed_count = 0
                for step in steps:
                    step_status = str(step.status) if step.status else ""
                    if step_status != "Completed":
                        await researcher.execute_research_step(step)
                        completed_count += 1
                        
                        # Update task progress
                        current_task.completed_steps = completed_count
                        current_task.progress = (completed_count / len(steps)) * 100
                        current_task.save()
                
                # Generate final summary
                if completed_count > 0:
                    final_result = await researcher.generate_final_summary(current_task)
                    print(f"📄 Generated final summary: {final_result.title}")
                
            elif choice == "3":
                # Ask questions
                if not current_task:
                    print("❌ No task selected. Please create or select a task first.")
                    continue
                
                question = input("❓ Enter your question: ").strip()
                if question:
                    answer = await researcher.answer_question(current_task.id, question)
                    print(f"\n💡 Answer: {answer}")
                
            elif choice == "4":
                # View research summary
                if not current_task:
                    print("❌ No task selected. Please create or select a task first.")
                    continue
                
                # Find final summary by result_type instead of boolean field
                all_results = ResearchResult.find_by(task_id=current_task.id)
                results = [r for r in all_results if r.result_type == "Final Summary"]
                
                if results:
                    result = results[0]
                    print(f"\n📄 Research Summary: {result.title}")
                    print("=" * 60)
                    print(result.content)
                else:
                    print("❌ No summary available yet. Complete research first.")
                
            elif choice == "5":
                # List all tasks
                tasks = ResearchTask.all()
                if tasks:
                    print(f"\n📚 All Research Tasks ({len(tasks)} total):")
                    print("=" * 60)
                    for i, task in enumerate(tasks, 1):
                        status_str = str(task.status) if task.status else "Unknown"
                        status_icon = "✅" if status_str == "Completed" else "⏳"
                        progress_val = float(task.progress) if task.progress else 0.0
                        print(f"{i}. {status_icon} {task.title}")
                        print(f"   Status: {status_str} | Progress: {progress_val:.1f}%")
                        if task.started_at:
                            try:
                                print(f"   Started: {task.started_at.strftime('%Y-%m-%d %H:%M')}")
                            except AttributeError:
                                print(f"   Started: {task.started_at}")
                        print()
                else:
                    print("📚 No research tasks found.")
            
            elif choice == "6":
                # Select existing task
                tasks = ResearchTask.all()
                if tasks:
                    print(f"\n🔍 Available Research Tasks:")
                    for i, task in enumerate(tasks, 1):
                        status_str = str(task.status) if task.status else "Unknown"
                        status_icon = "✅" if status_str == "Completed" else "⏳"
                        print(f"{i}. {status_icon} {task.title} ({status_str})")
                    
                    try:
                        selection = int(input("Enter task number: ")) - 1
                        if 0 <= selection < len(tasks):
                            current_task = tasks[selection]
                            print(f"📌 Selected: {current_task.title}")
                        else:
                            print("❌ Invalid selection")
                    except ValueError:
                        print("❌ Please enter a valid number")
                else:
                    print("📚 No research tasks found.")
            
            elif choice == "7":
                # View detailed results
                if not current_task:
                    print("❌ No task selected. Please create or select a task first.")
                    continue
                
                results = ResearchResult.find_by(task_id=current_task.id)
                
                if results:
                    print(f"\n📄 Detailed Research Results for: {current_task.title}")
                    print("=" * 60)
                    
                    for result in results:
                        print(f"\n📋 {result.title}")
                        print(f"Type: {result.result_type}")
                        if result.generated_at:
                            print(f"Generated: {result.generated_at.strftime('%Y-%m-%d %H:%M')}")
                        print(f"Content: {result.content[:200]}...")
                        if len(result.content) > 200:
                            print("   (truncated - see Airtable for full content)")
                        print("-" * 40)
                else:
                    print("❌ No detailed results available yet.")
            
            elif choice == "8":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-8.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def demo_mode():
    """Automated demo mode"""
    
    print("\n🎯 Running Agentic Researcher Demo...")
    print("=" * 50)
    
    researcher = AgenticResearcher()
    
    # Setup tables
    researcher.setup_tables()
    
    # Create demo research task
    task = await researcher.create_research_task(
        title="Artificial Intelligence in Healthcare",
        description="Investigate the current applications, benefits, and challenges of AI in healthcare systems, focusing on diagnostic tools, treatment recommendations, and patient outcomes.",
        priority=ResearchPriority.HIGH
    )
    
    # Execute research
    steps = await researcher.define_research_steps(task)
    
    for step in steps:
        await researcher.execute_research_step(step)
    
    # Generate final summary
    final_result = await researcher.generate_final_summary(task)
    
    print(f"\n📊 Demo Research Summary:")
    print("=" * 50)
    print(final_result.content)
    
    # Ask a sample question
    question = "What are the main benefits of AI in healthcare?"
    answer = await researcher.answer_question(task.id, question)
    
    print(f"\n❓ Sample Q&A:")
    print(f"Q: {question}")
    print(f"A: {answer}")
    
    print("\n🎉 Demo completed! Check your Airtable base for detailed results.")


def main():
    """Main entry point"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Agentic Researcher - AI-powered research assistant')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    args = parser.parse_args()
    
    print("🚀 Pydantic Airtable - Agentic Researcher")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ["AIRTABLE_ACCESS_TOKEN", "AIRTABLE_BASE_ID", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\n📋 Setup Instructions:")
        print("1. Create a .env file with:")
        for var in required_vars:
            print(f"   {var}=your_value_here")
        print("\n2. Get credentials:")
        print("   - Airtable PAT: https://airtable.com/developers/web/api/authentication")
        print("   - OpenAI API Key: https://platform.openai.com/api-keys")
        return
    
    # Choose mode based on arguments or prompt user
    if args.demo:
        mode = "2"
    elif args.interactive:
        mode = "1"
    else:
        mode = input("\nChoose mode:\n1. Interactive\n2. Demo\nEnter choice (1-2): ").strip()
    
    try:
        if mode == "1":
            asyncio.run(interactive_mode())
        elif mode == "2":
            asyncio.run(demo_mode())
        else:
            print("❌ Invalid choice")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()