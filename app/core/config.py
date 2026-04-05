from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    DATABASE_URL: str
    GROQ_MODEL: str = "llama3-70b-8192"

    class Config:
        env_file = ".env"

settings = Settings()