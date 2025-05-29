from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/taskdb"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "your-secret-key-here"
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
