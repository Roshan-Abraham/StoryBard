from .constants import ASSISTANT_IDS
from .base_assistant import Agent

def create_storyboard_assistant():
    """Creates and configures the storyboard assistant."""
    return Agent(assistant_id=ASSISTANT_IDS["storyboard"])
