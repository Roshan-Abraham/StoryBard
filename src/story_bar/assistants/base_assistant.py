from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from openai import OpenAI
import time
from langgraph import Graph, Node
from src.story_bar.tools.file_tools import FileWriterNode, FileReaderNode
class AgentState(BaseModel):
    """State for agent execution"""
    messages: List = []
    thread_id: Optional[str] = None
    document_status: Dict[str, str] = {}  # Track document paths and statuses

class Agent:
    def __init__(self, assistant_id: str = None, tools: Optional[Dict[str, Any]] = None):
        self.client = OpenAI()
        self.tools = tools or {}
        self.file_manager = FileManager()
        
        # Add file tools by default
        self.tools['file_writer'] = FileWriterNode()
        self.tools['file_reader'] = FileReaderNode()
        
        if assistant_id:
            self.assistant = self.get_assistant(assistant_id)
        else:
            raise ValueError("An assistant_id must be provided to retrieve an existing assistant.")
        
        self.session_context = {}
       
        
    def update_tools(self):
        """Update assistant's tools"""
        tools = [tool.to_openai_function() for tool in self.tools.values()]
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tools=tools
        )

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
            # Initialize session directory
            self.file_manager.get_session_dir(state.thread_id)

        # Add context to message
        context_message = f"Session Context:\n{json.dumps(self.session_context, indent=2)}\n\nUser Message:\n{user_message}"

        # Add user message to thread
        self.client.beta.threads.messages.create(
            thread_id=state.thread_id,
            role="user",
            content=context_message
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

    def update_session_context(self, context: Dict[str, Any]):
        """Update the shared session context"""
        self.session_context.update(context)