from main_graph import WorkflowManager, WorkflowState
import uuid
from IPython.display import Image

def main():
    # Initialize the workflow manager
    manager = WorkflowManager()
    
    # Save and display the workflow graph
    graph_path = manager.save_graph_visualization()
    try:
        # Display graph if in IPython environment
        display(Image(graph_path))
    except NameError:
        print(f"Graph saved to {graph_path}")
    
    # Create initial state
    initial_state = WorkflowState(
        messages=[
            {
                "role": "user",
                "content": "Create a story about a space explorer discovering a mysterious planet."
            }
        ],
        current_assistant="story_genesis",
        agent_states={},
        feedback={},
        session_id=str(uuid.uuid4()),
        thread_id=None,
        next_assistant=None,
        shared_context={}
    )
    
    # Run the workflow
    from main_graph import run_workflow
    run_workflow(initial_state)

if __name__ == "__main__":
    main()
