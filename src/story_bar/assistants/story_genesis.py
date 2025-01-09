from .constants import ASSISTANT_IDS
from .base_assistant import Agent

def create_script_consistency_assistant():
    """Creates and configures the script consistency assistant."""
    return Agent(assistant_id=ASSISTANT_IDS["script_consistency"])
