"""
Configuration management using Pydantic Settings
"""
from functools import lru_cache
from typing import List, Set
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Configuration
    APP_NAME: str = Field(default="AI Image Editor", description="Application name")
    DEBUG: bool = Field(default=False, description="Debug mode")
    VERSION: str = Field(default="1.0.0", description="API version")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    
    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # File Upload Configuration
    UPLOAD_DIR: str = Field(default="./uploads", description="Upload directory")
    OUTPUT_DIR: str = Field(default="./outputs", description="Output directory")
    MAX_FILE_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file size in bytes"
    )
    ALLOWED_EXTENSIONS: str = Field(
        default=".jpg,.jpeg,.png,.webp",
        description="Comma-separated list of allowed file extensions"
    )
    
    # AI Model Configuration
    MODEL_CACHE_DIR: str = Field(default="./models", description="Model cache directory")
    DEFAULT_MODEL: str = Field(
        default="runwayml/stable-diffusion-v1-5",
        description="Default AI model to use"
    )
    DEVICE: str = Field(
        default="auto",
        description="Device to use (auto, cuda, cpu)"
    )
    
    # Hugging Face Configuration
    HF_TOKEN: str = Field(default="", description="Hugging Face access token")
    
    # Generation Configuration
    DEFAULT_STEPS: int = Field(default=30, description="Default inference steps")
    DEFAULT_STRENGTH: float = Field(default=0.75, description="Default strength")
    MAX_STEPS: int = Field(default=50, description="Maximum inference steps")
    MAX_IMAGE_SIZE: int = Field(default=1024, description="Maximum image dimension")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @validator("CORS_ORIGINS")
    def parse_cors_origins(cls, v: str) -> str:
        """Validate CORS origins format"""
        if not v:
            return "http://localhost:3000"
        return v
    
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    def get_allowed_extensions_set(self) -> Set[str]:
        """Get allowed extensions as a set"""
        return {ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()}
    
    def get_device(self) -> str:
        """Get the device to use for AI inference"""
        if self.DEVICE == "auto":
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        return self.DEVICE


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
