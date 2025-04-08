# project-service/app/api/resource.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth_client import get_current_active_user
from app.api.project import check_project_permissions
from app.crud.resource import (
    get_resource_by_id,
    get_resources_by_project,
    create_resource,
    update_resource,
    delete_resource,
    get_resource_assignment_by_id,
    get_resource_assignments_by_project,
    get_resource_assignments_by_resource,
    create_resource_assignment,
    update_resource_assignment,
    delete_resource_assignment,
    get_resource_utilization
)
from app.schemas.resource import (
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    ResourceAssignmentCreate,
    ResourceAssignmentUpdate,
    ResourceAssignmentResponse,
    ResourceUtilizationResponse
)

router = APIRouter()

# Resource Operations Endpoints
@router.post("/projects/{project_id}/resources", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_new_resource(
    project_id: str,
    resource_data: ResourceCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    # Force set the project_id from the path parameter
    resource_data.project_id = project_id
    
    resource = create_resource(db, resource_data)
    return resource

@router.get("/projects/{project_id}/resources", response_model=List[ResourceResponse])
async def list_project_resources(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    resources = get_resources_by_project(db, project_id, skip, limit, type)
    return resources

@router.get("/projects/{project_id}/resources/{resource_id}", response_model=ResourceResponse)
async def get_resource_details(
    project_id: str,
    resource_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    resource = get_resource_by_id(db, resource_id)
    if not resource or resource.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    return resource

@router.put("/projects/{project_id}/resources/{resource_id}", response_model=ResourceResponse)
async def update_resource_details(
    project_id: str,
    resource_id: str,
    resource_data: ResourceUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    resource = get_resource_by_id(db, resource_id)
    if not resource or resource.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    updated_resource = update_resource(db, resource_id, resource_data)
    return updated_resource

@router.delete("/projects/{project_id}/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_resource(
    project_id: str,
    resource_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    resource = get_resource_by_id(db, resource_id)
    if not resource or resource.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    result = delete_resource(db, resource_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resource"
        )
    
    return None

# Resource Assignment Endpoints
@router.post("/projects/{project_id}/resource-assignments", response_model=ResourceAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_new_resource_assignment(
    project_id: str,
    assignment_data: ResourceAssignmentCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    # Force set the project_id from the path parameter
    assignment_data.project_id = project_id
    
    assignment = create_resource_assignment(db, assignment_data)
    return assignment

@router.get("/projects/{project_id}/resource-assignments", response_model=List[ResourceAssignmentResponse])
async def list_project_resource_assignments(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    resource_id: Optional[str] = None,
    task_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    if resource_id:
        assignments = get_resource_assignments_by_resource(db, resource_id)
    else:
        assignments = get_resource_assignments_by_project(db, project_id, skip, limit, task_id)
    
    return assignments

@router.get("/projects/{project_id}/resource-assignments/{assignment_id}", response_model=ResourceAssignmentResponse)
async def get_resource_assignment_details(
    project_id: str,
    assignment_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    assignment = get_resource_assignment_by_id(db, assignment_id)
    if not assignment or assignment.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource assignment not found"
        )
    
    return assignment

@router.put("/projects/{project_id}/resource-assignments/{assignment_id}", response_model=ResourceAssignmentResponse)
async def update_resource_assignment_details(
    project_id: str,
    assignment_id: str,
    assignment_data: ResourceAssignmentUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    assignment = get_resource_assignment_by_id(db, assignment_id)
    if not assignment or assignment.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource assignment not found"
        )
    
    updated_assignment = update_resource_assignment(db, assignment_id, assignment_data)
    return updated_assignment

@router.delete("/projects/{project_id}/resource-assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_resource_assignment(
    project_id: str,
    assignment_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    assignment = get_resource_assignment_by_id(db, assignment_id)
    if not assignment or assignment.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource assignment not found"
        )
    
    result = delete_resource_assignment(db, assignment_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resource assignment"
        )
    
    return None

# Resource Utilization Endpoints
@router.get("/projects/{project_id}/resources/{resource_id}/utilization", response_model=ResourceUtilizationResponse)
async def get_resource_utilization_data(
    project_id: str,
    resource_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    resource = get_resource_by_id(db, resource_id)
    if not resource or resource.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    utilization_data = get_resource_utilization(db, resource_id, start_date, end_date)
    return utilization_data