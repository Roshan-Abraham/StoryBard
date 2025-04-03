from .base import ToolNode, ToolInput, ToolOutput
from typing import Dict, Any, Optional
from pydantic import Field
from ..utils.graph_helper import GraphGenerator

class GraphGeneratorInput(ToolInput):
    data: Dict[str, Any] = Field(description="Data to visualize in the graph")
    graph_type: str = Field(default="metadata", description="Type of graph to generate")

class GraphGeneratorOutput(ToolOutput):
    graph_data: Dict[str, Any]
    visualization_path: Optional[str] = None

class GraphGeneratorNode(ToolNode):
    """Node for generating interactive graphs"""
    input_model = GraphGeneratorInput
    output_model = GraphGeneratorOutput
    
    def __init__(self):
        super().__init__(
            name="graph_generator",
            description="Generates interactive graphs for story visualization"
        )
        self.graph_gen = GraphGenerator()
        
    def _execute(self, validated_input: GraphGeneratorInput) -> GraphGeneratorOutput:
        result = self.graph_gen.generate_interactive_graph(
            validated_input.data,
            validated_input.graph_type
        )
        
        if not result.success:
            return GraphGeneratorOutput(
                success=False,
                error_message=result.error_message
            )
            
        return GraphGeneratorOutput(
            graph_data=result.graph_data,
            visualization_path=result.visualization_path
        )
