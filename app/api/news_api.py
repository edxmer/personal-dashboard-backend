from app.core.config import settings, news_api_calls, NewsApiCall, CACHE_FOLDER_PATH
from app.schemas.news_schema import Article
from app.services.serialization import save_data, load_data
from pydantic import ValidationError
from pathlib import Path
from datetime import datetime, timedelta
import httpx
import asyncio

_BREAK_BETWEEN_CALLS: float = 1.1

_SAVE_LOCATION: Path = CACHE_FOLDER_PATH / 'news.pkl'
_METADATA_LOCATION: Path = CACHE_FOLDER_PATH / 'news.metadata.pkl'

async def _call_gnews_api(client: httpx.AsyncClient, call: NewsApiCall) -> dict:
    url = f'https://gnews.io/api/v4/{call.endpoint}'
    
    parameters = call.parameters.copy()
    parameters['max'] = call.max_count
    parameters['apikey'] = settings.gnews_api_key
    
    print(f'Requesting {url} with parameters: {parameters}...')
    
    try:
        response = await client.get(url, params=parameters)
        response.raise_for_status()
        
        print('Success!')
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f'HTTPStatusError raised for GNews API\'s {call.endpoint} endpoint: {e.response.status_code if e.response is not None else '-'}')
    except Exception:
        print("Exception raised for GNews API")
    return {}

async def _get_gnews_api_responses() -> list[dict]:
    responses = []
    async with httpx.AsyncClient() as client:
        for call in news_api_calls:
            response = await _call_gnews_api(client, call)
            if response:
                response['category'] = call.category
                responses.append(response)
            await asyncio.sleep(_BREAK_BETWEEN_CALLS)
    return responses

async def _get_gnews_api_schema_responses() -> list[Article]:
    responses = await _get_gnews_api_responses()
    
    # Convert to the schema format
    articles: list[Article] = []
    for response in responses:
        batch = response['articles']
        category = response['category']
        for article in batch:
            try:
                articles.append(Article(**article, category=category))
            except ValidationError as e:
                print(f'Validation error on article: {e.error_count} errors found.')
    return articles

def _get_metadata() -> dict:
    if not _METADATA_LOCATION.exists():
        return {}
    
    metadata = load_data(_METADATA_LOCATION)
    return metadata

async def fetch_and_cache_news():
    news = await _get_gnews_api_schema_responses()
    date = datetime.now()
    metadata = {'date': date}
    
    _SAVE_LOCATION.parent.mkdir(parents=True, exist_ok=True)
    
    save_data(news, _SAVE_LOCATION)
    save_data(metadata, _METADATA_LOCATION)

def get_news() -> list[Article]:
    if not _SAVE_LOCATION.exists():
        return []
    
    news: list[Article] = load_data(_SAVE_LOCATION)
    
    return news

def should_recache() -> bool:
    if not _SAVE_LOCATION.exists() or not _METADATA_LOCATION.exists():
        return True
    
    metadata = _get_metadata()
    
    last_cache_date: datetime = metadata['date']
    elapsed_time: timedelta = datetime.now() - last_cache_date
    
    elapsed_hours = elapsed_time.total_seconds() / (60.0 * 60.0)
    
    return elapsed_hours >= 12
    