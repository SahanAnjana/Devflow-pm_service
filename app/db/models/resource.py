# project-service/app/db/models/resource.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Resource(Base):
    """
    Resource model for project resources
    Resources can be people, equipment, or materials used in the project
    """
    __tablename__ = "resources"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)  # person, equipment, material, etc.
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    cost_rate = Column(Float, nullable=True)  # cost per hour or unit
    availability = Column(Float, default=100.0)  # percentage of availability (e.g. 100% = full-time)
    skills = Column(Text, nullable=True)  # store as JSON string
    description = Column(Text, nullable=True)
    
    # Additional fields for person type resources
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Additional properties as JSON for flexible extension
    properties = Column(JSON, nullable=True)  # MySQL 5.7+ supports JSON
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="resources")
    assignments = relationship("ResourceAssignment", back_populates="resource", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Resource {self.name} ({self.type})>"

class ResourceAssignment(Base):
    """
    ResourceAssignment model for assigning resources to tasks
    """
    __tablename__ = "resource_assignments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(String(36), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = Column(String(50), nullable=True)  # Role in this particular assignment
    allocation_percentage = Column(Float, default=100.0)  # Percentage of resource allocated to this task
    start_date = Column(DateTime, nullable=True)  # If different from task start date
    end_date = Column(DateTime, nullable=True)  # If different from task end date
    hours_allocated = Column(Float, nullable=True)  # Total hours allocated to this task
    
    # Additional properties as JSON for flexible extension
    properties = Column(JSON, nullable=True)  # MySQL 5.7+ supports JSON
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project")
    resource = relationship("Resource", back_populates="assignments")
    task = relationship("Task", back_populates="resource_assignments")
    
    def __repr__(self):
        return f"<ResourceAssignment {self.resource_id} to {self.task_id}>"