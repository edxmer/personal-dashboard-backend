import asyncio
import uvicorn
from fastapi import FastAPI, Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.api.news_api import fetch_and_cache_news, get_news, should_recache
from app.schemas.news_schema import Article

# API Lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_and_cache_news, 'cron', hour='6,20')
    scheduler.start()
    
    if should_recache():
        asyncio.create_task(fetch_and_cache_news())
    
    yield
    
    scheduler.shutdown()

# API key validation

api_key_header = APIKeyHeader(name='API_KEY', auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Missing or invalid API key'
        )
    return api_key

# Create the API instance

app = FastAPI(lifespan=lifespan, dependencies=[Depends(validate_api_key)])

# Expose endpoints

@app.get('/api/news', response_model=list[Article])
def read_news():
    return get_news()

# Start the server

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='127.0.0.1', port=8000, reload=False)