from typing import List, Dict, Optional
from dataclasses import dataclass
import re
from openai import OpenAI
import os

@dataclass
class CleaningResult:
    cleaned_text: str
    modifications: List[str]
    original_text: str

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]

@dataclass
class PromptResult:
    cleaned_text: str
    structured_data: Dict
    scene_details: Optional[Dict] = None
    validation_points: List[str] = None

class PromptCleaner:
    """Handles cleaning and validation of prompts"""
    
    def __init__(self):
        self.cleaning_rules = [
            self._remove_extra_whitespace,
            self._normalize_punctuation,
            self._fix_common_typos
        ]
        self.validation_rules = {
            'structure': self._validate_structure,
            'content': self._validate_content,
            'length': self._validate_length
        }
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.prompt_templates = {
            'scene': self._load_template('scene_prompt.txt'),
            'character': self._load_template('character_prompt.txt'),
            'validation': self._load_template('validation_prompt.txt')
        }

    def clean_prompt(self, prompt: str) -> CleaningResult:
        """Cleans and formats prompts for consistency."""
        original = prompt
        modifications = []
        
        for rule in self.cleaning_rules:
            prompt, mod = rule(prompt)
            if mod:
                modifications.extend(mod)
        
        return CleaningResult(
            cleaned_text=prompt,
            modifications=modifications,
            original_text=original
        )

    def validate_prompt_structure(self, prompt: Dict) -> ValidationResult:
        """Validates the structure of a prompt template."""
        errors = []
        
        for rule_name, rule in self.validation_rules.items():
            rule_errors = rule(prompt)
            if rule_errors:
                errors.extend(rule_errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )

    def process_creative_prompt(self, prompt: str, prompt_type: str = 'scene') -> PromptResult:
        """Process creative prompt through LLM for structured output"""
        clean_result = self.clean_prompt(prompt)
        
        # Get structured data through LLM
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.prompt_templates[prompt_type]},
                {"role": "user", "content": clean_result.cleaned_text}
            ]
        )
        
        structured_data = self._parse_llm_response(response.choices[0].message.content)
        
        return PromptResult(
            cleaned_text=clean_result.cleaned_text,
            structured_data=structured_data,
            scene_details=self._extract_scene_details(structured_data),
            validation_points=self._extract_validation_points(structured_data)
        )

    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response into structured data"""
        try:
            # Implement parsing logic for JSON-formatted LLM response
            return eval(response)  # Use json.loads in production
        except:
            return {"error": "Failed to parse LLM response"}

    def _extract_scene_details(self, data: Dict) -> Dict:
        """Extract scene-specific details for image generation"""
        return {
            "setting": data.get("setting", {}),
            "mood": data.get("mood", "neutral"),
            "lighting": data.get("lighting", "natural"),
            "perspective": data.get("perspective", "eye-level"),
            "key_elements": data.get("key_elements", [])
        }

    def _extract_validation_points(self, data: Dict) -> List[str]:
        """Extract validation points for consistency checking"""
        return [
            f"character:{char['name']}" for char in data.get("characters", [])
        ] + [
            f"plot_point:{point}" for point in data.get("plot_points", [])
        ]

    def _load_template(self, template_name: str) -> str:
        """Load prompt template from file"""
        # Implement template loading
        return "Default template content"

    def _remove_extra_whitespace(self, text: str) -> tuple[str, List[str]]:
        original = text
        text = re.sub(r'\s+', ' ', text.strip())
        return text, ["Removed extra whitespace"] if text != original else []

    def _normalize_punctuation(self, text: str) -> tuple[str, List[str]]:
        # Implement punctuation normalization
        return text, []

    def _fix_common_typos(self, text: str) -> tuple[str, List[str]]:
        # Implement typo fixing
        return text, []

    def _validate_structure(self, prompt: Dict) -> List[str]:
        # Implement structure validation
        return []

    def _validate_content(self, prompt: Dict) -> List[str]:
        # Implement content validation
        return []

    def _validate_length(self, prompt: Dict) -> List[str]:
        # Implement length validation
        return []
