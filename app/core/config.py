from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dataclasses import dataclass

ENV_PATH = Path(__file__).resolve().parent.parent.parent / '.env'

class Settings(BaseSettings):
    debug: bool = False
    
    gnews_api_key: str
    dropbox_api_key: str
    
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

@dataclass
class NewsApiCall:
    endpoint: str
    parameters: dict
    max_count: int

# Setting variables that should be used from outside

settings = Settings() # type: ignore

news_api_calls: list[NewsApiCall] = [
    NewsApiCall('search', {'q': '"artificial intelligence" OR "PyTorch" OR "machine learning"', 'lang': 'en'}, 6),
    NewsApiCall('top-headlines', {'category': 'general', 'lang': 'en'}, 3),
    NewsApiCall('top-headlines', {'category': 'general', 'country': 'hu'}, 2),
    NewsApiCall('search', {'q':'"microcontroller" OR "PCB" OR "3D printing"', 'lang': 'en'}, 2),
    NewsApiCall('search', {'q': '"healthcare IT" OR "medical AI"', 'lang': 'en'}, 2),
]