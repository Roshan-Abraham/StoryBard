from story_bar.config import get_settings
from .base_assistant import Agent
from story_bar.tools.prompt_tools import PromptCleanerNode

def create_metadata_simulator_assistant():
    """Creates and configures the metadata and simulator assistant."""
    
    tools = {
        "prompt_cleaner": PromptCleanerNode(),
        "metadata_generator": MetadataGeneratorNode()
    }
    
    assistant = Agent(
        assistant_name="metadata_simulator",
        tools=tools
    )
    
    assistant.session_context.update({
        "stage": "simulation",
        "metadata": {}
    })
    
    return assistant

