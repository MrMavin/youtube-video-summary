from jinja2 import Template
import os
from datetime import datetime

# System prompt template
SYSTEM_PROMPT_TEMPLATE = Template("""
Summarize this partial transcript making it short and informative.

The summary should be accurate and factual, no formatting.
""".strip())

# User prompt template for preprocessing
PREPROCESSING_PROMPT_TEMPLATE = Template("""
{{ transcript_content }}
""".strip())

# User prompt template for final processing
FINAL_PROCESSING_SYSTEM_PROMPT_TEMPLATE = Template("""
From the summaries provided, create a detailed final result that includes:

- Title
- Summary (2-3 sentences)
- Insights

No formatting.
""".strip())


def render_system_prompt():
    """Render the system prompt for preprocessing"""
    return SYSTEM_PROMPT_TEMPLATE.render()


def render_final_system_prompt():
    """Render the system prompt for final processing"""
    return FINAL_PROCESSING_SYSTEM_PROMPT_TEMPLATE.render()


def render_preprocessing_prompt(transcript_content):
    """Render the preprocessing prompt with transcript content"""
    return PREPROCESSING_PROMPT_TEMPLATE.render(
        transcript_content=transcript_content
    )


def render_final_processing_prompt(summaries):
    """Render the final processing prompt with all chunk summaries"""
    return summaries


# Custom prompts can be added here
CUSTOM_PROMPTS = {
    "extract_quotes": Template("""
    Extract the most impactful and quotable moments from this transcript:
    
    {{ transcript_content }}
    
    Provide 5-10 notable quotes with context about why each is significant.
    """.strip()),

    "create_outline": Template("""
    Create a detailed outline of this video content:
    
    {{ transcript_content }}
    
    Structure it as a hierarchical outline with main points and sub-points.
    """.strip()),

    "extract_actionables": Template("""
    Identify all actionable items, recommendations, or next steps mentioned in this content:
    
    {{ transcript_content }}
    
    List them as clear, implementable action items.
    """.strip())
}


def render_custom_prompt(prompt_name, **kwargs):
    """Render a custom prompt template"""
    if prompt_name not in CUSTOM_PROMPTS:
        raise ValueError(f"Custom prompt '{prompt_name}' not found")

    return CUSTOM_PROMPTS[prompt_name].render(**kwargs)
