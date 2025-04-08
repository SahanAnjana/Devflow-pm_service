# project-service/app/crud/task.py
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Set, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from app.db.models.task import Task, BoardColumn, task_dependencies
from app.db.models.project import Project

# Task CRUD operations
def get_task_by_id(db: Session, task_id: str) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks_by_project(
    db: Session, 
    project_id: str, 
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    assignee_id: Optional[str] = None
) -> List[Task]:
    query = db.query(Task).filter(Task.project_id == project_id)
    
    if status:
        query = query.filter(Task.status == status)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    
    return query.offset(skip).limit(limit).all()

def create_task(db: Session, task_data):
    """Create a new task"""
    task_id = str(uuid.uuid4())
    db_task = Task(
        id=task_id,
        project_id=task_data.project_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        reporter_id=task_data.reporter_id,
        assignee_id=task_data.assignee_id,
        due_date=task_data.due_date,
        estimated_hours=task_data.estimated_hours,
        tags=task_data.tags,
        column_id=task_data.column_id,
        created_at=datetime.utcnow()
    )
    
    # If column_id is not provided but we have default columns, use the first one
    if not task_data.column_id:
        default_column = db.query(BoardColumn).filter(
            BoardColumn.project_id == task_data.project_id
        ).order_by(BoardColumn.order).first()
        
        if default_column:
            db_task.column_id = default_column.id
    
    # Set position if not provided
    if task_data.position is None and db_task.column_id:
        # Get the highest position in the column and add 1
        max_position = db.query(func.max(Task.position)).filter(
            Task.column_id == db_task.column_id
        ).scalar() or 0
        db_task.position = max_position + 1
    else:
        db_task.position = task_data.position
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: str, task_data):
    """Update a task's details"""
    db_task = get_task_by_id(db, task_id)
    if not db_task:
        return None
    
    update_data = task_data.dict(exclude_unset=True)
    
    # Special handling for column changes (may need position update)
    column_changed = 'column_id' in update_data and update_data['column_id'] != db_task.column_id
    position_provided = 'position' in update_data
    
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    # If column changed but no position provided, put at the end of the new column
    if column_changed and not position_provided and db_task.column_id:
        max_position = db.query(func.max(Task.position)).filter(
            Task.column_id == db_task.column_id
        ).scalar() or 0
        db_task.position = max_position + 1
    
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: str) -> bool:
    """Delete a task"""
    db_task = get_task_by_id(db, task_id)
    if not db_task:
        return False
    
    # Clean up dependencies
    db.execute(task_dependencies.delete().where(
        (task_dependencies.c.task_id == task_id) | 
        (task_dependencies.c.dependency_id == task_id)
    ))
    
    db.delete(db_task)
    db.commit()
    return True

def update_task_status(db: Session, task_id: str, status: str):
    """Update task status"""
    db_task = get_task_by_id(db, task_id)
    if not db_task:
        return None
    
    db_task.status = status
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task_assignee(db: Session, task_id: str, assignee_id: Optional[str]):
    """Assign or unassign task"""
    db_task = get_task_by_id(db, task_id)
    if not db_task:
        return None
    
    db_task.assignee_id = assignee_id
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task_position(db: Session, task_id: str, column_id: Optional[str], position: int):
    """Update task position in a column"""
    db_task = get_task_by_id(db, task_id)
    if not db_task:
        return None
    
    old_column_id = db_task.column_id
    new_column_id = column_id if column_id is not None else old_column_id
    
    # Column change detection
    column_changed = new_column_id != old_column_id
    
    # Get the current tasks in the target column ordered by position
    tasks_in_column = db.query(Task).filter(Task.column_id == new_column_id).order_by(Task.position).all()
    
    # If moving to a different column, remove from old column first
    if column_changed and old_column_id:
        db_task.column_id = new_column_id
    
    # Update positions
    # If position is beyond the end, put it at the end
    if position >= len(tasks_in_column):
        db_task.position = len(tasks_in_column)
    else:
        # Check if task is already in this column (and not changing columns)
        if not column_changed and db_task.column_id == new_column_id:
            current_position = next((i for i, t in enumerate(tasks_in_column) if t.id == task_id), None)
            
            # If moving up in the same column
            if current_position is not None and position < current_position:
                for task in tasks_in_column:
                    if position <= task.position < current_position:
                        task.position += 1
                db_task.position = position
            # If moving down in the same column
            elif current_position is not None and position > current_position:
                for task in tasks_in_column:
                    if current_position < task.position <= position:
                        task.position -= 1
                db_task.position = position
        else:
            # Moving to a new position in a different column
            for task in tasks_in_column:
                if task.position >= position:
                    task.position += 1
            db_task.position = position
    
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task_schedule(db: Session, task_id: str, schedule_data):
    """Update task schedule for Gantt chart"""
    db_task = get_task_by_id(db, task_id)
    if not db_task:
        return None
    
    if schedule_data.start_date is not None:
        db_task.start_date = schedule_data.start_date
    
    if schedule_data.due_date is not None:
        db_task.due_date = schedule_data.due_date
    
    if schedule_data.estimated_hours is not None:
        db_task.estimated_hours = schedule_data.estimated_hours
    
    # Update dependencies if provided
    if schedule_data.dependencies is not None:
        # First, clear existing dependencies
        db.execute(task_dependencies.delete().where(task_dependencies.c.task_id == task_id))
        
        # Then add the new ones
        for dep_id in schedule_data.dependencies:
            # Verify the dependency exists and is in the same project
            dep_task = get_task_by_id(db, dep_id)
            if dep_task and dep_task.project_id == db_task.project_id and dep_id != task_id:
                db.execute(task_dependencies.insert().values(task_id=task_id, dependency_id=dep_id))
    
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task

