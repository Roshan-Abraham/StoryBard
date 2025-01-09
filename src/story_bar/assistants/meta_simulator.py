from .constants import ASSISTANT_IDS
from .base_assistant import Agent

def create_metadata_simulator_assistant():
    """Creates and configures the metadata and simulator assistant."""
    return Agent(assistant_id=ASSISTANT_IDS["metadata_simulator"])

