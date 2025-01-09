from .constants import ASSISTANT_IDS
from .base_assistant import Agent

def create_director_cinematographer_assistant():
    """Creates and configures the director and cinematographer assistant."""
    return Agent(assistant_id=ASSISTANT_IDS["director_cinematographer"])
