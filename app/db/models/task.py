# project-service/app/db/models/task.py
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

# Task dependencies association table
task_dependencies = Table(
    'task_dependencies',
    Base.metadata,
    Column('task_id', String(36), ForeignKey('tasks.id'), primary_key=True),
    Column('dependency_id', String(36), ForeignKey('tasks.id'), primary_key=True)
)

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), index=True)
    title = Column(String(200), index=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="to_do")  # to_do, in_progress, in_review, done
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    reporter_id = Column(String(36), index=True)  # User who created the task
    assignee_id = Column(String(36), nullable=True, index=True)  # User assigned to the task
    due_date = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)  # For Gantt chart
    estimated_hours = Column(Float, nullable=True)
    tags = Column(JSON, nullable=True)  # Store as JSON array
    column_id = Column(String(36), ForeignKey("board_columns.id"), nullable=True)
    position = Column(Integer, nullable=True)  # Position within a column
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    column = relationship("BoardColumn", back_populates="tasks")
    
    # Many-to-many relationship for task dependencies
    dependencies = relationship(
        "Task",
        secondary=task_dependencies,
        primaryjoin=(task_dependencies.c.task_id == id),
        secondaryjoin=(task_dependencies.c.dependency_id == id),
        backref="dependent_tasks"
    )

class BoardColumn(Base):
    __tablename__ = "board_columns"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), index=True)
    name = Column(String(100))
    order = Column(Integer, default=0)  # Order in the board
    wip_limit = Column(Integer, nullable=True)  # Work in progress limit
    color = Column(String(20), nullable=True)  # Color for the column
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="board_columns")
    tasks = relationship("Task", back_populates="column")

# Update Project model to include relationships
from app.db.models.project import Project
Project.tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
Project.board_columns = relationship("BoardColumn", back_populates="project", cascade="all, delete-orphan")