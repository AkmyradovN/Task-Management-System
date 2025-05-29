from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=5)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

class TaskLogBase(BaseModel):
    status: str
    created_at: datetime

class TaskLog(TaskLogBase):
    id: int
    task_id: int
    
    class Config:
        from_attributes = True

class Task(TaskBase):
    id: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    logs: List[TaskLog] = []
    
    class Config:
        from_attributes = True

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PaginatedTasks(BaseModel):
    items: List[TaskResponse]
    total: int
    page: int
    per_page: int
    pages: int