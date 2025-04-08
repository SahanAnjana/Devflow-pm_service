# project-service/app/schemas/resource.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator

# Resource Schemas
class ResourceBase(BaseModel):
    """Base schema for Resource"""
    name: str
    type: str  # person, equipment, material, etc.
    cost_rate: Optional[float] = None
    availability: float = 100.0
    skills: Optional[List[str]] = None
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

class ResourceCreate(ResourceBase):
    """Schema for creating a Resource"""
    project_id: UUID
    user_id: Optional[UUID] = None

class ResourceUpdate(BaseModel):
    """Schema for updating a Resource"""
    name: Optional[str] = None
    type: Optional[str] = None
    cost_rate: Optional[float] = None
    availability: Optional[float] = None
    skills: Optional[List[str]] = None
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    user_id: Optional[UUID] = None

class ResourceResponse(ResourceBase):
    """Schema for Resource response"""
    id: UUID
    project_id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Resource Assignment Schemas
class ResourceAssignmentBase(BaseModel):
    """Base schema for ResourceAssignment"""
    role: Optional[str] = None
    allocation_percentage: float = 100.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    hours_allocated: Optional[float] = None
    properties: Optional[Dict[str, Any]] = None

class ResourceAssignmentCreate(ResourceAssignmentBase):
    """Schema for creating a ResourceAssignment"""
    project_id: UUID
    resource_id: UUID
    task_id: UUID

class ResourceAssignmentUpdate(BaseModel):
    """Schema for updating a ResourceAssignment"""
    role: Optional[str] = None
    allocation_percentage: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    hours_allocated: Optional[float] = None
    properties: Optional[Dict[str, Any]] = None
    resource_id: Optional[UUID] = None
    task_id: Optional[UUID] = None

class ResourceAssignmentResponse(ResourceAssignmentBase):
    """Schema for ResourceAssignment response"""
    id: UUID
    project_id: UUID
    resource_id: UUID
    task_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ResourceUtilizationTaskData(BaseModel):
    """Schema for task data in resource utilization"""
    task_id: UUID
    task_title: str
    allocation: float

class ResourceUtilizationResponse(BaseModel):
    """Schema for resource utilization response"""
    resource_id: UUID
    resource_name: str
    resource_type: str
    start_date: str
    end_date: str
    overall_utilization: float
    availability: float
    overallocated_days: int
    daily_utilization: Dict[str, float]
    weekly_utilization: Dict[str, float]
    monthly_utilization: Dict[str, float]
    tasks_by_day: Dict[str, List[Dict[str, Any]]]