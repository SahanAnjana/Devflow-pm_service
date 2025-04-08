# project-service/app/api/qa.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth_client import get_current_active_user
from app.api.project import check_project_permissions
from app.crud.qa import (
    # Issue CRUD operations
    get_issue_by_id,
    get_issues_by_project,
    create_issue,
    update_issue,
    delete_issue,
    update_issue_status,
    update_issue_assignee,
    get_issue_statistics,
    
    # Test Case CRUD operations
    get_test_case_by_id,
    get_test_cases_by_project,
    create_test_case,
    update_test_case,
    delete_test_case,
    
    # Test Run CRUD operations
    get_test_run_by_id,
    get_test_runs_by_project,
    create_test_run,
    update_test_run,
    delete_test_run,
    get_test_run_result,
    create_test_run_result,
    update_test_run_result,
    
    # Test metrics
    get_test_metrics
)
from app.schemas.issue_test import (
    # Issue schemas
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueStatusUpdate,
    IssueAssigneeUpdate,
    IssueStatisticsResponse,
    
    # Test case schemas
    TestCaseCreate,
    TestCaseUpdate,
    TestCaseResponse,
    
    # Test run schemas
    TestRunCreate,
    TestRunUpdate,
    TestRunResponse,
    TestRunResultCreate,
    TestRunResultUpdate,
    TestRunResultResponse,
    
    # Test metrics schema
    TestMetricsResponse
)

router = APIRouter()

# Helper function to check issue and test case permissions
def check_issue_permissions(db: Session, issue_id: str, user_id: str, required_roles: List[str] = None):
    """Check if the user has appropriate permissions for an issue"""
    if required_roles is None:
        required_roles = ["owner", "admin"]
    
    # Get the issue
    issue = get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check project permissions
    check_project_permissions(db, issue.project_id, user_id, required_roles)
    
    return issue

def check_test_case_permissions(db: Session, test_case_id: str, user_id: str, required_roles: List[str] = None):
    """Check if the user has appropriate permissions for a test case"""
    if required_roles is None:
        required_roles = ["owner", "admin"]
    
    # Get the test case
    test_case = get_test_case_by_id(db, test_case_id)
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found"
        )
    
    # Check project permissions
    check_project_permissions(db, test_case.project_id, user_id, required_roles)
    
    return test_case

def check_test_run_permissions(db: Session, test_run_id: str, user_id: str, required_roles: List[str] = None):
    """Check if the user has appropriate permissions for a test run"""
    if required_roles is None:
        required_roles = ["owner", "admin"]
    
    # Get the test run
    test_run = get_test_run_by_id(db, test_run_id)
    if not test_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test run not found"
        )
    
    # Check project permissions
    check_project_permissions(db, test_run.project_id, user_id, required_roles)
    
    return test_run

