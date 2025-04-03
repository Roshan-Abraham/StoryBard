from story_bar.config import get_settings
from .base_assistant import Agent
from story_bar.tools.image_tools import StoryboardImageTool

def create_storyboard_assistant():
    """Creates and configures the storyboard assistant."""
    settings = get_settings()
    image_gen_tool = StoryboardImageTool()
    
    tools = {"storyboard_image_gen": image_gen_tool}
    
    assistant = Agent(
        assistant_id=settings.ASSISTANT_IDS.get("storyboard"),
        tools=tools
    )
    
    if not settings.ASSISTANT_IDS.get("storyboard"):
        assistant.name = "Storyboard Assistant"
        assistant.instructions = """You are a storyboard assistant that helps create 
        visual representations of scenes. Use the image generation tool to create 
        storyboard frames based on scene descriptions."""
        
    return assistant