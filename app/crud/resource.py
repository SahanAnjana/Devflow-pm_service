# project-service/app/crud/resource.py
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.db.models.resource import Resource, ResourceAssignment
from app.db.models.task import Task
from app.schemas.resource import (
    ResourceCreate,
    ResourceUpdate,
    ResourceAssignmentCreate,
    ResourceAssignmentUpdate
)

# Resource CRUD Operations
def get_resource_by_id(db: Session, resource_id: str) -> Optional[Resource]:
    """Get a resource by ID"""
    return db.query(Resource).filter(Resource.id == resource_id).first()

def get_resources_by_project(
    db: Session, 
    project_id: str, 
    skip: int = 0, 
    limit: int = 100,
    type: Optional[str] = None
) -> List[Resource]:
    """Get resources for a project with optional filtering"""
    query = db.query(Resource).filter(Resource.project_id == project_id)
    
    if type:
        query = query.filter(Resource.type == type)
    
    return query.offset(skip).limit(limit).all()

def create_resource(db: Session, resource: ResourceCreate) -> Resource:
    """Create a new resource"""
    db_resource = Resource(
        name=resource.name,
        type=resource.type,
        project_id=resource.project_id,
        cost_rate=resource.cost_rate,
        availability=resource.availability,
        skills=resource.skills,
        description=resource.description,
        email=resource.email,
        phone=resource.phone,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

def update_resource(db: Session, resource_id: str, resource: ResourceUpdate) -> Optional[Resource]:
    """Update an existing resource"""
    db_resource = get_resource_by_id(db, resource_id)
    if not db_resource:
        return None
    
    update_data = resource.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_resource, key, value)
    
    db_resource.updated_at = datetime.utcnow()
    
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

def delete_resource(db: Session, resource_id: str) -> bool:
    """Delete a resource"""
    db_resource = get_resource_by_id(db, resource_id)
    if not db_resource:
        return False
    
    # First delete all assignments for this resource
    db.query(ResourceAssignment).filter(ResourceAssignment.resource_id == resource_id).delete()
    
    db.delete(db_resource)
    db.commit()
    return True

# Resource Assignment CRUD Operations
def get_resource_assignment_by_id(db: Session, assignment_id: str) -> Optional[ResourceAssignment]:
    """Get a resource assignment by ID"""
    return db.query(ResourceAssignment).filter(ResourceAssignment.id == assignment_id).first()

def get_resource_assignments_by_project(
    db: Session, 
    project_id: str, 
    skip: int = 0, 
    limit: int = 100,
    task_id: Optional[str] = None
) -> List[ResourceAssignment]:
    """Get resource assignments for a project with optional filtering"""
    query = db.query(ResourceAssignment).filter(ResourceAssignment.project_id == project_id)
    
    if task_id:
        query = query.filter(ResourceAssignment.task_id == task_id)
    
    return query.offset(skip).limit(limit).all()

def get_resource_assignments_by_resource(
    db: Session, 
    resource_id: str
) -> List[ResourceAssignment]:
    """Get all assignments for a specific resource"""
    return db.query(ResourceAssignment).filter(ResourceAssignment.resource_id == resource_id).all()

def create_resource_assignment(db: Session, assignment: ResourceAssignmentCreate) -> ResourceAssignment:
    """Create a new resource assignment"""
    # Check if task exists
    task = db.query(Task).filter(Task.id == assignment.task_id).first()
    if not task:
        raise ValueError("Task not found")
    
    # Check if resource exists
    resource = db.query(Resource).filter(Resource.id == assignment.resource_id).first()
    if not resource:
        raise ValueError("Resource not found")
    
    db_assignment = ResourceAssignment(
        project_id=assignment.project_id,
        resource_id=assignment.resource_id,
        task_id=assignment.task_id,
        role=assignment.role,
        allocation_percentage=assignment.allocation_percentage,
        start_date=assignment.start_date or task.start_date,
        end_date=assignment.end_date or task.due_date,
        hours_allocated=assignment.hours_allocated,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def update_resource_assignment(db: Session, assignment_id: str, assignment: ResourceAssignmentUpdate) -> Optional[ResourceAssignment]:
    """Update an existing resource assignment"""
    db_assignment = get_resource_assignment_by_id(db, assignment_id)
    if not db_assignment:
        return None
    
    update_data = assignment.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_assignment, key, value)
    
    db_assignment.updated_at = datetime.utcnow()
    
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def delete_resource_assignment(db: Session, assignment_id: str) -> bool:
    """Delete a resource assignment"""
    db_assignment = get_resource_assignment_by_id(db, assignment_id)
    if not db_assignment:
        return False
    
    db.delete(db_assignment)
    db.commit()
    return True

