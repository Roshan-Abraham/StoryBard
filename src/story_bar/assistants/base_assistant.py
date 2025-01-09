from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from openai import OpenAI
import time
from src.utils.file_utils import read_json, write_json, read_text, write_text

class AgentState(BaseModel):
    """State for agent execution"""
    messages: List = []
    thread_id: Optional[str] = None
    document_status: Dict[str, str] = {}  # Track document paths and statuses

class Agent:
    def __init__(self, assistant_id: str):
        self.client = OpenAI()
        self.assistant = self.get_assistant(assistant_id)
        self.name = self.assistant.name
        self.instructions = self.assistant.instructions
        self.tools = self.assistant.tools
        self.model = self.assistant.model
        
    def get_assistant(self, assistant_id: str):
        """Retrieve an existing OpenAI assistant using its ID"""
        try:
            assistant = self.client.beta.assistants.retrieve(assistant_id=assistant_id)
            return assistant
        except Exception as e:
            raise Exception(f"Failed to retrieve assistant with ID {assistant_id}: {str(e)}")

    def run(self, state: AgentState, user_message: str, additional_instructions: Optional[str] = None) -> Dict[str, Any]:
        """Run the assistant with the given message"""
        
        # Create thread if it doesn't exist
        if not state.thread_id:
            thread = self.client.beta.threads.create()
            state.thread_id = thread.id

        # Add user message to thread
        self.client.beta.threads.messages.create(
            thread_id=state.thread_id,
            role="user",
            content=user_message
        )

        # Run the assistant
        run = self.client.beta.threads.runs.create(
            thread_id=state.thread_id,
            assistant_id=self.assistant.id,
            instructions=additional_instructions or self.instructions
        )

        # Wait for completion
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=state.thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                raise Exception(f"Run failed: {run_status.last_error}")
            time.sleep(1)

        # Get messages
        messages = self.client.beta.threads.messages.list(
            thread_id=state.thread_id
        )
        
        # Update state with latest messages
        state.messages = messages.data
        
        return {
            'messages': messages.data,
            'thread_id': state.thread_id
        }

    def handle_tool_calls(self, messages: List[Dict]) -> Optional[Dict]:
        """Process any tool calls from the assistant's response"""
        if not messages:
            return None
            
        latest_message = messages[0]
        if not hasattr(latest_message, "tool_calls"):
            return None

        results = []
        for tool_call in latest_message.tool_calls:
            if tool_call.function.name in self.tools:
                tool = self.tools[tool_call.function.name]
                result = tool.invoke(tool_call.function.arguments)
                results.append({
                    "tool_call_id": tool_call.id,
                    "output": str(result)
                })
        
        return results if results else None 

    def update_document_status(self, state: AgentState, doc_name: str, path: str):
        """Update the status of a document in the state."""
        state.document_status[doc_name] = path 