import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "NexusOps Enterprise Control Plane"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./nexusops.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "nexusops-enterprise-secret-key-fde-portfolio-2026"
    
    # AI Agents
    OPENAI_API_KEY: str = "demo-key"
    LLM_MODEL: str = "gpt-4o-mini"
    HUMAN_IN_THE_LOOP_THRESHOLD: float = 0.75

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
