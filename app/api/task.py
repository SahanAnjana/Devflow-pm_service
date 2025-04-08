# project-service/app/api/task.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth_client import get_current_active_user
from app.api.project import check_project_permissions
from app.crud.task import (
    get_task_by_id,
    get_tasks_by_project,
    create_task,
    update_task,
    delete_task,
    update_task_status,
    update_task_assignee,
    update_task_position,
    update_task_schedule,
    get_board_columns,
    create_board_column,
    update_board_column,
    delete_board_column,
    get_gantt_chart_data,
    calculate_critical_path
)
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStatusUpdate,
    TaskAssigneeUpdate,
    TaskPositionUpdate,
    TaskScheduleUpdate,
    BoardColumnCreate,
    BoardColumnUpdate,
    BoardColumnResponse,
    BoardResponse,
    GanttChartResponse,
    GanttTaskResponse,
    CriticalPathResponse
)

router = APIRouter()

# Helper function to check task permissions
def check_task_permissions(db: Session, task_id: str, user_id: str, required_roles: List[str] = None):
    """Check if the user has appropriate permissions for a task"""
    if required_roles is None:
        required_roles = ["owner", "admin"]
    
    # Get the task
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check project permissions
    check_project_permissions(db, task.project_id, user_id, required_roles)
    
    return task

# Task Operations Endpoints
@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    project_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    # Force set the project_id from the path parameter
    task_data.project_id = project_id
    
    # Set current user as reporter if not specified
    if not hasattr(task_data, "reporter_id") or not task_data.reporter_id:
        task_data.reporter_id = current_user["user_id"]
    
    task = create_task(db, task_data)
    return task

@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def list_project_tasks(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    assignee_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    tasks = get_tasks_by_project(db, project_id, skip, limit, status, assignee_id)
    return tasks

@router.get("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task_details(
    project_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    task = get_task_by_id(db, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task

@router.put("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task_details(
    project_id: str,
    task_id: str,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    task = get_task_by_id(db, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    updated_task = update_task(db, task_id, task_data)
    return updated_task

@router.delete("/projects/{project_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_task(
    project_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    task = get_task_by_id(db, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    result = delete_task(db, task_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )
    
    return None

@router.put("/projects/{project_id}/tasks/{task_id}/status", response_model=TaskResponse)
async def update_task_status_endpoint(
    project_id: str,
    task_id: str,
    status_data: TaskStatusUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    task = get_task_by_id(db, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    updated_task = update_task_status(db, task_id, status_data.status)
    return updated_task

@router.put("/projects/{project_id}/tasks/{task_id}/assignee", response_model=TaskResponse)
async def update_task_assignee_endpoint(
    project_id: str,
    task_id: str,
    assignee_data: TaskAssigneeUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    task = get_task_by_id(db, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    updated_task = update_task_assignee(db, task_id, assignee_data.assignee_id)
    return updated_task

@router.put("/projects/{project_id}/tasks/{task_id}/position", response_model=TaskResponse)
async def update_task_position_endpoint(
    project_id: str,
    task_id: str,
    position_data: TaskPositionUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    task = get_task_by_id(db, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    updated_task = update_task_position(db, task_id, position_data.column_id, position_data.position)
    return updated_task

@router.put("/projects/{project_id}/tasks/{task_id}/schedule", response_model=TaskResponse)
async def update_task_schedule_endpoint(
    project_id: str,
    task_id: str,
    schedule_data: TaskScheduleUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    task = get_task_by_id(db, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    updated_task = update_task_schedule(db, task_id, schedule_data)
    return updated_task

# Board Management Endpoints
@router.get("/projects/{project_id}/board", response_model=BoardResponse)
async def get_project_board(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    columns = get_board_columns(db, project_id)
    return {"columns": columns}

@router.post("/projects/{project_id}/board/columns", response_model=BoardColumnResponse, status_code=status.HTTP_201_CREATED)
async def create_board_column_endpoint(
    project_id: str,
    column_data: BoardColumnCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    # Force set the project_id from the path parameter
    column_data.project_id = project_id
    
    column = create_board_column(db, column_data)
    return column

@router.put("/projects/{project_id}/board/columns/{column_id}", response_model=BoardColumnResponse)
async def update_board_column_endpoint(
    project_id: str,
    column_id: str,
    column_data: BoardColumnUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    column = update_board_column(db, column_id, column_data)
    if not column or column.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    return column

@router.delete("/projects/{project_id}/board/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board_column_endpoint(
    project_id: str,
    column_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    result = delete_board_column(db, column_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    return None

# Gantt Chart Endpoints
@router.get("/projects/{project_id}/gantt", response_model=GanttChartResponse)
async def get_project_gantt_chart(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    tasks = get_gantt_chart_data(db, project_id)
    
    # Convert tasks to GanttTaskResponse format
    gantt_tasks = []
    for task in tasks:
        progress = None
        if task.status == "done":
            progress = 100
        elif task.status == "in_progress":
            progress = 50
        elif task.status == "in_review":
            progress = 75
        elif task.status == "to_do":
            progress = 0
        
        gantt_tasks.append(GanttTaskResponse(
            id=task.id,
            title=task.title,
            start_date=task.start_date,
            due_date=task.due_date,
            progress=progress,
            dependencies=[dep.id for dep in task.dependencies],
            assignee_id=task.assignee_id
        ))
    
    return {"tasks": gantt_tasks}

@router.get("/projects/{project_id}/critical-path", response_model=CriticalPathResponse)
async def get_project_critical_path(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    path, duration = calculate_critical_path(db, project_id)
    return {"path": path, "duration": duration}