import pytest
from workflows.main_graph import WorkflowState, create_workflow, run_workflow
import uuid

def test_workflow_initialization():
    """Test basic workflow initialization"""
    initial_state = WorkflowState(
        messages=[],
        current_assistant="story_genesis",
        agent_states={},
        feedback={},
        session_id=str(uuid.uuid4()),
        thread_id=None,
        next_assistant=None,
        shared_context={}
    )
    
    graph = create_workflow()
    assert graph is not None

def test_workflow_transitions():
    """Test workflow transitions between assistants"""
    initial_state = WorkflowState(
        messages=[],
        current_assistant="story_genesis",
        agent_states={},
        feedback={"next_assistant": "script_consistency"},
        session_id=str(uuid.uuid4()),
        thread_id=None,
        next_assistant=None,
        shared_context={}
    )
    
    try:
        run_workflow(initial_state)
    except Exception as e:
        pytest.fail(f"Workflow execution failed: {str(e)}")
