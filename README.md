# Personal dashboard backend

I am making this because I want a simple way to check out the most relevant news, my todo for today, my shopping list and stuff like that in a single place.

## Quick start

TODO: write this when I finish the project

## Current components

1. News, from GNews API
2. todo (today's todo and shopping list), from SuperProductivity, using the Dropbox sync


## File structure

```
dashboard/
	.gitignore
	backend/
		app/
			__init__.py 
			main.py
			core/
				__init__.py
				config.py
                    settings: Settings
                    news_api_calls: list[NewsApiCall]
			components/
				__init__.py
				news-api.py
					get_curated_news()
				todo-api.py
					get_todo_today()
					get_todo_shopping()
			schemas/
				__init__.py
				news_schema.py
				todo_schema.py
            services/
                __init__.py
                serialization.py
                    save_data(data, path)
                    load_data(path)
        _cached/ # It will save the articles and other stuff here
		requirements.txt
		.env # API keys & debug mode
```