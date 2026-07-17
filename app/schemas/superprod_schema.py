from pydantic import BaseModel
from datetime import datetime

# Internal
class _Task(BaseModel):
    id: str
    title: str
    is_done: bool
    due_day: datetime | None = None
    
    project_id: str
    tag_ids: list[str]

class _Project(BaseModel):
    id: str
    title: str
    
    task_ids: list[str]
    
class _Section(BaseModel):
    id: str
    title: str
    
    project_id: str
    task_ids: list[str]

class _Tag(BaseModel):
    id: str
    title: str
    
    task_ids: list[str]

class _SuperProcuctivityData(BaseModel):
    tasks: dict[str, _Task]
    projects: dict[str, _Project]
    sections: dict[str, _Section]
    tags: dict[str, _Tag]

class Task(BaseModel):
    title: str
    is_done: bool
    due_day: datetime | None = None
    
    project: str
    tags: list[str]
    section: str | None = None