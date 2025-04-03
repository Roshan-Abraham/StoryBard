from typing import Annotated, Any, Dict, Sequence, TypedDict, List
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import END, Graph
from IPython.display import Image, display
import json
from langgraph.graph.message import add_messages
import os
import asyncio
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI


os.environ["OPENAI_API_KEY"] = "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"

# -------------------- 1. Define Tool Classes --------------------
class StoryValidator:
    @tool
    def validate_story(self, story: str) -> str:
        """Validates the story structure and content."""
        return f"Story validated successfully: {len(story)} characters analyzed"

class MetadataGenerator:
    @tool
    def generate_metadata(self, story: str) -> dict:
        """Generates metadata for the story including themes, tone, and key elements."""
        return {
            "themes": ["learning", "growth", "creativity"],
            "tone": "inspirational",
            "key_elements": ["character development", "surprise ending"]
        }

# -------------------- 2. Define State --------------------
class State(TypedDict):
    """The state of our story generation flow."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    current_node: str
    next_node: str | None
    story_data: Dict[str, Any]

# -------------------- 3. Define Assistant Creator --------------------
def create_story_assistant():
    """Creates and configures the story generation assistant."""
    
    # Initialize tool instances
    validator = StoryValidator()
    metadata_gen = MetadataGenerator()

    # Collect tools
    story_tools = [
        validator.validate_story,
        metadata_gen.generate_metadata
    ]

    # Create the OpenAI Assistant with tools
    assistant = OpenAIAssistantRunnable(
        assistant_id="asst_UYnqHYzFIoW5cf8nSw09CvAN",
        as_agent=True,
        tools=story_tools
    )

    return assistant

# -------------------- 4. Graph Functions --------------------
def save_graph_visualization(graph: Graph, output_path: str = "story_graph"):
    """Save the graph visualization as both Mermaid diagram and PNG."""
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        with open(f"{output_path}.png", "wb") as f:
            f.write(png_data)
        print(f"Graph visualization saved to {output_path}.png")
    except Exception as e:
        print(f"Error saving graph visualization: {e}")
        try:
            mermaid_diagram = graph.get_graph().draw_mermaid()
            with open(f"{output_path}.mmd", "w") as f:
                f.write(mermaid_diagram)
            print(f"Fallback: Mermaid diagram saved to {output_path}.mmd")
        except Exception as e:
            print(f"Could not save visualization: {e}")

def create_story_graph() -> Graph:
    """Create a simple story generation workflow graph."""
    
    # Initialize the assistant
    story_assistant = create_story_assistant()
    
    async def process_story(state: State) -> State:
        """Process story with single assistant."""
        try:
            if len(state["messages"]) > 0:
                # Convert messages to the format expected by the assistant
                messages = []
                for msg in state["messages"]:
                    if isinstance(msg, dict):
                        if msg["role"] == "user":
                            messages.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            messages.append(AIMessage(content=msg["content"]))
                    else:
                        messages.append(msg)
                
                # Invoke the assistant using LangChain's interface
                response = await story_assistant.ainvoke({
                    "messages": messages,
                })
                
                # Extract the response content
                response_content = response.content if hasattr(response, 'content') else str(response)
                
                return {
                    **state,
                    "messages": state["messages"] + [{"role": "assistant", "content": response_content}],
                    "next_node": END
                }
            else:
                return {
                    **state,
                    "messages": state["messages"],
                    "next_node": END
                }
                
        except Exception as e:
            print(f"Error in process_story: {e}")
            raise

    # Create and compile the graph
    graph = Graph()
    graph.add_node("process_story", process_story)
    graph.add_edge("process_story", END)
    graph.set_entry_point("process_story")

    return graph.compile()

def create_initial_state() -> State:
    """Create the initial state for the graph."""
    return {
        "messages": [],
        "current_node": "process_story",
        "next_node": None,
        "story_data": {}
    }

async def run_story_generation(user_input: str):
    """Run the story generation workflow."""
    graph = create_story_graph()
    save_graph_visualization(graph)
    
    state = create_initial_state()
    state["messages"].append({"role": "user", "content": user_input})
    
    final_state = await graph.ainvoke(state)
    return final_state

def print_messages(state):
    """Helper function to print messages from the state"""
    for message in state["messages"]:
        if isinstance(message, dict) and "content" in message:
            print(f"\n{message['role'].upper()}: {message['content']}")
        elif hasattr(message, 'content') and message.content:
            print(f"\n{message.role.upper()}: {message.content}")

if __name__ == "__main__":
    # Create and save graph visualization
    graph = create_story_graph()
    save_graph_visualization(graph)
    print("Graph has been created and saved.")
    
    # Display the graph visualization
    try:
        display(Image("story_graph.png"))
    except Exception as e:
        print(f"Error displaying graph: {e}")
    
    # Print graph structure
    graph_structure = graph.get_graph()
    print(f"Nodes: {list(graph_structure.nodes)}")
    print(f"Number of edges: {len(list(graph_structure.edges))}")
    
    # Test query
    test_query = """Create a short story about a robot who learns to paint. 
    Include these elements:
    - The robot should start with no knowledge of art
    - There should be a mentor character
    - The story should have a surprising ending
    Keep it under 500 words."""
    
    print("\nSending test query to the assistant...")
    print(f"Query: {test_query}\n")
    print("Waiting for response...\n")
    
    # try:
    # Run the async function
    final_state = asyncio.run(run_story_generation(test_query))
    
    # Print the results
    print("\n=== RESPONSE ===")
    print_messages(final_state)
    # except Exception as e:
    #     print(f"Error running story generation: {e}")
