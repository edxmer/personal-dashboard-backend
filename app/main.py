import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import uvicorn

from app.components.news_api import fetch_and_cache_news, get_news
from app.schemas.news_schema import Article

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_and_cache_news, 'cron', hour='6,20')
    scheduler.start()
    
    from app.components.news_api import _CACHE_LOCATION
    if not _CACHE_LOCATION.exists():
        asyncio.create_task(fetch_and_cache_news())
    
    yield
    
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# Expose endpoints

@app.get('/api/news', response_model=list[Article])
def read_news():
    return get_news()

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='127.0.0.1', port=8000, reload=True)