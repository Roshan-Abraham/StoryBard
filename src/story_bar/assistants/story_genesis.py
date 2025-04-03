from story_bar.config import get_settings
from .base_assistant import Agent
from story_bar.tools.prompt_tools import PromptCleanerNode

def create_script_genesis_assistant():
    """Creates and configures the story genesis assistant."""
    
    tools = {
        "prompt_cleaner": PromptCleanerNode(),
        "story_analyzer": StoryAnalyzerNode()
    }
    
    assistant = Agent(
        assistant_name="story_genesis",
        tools=tools
    )
    
    # Update assistant configuration if needed
    assistant.session_context.update({
        "stage": "genesis",
        "analysis_complete": False
    })
    
    return assistant