# Issue Management Endpoints
@router.post("/projects/{project_id}/issues", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_new_issue(
    project_id: str,
    issue_data: IssueCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    # Force set the project_id from the path parameter
    issue_data.project_id = project_id
    
    # Set current user as reporter if not specified
    if not hasattr(issue_data, "reporter_id") or not issue_data.reporter_id:
        issue_data.reporter_id = current_user["user_id"]
    
    issue = create_issue(db, issue_data)
    return issue

@router.get("/projects/{project_id}/issues", response_model=List[IssueResponse])
async def list_project_issues(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[str] = None,
    reporter_id: Optional[str] = None,
    issue_type: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    issues = get_issues_by_project(
        db, 
        project_id, 
        skip, 
        limit, 
        status, 
        priority, 
        assignee_id, 
        reporter_id, 
        issue_type
    )
    return issues

@router.get("/projects/{project_id}/issues/{issue_id}", response_model=IssueResponse)
async def get_issue_details(
    project_id: str,
    issue_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    issue = get_issue_by_id(db, issue_id)
    if not issue or issue.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    return issue

@router.put("/projects/{project_id}/issues/{issue_id}", response_model=IssueResponse)
async def update_issue_details(
    project_id: str,
    issue_id: str,
    issue_data: IssueUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    issue = get_issue_by_id(db, issue_id)
    if not issue or issue.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    updated_issue = update_issue(db, issue_id, issue_data)
    return updated_issue

@router.put("/projects/{project_id}/issues/{issue_id}/status", response_model=IssueResponse)
async def update_issue_status_endpoint(
    project_id: str,
    issue_id: str,
    status_data: IssueStatusUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    issue = get_issue_by_id(db, issue_id)
    if not issue or issue.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    updated_issue = update_issue_status(db, issue_id, status_data.status)
    return updated_issue

@router.put("/projects/{project_id}/issues/{issue_id}/assignee", response_model=IssueResponse)
async def update_issue_assignee_endpoint(
    project_id: str,
    issue_id: str,
    assignee_data: IssueAssigneeUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    issue = get_issue_by_id(db, issue_id)
    if not issue or issue.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    updated_issue = update_issue_assignee(db, issue_id, assignee_data.assignee_id)
    return updated_issue

@router.delete("/projects/{project_id}/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_issue(
    project_id: str,
    issue_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    issue = get_issue_by_id(db, issue_id)
    if not issue or issue.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    result = delete_issue(db, issue_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete issue"
        )
    
    return None

@router.get("/projects/{project_id}/issue-statistics", response_model=IssueStatisticsResponse)
async def get_project_issue_statistics(
    project_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    statistics = get_issue_statistics(db, project_id, start_date, end_date)
    return statistics

# Test Case Management Endpoints
@router.post("/projects/{project_id}/test-cases", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_new_test_case(
    project_id: str,
    test_case_data: TestCaseCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    # Force set the project_id from the path parameter
    test_case_data.project_id = project_id
    
    # Set current user as creator if not specified
    if not hasattr(test_case_data, "created_by") or not test_case_data.created_by:
        test_case_data.created_by = current_user["user_id"]
    
    test_case = create_test_case(db, test_case_data)
    return test_case

@router.get("/projects/{project_id}/test-cases", response_model=List[TestCaseResponse])
async def list_project_test_cases(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    test_cases = get_test_cases_by_project(db, project_id, skip, limit, category, priority, status)
    return test_cases

@router.get("/projects/{project_id}/test-cases/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case_details(
    project_id: str,
    test_case_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    test_case = get_test_case_by_id(db, test_case_id)
    if not test_case or test_case.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found"
        )
    
    return test_case

@router.put("/projects/{project_id}/test-cases/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case_details(
    project_id: str,
    test_case_id: str,
    test_case_data: TestCaseUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    test_case = get_test_case_by_id(db, test_case_id)
    if not test_case or test_case.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found"
        )
    
    # Set current user as updater
    test_case_data.updated_by = current_user["user_id"]
    
    updated_test_case = update_test_case(db, test_case_id, test_case_data)
    return updated_test_case

@router.delete("/projects/{project_id}/test-cases/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_test_case(
    project_id: str,
    test_case_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    test_case = get_test_case_by_id(db, test_case_id)
    if not test_case or test_case.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found"
        )
    
    result = delete_test_case(db, test_case_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete test case"
        )
    
    return None

# Test Run Management Endpoints
@router.post("/projects/{project_id}/test-runs", response_model=TestRunResponse, status_code=status.HTTP_201_CREATED)
async def create_new_test_run(
    project_id: str,
    test_run_data: TestRunCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    # Force set the project_id from the path parameter
    test_run_data.project_id = project_id
    
    # Set current user as creator if not specified
    if not hasattr(test_run_data, "created_by") or not test_run_data.created_by:
        test_run_data.created_by = current_user["user_id"]
    
    test_run = create_test_run(db, test_run_data)
    return test_run

@router.get("/projects/{project_id}/test-runs", response_model=List[TestRunResponse])
async def list_project_test_runs(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    executor_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    test_runs = get_test_runs_by_project(db, project_id, skip, limit, status, executor_id)
    return test_runs

@router.get("/projects/{project_id}/test-runs/{test_run_id}", response_model=TestRunResponse)
async def get_test_run_details(
    project_id: str,
    test_run_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    test_run = get_test_run_by_id(db, test_run_id)
    if not test_run or test_run.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test run not found"
        )
    
    return test_run

@router.put("/projects/{project_id}/test-runs/{test_run_id}", response_model=TestRunResponse)
async def update_test_run_details(
    project_id: str,
    test_run_id: str,
    test_run_data: TestRunUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    test_run = get_test_run_by_id(db, test_run_id)
    if not test_run or test_run.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test run not found"
        )
    
    updated_test_run = update_test_run(db, test_run_id, test_run_data)
    return updated_test_run

@router.delete("/projects/{project_id}/test-runs/{test_run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_test_run(
    project_id: str,
    test_run_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin"])
    
    test_run = get_test_run_by_id(db, test_run_id)
    if not test_run or test_run.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test run not found"
        )
    
    result = delete_test_run(db, test_run_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete test run"
        )
    
    return None

# Test Run Results Endpoints
@router.post("/projects/{project_id}/test-runs/{test_run_id}/results", response_model=TestRunResultResponse, status_code=status.HTTP_201_CREATED)
async def create_test_run_result_endpoint(
    project_id: str,
    test_run_id: str,
    result_data: TestRunResultCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    # Check if test run exists and belongs to the project
    test_run = get_test_run_by_id(db, test_run_id)
    if not test_run or test_run.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test run not found"
        )
    
    # Set test_run_id and executor_id
    result_data.test_run_id = test_run_id
    if not hasattr(result_data, "executor_id") or not result_data.executor_id:
        result_data.executor_id = current_user["user_id"]
    
    result = create_test_run_result(db, result_data)
    return result

@router.put("/projects/{project_id}/test-runs/{test_run_id}/results/{result_id}", response_model=TestRunResultResponse)
async def update_test_run_result_endpoint(
    project_id: str,
    test_run_id: str,
    result_id: str,
    result_data: TestRunResultUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member"])
    
    # Check if test run exists and belongs to the project
    test_run = get_test_run_by_id(db, test_run_id)
    if not test_run or test_run.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test run not found"
        )
    
    # Check if the result exists
    result = get_test_run_result(db, result_id)
    if not result or result.test_run_id != test_run_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test run result not found"
        )
    
    updated_result = update_test_run_result(db, result_id, result_data)
    return updated_result

@router.get("/projects/{project_id}/test-metrics", response_model=TestMetricsResponse)
async def get_project_test_metrics(
    project_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check project exists and user has permissions
    check_project_permissions(db, project_id, current_user["user_id"], ["owner", "admin", "member", "guest"])
    
    metrics = get_test_metrics(db, project_id, start_date, end_date)
    return metrics