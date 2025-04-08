# project-service/app/schemas/task.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "to_do"  # to_do, in_progress, in_review, done
    priority: str = "medium"  # low, medium, high, critical
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    tags: Optional[List[str]] = None
    column_id: Optional[str] = None
    position: Optional[int] = None  # Position within a column or list

class TaskCreate(TaskBase):
    project_id: str
    reporter_id: str
    assignee_id: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    tags: Optional[List[str]] = None
    assignee_id: Optional[str] = None
    column_id: Optional[str] = None
    position: Optional[int] = None

class TaskStatusUpdate(BaseModel):
    status: str

class TaskAssigneeUpdate(BaseModel):
    assignee_id: Optional[str] = None

class TaskPositionUpdate(BaseModel):
    column_id: Optional[str] = None
    position: int

class TaskScheduleUpdate(BaseModel):
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    dependencies: Optional[List[str]] = None  # List of task IDs this task depends on

class TaskResponse(TaskBase):
    id: str
    project_id: str
    reporter_id: str
    assignee_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    dependencies: List[str] = []  # List of task IDs this task depends on
    
    class Config:
        orm_mode = True

# Board schemas
class BoardColumnBase(BaseModel):
    name: str
    order: int
    wip_limit: Optional[int] = None  # Work in progress limit
    color: Optional[str] = None

class BoardColumnCreate(BoardColumnBase):
    project_id: str

class BoardColumnUpdate(BaseModel):
    name: Optional[str] = None
    order: Optional[int] = None
    wip_limit: Optional[int] = None
    color: Optional[str] = None

class BoardColumnResponse(BoardColumnBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class BoardResponse(BaseModel):
    columns: List[BoardColumnResponse]
    
    class Config:
        orm_mode = True

# Gantt chart schemas
class GanttTaskResponse(BaseModel):
    id: str
    title: str
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    progress: Optional[float] = None
    dependencies: List[str] = []
    assignee_id: Optional[str] = None
    
    class Config:
        orm_mode = True

class GanttChartResponse(BaseModel):
    tasks: List[GanttTaskResponse]
    
    class Config:
        orm_mode = True

class CriticalPathResponse(BaseModel):
    path: List[str]  # List of task IDs in the critical path
    duration: float  # Duration in hours
    
    class Config:
        orm_mode = True