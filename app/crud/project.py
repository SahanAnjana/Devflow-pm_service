# project-service/app/crud/project.py
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models.project import Project, ProjectSettings, ProjectMember

# Project CRUD operations
def get_project_by_id(db: Session, project_id: str) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    return db.query(Project).offset(skip).limit(limit).all()

def get_user_projects(db: Session, user_id: str) -> List[Project]:
    """Get all projects where user is a member"""
    return (
        db.query(Project)
        .join(ProjectMember)
        .filter(ProjectMember.user_id == user_id)
        .all()
    )

def create_project(db: Session, project_data):
    # Create the project
    project_id = str(uuid.uuid4())
    db_project = Project(
        id=project_id,
        name=project_data.name,
        description=project_data.description,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        status=project_data.status,
        owner_id=project_data.owner_id,
        created_at=datetime.utcnow()
    )
    db.add(db_project)
    
    # Add owner as a project member with 'owner' role
    db_member = ProjectMember(
        id=str(uuid.uuid4()),
        project_id=project_id,
        user_id=project_data.owner_id,
        role="owner",
        joined_at=datetime.utcnow()
    )
    db.add(db_member)
    
    # Create default project settings
    db_settings = ProjectSettings(
        id=str(uuid.uuid4()),
        project_id=project_id,
        visibility="private",
        enable_tasks=True,
        enable_issues=True,
        enable_wiki=False,
        created_at=datetime.utcnow()
    )
    db.add(db_settings)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: str, project_data):
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return None
    
    update_data = project_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_project, key, value)
    
    db_project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: str) -> bool:
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return False
    
    db.delete(db_project)
    db.commit()
    return True

# Project Settings CRUD operations
def get_project_settings(db: Session, project_id: str) -> Optional[ProjectSettings]:
    return db.query(ProjectSettings).filter(ProjectSettings.project_id == project_id).first()

def update_project_settings(db: Session, project_id: str, settings_data):
    db_settings = get_project_settings(db, project_id)
    if not db_settings:
        return None
    
    update_data = settings_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_settings, key, value)
    
    db_settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_settings)
    return db_settings

# Project Members CRUD operations
def get_project_members(db: Session, project_id: str) -> List[ProjectMember]:
    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()

def get_project_member(db: Session, project_id: str, user_id: str) -> Optional[ProjectMember]:
    return (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )

def add_project_member(db: Session, member_data):
    # Check if member already exists
    existing_member = get_project_member(db, member_data.project_id, member_data.user_id)
    if existing_member:
        return existing_member
    
    db_member = ProjectMember(
        id=str(uuid.uuid4()),
        project_id=member_data.project_id,
        user_id=member_data.user_id,
        role=member_data.role,
        joined_at=datetime.utcnow()
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def update_project_member_role(db: Session, project_id: str, user_id: str, role_data):
    db_member = get_project_member(db, project_id, user_id)
    if not db_member:
        return None
    
    if role_data.role:
        db_member.role = role_data.role
    
    db_member.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_member)
    return db_member

def remove_project_member(db: Session, project_id: str, user_id: str) -> bool:
    db_member = get_project_member(db, project_id, user_id)
    if not db_member:
        return False
    
    # Prevent removing the project owner
    if db_member.role == "owner":
        return False
    
    db.delete(db_member)
    db.commit()
    return True