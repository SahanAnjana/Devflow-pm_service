# project-service/app/schemas/project.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "planning"  # planning, active, on_hold, completed, cancelled

class ProjectCreate(ProjectBase):
    owner_id: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    owner_id: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Project Settings schemas
class ProjectSettingsBase(BaseModel):
    visibility: str = "private"  # private, internal, public
    enable_tasks: bool = True
    enable_issues: bool = True
    enable_wiki: bool = False
    default_assignee_id: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, bool]] = None

class ProjectSettingsCreate(ProjectSettingsBase):
    project_id: str

class ProjectSettingsUpdate(BaseModel):
    visibility: Optional[str] = None
    enable_tasks: Optional[bool] = None
    enable_issues: Optional[bool] = None
    enable_wiki: Optional[bool] = None
    default_assignee_id: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, bool]] = None

class ProjectSettingsResponse(ProjectSettingsBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Project Member schemas
class ProjectMemberBase(BaseModel):
    user_id: str
    role: str = "member"  # owner, admin, member, guest

class ProjectMemberCreate(ProjectMemberBase):
    project_id: str

class ProjectMemberUpdate(BaseModel):
    role: Optional[str] = None

class ProjectMemberResponse(ProjectMemberBase):
    id: str
    project_id: str
    joined_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Project with members response
class ProjectWithMembersResponse(ProjectResponse):
    members: List[ProjectMemberResponse] = []
    settings: Optional[ProjectSettingsResponse] = None

    class Config:
        orm_mode = True