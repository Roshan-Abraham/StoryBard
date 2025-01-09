from pydantic_settings import BaseSettings
from typing import Dict, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """System-wide settings and configuration"""
    
    # LLM Model Configuration
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL_NAME: str = "claude-3-sonnet-20240229"
    ANTHROPIC_TEMPERATURE: float = 1.0
    
    # OpenAI Configuration (if needed as fallback)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL_NAME: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7
    
    # Image Generation Configuration
    IMAGE_GEN_MODEL: str = "stable-diffusion-xl"
    IMAGE_GEN_API_KEY: Optional[str] = None
    IMAGE_OUTPUT_DIR: str = "output/images"
    IMAGE_SIZE: tuple = (1024, 1024)
    
    # Graph Generation Configuration
    GRAPH_OUTPUT_DIR: str = "output/graphs"
    GRAPH_FORMAT: str = "html"
    
    # Validation Settings
    MAX_SCRIPT_LENGTH: int = 50000
    MIN_SCRIPT_LENGTH: int = 1000
    VALIDATION_STRICTNESS: str = "medium"  # Options: low, medium, high
    
    # Assistant Configuration
    STORY_GENESIS_TEMPERATURE: float = 0.8
    SCRIPT_CONSISTENCY_TEMPERATURE: float = 0.5
    METADATA_SIMULATOR_TEMPERATURE: float = 0.7
    STORYBOARD_TEMPERATURE: float = 0.9
    DIRECTOR_TEMPERATURE: float = 0.6
    
    # Workflow Settings
    MAX_ITERATIONS: int = 10
    TIMEOUT_SECONDS: int = 300
    ENABLE_LOGGING: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Storage Configuration
    STORAGE_DIR: str = "data/storage"
    CACHE_DIR: str = "data/cache"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Returns cached settings instance"""
    return Settings() 