from story_bar.config import get_settings
from .base_assistant import Agent
from story_bar.tools.image_tools import StoryboardImageNode
from story_bar.tools.prompt_tools import PromptCleanerNode

def create_director_cinematographer_assistant():
    """Creates and configures the director and cinematographer assistant."""
    
    tools = {
        "storyboard_image": StoryboardImageNode(),
        "prompt_cleaner": PromptCleanerNode()
    }
    
    assistant = Agent(
        assistant_name="director_cinematographer",
        tools=tools
    )
    
    assistant.session_context.update({
        "stage": "direction",
        "shot_list": []
    })
    
    return assistant
