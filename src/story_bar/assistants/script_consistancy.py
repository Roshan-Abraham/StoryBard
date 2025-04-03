from story_bar.config import get_settings
from .base_assistant import Agent
from story_bar.tools.prompt_tools import PromptCleanerNode
from story_bar.tools.file_tools import FileWriterNode, FileReaderNode

def create_script_consistency_assistant():
    """Creates and configures the script consistency assistant."""
    
    tools = {
        "prompt_cleaner": PromptCleanerNode(),
        "file_writer": FileWriterNode(),
        "file_reader": FileReaderNode()
    }
    
    assistant = Agent(
        assistant_name="script_consistency",
        tools=tools
    )
    
    assistant.session_context.update({
        "stage": "consistency_check",
        "validated_scenes": []
    })
    
    return assistant
