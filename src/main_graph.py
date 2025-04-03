from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, TypedDict, Any
from langgraph.graph import END, START, StateGraph
import uuid
from story_bar.tools.file_tools import FileWriterNode, FileReaderNode
from story_bar.assistants.base_assistant import Agent, AgentState
from story_bar.assistants.directory_planner import create_director_cinematographer_assistant
from story_bar.assistants.meta_simulator import create_metadata_simulator_assistant
from story_bar.assistants.script_consistancy import create_script_consistency_assistant
from story_bar.assistants.storyboard_generator import create_storyboard_assistant
from story_bar.assistants.story_genesis import create_script_genesis_assistant
from openai import OpenAI
from story_bar.config import get_settings
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState

class WorkflowState(MessagesState, TypedDict):
    """Overall workflow state"""
    current_assistant: str
    agent_states: Dict[str, AgentState]
    feedback: Dict[str, Any]
    session_id: str
    thread_id: Optional[str]
    next_assistant: Optional[str]
    shared_context: Dict[str, Any]

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
                {"role": "system", "content": transition_content}
            ],
            "current_assistant": "pending_transition",
            "next_assistant": state.get("feedback", {}).get("next_assistant")
        }

class WorkflowManager:
    """Manages the AI workflow and transitions between assistants"""
    
    def __init__(self):
        self.builder = StateGraph(
            WorkflowState,
            config_schema={"recursion_limit": int}
        )
        self.shared_tools = self._initialize_shared_tools()
        self.settings = get_settings()
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
        for name, assistant_id in self.settings.ASSISTANT_IDS.items():
            assistant = Agent(assistant_name=name)
            # Inject shared tools
            assistant.tools.update(self.shared_tools)
            self.builder.add_node(name, assistant)
            self.builder.add_node(f"leave_{name}", AssistantTransition(name))

    def _ensure_session_continuity(self, state: WorkflowState) -> WorkflowState:
        """Ensure session continuity between assistant transitions"""
        client = OpenAI()
        
        if not state["thread_id"]:
            # Initialize OpenAI thread if not exists
            thread = client.beta.threads.create()
            state["thread_id"] = thread.id
        
        # Update agent states with thread_id
        for assistant_name in self.settings.ASSISTANT_IDS:
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
        for name in self.settings.ASSISTANT_IDS:
            # Main flow edge
            self.builder.add_edge(name, f"leave_{name}")
            
            # Conditional routing after leave
            self.builder.add_conditional_edges(
                f"leave_{name}",
                self._route_after_leave,
                [*self.ALLOWED_TRANSITIONS[name], END]
            )

    def _setup_transitions(self):
        """Setup transitions between assistants"""
        for name in self.settings.ASSISTANT_IDS:
            def transition_fn(state: Dict[str, Any]) -> Dict[str, Any]:
                next_assistant = state.get("next_assistant")
                return {
                    "current_assistant": next_assistant,
                    "messages": state["messages"]
                }
            
            self.builder.add_conditional_edges(
                name,
                transition_fn,
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
