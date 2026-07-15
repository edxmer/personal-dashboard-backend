# Personal dashboard backend

I am making this because I want a simple way to check out the most relevant news, my todo for today, my shopping list and stuff like that in a single place.

## Quick start

1. Clone the repo
2. Create a python (minimum version 3.14) venv: `python -m venv .venv`
3. Activate the venv
3. Install dependencies: `python -m pip -r requirements.txt`
4. Start the project: `python -m app.main`

## Current components

1. News, from GNews API


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
				news_api.py
					get_curated_news()
				todo_api.py # uncomplete
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