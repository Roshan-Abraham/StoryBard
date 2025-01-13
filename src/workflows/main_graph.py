from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, TypedDict
from openai.types.beta.threads import ThreadMessage
from langgraph.graph import END, START, StateGraph
import uuid
from src.story_bar.tools.file_tools import FileWriterNode, FileReaderNode
from src.story_bar.assistants.constants import ASSISTANT_IDS
from src.story_bar.assistants.base_assistant import Agent, AgentState
from src.story_bar.assistants.directory_planner import create_director_cinematographer_assistant
from src.story_bar.assistants.meta_simulator import create_metadata_simulator_assistant
from src.story_bar.assistants.script_consistancy import create_script_consistency_assistant
from src.story_bar.assistants.storyboard_generator import create_storyboard_assistant
from src.story_bar.assistants.story_genesis import create_script_genesis_assistant

@dataclass
class WorkflowState(TypedDict):
    """State definition for the workflow"""
    messages: List[ThreadMessage]
    current_assistant: str
    agent_states: Dict[str, AgentState]  # Track thread states for each assistant
    feedback: Dict
    session_id: str  # Add session ID to track conversation context
    thread_id: Optional[str] = None  # OpenAI thread ID
    next_assistant: Optional[str] = None
    shared_context: Dict[str, Any] = {}  # Shared context between assistants

class AssistantTransition:
    """Handles transitions between assistants"""
    def __init__(self, assistant_name: str):
        self.assistant_name = assistant_name
    
    def __call__(self, state: WorkflowState) -> WorkflowState:
        """Creates a transition state for the assistant"""
        # Get the last message content
        last_message = state["messages"][-1] if state["messages"] else None
        transition_content = f"Transitioning from {self.assistant_name}"
        
        if last_message:
            transition_content += f"\nLast message: {last_message.content}"

        return {
            **state,
            "messages": [
                *state["messages"],
                ThreadMessage(
                    role="system",
                    content=transition_content
                )
            ],
            "current_assistant": "pending_transition",
            "next_assistant": state.get("feedback", {}).get("next_assistant")
        }

class WorkflowManager:
    """Manages the AI workflow and transitions between assistants"""
    
    ASSISTANT_NODES = {
        "story_genesis": create_script_genesis_assistant,
        "script_consistency": create_script_consistency_assistant,
        "metadata_simulator": create_metadata_simulator_assistant,
        "storyboard": create_storyboard_assistant,
        "director_cinematographer": create_director_cinematographer_assistant,
    }

    # Define the allowed transitions between assistants
    ALLOWED_TRANSITIONS = {
        "story_genesis": ["script_consistency"],
        "script_consistency": ["metadata_simulator", "storyboard"],
        "metadata_simulator": ["script_consistency", "storyboard", "director_cinematographer"],
        "storyboard": ["script_consistency", "director_cinematographer"],
        "director_cinematographer": ["script_consistency", "storyboard"]
    }

    def __init__(self):
        self.builder = StateGraph(WorkflowState)
        self.shared_tools = self._initialize_shared_tools()
        self._setup_nodes()
        self._setup_edges()
        
    def _initialize_shared_tools(self):
        """Initialize tools that will be shared across assistants"""
        return {
            'file_writer': FileWriterNode(),
            'file_reader': FileReaderNode(),
            # Add other shared tools here
        }
    
    def _setup_nodes(self):
        """Setup all nodes in the workflow graph"""
        # Add main assistant nodes with shared tools
        for name, creator in self.ASSISTANT_NODES.items():
            assistant = creator()
            # Inject shared tools
            assistant.tools.update(self.shared_tools)
            self.builder.add_node(name, assistant)
            self.builder.add_node(f"leave_{name}", AssistantTransition(name))

    def _ensure_session_continuity(self, state: WorkflowState) -> WorkflowState:
        """Ensure session continuity between assistant transitions"""
        if not state["thread_id"]:
            # Initialize OpenAI thread if not exists
            client = OpenAI()
            thread = client.beta.threads.create()
            state["thread_id"] = thread.id
        
        # Update agent states with thread_id
        for assistant_name in self.ASSISTANT_NODES:
            if assistant_name not in state["agent_states"]:
                state["agent_states"][assistant_name] = AgentState(
                    thread_id=state["thread_id"],
                    messages=[],
                    document_status={}
                )
        
        return state

    def _route_after_leave(self, state: WorkflowState) -> str:
        """Determines the next assistant after leaving current one"""
        state = self._ensure_session_continuity(state)
        current = state["current_assistant"]
        next_assistant = state["next_assistant"]

        # Check if the transition is allowed
        if next_assistant in self.ALLOWED_TRANSITIONS.get(current, []):
            return next_assistant
        return END

    def _setup_edges(self):
        """Setup all edges in the workflow graph"""
        # Initial edge now starts with story_genesis
        self.builder.add_edge(START, "story_genesis")
        
        # Setup transitions for each assistant
        for name in self.ASSISTANT_NODES:
            # Main flow edge
            self.builder.add_edge(name, f"leave_{name}")
            
            # Conditional routing after leave
            self.builder.add_conditional_edges(
                f"leave_{name}",
                self._route_after_leave,
                [*self.ALLOWED_TRANSITIONS[name], END]
            )

    def compile(self):
        """Compiles and returns the workflow graph"""
        return self.builder.compile()

    def save_graph_visualization(self, output_path: str = "workflow_graph"):
        """Save the graph visualization as both Mermaid diagram and PNG."""
        try:
            graph = self.compile()
            png_data = graph.get_graph().draw_mermaid_png()
            with open(f"{output_path}.png", "wb") as f:
                f.write(png_data)
            print(f"Graph visualization saved to {output_path}.png")
            return f"{output_path}.png"
        except Exception as e:
            print(f"Error saving graph visualization: {e}")
            try:
                mermaid_diagram = graph.get_graph().draw_mermaid()
                with open(f"{output_path}.mmd", "w") as f:
                    f.write(mermaid_diagram)
                print(f"Fallback: Mermaid diagram saved to {output_path}.mmd")
            except Exception as e:
                print(f"Could not save visualization: {e}")

def create_workflow():
    """Creates and returns a compiled workflow"""
    manager = WorkflowManager()
    return manager.compile()

def run_workflow(initial_state: WorkflowState):
    """Runs the workflow with the given initial state"""
    if not initial_state.get("session_id"):
        initial_state["session_id"] = str(uuid.uuid4())
    
    graph = create_workflow()
    while True:
        initial_state = WorkflowManager()._ensure_session_continuity(initial_state)
        next_state = graph.invoke(initial_state)
        if next_state == END:
            break
        initial_state = next_state

# Example usage
if __name__ == "__main__":
    from IPython.display import Image, display
    
    # Initialize workflow manager
    manager = WorkflowManager()
    
    # Save and display the graph visualization
    graph_path = manager.save_graph_visualization()
    try:
        display(Image(graph_path))
    except Exception as e:
        print(f"Error displaying graph: {e}")
    
    # Continue with the existing workflow execution
    initial_state = WorkflowState(
        messages=[],
        current_assistant="story_genesis",  # Changed initial assistant
        agent_states={},  # Initialize empty agent states
        feedback={},
        session_id=str(uuid.uuid4()),
        thread_id=None,
        next_assistant=None,
        shared_context={}
    )
    run_workflow(initial_state)
