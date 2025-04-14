# project-service/app/db/models/project.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), index=True)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="planning")  # planning, active, on_hold, completed, cancelled
    owner_id = Column(String(36), index=True)  # Reference to user ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    settings = relationship("ProjectSettings", back_populates="project", uselist=False, cascade="all, delete-orphan")
    resources = relationship("Resource", back_populates="project", cascade="all, delete-orphan") 
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    board_columns = relationship("BoardColumn", back_populates="project", cascade="all, delete-orphan")
        
class ProjectSettings(Base):
    __tablename__ = "project_settings"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), unique=True)
    visibility = Column(String(20), default="private")  # private, internal, public
    enable_tasks = Column(Boolean, default=True)
    enable_issues = Column(Boolean, default=True)
    enable_wiki = Column(Boolean, default=False)
    default_assignee_id = Column(String(36), nullable=True)
    custom_fields = Column(JSON, nullable=True)
    notification_settings = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="settings")

class ProjectMember(Base):
    __tablename__ = "project_members"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), index=True)
    user_id = Column(String(36), index=True)  # Reference to user ID
    role = Column(String(20), default="member")  # owner, admin, member, guest
    joined_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="members")
    
    __table_args__ = (
        # Unique constraint to ensure a user can be added only once to a project
        {"sqlite_autoincrement": True},
    )