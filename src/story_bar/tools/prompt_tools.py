from .base import ToolNode, ToolInput, ToolOutput
from typing import List, Optional
from pydantic import Field
from ..utils.prompt_cleaner import PromptCleaner

class PromptCleanerInput(ToolInput):
    prompt: str = Field(description="The prompt text to clean")
    template: Optional[dict] = Field(default=None, description="Optional template for validation")

class PromptCleanerOutput(ToolOutput):
    cleaned_text: str
    modifications: List[str]
    is_valid: bool
    validation_errors: List[str] = Field(default_factory=list)

class PromptCleanerNode(ToolNode):
    """Node for cleaning and validating prompts"""
    input_model = PromptCleanerInput
    output_model = PromptCleanerOutput
    
    def __init__(self):
        super().__init__(
            name="prompt_cleaner",
            description="Cleans and validates prompt text for consistency"
        )
        self.cleaner = PromptCleaner()
        
    def _execute(self, validated_input: PromptCleanerInput) -> PromptCleanerOutput:
        clean_result = self.cleaner.clean_prompt(validated_input.prompt)
        validation_result = self.cleaner.validate_prompt_structure(validated_input.template or {})
        
        return PromptCleanerOutput(
            cleaned_text=clean_result.cleaned_text,
            modifications=clean_result.modifications,
            is_valid=validation_result.is_valid,
            validation_errors=validation_result.errors
        )
