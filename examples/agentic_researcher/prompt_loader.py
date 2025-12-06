"""
Prompt loader utility for the Agentic Researcher

This module provides utilities to load and format prompts from external YAML files.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class PromptLoader:
    """Load and format prompts from YAML files"""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize the prompt loader
        
        Args:
            prompts_dir: Directory containing prompt files (defaults to ./prompts/)
        """
        if prompts_dir is None:
            # Default to prompts directory relative to this file
            self.prompts_dir = Path(__file__).parent / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
    
    def load_prompt(self, prompt_name: str) -> Dict[str, Any]:
        """
        Load a prompt from a YAML file
        
        Args:
            prompt_name: Name of the prompt file (without .yaml extension)
            
        Returns:
            Dictionary containing prompt templates and system messages
        """
        prompt_file = self.prompts_dir / f"{prompt_name}.yaml"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def format_keywords_extraction(self, description: str) -> tuple[str, str]:
        """
        Format the keywords extraction prompt
        
        Args:
            description: Task description to extract keywords from
            
        Returns:
            Tuple of (system_message, user_message)
        """
        prompt_data = self.load_prompt("keywords_extraction")
        
        system_message = prompt_data["system_message"]
        user_message = prompt_data["user_template"].format(description=description)
        
        return system_message, user_message
    
    def format_research_steps_definition(
        self, 
        task_title: str,
        task_description: str, 
        task_keywords: str,
        task_priority: str,
        budget_hours: str
    ) -> tuple[str, str]:
        """
        Format the research steps definition prompt
        
        Returns:
            Tuple of (system_message, user_message)
        """
        prompt_data = self.load_prompt("research_steps_definition")
        
        system_message = prompt_data["system_message"]
        user_message = prompt_data["user_template"].format(
            task_title=task_title,
            task_description=task_description,
            task_keywords=task_keywords,
            task_priority=task_priority,
            budget_hours=budget_hours
        )
        
        return system_message, user_message
    
    def format_research_execution(
        self,
        step_type_lower: str,
        step_number: int,
        total_steps: int,
        task_title: str,
        task_description: str,
        step_title: str,
        step_description: str,
        step_type: str,
        research_query: str,
        research_data: str = "",
        context: str = ""
    ) -> tuple[str, str]:
        """
        Format the research execution prompt
        
        Returns:
            Tuple of (system_message, user_message)
        """
        prompt_data = self.load_prompt("research_execution")
        
        system_message = prompt_data["system_template"].format(
            step_type_lower=step_type_lower
        )
        user_message = prompt_data["user_template"].format(
            step_number=step_number,
            total_steps=total_steps,
            task_title=task_title,
            task_description=task_description,
            step_title=step_title,
            step_description=step_description,
            step_type=step_type,
            research_query=research_query,
            research_data=research_data,
            context=context
        )
        
        return system_message, user_message
    
    def format_final_summary(
        self,
        task_title: str,
        task_description: str,
        all_findings: str
    ) -> tuple[str, str]:
        """
        Format the final summary prompt
        
        Returns:
            Tuple of (system_message, user_message)
        """
        prompt_data = self.load_prompt("final_summary")
        
        system_message = prompt_data["system_message"]
        user_message = prompt_data["user_template"].format(
            task_title=task_title,
            task_description=task_description,
            all_findings=all_findings
        )
        
        return system_message, user_message
    
    def format_qa_answering(self, research_context: str, question: str) -> str:
        """
        Format the Q&A answering prompt
        
        Returns:
            Formatted user message for Q&A
        """
        prompt_data = self.load_prompt("qa_answering")
        
        return prompt_data["user_template"].format(
            research_context=research_context,
            question=question
        )
