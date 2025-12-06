# Agentic Researcher Prompts

This directory contains all the AI prompts used by the Agentic Researcher in external YAML files. This makes them easy to customize and maintain without modifying the code.

## Structure

Each prompt file is a YAML document containing templates that are used by the system:

### `keywords_extraction.yaml`
- **Purpose**: Extracts relevant keywords from research task descriptions
- **Templates**: 
  - `system_message`: System role definition
  - `user_template`: User prompt with `{description}` placeholder

### `research_steps_definition.yaml`
- **Purpose**: Defines comprehensive research steps for a given task
- **Templates**:
  - `system_message`: System role definition
  - `user_template`: User prompt with task details placeholders

### `research_execution.yaml`
- **Purpose**: Executes individual research steps
- **Templates**:
  - `system_template`: System role with `{step_type_lower}` placeholder
  - `user_template`: User prompt with step and task details placeholders

### `final_summary.yaml`
- **Purpose**: Creates final research summaries
- **Templates**:
  - `system_message`: System role definition
  - `user_template`: User prompt with task and findings placeholders

### `qa_answering.yaml`
- **Purpose**: Answers questions based on research results
- **Templates**:
  - `user_template`: User prompt with research context and question placeholders

## Customization

### Modifying Prompts

1. **Edit the YAML files** directly to customize prompts
2. **Maintain placeholders** (e.g., `{task_title}`, `{description}`) as they are filled by the code
3. **Test your changes** by running the interactive mode

### Adding New Prompts

1. Create a new `.yaml` file in this directory
2. Add loading methods to `prompt_loader.py`
3. Update the main code to use the new prompts

### Example Customization

To make the system more formal, you could edit `research_execution.yaml`:

```yaml
system_template: "You are a senior research analyst with expertise in {step_type_lower}. Provide academically rigorous and thoroughly documented research."

user_template: |
  Research Assignment {step_number} of {total_steps}:
  
  Project: {task_title}
  Objective: {task_description}
  
  Current Assignment: {step_title}
  Methodology: {step_type}
  Research Focus: {research_query}
  
  Please provide a comprehensive analysis following academic standards...
```

## Template Variables

Common variables available in templates:

- **Task variables**: `{task_title}`, `{task_description}`, `{task_keywords}`, `{task_priority}`
- **Step variables**: `{step_title}`, `{step_description}`, `{step_type}`, `{step_number}`, `{total_steps}`
- **Content variables**: `{research_context}`, `{all_findings}`, `{question}`, `{description}`
- **Formatting variables**: `{step_type_lower}`, `{budget_hours}`, `{context}`

## Best Practices

1. **Keep placeholders intact** - The code expects specific variable names
2. **Test incrementally** - Make small changes and test to ensure they work
3. **Maintain JSON structure requirements** - Some prompts expect JSON responses
4. **Consider tone consistency** - Maintain a consistent voice across related prompts
5. **Document your changes** - Add comments to explain significant modifications

## Loading System

The `PromptLoader` class automatically:
- Loads YAML files from this directory
- Formats templates with provided variables  
- Returns system and user messages for OpenAI API calls
- Handles missing files with clear error messages

Changes to prompt files are loaded dynamically, so you can modify prompts without restarting the application.
