# hr-service/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DB_HOST: str = "195.35.45.118"
    DB_PORT: str = "3306"
    DB_USER: str = "devflow"
    DB_PASSWORD: str = "Devflow2025"
    DB_NAME: str = "project_db"

    # Construct the MySQL URL from components
    @property
    def PMYSQL_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Auth service settings
    AUTH_SERVICE_URL: str = "http://140.245.213.62:8000"
    
    # Application settings
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "Project Service"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()