from langchain_anthropic import ChatAnthropic
from datetime import datetime
from ..utils.validator import validate_consistency, validate_workflow
from .base_assistant import Agent, CompleteOrEscalate

def create_script_consistency_assistant():
    """Creates and configures the script consistency assistant."""
    
    system_prompt = (
        "You are a script consistency manager, tasked with generating, validating "
        "and refining scripts based on user needs. Ensure consistency in plot, "
        "characters, and narrative flow. Use your tools to validate workflows "
        "and generate supplementary materials.\n"
        f"Current time: {datetime.now()}"
    )

    tool_list = [
        validate_consistency,
        validate_workflow,
        CompleteOrEscalate
    ]

    model = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=1)
    
    return Agent(model=model, tools=tool_list, system=system_prompt)
