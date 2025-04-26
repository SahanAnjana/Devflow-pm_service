# project-service/app/crud/qa.py
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta, timezone
from app.db.models.qa import Issue, IssueComment, IssueAttachment, TestCase, TestRun, TestRunResult
from app.schemas.qa import (
    IssueCreate, IssueUpdate,
    IssueCommentCreate, IssueAttachmentCreate,
    TestCaseCreate, TestCaseUpdate,
    TestRunCreate, TestRunUpdate,
    TestRunResultCreate, TestRunResultUpdate
)
import uuid

# Issue CRUD Operations
def get_issue_by_id(db: Session, issue_id: str) -> Optional[Issue]:
    """Get an issue by its ID"""
    return db.query(Issue).filter(Issue.id == issue_id).first()

def get_issues_by_project(
    db: Session,
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[str] = None,
    reporter_id: Optional[str] = None,
    issue_type: Optional[str] = None
) -> List[Issue]:
    """Get all issues for a project with optional filters"""
    query = db.query(Issue).filter(Issue.project_id == project_id)
    
    if status:
        query = query.filter(Issue.status == status)
    if priority:
        query = query.filter(Issue.priority == priority)
    if assignee_id:
        query = query.filter(Issue.assignee_id == assignee_id)
    if reporter_id:
        query = query.filter(Issue.reporter_id == reporter_id)
    if issue_type:
        query = query.filter(Issue.issue_type == issue_type)
    
    return query.offset(skip).limit(limit).all()

def create_issue(db: Session, issue: IssueCreate) -> Issue:
    """Create a new issue"""
    now = datetime.now(timezone.utc)
    db_issue = Issue(
        id=str(uuid.uuid4()),
        title=issue.title,
        description=issue.description,
        project_id=issue.project_id,
        status=issue.status,
        priority=issue.priority,
        issue_type=issue.issue_type,
        assignee_id=issue.assignee_id,
        reporter_id=issue.reporter_id,
        created_at=now,
        updated_at=now
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

def update_issue(db: Session, issue_id: str, issue_data: IssueUpdate) -> Optional[Issue]:
    """Update an issue"""
    db_issue = get_issue_by_id(db, issue_id)
    if not db_issue:
        return None
    
    # Update attributes
    update_data = issue_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_issue, key, value)
    
    db_issue.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_issue)
    return db_issue

def delete_issue(db: Session, issue_id: str) -> bool:
    """Delete an issue"""
    db_issue = get_issue_by_id(db, issue_id)
    if not db_issue:
        return False
    
    db.delete(db_issue)
    db.commit()
    return True

def update_issue_status(db: Session, issue_id: str, status: str) -> Optional[Issue]:
    """Update an issue's status"""
    db_issue = get_issue_by_id(db, issue_id)
    if not db_issue:
        return None
    
    db_issue.status = status
    db_issue.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_issue)
    return db_issue

def update_issue_assignee(db: Session, issue_id: str, assignee_id: str) -> Optional[Issue]:
    """Update an issue's assignee"""
    db_issue = get_issue_by_id(db, issue_id)
    if not db_issue:
        return None
    
    db_issue.assignee_id = assignee_id
    db_issue.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_issue)
    return db_issue

