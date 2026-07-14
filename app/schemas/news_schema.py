from pydantic import BaseModel, HttpUrl
from datetime import datetime

class NewsSource(BaseModel):
    name: str

class Article(BaseModel):
    title: str
    description: str
    content: str
    url: HttpUrl
    image: HttpUrl | None = None
    publishedAt: datetime
    lang: str
    source: NewsSource