# Board CRUD operations
def get_board_columns(db: Session, project_id: str) -> List[BoardColumn]:
    """Get all columns for a project's board"""
    return db.query(BoardColumn).filter(
        BoardColumn.project_id == project_id
    ).order_by(BoardColumn.order).all()

def get_column_by_id(db: Session, column_id: str) -> Optional[BoardColumn]:
    """Get a board column by ID"""
    return db.query(BoardColumn).filter(BoardColumn.id == column_id).first()

def create_board_column(db: Session, column_data):
    """Create a new board column"""
    column_id = str(uuid.uuid4())
    
    # If order not specified, put it at the end
    if column_data.order is None:
        max_order = db.query(func.max(BoardColumn.order)).filter(
            BoardColumn.project_id == column_data.project_id
        ).scalar() or -1
        column_data.order = max_order + 1
    
    db_column = BoardColumn(
        id=column_id,
        project_id=column_data.project_id,
        name=column_data.name,
        order=column_data.order,
        wip_limit=column_data.wip_limit,
        color=column_data.color,
        created_at=datetime.utcnow()
    )
    
    db.add(db_column)
    db.commit()
    db.refresh(db_column)
    return db_column

def update_board_column(db: Session, column_id: str, column_data):
    """Update a board column"""
    db_column = get_column_by_id(db, column_id)
    if not db_column:
        return None
    
    update_data = column_data.dict(exclude_unset=True)
    
    # Special handling for order changes to maintain consistency
    if 'order' in update_data and update_data['order'] != db_column.order:
        old_order = db_column.order
        new_order = update_data['order']
        
        # Shift other columns
        if new_order > old_order:
            # Moving right: shift columns between old and new order to the left
            db.query(BoardColumn).filter(
                BoardColumn.project_id == db_column.project_id,
                BoardColumn.order > old_order,
                BoardColumn.order <= new_order
            ).update({BoardColumn.order: BoardColumn.order - 1})
        else:
            # Moving left: shift columns between new and old order to the right
            db.query(BoardColumn).filter(
                BoardColumn.project_id == db_column.project_id,
                BoardColumn.order >= new_order,
                BoardColumn.order < old_order
            ).update({BoardColumn.order: BoardColumn.order + 1})
    
    for key, value in update_data.items():
        setattr(db_column, key, value)
    
    db_column.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_column)
    return db_column

def delete_board_column(db: Session, column_id: str) -> bool:
    """Delete a board column and reorder remaining columns"""
    db_column = get_column_by_id(db, column_id)
    if not db_column:
        return False
    
    project_id = db_column.project_id
    order = db_column.order
    
    # Move tasks in this column to another column or set to NULL
    default_column = db.query(BoardColumn).filter(
        BoardColumn.project_id == project_id,
        BoardColumn.id != column_id
    ).order_by(BoardColumn.order).first()
    
    if default_column:
        # Move tasks to the default column
        db.query(Task).filter(Task.column_id == column_id).update(
            {Task.column_id: default_column.id, Task.position: None}
        )
    else:
        # No other column exists, set column_id to NULL
        db.query(Task).filter(Task.column_id == column_id).update(
            {Task.column_id: None, Task.position: None}
        )
    
    # Delete the column
    db.delete(db_column)
    
    # Reorder remaining columns
    db.query(BoardColumn).filter(
        BoardColumn.project_id == project_id,
        BoardColumn.order > order
    ).update({BoardColumn.order: BoardColumn.order - 1})
    
    db.commit()
    return True

