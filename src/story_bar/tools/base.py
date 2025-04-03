from typing import Any, Dict, Optional, TypeVar
from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph

class ToolInput(BaseModel):
    """Base model for tool inputs"""
    pass

class ToolOutput(BaseModel):
    """Base model for tool outputs"""
    success: bool = Field(default=True)
    error_message: Optional[str] = None

T_Input = TypeVar('T_Input', bound=ToolInput)
T_Output = TypeVar('T_Output', bound=ToolOutput)

class ToolNode:
    """Base class for all tool nodes"""
    input_model: type[ToolInput]
    output_model: type[ToolOutput]
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    def to_openai_function(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_model.model_json_schema()
            }
        }
        
    def invoke(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool's functionality with validated input"""
        params = self.params_model(**args)
        try:
            validated_input = self.input_model.model_validate(args)
            result = self._execute(validated_input)
            validated_output = self.output_model.model_validate(result)
            return {
                "tool_result": validated_output.model_dump(),
                "messages": [ToolMessage(content=str(validated_output), tool_call_id=self.name)]
            }
        except Exception as e:
            error_output = self.output_model(success=False, error_message=str(e))
            return {
                "tool_result": error_output.model_dump(),
                "messages": [ToolMessage(content=str(error_output), tool_call_id=self.name)]
            }
        
    def _execute(self, validated_input: T_Input) -> T_Output:
        """Internal execution logic to be implemented by subclasses"""
        raise NotImplementedError
