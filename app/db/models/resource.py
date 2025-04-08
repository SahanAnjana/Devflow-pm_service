# project-service/app/db/models/resource.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base

class Resource(Base):
    """
    Resource model for project resources
    Resources can be people, equipment, or materials used in the project
    """
    __tablename__ = "resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # person, equipment, material, etc.
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    cost_rate = Column(Float, nullable=True)  # cost per hour or unit
    availability = Column(Float, default=100.0)  # percentage of availability (e.g. 100% = full-time)
    skills = Column(ARRAY(String), nullable=True)  # list of skills for person resources
    description = Column(Text, nullable=True)
    
    # Additional fields for person type resources
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    # Additional properties as JSON for flexible extension
    properties = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="resources")
    user = relationship("User", back_populates="resources")
    assignments = relationship("ResourceAssignment", back_populates="resource", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Resource {self.name} ({self.type})>"

class ResourceAssignment(Base):
    """
    ResourceAssignment model for assigning resources to tasks
    """
    __tablename__ = "resource_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = Column(String, nullable=True)  # Role in this particular assignment
    allocation_percentage = Column(Float, default=100.0)  # Percentage of resource allocated to this task
    start_date = Column(DateTime, nullable=True)  # If different from task start date
    end_date = Column(DateTime, nullable=True)  # If different from task end date
    hours_allocated = Column(Float, nullable=True)  # Total hours allocated to this task
    
    # Additional properties as JSON for flexible extension
    properties = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project")
    resource = relationship("Resource", back_populates="assignments")
    task = relationship("Task", back_populates="resource_assignments")
    
    def __repr__(self):
        return f"<ResourceAssignment {self.resource_id} to {self.task_id}>"