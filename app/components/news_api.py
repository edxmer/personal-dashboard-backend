from app.core.config import settings, news_api_calls, NewsApiCall
import requests
import time

_BREAK_BETWEEN_CALLS: float = 1.1

def _call_gnews_api(call: NewsApiCall) -> dict:
    url = f'https://gnews.io/api/v4/{call.endpoint}'
    
    parameters = call.parameters.copy()
    parameters['max'] = call.max_count
    parameters['apikey'] = settings.gnews_api_key
    
    try:
        response = requests.get(url, params=parameters)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f'HTTPError raised for GNews API\'s {call.endpoint} endpoint: {e.response.status_code if e.response is not None else '-'}')
    except Exception:
        print("Exception raised for GNews API")
    return {}

def _gather_gnews_api_responses() -> list[dict]:
    responses = []
    for call in news_api_calls:
        response = _call_gnews_api(call)
        if response:
            responses.append(response)
        # First, I tried making all of this async calls, but the gnews api didnt like that,
        # so now I'm even putting breaks between calls, I hope it works this way
        time.sleep(_BREAK_BETWEEN_CALLS)
    return responses

def get_curated_news() -> list[dict]:
    responses = _gather_gnews_api_responses()
    return responses