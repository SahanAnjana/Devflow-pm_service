# project-service/app/db/models/qa.py
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Issue(Base):
    """Issue or bug model for tracking software defects"""
    __tablename__ = "issues"
    
    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    status = Column(String(20), nullable=False, default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority = Column(String(20), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    issue_type = Column(String(20), nullable=False, default="BUG")  # BUG, ENHANCEMENT, TASK
    assignee_id = Column(String(36), nullable=True)
    reporter_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    attachments = relationship("IssueAttachment", back_populates="issue", cascade="all, delete")
    comments = relationship("IssueComment", back_populates="issue", cascade="all, delete")
    
    # Optional fields for linking
    related_test_case_id = Column(String(36), ForeignKey("test_cases.id"), nullable=True)
    related_test_case = relationship("TestCase", back_populates="related_issues")

class IssueAttachment(Base):
    """Attachment model for issue files"""
    __tablename__ = "issue_attachments"
    
    id = Column(String(36), primary_key=True, index=True)
    issue_id = Column(String(36), ForeignKey("issues.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_by = Column(String(36), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    issue = relationship("Issue", back_populates="attachments")

class IssueComment(Base):
    """Comment model for issue discussions"""
    __tablename__ = "issue_comments"
    
    id = Column(String(36), primary_key=True, index=True)
    issue_id = Column(String(36), ForeignKey("issues.id"), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    issue = relationship("Issue", back_populates="comments")

class TestCase(Base):
    """Test case model for defining test scenarios"""
    __tablename__ = "test_cases"
    
    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    steps = Column(JSON, nullable=False)  # Array of test steps
    expected_results = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # Functional, Security, Performance, etc.
    priority = Column(String(20), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, DRAFT, DEPRECATED
    prerequisites = Column(Text, nullable=True)
    created_by = Column(String(36), nullable=False)
    updated_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    automated = Column(Boolean, default=False)
    automation_script_path = Column(String(512), nullable=True)
    
    # Relationships
    related_issues = relationship("Issue", back_populates="related_test_case")
    test_results = relationship("TestRunResult", back_populates="test_case", cascade="all, delete")

class TestRun(Base):
    """Test run model for tracking test execution"""
    __tablename__ = "test_runs"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    status = Column(String(20), nullable=False, default="PLANNED")  # PLANNED, IN_PROGRESS, COMPLETED, ABORTED
    environment = Column(String(50), nullable=False)  # DEV, QA, STAGING, PROD
    test_cases = Column(JSON, nullable=False)  # Array of test case IDs
    executor_id = Column(String(36), nullable=True)
    created_by = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Relationships
    results = relationship("TestRunResult", back_populates="test_run", cascade="all, delete")

class TestRunResult(Base):
    """Test run result model for recording test execution outcomes"""
    __tablename__ = "test_run_results"
    
    id = Column(String(36), primary_key=True, index=True)
    test_run_id = Column(String(36), ForeignKey("test_runs.id"), nullable=False)
    test_case_id = Column(String(36), ForeignKey("test_cases.id"), nullable=False)
    status = Column(String(20), nullable=False)  # PASSED, FAILED, BLOCKED, SKIPPED
    notes = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)  # in seconds
    executor_id = Column(String(36), nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow)
    defects = Column(JSON, nullable=True)  # Array of related issue IDs
    
    # Relationships
    test_run = relationship("TestRun", back_populates="results")
    test_case = relationship("TestCase", back_populates="test_results")