def get_issue_statistics(
    db: Session, 
    project_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Get issue statistics for a project"""
    query = db.query(Issue).filter(Issue.project_id == project_id)
    
    # Apply date filters if provided
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.filter(Issue.created_at >= start)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.filter(Issue.created_at <= end)
    
    # All issues in the filtered set
    issues = query.all()
    
    # Count by status
    status_counts = {}
    for issue in issues:
        if issue.status not in status_counts:
            status_counts[issue.status] = 0
        status_counts[issue.status] += 1
    
    # Count by priority
    priority_counts = {}
    for issue in issues:
        if issue.priority not in priority_counts:
            priority_counts[issue.priority] = 0
        priority_counts[issue.priority] += 1
    
    # Count by type
    type_counts = {}
    for issue in issues:
        if issue.issue_type not in type_counts:
            type_counts[issue.issue_type] = 0
        type_counts[issue.issue_type] += 1
    
    # Count by assignee
    assignee_counts = {}
    for issue in issues:
        if issue.assignee_id:
            if issue.assignee_id not in assignee_counts:
                assignee_counts[issue.assignee_id] = 0
            assignee_counts[issue.assignee_id] += 1
    
    # Calculate average resolution time for closed issues
    closed_issues = [i for i in issues if i.status == "CLOSED" or i.status == "RESOLVED"]
    avg_resolution_time = None
    if closed_issues:
        resolution_times = []
        for issue in closed_issues:
            if issue.resolved_at and issue.created_at:
                resolution_time = (issue.resolved_at - issue.created_at).total_seconds() / 3600  # in hours
                resolution_times.append(resolution_time)
        
        if resolution_times:
            avg_resolution_time = sum(resolution_times) / len(resolution_times)
    
    return {
        "total_issues": len(issues),
        "status_distribution": status_counts,
        "priority_distribution": priority_counts,
        "type_distribution": type_counts,
        "assignee_distribution": assignee_counts,
        "avg_resolution_time_hours": avg_resolution_time,
        "open_issues": len([i for i in issues if i.status not in ["CLOSED", "RESOLVED"]]),
        "closed_issues": len(closed_issues)
    }

# Test Case CRUD Operations
def get_test_case_by_id(db: Session, test_case_id: str) -> Optional[TestCase]:
    """Get a test case by its ID"""
    return db.query(TestCase).filter(TestCase.id == test_case_id).first()

def get_test_cases_by_project(
    db: Session,
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None
) -> List[TestCase]:
    """Get all test cases for a project with optional filters"""
    query = db.query(TestCase).filter(TestCase.project_id == project_id)
    
    if category:
        query = query.filter(TestCase.category == category)
    if priority:
        query = query.filter(TestCase.priority == priority)
    if status:
        query = query.filter(TestCase.status == status)
    
    return query.offset(skip).limit(limit).all()

def create_test_case(db: Session, test_case: TestCaseCreate) -> TestCase:
    """Create a new test case"""
    now = datetime.now(timezone.utc)
    db_test_case = TestCase(
        id=str(uuid.uuid4()),
        title=test_case.title,
        description=test_case.description,
        project_id=test_case.project_id,
        steps=test_case.steps,
        expected_results=test_case.expected_results,
        category=test_case.category,
        priority=test_case.priority,
        status=test_case.status,
        prerequisites=test_case.prerequisites,
        created_by=test_case.created_by,
        updated_by=test_case.created_by,
        created_at=now,
        updated_at=now
    )
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    return db_test_case

def update_test_case(db: Session, test_case_id: str, test_case_data: TestCaseUpdate) -> Optional[TestCase]:
    """Update a test case"""
    db_test_case = get_test_case_by_id(db, test_case_id)
    if not db_test_case:
        return None
    
    # Update attributes
    update_data = test_case_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_test_case, key, value)
    
    db_test_case.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_test_case)
    return db_test_case

def delete_test_case(db: Session, test_case_id: str) -> bool:
    """Delete a test case"""
    db_test_case = get_test_case_by_id(db, test_case_id)
    if not db_test_case:
        return False
    
    db.delete(db_test_case)
    db.commit()
    return True

# Test Run CRUD Operations
def get_test_run_by_id(db: Session, test_run_id: str) -> Optional[TestRun]:
    """Get a test run by its ID"""
    return db.query(TestRun).filter(TestRun.id == test_run_id).first()

def get_test_runs_by_project(
    db: Session,
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    executor_id: Optional[str] = None
) -> List[TestRun]:
    """Get all test runs for a project with optional filters"""
    query = db.query(TestRun).filter(TestRun.project_id == project_id)
    
    if status:
        query = query.filter(TestRun.status == status)
    if executor_id:
        query = query.filter(TestRun.executor_id == executor_id)
    
    return query.offset(skip).limit(limit).all()

def create_test_run(db: Session, test_run: TestRunCreate) -> TestRun:
    """Create a new test run"""
    now = datetime.now(timezone.utc)
    db_test_run = TestRun(
        id=str(uuid.uuid4()),
        name=test_run.name,
        description=test_run.description,
        project_id=test_run.project_id,
        status=test_run.status,
        environment=test_run.environment,
        test_cases=test_run.test_cases,
        executor_id=test_run.executor_id,
        created_by=test_run.created_by,
        created_at=now,
        updated_at=now,
        start_date=test_run.start_date,
        end_date=test_run.end_date
    )
    db.add(db_test_run)
    db.commit()
    db.refresh(db_test_run)
    return db_test_run

def update_test_run(db: Session, test_run_id: str, test_run_data: TestRunUpdate) -> Optional[TestRun]:
    """Update a test run"""
    db_test_run = get_test_run_by_id(db, test_run_id)
    if not db_test_run:
        return None
    
    # Update attributes
    update_data = test_run_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_test_run, key, value)
    
    db_test_run.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_test_run)
    return db_test_run

def delete_test_run(db: Session, test_run_id: str) -> bool:
    """Delete a test run"""
    db_test_run = get_test_run_by_id(db, test_run_id)
    if not db_test_run:
        return False
    
    db.delete(db_test_run)
    db.commit()
    return True

def get_test_run_result(db: Session, result_id: str) -> Optional[TestRunResult]:
    """Get a test run result by its ID"""
    return db.query(TestRunResult).filter(TestRunResult.id == result_id).first()

def create_test_run_result(db: Session, result: TestRunResultCreate) -> TestRunResult:
    """Create a new test run result"""
    db_result = TestRunResult(
        id=str(uuid.uuid4()),
        test_run_id=result.test_run_id,
        test_case_id=result.test_case_id,
        status=result.status,
        notes=result.notes,
        execution_time=result.execution_time,
        executor_id=result.executor_id,
        executed_at=datetime.now(timezone.utc),
        defects=result.defects
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def update_test_run_result(db: Session, result_id: str, result_data: TestRunResultUpdate) -> Optional[TestRunResult]:
    """Update a test run result"""
    db_result = get_test_run_result(db, result_id)
    if not db_result:
        return None
    
    # Update attributes
    update_data = result_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_result, key, value)
    
    db.commit()
    db.refresh(db_result)
    return db_result

def get_test_metrics(
    db: Session, 
    project_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Get test metrics for a project"""
    # Get test runs for the project
    query = db.query(TestRun).filter(TestRun.project_id == project_id)
    
    # Apply date filters if provided
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.filter(TestRun.created_at >= start)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.filter(TestRun.created_at <= end)
    
    test_runs = query.all()
    
    # Get all test results for these runs
    test_run_ids = [tr.id for tr in test_runs]
    results = []
    if test_run_ids:
        results = db.query(TestRunResult).filter(
            TestRunResult.test_run_id.in_(test_run_ids)
        ).all()
    
    # Test case pass rate
    total_executions = len(results)
    passed_executions = len([r for r in results if r.status == "PASSED"])
    failed_executions = len([r for r in results if r.status == "FAILED"])
    blocked_executions = len([r for r in results if r.status == "BLOCKED"])
    skipped_executions = len([r for r in results if r.status == "SKIPPED"])
    
    pass_rate = 0
    if total_executions > 0:
        pass_rate = (passed_executions / total_executions) * 100
    
    # Average execution time
    avg_execution_time = None
    if results:
        execution_times = [r.execution_time for r in results if r.execution_time is not None]
        if execution_times:
            avg_execution_time = sum(execution_times) / len(execution_times)
    1
    return {
        "total_test_runs": len(test_runs),
        "total_test_executions": total_executions,
        "pass_rate": pass_rate,
        "results_distribution": {
            "passed": passed_executions,
            "failed": failed_executions,
            "blocked": blocked_executions,
            "skipped": skipped_executions
        },
        "avg_execution_time": avg_execution_time,
        "completed_test_runs": len([tr for tr in test_runs if tr.status == "COMPLETED"]),
        "in_progress_test_runs": len([tr for tr in test_runs if tr.status == "IN_PROGRESS"])
    }

# Issue Comment CRUD Operations
def create_issue_comment(db: Session, comment: IssueCommentCreate) -> IssueComment:
    """Create a new issue comment"""
    now = datetime.now(timezone.utc)
    db_comment = IssueComment(
        id=str(uuid.uuid4()),
        issue_id=comment.issue_id,
        content=comment.content,
        author_id=comment.author_id,
        created_at=now,
        updated_at=now
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_issue_comments(db: Session, issue_id: str) -> List[IssueComment]:
    """Get all comments for an issue"""
    return db.query(IssueComment).filter(IssueComment.issue_id == issue_id).all()

# Issue Attachment CRUD Operations
def create_issue_attachment(db: Session, attachment: IssueAttachmentCreate) -> IssueAttachment:
    """Create a new issue attachment"""
    db_attachment = IssueAttachment(
        id=str(uuid.uuid4()),
        issue_id=attachment.issue_id,
        file_name=attachment.file_name,
        file_path=attachment.file_path,
        file_type=attachment.file_type,
        file_size=attachment.file_size,
        uploaded_by=attachment.uploaded_by,
        uploaded_at=datetime.now(timezone.utc)
    )
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment

def get_issue_attachments(db: Session, issue_id: str) -> List[IssueAttachment]:
    """Get all attachments for an issue"""
    return db.query(IssueAttachment).filter(IssueAttachment.issue_id == issue_id).all()