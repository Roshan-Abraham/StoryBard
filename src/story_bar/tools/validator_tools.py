from .base import ToolNode, ToolInput, ToolOutput
from typing import List, Dict, Any
from pydantic import Field
from ..utils.validator import ScriptValidator

class ConsistencyValidatorInput(ToolInput):
    story_elements: str = Field(description="Story elements to validate for consistency")

class ConsistencyValidatorOutput(ToolOutput):
    is_valid: bool
    message: str
    errors: List[str] = Field(default_factory=list)

class ConsistencyValidatorNode(ToolNode):
    """Node for validating story consistency"""
    input_model = ConsistencyValidatorInput
    output_model = ConsistencyValidatorOutput
    
    def __init__(self):
        super().__init__(
            name="consistency_validator",
            description="Validates story consistency across scenes and characters"
        )
        self.validator = ScriptValidator()
        
    def _execute(self, validated_input: ConsistencyValidatorInput) -> ConsistencyValidatorOutput:
        result = self.validator.validate_consistency(validated_input.story_elements)
        return ConsistencyValidatorOutput(
            is_valid=result.is_valid,
            message=result.message,
            errors=result.errors
        )

class WorkflowValidatorInput(ToolInput):
    workflow_steps: str = Field(description="Workflow steps to validate")

class WorkflowValidatorOutput(ToolOutput):
    is_valid: bool
    message: str
    errors: List[str] = Field(default_factory=list)

class WorkflowValidatorNode(ToolNode):
    """Node for validating production workflow"""
    input_model = WorkflowValidatorInput
    output_model = WorkflowValidatorOutput
    
    def __init__(self):
        super().__init__(
            name="workflow_validator",
            description="Validates production workflow and dependencies"
        )
        self.validator = ScriptValidator()
        
    def _execute(self, validated_input: WorkflowValidatorInput) -> WorkflowValidatorOutput:
        result = self.validator.validate_workflow(validated_input.workflow_steps)
        return WorkflowValidatorOutput(
            is_valid=result.is_valid,
            message=result.message,
            errors=result.errors
        )
