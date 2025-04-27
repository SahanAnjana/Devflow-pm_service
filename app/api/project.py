# project-service/app/api/project.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth_client import get_current_pm_user, get_current_admin_user
from app.crud.project import (
    get_project_by_id,
    get_projects,
    get_user_projects,
    create_project,
    update_project,
    delete_project,
    get_project_settings,
    update_project_settings,
    get_project_members,
    add_project_member,
    update_project_member_role,
    remove_project_member,
    get_project_member
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithMembersResponse,
    ProjectSettingsUpdate,
    ProjectSettingsResponse,
    ProjectMemberCreate,
    ProjectMemberUpdate,
    ProjectMemberResponse
)

router = APIRouter()

# # Helper function to check project permissions
# def check_project_permissions(db: Session, project_id: str, user_id: str, required_roles: List[str] = None):
#     """Check if the user has appropriate permissions for a project"""
#     if required_roles is None:
#         required_roles = ["owner", "admin"]
    
#     # Check if project exists
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Project not found"
#         )
    
#     # Check permissions
#     member = get_project_member(db, project_id, user_id)
#     if not member or member.role not in required_roles:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions"
#         )
    
#     return project

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_pm_user),
    db: Session = Depends(get_db)
):
    # # Set the current user as the owner if not specified
    # if not project_data.owner_id:
    #     project_data.owner_id = current_user["user_id"]
    
    # # Only allow setting other users as owners if admin
    # if project_data.owner_id != current_user["user_id"] and current_user.get("role") != "admin":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Cannot set another user as project owner"
    #     )
    
    project = create_project(db, project_data)
    return project

@router.get("/", response_model=List[ProjectResponse])
async def read_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_pm_user),
    db: Session = Depends(get_db)
):
    # Admin can see all projects, others only see projects they're members of
    if current_user.get("role") == "admin":
        projects = get_projects(db, skip=skip, limit=limit)
    else:
        projects = get_user_projects(db, current_user["user_id"])
    
    return projects

@router.get("/{project_id}", response_model=ProjectWithMembersResponse)
async def read_project(
    project_id: str,
    current_user: dict = Depends(get_current_pm_user),
    db: Session = Depends(get_db)
):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_info(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: dict = Depends(get_current_pm_user),
    db: Session = Depends(get_db)
):
    # # Check project exists and user has permissions
    # check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    # # Only owners and admins can change the owner
    # if project_data.owner_id is not None:
    #     member = get_project_member(db, project_id, current_user["user_id"])
    #     if member.role != "owner" and current_user.get("role") != "admin":
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail="Only project owners can transfer ownership"
    #         )
    
    updated_project = update_project(db, project_id, project_data)
    return updated_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_record(
    project_id: str,
    current_user: dict = Depends(get_current_pm_user),
    db: Session = Depends(get_db)
):
    # Only project owners and system admins can delete projects
    # check_project_permissions(db, project_id, current_user["user_id"], ["owner"])
    
    # # Allow admins to delete any project
    # is_admin = current_user.get("role") == "admin"
    # if not is_admin:
    #     # Verify user is the owner
    #     member = get_project_member(db, project_id, current_user["user_id"])
    #     if not member or member.role != "owner":
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail="Only project owners can delete projects"
    #         )
    
    result = delete_project(db, project_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return None

# Project Settings Endpoints
@router.get("/{project_id}/settings", response_model=ProjectSettingsResponse)
async def read_project_settings(
    project_id: str,
    current_user: dict = Depends(get_current_pm_user),
    db: Session = Depends(get_db)
):
    # # Check project exists and user has permissions
    # check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    settings = get_project_settings(db, project_id)
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project settings not found"
        )
    return settings

@router.put("/{project_id}/settings", response_model=ProjectSettingsResponse)
async def update_project_settings_info(
    project_id: str,
    settings_data: ProjectSettingsUpdate,
    current_user: dict = Depends(get_current_pm_user),
    db: Session = Depends(get_db)
):
    # # Check project exists and user has appropriate permissions
    # check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    updated_settings = update_project_settings(db, project_id, settings_data)
    if not updated_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project settings not found"
        )
    return updated_settings

# Project Members Endpoints
@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def read_project_members(
    project_id: str,
    current_user: dict = Depends(get_current_pm_user),
    db: Session = Depends(get_db)
):
    # # Check project exists and user has permissions
    # check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    members = get_project_members(db, project_id)
    return members

@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member_to_project(
    project_id: str,
    member_data: ProjectMemberCreate,
    current_user: dict = Depends(get_current_pm_user),
    db: Session = Depends(get_db)
):
    # # Check project exists and user has permissions
    # check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    # Force set the project_id from the path parameter
    member_data.project_id = project_id
    
    # Prevent setting someone as owner using this endpoint
    if member_data.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add a member as an owner. Use the transfer ownership endpoint."
        )
    
    member = add_project_member(db, member_data)
    return member

@router.put("/{project_id}/members/{user_id}/role", response_model=ProjectMemberResponse)
async def update_member_role(
    project_id: str,
    user_id: str,
    role_data: ProjectMemberUpdate,
    current_user: dict = Depends(get_current_pm_user),
    db: Session = Depends(get_db)
):
    # # Check project exists and user has permissions
    # check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    # # Prevent changing owner role
    # member = get_project_member(db, project_id, user_id)
    # if member and member.role == "owner" and role_data.role != "owner":
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Cannot change the role of the project owner"
    #     )
    
    # Prevent making someone else owner (should use a separate transfer ownership endpoint)
    if role_data.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change a member to owner. Use the transfer ownership endpoint."
        )
    
    updated_member = update_project_member_role(db, project_id, user_id, role_data)
    if not updated_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found"
        )
    return updated_member

@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member_from_project(
    project_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_pm_user),
    db: Session = Depends(get_db)
):
    # # Check project exists and user has permissions
    # check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    # Prevent removing the owner
    member = get_project_member(db, project_id, user_id)
    if member and member.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the project owner"
        )
    
    result = remove_project_member(db, project_id, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found or is the owner"
        )
    return None