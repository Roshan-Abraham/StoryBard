from typing import Optional, Dict, List, Any, TypedDict, Annotated
from pydantic import BaseModel
from openai import OpenAI
import time
from typing import Literal
from langgraph.graph import MessagesState
# from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from story_bar.tools.file_tools import FileWriterNode, FileReaderNode
from story_bar.config import get_settings

class AgentState(MessagesState, TypedDict):
    """Base state schema for assistants"""
    thread_id: Optional[str]
    tool_results: Dict[str, Any]
    context: Dict[str, Any]

class Agent:
    def __init__(self, assistant_name: str, tools: Optional[Dict[str, Any]] = None):
        self.client = OpenAI()
        self.tools = tools or {}
        self.settings = get_settings()
        self.assistant = self._setup_assistant(assistant_name)
        self.session_context = {}
        
        # Add file tools by default
        self.tools['file_writer'] = FileWriterNode()
        self.tools['file_reader'] = FileReaderNode()

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Make the agent callable as a node function"""
        response = self.run(state)
        return {
            "messages": response["messages"],
            "thread_id": response["thread_id"],
            "context": self.session_context
        }

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
        
        # Create thread and run if it doesn't exist
        if not state["thread_id"]:
            run = self.client.beta.threads.create_and_run(
                assistant_id=self.assistant.id,
                thread={
                    "messages": [
                        {"role": "user", "content": user_message}
                    ]
                },
                additional_instructions=additional_instructions or self.instructions
            )
            state["thread_id"] = run.thread_id
        else:
            # Add user message to thread and create a run
            run = self.client.beta.threads.runs.create(
                thread_id=state["thread_id"],
                assistant_id=self.assistant.id,
                additional_messages=[
                    {"role": "user", "content": user_message}
                ],
                additional_instructions=additional_instructions or self.instructions
            )

        # Wait for completion
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=state["thread_id"],
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                raise Exception(f"Run failed: {run_status.last_error}")
            time.sleep(1)

        # Get messages
        messages = self.client.beta.threads.messages.list(
            thread_id=state["thread_id"]
        )
        
        # Update state with latest messages
        state["messages"] = messages.data
        
        return {
            'messages': messages.data,
            'thread_id': state["thread_id"]
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
        state["document_status"][doc_name] = path

    def update_session_context(self, context: Dict[str, Any]):
        """Update the shared session context"""
        self.session_context.update(context)