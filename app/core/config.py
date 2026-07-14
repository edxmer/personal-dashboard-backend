from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent.parent / '.env'

class Settings(BaseSettings):
    debug: bool = False
    
    gnews_api_key: str
    dropbox_api_key: str
    
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

settings = Settings() # type: ignore