# Resource Utilization
def get_resource_utilization(
    db: Session, 
    resource_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Get utilization data for a specific resource"""
    resource = get_resource_by_id(db, resource_id)
    if not resource:
        raise ValueError("Resource not found")
    
    # Convert string dates to datetime objects if provided
    start_dt = None
    end_dt = None
    
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Get all assignments for this resource
    query = db.query(ResourceAssignment).filter(ResourceAssignment.resource_id == resource_id)
    
    if start_dt:
        query = query.filter(or_(
            ResourceAssignment.end_date >= start_dt,
            ResourceAssignment.end_date == None
        ))
    
    if end_dt:
        query = query.filter(or_(
            ResourceAssignment.start_date <= end_dt,
            ResourceAssignment.start_date == None
        ))
    
    assignments = query.all()
    
    # Calculate total allocation across time periods
    utilization_by_day = {}
    tasks_by_day = {}
    
    # If no date range specified, determine from assignments
    if not start_dt or not end_dt:
        all_dates = []
        for assignment in assignments:
            if assignment.start_date:
                all_dates.append(assignment.start_date)
            if assignment.end_date:
                all_dates.append(assignment.end_date)
        
        if all_dates:
            if not start_dt:
                start_dt = min(all_dates)
            if not end_dt:
                end_dt = max(all_dates)
    
    # Default to current month if no dates determined
    if not start_dt:
        start_dt = datetime.now().replace(day=1)
    if not end_dt:
        end_dt = (start_dt.replace(month=start_dt.month+1) - timedelta(days=1))
    
    # Calculate daily allocation percentages
    current_date = start_dt
    while current_date <= end_dt:
        date_str = current_date.strftime("%Y-%m-%d")
        utilization_by_day[date_str] = 0
        tasks_by_day[date_str] = []
        
        for assignment in assignments:
            # Skip if assignment date range doesn't include current date
            if (assignment.start_date and assignment.start_date > current_date) or \
               (assignment.end_date and assignment.end_date < current_date):
                continue
            
            # Add this assignment's allocation to the day
            utilization_by_day[date_str] += assignment.allocation_percentage
            
            # Add task to the list for this day
            task = db.query(Task).filter(Task.id == assignment.task_id).first()
            if task:
                tasks_by_day[date_str].append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "allocation": assignment.allocation_percentage
                })
        
        current_date += timedelta(days=1)
    
    # Group by week and month
    weekly_utilization = {}
    monthly_utilization = {}
    
    for date_str, allocation in utilization_by_day.items():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Weekly (use ISO week numbers)
        week_key = f"{date_obj.year}-W{date_obj.isocalendar()[1]}"
        if week_key not in weekly_utilization:
            weekly_utilization[week_key] = {"total": 0, "days": 0}
        weekly_utilization[week_key]["total"] += allocation
        weekly_utilization[week_key]["days"] += 1
        
        # Monthly
        month_key = date_obj.strftime("%Y-%m")
        if month_key not in monthly_utilization:
            monthly_utilization[month_key] = {"total": 0, "days": 0}
        monthly_utilization[month_key]["total"] += allocation
        monthly_utilization[month_key]["days"] += 1
    
    # Calculate averages
    for week_key in weekly_utilization:
        weekly_utilization[week_key] = round(
            weekly_utilization[week_key]["total"] / weekly_utilization[week_key]["days"], 2
        )
    
    for month_key in monthly_utilization:
        monthly_utilization[month_key] = round(
            monthly_utilization[month_key]["total"] / monthly_utilization[month_key]["days"], 2
        )
    
    # Calculate overall utilization
    total_days = (end_dt - start_dt).days + 1
    total_allocation = sum(utilization_by_day.values())
    average_utilization = round(total_allocation / total_days, 2)
    
    # Calculate overallocation days
    overallocated_days = sum(1 for allocation in utilization_by_day.values() if allocation > 100)
    
    return {
        "resource_id": resource_id,
        "resource_name": resource.name,
        "resource_type": resource.type,
        "start_date": start_dt.strftime("%Y-%m-%d"),
        "end_date": end_dt.strftime("%Y-%m-%d"),
        "overall_utilization": average_utilization,
        "availability": resource.availability,
        "overallocated_days": overallocated_days,
        "daily_utilization": utilization_by_day,
        "weekly_utilization": weekly_utilization,
        "monthly_utilization": monthly_utilization,
        "tasks_by_day": tasks_by_day
    }