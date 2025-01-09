from typing import Optional, List, Dict
from dataclasses import dataclass
import logging
import os
from openai import OpenAI
import requests
from PIL import Image
import io

@dataclass
class ImageGenerationResult:
    success: bool
    image_path: Optional[str]
    error_message: Optional[str] = None

@dataclass
class ImageProcessingResult:
    success: bool
    processed_image_path: Optional[str]
    modifications: List[str]
    error_message: Optional[str] = None

class ImageGenerator:
    """Handles image generation and processing for storyboards using DALL-E"""
    
    def __init__(self, model_name: str = "dall-e-3"):
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_image(self, prompt: str) -> ImageGenerationResult:
        """Creates visual frames for storyboards using DALL-E."""
        try:
            self.logger.info(f"Generating image for prompt: {prompt}")
            image_path = self._generate_using_ai_model(prompt)
            return ImageGenerationResult(success=True, image_path=image_path)
        except Exception as e:
            self.logger.error(f"Image generation failed: {str(e)}")
            return ImageGenerationResult(success=False, image_path=None, error_message=str(e))

    def process_image(self, image_path: str) -> ImageProcessingResult:
        """Processes and enhances the generated image."""
        try:
            self.logger.info(f"Processing image: {image_path}")
            processed_path = self._apply_image_processing(image_path)
            modifications = self._get_modification_list()
            return ImageProcessingResult(
                success=True, 
                processed_image_path=processed_path, 
                modifications=modifications
            )
        except Exception as e:
            self.logger.error(f"Image processing failed: {str(e)}")
            return ImageProcessingResult(
                success=False, 
                processed_image_path=None, 
                modifications=[], 
                error_message=str(e)
            )

    def create_prompt_from_feedback(self, feedback: Dict) -> str:
        """Creates an enhanced prompt based on user feedback."""
        base_prompt = feedback.get("base_prompt", "")
        style = feedback.get("style", "realistic")
        mood = feedback.get("mood", "neutral")
        adjustments = feedback.get("adjustments", [])
        
        prompt_parts = [base_prompt]
        
        if style:
            prompt_parts.append(f"Style: {style}")
        if mood:
            prompt_parts.append(f"Mood: {mood}")
        if adjustments:
            prompt_parts.append(f"Additional details: {', '.join(adjustments)}")
            
        prompt = ". ".join(prompt_parts)
        self.logger.info(f"Created enhanced prompt: {prompt}")
        return prompt

    def refine_prompt(self, original_prompt: str, instructions: Dict) -> str:
        """Refines the prompt with specific artistic instructions."""
        refinements = []
        
        if "style" in instructions:
            refinements.append(f"in the style of {instructions['style']}")
        if "lighting" in instructions:
            refinements.append(f"with {instructions['lighting']} lighting")
        if "perspective" in instructions:
            refinements.append(f"from a {instructions['perspective']} perspective")
        if "details" in instructions:
            refinements.append(f"with focus on {instructions['details']}")
            
        refined_prompt = f"{original_prompt} {', '.join(refinements)}"
        self.logger.info(f"Refined prompt: {refined_prompt}")
        return refined_prompt

    def _generate_using_ai_model(self, prompt: str) -> str:
        """Generates image using DALL-E API."""
        try:
            response = self.client.images.generate(
                model=self.model_name,
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            image_data = requests.get(image_url).content
            
            # Save the image
            image_filename = f"generated_{hash(prompt)}.png"
            image_path = os.path.join(self.output_dir, image_filename)
            
            with open(image_path, "wb") as f:
                f.write(image_data)
                
            return image_path
            
        except Exception as e:
            self.logger.error(f"DALL-E image generation failed: {str(e)}")
            raise

    def _apply_image_processing(self, image_path: str) -> str:
        """Applies basic image processing using PIL."""
        try:
            # Load the image
            with Image.open(image_path) as img:
                # Apply basic enhancements
                processed_filename = f"processed_{os.path.basename(image_path)}"
                processed_path = os.path.join(self.output_dir, processed_filename)
                
                # Save the processed image
                img.save(processed_path, quality=95, optimize=True)
                
            return processed_path
            
        except Exception as e:
            self.logger.error(f"Image processing failed: {str(e)}")
            raise

    def _get_modification_list(self) -> List[str]:
        """Returns list of applied image modifications."""
        return [
            "quality_optimization",
            "format_standardization"
        ]