# Gantt chart operations
def get_gantt_chart_data(db: Session, project_id: str) -> List[Task]:
    """Get tasks with schedule information for Gantt chart"""
    return db.query(Task).filter(
        Task.project_id == project_id
    ).options(
        joinedload(Task.dependencies)
    ).all()

def calculate_critical_path(db: Session, project_id: str) -> Tuple[List[str], float]:
    """
    Calculate critical path for project tasks
    Returns a tuple of (task_ids, duration)
    """
    # Get all tasks with their dependencies
    tasks = db.query(Task).filter(
        Task.project_id == project_id
    ).options(
        joinedload(Task.dependencies)
    ).all()
    
    # Create a dictionary mapping task IDs to tasks
    task_map = {task.id: task for task in tasks}
    
    # If no tasks with estimates, return empty path
    if not any(task.estimated_hours for task in tasks):
        return ([], 0)
    
    # Find tasks with no dependencies (starting tasks)
    start_tasks = [t for t in tasks if not t.dependencies]
    
    # If no start tasks, return empty path
    if not start_tasks:
        return ([], 0)
    
    # Find tasks with no dependent tasks (end tasks)
    dependent_ids = set()
    for task in tasks:
        for dep in task.dependencies:
            dependent_ids.add(dep.id)
    end_tasks = [t for t in tasks if t.id not in dependent_ids]
    
    # If no end tasks, use all tasks as potential ends
    if not end_tasks:
        end_tasks = tasks
    
    # Calculate earliest start time (EST) and earliest finish time (EFT) for each task
    # Forward pass
    est = {task.id: 0 for task in tasks}
    eft = {task.id: 0 for task in tasks}
    
    def calculate_forward(task_id):
        task = task_map[task_id]
        max_dep_eft = 0
        for dep in task.dependencies:
            if dep.id not in eft:
                calculate_forward(dep.id)
            max_dep_eft = max(max_dep_eft, eft[dep.id])
        
        est[task_id] = max_dep_eft
        eft[task_id] = est[task_id] + (task.estimated_hours or 0)
    
    for task in tasks:
        if task.id not in eft or eft[task.id] == 0:
            calculate_forward(task.id)
    
    # Find project completion time
    project_completion = max(eft.values())
    
    # Calculate latest start time (LST) and latest finish time (LFT) for each task
    # Backward pass
    lst = {task.id: project_completion for task in tasks}
    lft = {task.id: project_completion for task in tasks}
    
    for task in end_tasks:
        lft[task.id] = project_completion
        lst[task.id] = lft[task.id] - (task.estimated_hours or 0)
    
    # Get dependent tasks for each task
    dependent_tasks = {task.id: [] for task in tasks}
    for task in tasks:
        for dep in task.dependencies:
            dependent_tasks[dep.id].append(task)
    
    def calculate_backward(task_id):
        task = task_map[task_id]
        min_dep_lst = project_completion
        
        for dep_task in dependent_tasks[task_id]:
            if dep_task.id not in lst:
                calculate_backward(dep_task.id)
            min_dep_lst = min(min_dep_lst, lst[dep_task.id])
        
        if dependent_tasks[task_id]:  # If it has dependent tasks
            lft[task_id] = min_dep_lst
            lst[task_id] = lft[task_id] - (task.estimated_hours or 0)
    
    for task in tasks:
        if dependent_tasks[task.id]:  # If it has dependent tasks
            calculate_backward(task.id)
    
    # Calculate slack for each task
    slack = {task.id: lst[task.id] - est[task.id] for task in tasks}
    
    # Tasks on critical path have zero slack
    critical_path = [task.id for task in tasks if slack[task.id] == 0 and (task.estimated_hours or 0) > 0]
    
    # Sort critical path by dependencies
    ordered_path = []
    visited = set()
    
    def topologically_sort(task_id):
        if task_id in visited:
            return
        
        visited.add(task_id)
        task = task_map[task_id]
        
        for dep in task.dependencies:
            if dep.id in critical_path:
                topologically_sort(dep.id)
        
        if task_id in critical_path:
            ordered_path.append(task_id)
    
    for task_id in critical_path:
        if task_id not in visited:
            topologically_sort(task_id)
    
    return (ordered_path, project_completion)