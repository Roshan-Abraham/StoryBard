from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, TypedDict
from openai.types.beta.threads import ThreadMessage
from langgraph.graph import END, START, StateGraph

from src.story_bar.assistants.constants import ASSISTANT_IDS
from src.story_bar.assistants.base_assistant import Agent, AgentState
from src.story_bar.assistants.directory_planner import create_director_cinematographer_assistant
from src.story_bar.assistants.meta_simulator import create_metadata_simulator_assistant
from src.story_bar.assistants.script_consistancy import create_script_consistency_assistant
from src.story_bar.assistants.storyboard_generator import create_storyboard_assistant

@dataclass
class WorkflowState(TypedDict):
    """State definition for the workflow"""
    messages: List[ThreadMessage]
    current_assistant: str
    agent_states: Dict[str, AgentState]  # Track thread states for each assistant
    feedback: Dict
    next_assistant: Optional[str] = None

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
        "script_consistency": create_script_consistency_assistant,
        "metadata_simulator": create_metadata_simulator_assistant,
        "storyboard": create_storyboard_assistant,
        "director_cinematographer": create_director_cinematographer_assistant,
    }

    # Define the allowed transitions between assistants
    ALLOWED_TRANSITIONS = {
        "script_consistency": ["metadata_simulator", "storyboard"],
        "metadata_simulator": ["script_consistency", "storyboard", "director_cinematographer"],
        "storyboard": ["script_consistency", "director_cinematographer"],
        "director_cinematographer": ["script_consistency", "storyboard"]
    }

    def __init__(self):
        self.builder = StateGraph(WorkflowState)
        self._setup_nodes()
        self._setup_edges()
        
    def _setup_nodes(self):
        """Setup all nodes in the workflow graph"""
        # Add main assistant nodes
        for name, creator in self.ASSISTANT_NODES.items():
            self.builder.add_node(name, creator())
            self.builder.add_node(f"leave_{name}", AssistantTransition(name))

    def _route_after_leave(self, state: WorkflowState) -> str:
        """Determines the next assistant after leaving current one"""
        current = state["current_assistant"]
        next_assistant = state["next_assistant"]

        # Check if the transition is allowed
        if next_assistant in self.ALLOWED_TRANSITIONS.get(current, []):
            return next_assistant
        return END

    def _setup_edges(self):
        """Setup all edges in the workflow graph"""
        # Initial edge
        self.builder.add_edge(START, "script_consistency")
        
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

def create_workflow():
    """Creates and returns a compiled workflow"""
    return WorkflowManager().compile()

def run_workflow(initial_state: WorkflowState):
    """Runs the workflow with the given initial state"""
    graph = create_workflow()
    
    while True:
        next_state = graph.invoke(initial_state)
        if next_state == END:
            break
        initial_state = next_state

# Example usage
if __name__ == "__main__":
    initial_state = WorkflowState(
        messages=[],
        current_assistant="script_consistency",
        agent_states={},  # Initialize empty agent states
        feedback={},
        next_assistant=None
    )
    run_workflow(initial_state)
