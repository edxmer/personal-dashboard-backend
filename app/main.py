import asyncio
import uvicorn
from fastapi import FastAPI, Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import app.api.news_api as news_api
import app.api.superprod_api as superprod_api
from app.core.config import settings

from app.schemas.news_schema import Article
from app.schemas.superprod_schema import Task

# * Create API lifespan *

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    
    
    scheduler.add_job(news_api.fetch_and_cache, 'cron', hour='6,20')
    scheduler.add_job(superprod_api.fetch_and_cache, 'interval', minutes=1)
    
    
    scheduler.start()
    
    
    if news_api.should_recache():
        asyncio.create_task(news_api.fetch_and_cache())
    
    if superprod_api.should_recache():
        asyncio.create_task(superprod_api.fetch_and_cache())
    
    yield
    
    scheduler.shutdown()


# * API key validation*

api_key_header = APIKeyHeader(name='API_KEY', auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Missing or invalid API key'
        )
    return api_key


# * Create the API instance *

app = FastAPI(lifespan=lifespan, dependencies=[Depends(validate_api_key)])


# * API endpoints *

@app.get('/api/news', response_model=list[Article])
def get_news():
    return news_api.get_news()

@app.get('/tasks/today', response_model=list[Task])
def get_tasks_today():
    return superprod_api.get_tasks_today()

# * Start the server *

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='127.0.0.1', port=8000, reload=False)