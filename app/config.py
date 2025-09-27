from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    secret_key: str = "your-secret-key-here"
    environment: str = "development"
    debug: bool = True
    
    # API Configuration
    api_title: str = "Smart Tourist Safety & Incident Response System"
    api_description: str = "Backend API for monitoring tourist safety and managing incident responses"
    api_version: str = "1.0.0"
    
    # Database Configuration
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()