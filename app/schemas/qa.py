# project-service/app/schemas/issue_test.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Base schemas for Issue
class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "OPEN"
    priority: str = "MEDIUM"
    issue_type: str = "BUG"
    assignee_id: Optional[str] = None
    reporter_id: str
    
class IssueCreate(IssueBase):
    project_id: str
    
class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    issue_type: Optional[str] = None
    assignee_id: Optional[str] = None
    reporter_id: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
class IssueResponse(IssueBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class IssueStatusUpdate(BaseModel):
    status: str
    
class IssueAssigneeUpdate(BaseModel):
    assignee_id: Optional[str] = None

class IssueStatisticsResponse(BaseModel):
    total_issues: int
    status_distribution: Dict[str, int]
    priority_distribution: Dict[str, int]
    type_distribution: Dict[str, int]
    assignee_distribution: Dict[str, int]
    avg_resolution_time_hours: Optional[float] = None
    open_issues: int
    closed_issues: int

# Base schemas for IssueAttachment
class IssueAttachmentBase(BaseModel):
    file_name: str
    file_type: str
    file_size: int
    
class IssueAttachmentCreate(IssueAttachmentBase):
    issue_id: str
    file_path: str
    uploaded_by: str
    
class IssueAttachmentResponse(IssueAttachmentBase):
    id: str
    issue_id: str
    file_path: str
    uploaded_by: str
    uploaded_at: datetime
    
    class Config:
        orm_mode = True

# Base schemas for IssueComment
class IssueCommentBase(BaseModel):
    content: str
    
class IssueCommentCreate(IssueCommentBase):
    issue_id: str
    author_id: str
    
class IssueCommentUpdate(BaseModel):
    content: str
    
class IssueCommentResponse(IssueCommentBase):
    id: str
    issue_id: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Base schemas for TestCase
class TestCaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    steps: List[Dict[str, str]]
    expected_results: str
    category: str
    priority: str = "MEDIUM"
    status: str = "ACTIVE"
    prerequisites: Optional[str] = None
    automated: bool = False
    automation_script_path: Optional[str] = None
    
class TestCaseCreate(TestCaseBase):
    project_id: str
    created_by: str
    
class TestCaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[Dict[str, str]]] = None
    expected_results: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    prerequisites: Optional[str] = None
    updated_by: Optional[str] = None
    automated: Optional[bool] = None
    automation_script_path: Optional[str] = None
    
class TestCaseResponse(TestCaseBase):
    id: str
    project_id: str
    created_by: str
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Base schemas for TestRun
class TestRunBase(BaseModel):
    name: str
    description: Optional[str] = None
    environment: str
    test_cases: List[str]
    status: str = "PLANNED"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    executor_id: Optional[str] = None
    
class TestRunCreate(TestRunBase):
    project_id: str
    created_by: str
    
class TestRunUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    environment: Optional[str] = None
    test_cases: Optional[List[str]] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    executor_id: Optional[str] = None
    
class TestRunResponse(TestRunBase):
    id: str
    project_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Base schemas for TestRunResult
class TestRunResultBase(BaseModel):
    status: str
    notes: Optional[str] = None
    execution_time: Optional[float] = None
    defects: Optional[List[str]] = None
    
class TestRunResultCreate(TestRunResultBase):
    test_run_id: str
    test_case_id: str
    executor_id: str
    
class TestRunResultUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    execution_time: Optional[float] = None
    defects: Optional[List[str]] = None
    
class TestRunResultResponse(TestRunResultBase):
    id: str
    test_run_id: str
    test_case_id: str
    executor_id: str
    executed_at: datetime
    
    class Config:
        orm_mode = True

# Test metrics schema
class TestMetricsResponse(BaseModel):
    total_test_runs: int
    total_test_executions: int
    pass_rate: float
    results_distribution: Dict[str, int]
    avg_execution_time: Optional[float] = None
    completed_test_runs: int
    in_progress_test_runs: int