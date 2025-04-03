from .base import ToolNode, ToolInput, ToolOutput
from typing import Optional, Dict, Any
from pydantic import Field
from ..utils.image_gen import ImageGenerator

class ImageGenerationInput(ToolInput):
    prompt: str = Field(description="Description of the scene to visualize")
    feedback: Optional[Dict[str, Any]] = Field(default=None, description="Optional feedback for image refinement")
    instructions: Optional[str] = Field(default=None, description="Optional additional instructions")

class ImageGenerationOutput(ToolOutput):
    image_path: Optional[str] = None
    modifications: Optional[Dict[str, Any]] = None

class StoryboardImageNode(ToolNode):
    """Node for generating storyboard images"""
    input_model = ImageGenerationInput
    output_model = ImageGenerationOutput
    
    def __init__(self):
        super().__init__(
            name="storyboard_image_gen",
            description="Generates images for storyboard frames based on scene descriptions"
        )
        self.image_gen = ImageGenerator()
        
    def _execute(self, validated_input: ImageGenerationInput) -> ImageGenerationOutput:
        prompt = validated_input.prompt
        if validated_input.feedback:
            prompt = self.image_gen.create_prompt_from_feedback({
                "base_prompt": prompt,
                **validated_input.feedback
            })
        if validated_input.instructions:
            prompt = self.image_gen.refine_prompt(prompt, validated_input.instructions)
            
        result = self.image_gen.generate_image(prompt)
        if result.success and result.image_path:
            process_result = self.image_gen.process_image(result.image_path)
            return ImageGenerationOutput(
                image_path=process_result.processed_image_path,
                modifications=process_result.modifications
            )
        return ImageGenerationOutput(
            success=False,
            error_message=result.error_message
        )
