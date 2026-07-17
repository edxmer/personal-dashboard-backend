import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from requests.models import Response

import dropbox
from dropbox.files import FileMetadata
from dropbox.exceptions import ApiError

from app.core.config import settings, CACHE_FOLDER_PATH
from app.schemas.superprod_schema import _Task, _Project, _Section, _Tag, _SuperProcuctivityData, Task
from app.services.serialization import save_data, load_data

_RECACHE_AFTER_MINUTES: float = 12.0

_DBX_DATA_FILE_PATH: str = '/Apps/super_productivity/sync-data.json'

_SAVE_LOCATION: Path = CACHE_FOLDER_PATH / 'tasks.pkl'
_METADATA_LOCATION: Path = CACHE_FOLDER_PATH / 'tasks.metadata.pkl'

async def _request_raw_task_data() -> str:
    dbx = dropbox.Dropbox(
        app_key=settings.dropbox_app_key,
        app_secret=settings.dropbox_app_secret,
        oauth2_refresh_token=settings.dropbox_refresh_token
    )
    
    try:
        metadata: FileMetadata; response: Response
        metadata, response = await asyncio.to_thread(dbx.files_download, path=_DBX_DATA_FILE_PATH) # type: ignore
        
        content: bytes = response.content
        decoded: str = content.decode('utf-8')
        
        return decoded
        
    except ApiError as e:
        print(f'An ApiError was raised when requesting super productivity data from dropbox: {e}')
    except UnicodeDecodeError as e:
        print(f'A DownloadError was raised when requesting super productivity data from dropbox: {e}')
    
    return ""

async def _get_raw_task_data_dict() -> dict:
    raw_str_data = await _request_raw_task_data()
    
    # clip the starting 'pf_2__' characters
    
    clipped_str_data = raw_str_data[6:]
    
    data = json.loads(clipped_str_data)
    
    return data

async def _get_parsed_task_data() -> _SuperProcuctivityData:
    data: dict = await _get_raw_task_data_dict()
    
    #   * TASKS *
    
    task_ids: list[str] = data['state']['task']['ids']
    task_entities: dict[str, dict] = data['state']['task']['entities']
    #   'id'            str
    #   'title'         str
    #   'isDone'        bool
    #   'dueDay'        str         "yyyy-mm-dd"
    #   'projectId'     str
    #   'tagIds'        list[str]
    #   'created'       int
    #   'modified'      int
    
    #   * PROJECTS *

    project_ids: list[str] = data['state']['project']['ids']
    # The first item, with id "INBOX_PROJECT" is the built in inbox
    
    project_entities: dict[str, dict] = data['state']['project']['entities']
    #   'id'            str
    #   'title'         str
    #   'taskIds'       list[str]
    
    #   * SECTIONS *

    section_ids: list[str] = data['state']['section']['ids']
    
    section_entities: dict[str, dict] = data['state']['section']['entities']
    #   'id'            str
    #   'title'         str
    #   'contextId'     str         for me, this is the project id
    #   'contextType'   str         all of mine are "PROJECT", 
    #                               but maybe you can add these to other things as well
    #   'taskIds'       list[str]
    
    # I'll ignore all section entities whose context type is not "PROJECT"
    
    #   * TAGS *
    
    tag_ids: list[str] = data['state']['tag']['ids']
    # There is a built in tag called 'TODAY' that is 
    # automatically applied to all tasks due today
    
    tag_entities: dict[str, dict] = data['state']['tag']['entities']
    #   'id'            str
    #   'title'         str
    #   'taskIds'       list[str]
    
    #   ---
    
    # Converting dicts to schema types
    
    tasks: dict[str, _Task] = {}
    projects: dict[str, _Project] = {}
    sections: dict[str, _Section] = {}
    tags: dict[str, _Tag] = {}
    
    for id in task_ids:
        entity = task_entities[id]
        
        task = _Task(
            id=id,
            title=entity['title'],
            is_done=entity['isDone'],
            due_day=datetime.strptime(
                entity['dueDay'], 
                '%Y-%m-%d'
            ) if 'dueDay' in entity else None,
            project_id=entity['projectId'],
            tag_ids=entity['tagIds']
        )
        
        tasks[id] = task
    
    for id in project_ids:
        entity = project_entities[id]
        
        project = _Project(
            id=id,
            title=entity['title'],
            task_ids=entity['taskIds']
        )
        
        projects[id] = project
    
    for id in section_ids:
        entity = section_entities[id]
        
        if entity['contextType'] != 'PROJECT':
            continue
        
        section = _Section(
            id=id,
            title=entity['title'],
            project_id=entity['contextId'],
            task_ids=entity['taskIds']
        )
        
        sections[id] = section
    
    for id in tag_ids:
        entity = tag_entities[id]
        
        tag = _Tag(
            id=id,
            title=entity['title'],
            task_ids=entity['taskIds']
        )
        
        tags[id] = tag
        
    parsed_data = _SuperProcuctivityData(
        tasks=tasks,
        projects=projects,
        sections=sections,
        tags=tags
    )
    
    return parsed_data
    
def _extract_task_data(task_id: str, data: _SuperProcuctivityData) -> Task | None:
    if task_id not in data.tasks:
        return None
    
    task_data: _Task = data.tasks[task_id]
    
    title: str = task_data.title
    is_done: bool = task_data.is_done
    due_day: datetime | None = task_data.due_day
    
    project: str = data.projects[task_data.project_id].title
    tags: list[str] = [data.tags[id].title for id in task_data.tag_ids]
    
    section = None
    for section_data in data.sections.values():
        if task_data.id in section_data.task_ids:
            section = section_data.title
    
    return Task(
        title=title,
        is_done=is_done,
        due_day=due_day,
        project=project,
        tags=tags,
        section=section
    )
            
def _get_metadata() -> dict:
    if not _METADATA_LOCATION.exists():
        return {}
    
    metadata = load_data(_METADATA_LOCATION)
    return metadata

async def fetch_and_cache():
    print('INFO:\tFetching and caching superprod data...')
    data = await _get_parsed_task_data()
    date = datetime.now()
    metadata = {'date': date}
    
    _SAVE_LOCATION.parent.mkdir(parents=True, exist_ok=True)
    
    save_data(data, _SAVE_LOCATION)
    save_data(metadata, _METADATA_LOCATION)

def get_tasks_today() -> list[Task]:
    if not _SAVE_LOCATION.exists():
        return []
    
    data: _SuperProcuctivityData = load_data(_SAVE_LOCATION)
    
    today_ids: list[str] = data.tags['TODAY'].task_ids
    
    tasks = []
    for id in today_ids:
        task = _extract_task_data(id, data)
        if task is not None:
            tasks.append(task)
    
    return tasks

def should_recache() -> bool:
    if not _SAVE_LOCATION.exists() or not _METADATA_LOCATION.exists():
        return True
    
    metadata = _get_metadata()
    
    last_cache_date: datetime = metadata['date']
    elapsed_time: timedelta = datetime.now() - last_cache_date
    
    elapsed_minutes = elapsed_time.total_seconds() / 60.0
    
    return elapsed_minutes >= _RECACHE_AFTER_MINUTES