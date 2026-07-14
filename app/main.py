from app.core.config import settings

print('debug' if settings.debug else 'no debug', settings.dropbox_api_key, settings.gnews_api_key)