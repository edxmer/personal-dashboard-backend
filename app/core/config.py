from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dataclasses import dataclass

ENV_PATH: Path = Path(__file__).resolve().parent.parent.parent / '.env'
CACHE_FOLDER_PATH: Path = Path(__file__).resolve().parent.parent.parent / '_cache'

class Settings(BaseSettings):
    debug: bool = False
    
    api_key: str
    
    gnews_api_key: str
    
    # this has to be used instead of a refresh token because they always expire in 4 hours
    dropbox_refresh_token: str
    dropbox_app_key: str
    dropbox_app_secret: str
    
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

@dataclass
class NewsApiCall:
    endpoint: str
    parameters: dict
    max_count: int
    category: str

# Setting variables that should be used from outside

settings = Settings() # type: ignore

news_api_calls: list[NewsApiCall] = [
    NewsApiCall('top-headlines', {'category': 'world', 'lang': 'en'}, 3, 'WORLD'),
    NewsApiCall('top-headlines', {'category': 'nation', 'country': 'hu'}, 2, 'HUNGARY'),
    NewsApiCall('search', {'q': '"artificial intelligence" OR "machine learning"', 'lang': 'en'}, 3, 'AI'),
    NewsApiCall('search', {'q': '"healthcare ai" OR "medical ai"', 'lang': 'en'}, 2, 'MED AI'),
    NewsApiCall('top-headlines', {'category': 'technology' ,'lang': 'en'}, 2, 'TECH'),
    NewsApiCall('top-headlines', {'category': 'science' ,'lang': 'en'}, 2, 'SCIENCE'),
    NewsApiCall('top-headlines', {'category': 'health' ,'lang': 'en'}, 2, 'HEALTH'),
]