from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    env_name: str = 'Local'
    base_url: str = 'http://localhost:8000'
    db_url: str = 'sqlite:///./shortener.db'

    class Config:
        env_file = '.env'


@lru_cache()  # Least Recently Used Cache strategy
def getSettings() -> Settings:
    settings = Settings()
    print(f'Settings loaded: {settings.env_name}')
    return settings
