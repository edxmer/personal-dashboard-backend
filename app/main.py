from app.components.news_api import get_curated_news
from app.services.serialization import save_data, load_data
import json

#news = get_curated_news()
#save_data(news, 'news_1.pkl')

news: list[dict] = load_data('saved/news_1.pkl') # type: ignore

for news_item in news:
    print(json.dumps(news_item, indent=4, ensure_ascii=False))
    print('\n---\n')