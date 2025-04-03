from typing import Optional, Dict, List
from dataclasses import dataclass
from openai import OpenAI
import os

@dataclass
class ValidationResult:
    is_valid: bool
    message: str
    errors: List[str] = None

@dataclass
class ValidationRule:
    name: str
    description: str
    check_function: callable
    severity: str = "error"

class ScriptValidator:
    """Handles validation of scripts and workflows"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.validation_rules = {
            'narrative': self._get_narrative_rules(),
            'character': self._get_character_rules(),
            'consistency': self._get_consistency_rules()
        }
    
    def validate_workflow(self, workflow: str) -> ValidationResult:
        """Validates a workflow for the creation of the script and storyline."""
        errors = []
        for rule in self.validation_rules['workflow']:
            if not rule(workflow):
                errors.append(f"Failed validation rule: {rule.__name__}")
        
        is_valid = len(errors) == 0
        message = "Workflow validated successfully" if is_valid else "Workflow validation failed"
        
        return ValidationResult(
            is_valid=is_valid,
            message=message,
            errors=errors
        )

    def validate_consistency(self, script: str, validation_points: List[str]) -> ValidationResult:
        """Enhanced consistency validation with LLM assistance"""
        errors = []
        
        # Use LLM to check narrative consistency
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Analyze the following script for consistency issues:"},
                {"role": "user", "content": script}
            ]
        )
        
        llm_analysis = self._parse_llm_response(response.choices[0].message.content)
        
        # Combine LLM analysis with rule-based checks
        for point in validation_points:
            rule_type, value = point.split(":", 1)
            for rule in self.validation_rules[rule_type]:
                if not rule.check_function(script, value):
                    errors.append(f"{rule.severity}: {rule.description}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            message="Validation complete",
            errors=errors
        )

    def _get_narrative_rules(self) -> List[ValidationRule]:
        """Define narrative validation rules"""
        return [
            ValidationRule(
                name="plot_coherence",
                description="Check plot point coherence",
                check_function=self._check_plot_coherence
            ),
            ValidationRule(
                name="scene_flow",
                description="Check scene flow and transitions",
                check_function=self._check_scene_flow
            )
        ]

    def _check_plot_coherence(self, script: str, plot_point: str) -> bool:
        """Check if plot point maintains coherence"""
        # Implement plot coherence check
        return True

    def _check_scene_flow(self, script: str, scene_data: str) -> bool:
        """Check scene flow and transitions"""
        # Implement scene flow check
        return True

    def _get_character_rules(self):
        """Returns the list of character validation rules"""
        return [
            ValidationRule(
                name="character_consistency",
                description="Check character consistency",
                check_function=self._check_character_consistency
            )
        ]

    def _get_consistency_rules(self):
        """Returns the list of consistency validation rules"""
        return [
            ValidationRule(
                name="narrative_consistency",
                description="Check narrative consistency",
                check_function=self._check_narrative_consistency
            ),
            ValidationRule(
                name="plot_consistency",
                description="Check plot consistency",
                check_function=self._check_plot_consistency
            )
        ]

    def _check_workflow_structure(self, workflow: str) -> bool:
        # Implement workflow structure validation
        return True

    def _check_workflow_completeness(self, workflow: str) -> bool:
        # Implement workflow completeness validation
        return True

    def _check_narrative_consistency(self, script: str) -> bool:
        # Implement narrative consistency check
        return True

    def _check_character_consistency(self, script: str) -> bool:
        # Implement character consistency check
        return True

    def _check_plot_consistency(self, script: str) -> bool:
        # Implement plot consistency check
        return True

    def _parse_llm_response(self, response: str) -> Dict:
        """Parse the LLM response for consistency issues"""
        # Implement LLM response parsing
        return {}
