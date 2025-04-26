# pm-service/app/db/seed.py
import random
from datetime import datetime, timedelta, timezone
import uuid
from typing import List, Dict, Any
from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.crud import (
    project,
    task,
    resource,
    qa
)
from app.schemas.project import (
    ProjectCreate, ProjectUpdate,
    ProjectSettingsCreate, ProjectSettingsUpdate,
    ProjectMemberCreate, ProjectMemberUpdate
)
from app.schemas.task import (
    TaskCreate, TaskUpdate,
    BoardColumnCreate, BoardColumnUpdate
)
from app.schemas.resource import (
    ResourceCreate, ResourceUpdate,
    ResourceAssignmentCreate, ResourceAssignmentUpdate
)
from app.schemas.qa import (
    IssueCreate, IssueUpdate, 
    IssueAttachmentCreate, IssueCommentCreate,
    TestCaseCreate, TestCaseUpdate, 
    TestRunCreate, TestRunUpdate,
    TestRunResultCreate, TestRunResultUpdate
)

fake = Faker()

# Helper function to generate user IDs for consistency
def generate_user_ids(count: int = 5) -> List[str]:
    return [str(uuid.uuid4()) for _ in range(count)]

def seed_projects(db: Session) -> List:
    """Seed projects using ID-based checks"""
    projects_data = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",  # Predefined UUIDs
            "name": "Website Redesign",
            "description": "Redesign company website with modern UI/UX.",
            "status": "active"
        },
        {
            "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "name": "Mobile App Development",
            "description": "Develop cross-platform mobile app",
            "status": "planning"
        },
        {
            "id": "6ba7b811-9dad-11d1-80b4-00c04fd430c9",
            "name": "ERP Implementation",
            "description": "Implement new ERP system",
            "status": "active"
        }
    ]
    
    projects = []
    for proj_data in projects_data:
        # Check by predefined ID
        existing_proj = project.get_project_by_id(db, uuid.UUID(proj_data["id"]))
        if existing_proj:
            print(f"Project '{proj_data['name']}' already exists, skipping...")
            projects.append(existing_proj)
            continue
        
        try:
            now = datetime.now(timezone.utc)
            start_date = now - timedelta(days=random.randint(10, 30))
            end_date = start_date + timedelta(days=random.randint(60, 180))
            
            proj = project.create_project(db, ProjectCreate(
                id=uuid.UUID(proj_data["id"]),  # Use predefined ID
                name=proj_data["name"],
                description=proj_data["description"],
                status=proj_data["status"],
                start_date=start_date,
                end_date=end_date,
                owner_id=str(uuid.uuid4())
            ))
            projects.append(proj)
            print(f"Created project: {proj_data['name']}")
        except IntegrityError:
            db.rollback()
            existing_proj = project.get_project_by_id(db, UUID(proj_data["id"]))
            if existing_proj:
                projects.append(existing_proj)
                print(f"Project '{proj_data['name']}' already exists, using existing...")
    
    return projects
    
def seed_project_settings(db: Session, projects: List) -> List:
    """Seed project settings with random visibility."""
    settings_list = []
    for proj in projects:
        existing = project.get_project_settings(db, proj.id)
        if existing:
            print(f"Settings for project '{proj.name}' exist, skipping...")
            settings_list.append(existing)
            continue
        
        try:
            settings = project.create_project_settings(db, ProjectSettingsCreate(
                project_id=proj.id,
                visibility=random.choice(["private", "internal", "public"]),
                enable_wiki=random.choice([True, False])
            ))
            settings_list.append(settings)
            print(f"Created settings for project: {proj.name}")
        except IntegrityError:
            db.rollback()
            print(f"Failed to create settings for project '{proj.name}'")
    
    return settings_list

def seed_project_members(db: Session, projects: List, user_ids: List[str]) -> List:
    """Seed project members with different roles."""
    members = []
    for proj in projects:
        existing = project.get_project_members(db, proj.id)
        if existing:
            print(f"Project '{proj.name}' has existing members, skipping...")
            members.extend(existing)
            continue
        
        # Add owner as member
        members.append(project.create_project_member(db, ProjectMemberCreate(
            project_id=proj.id,
            user_id=proj.owner_id,
            role="owner"
        )))
        
        # Add 3-5 additional members
        for _ in range(random.randint(3, 5)):
            member_data = ProjectMemberCreate(
                project_id=proj.id,
                user_id=random.choice(user_ids),
                role=random.choice(["admin", "member", "guest"])
            )
            members.append(project.create_project_member(db, member_data))
        
        print(f"Added members to project: {proj.name}")
    
    return members

def seed_board_columns(db: Session, projects: List) -> Dict[str, List]:
    """Seed board columns for each project (To Do, In Progress, etc.)"""
    project_columns = {}
    column_names = ["To Do", "In Progress", "In Review", "Done"]
    
    for proj in projects:
        columns = []
        existing_columns = task.get_board_columns(db, proj.id)
        
        if existing_columns:
            print(f"Project '{proj.name}' already has board columns, skipping...")
            project_columns[proj.id] = existing_columns
            continue
        
        print(f"Creating board columns for project: {proj.name}")
        for idx, name in enumerate(column_names):
            column = task.create_board_column(db, BoardColumnCreate(
                project_id=proj.id,
                name=name,
                order=idx,
                wip_limit=5 if name == "In Progress" else None,
                color="#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])
            ))
            columns.append(column)
        
        project_columns[proj.id] = columns
    
    return project_columns

def seed_tasks(db: Session, projects: List, project_columns: Dict[str, List], user_ids: List[str]) -> List:
    """Seed tasks with dependencies and assignments"""
    tasks = []
    task_titles = {
        "Website Redesign": ["Design homepage", "Implement backend", "Mobile optimization"],
        "Mobile App Development": ["UI Design", "API Integration", "Testing"],
        "ERP Implementation": ["Requirement Analysis", "System Configuration", "User Training"],
        "Marketing Campaign": ["Content Creation", "Social Media Setup", "Analytics"]
    }
    
    for proj in projects:
        proj_titles = task_titles.get(proj.name, task_titles["Website Redesign"])
        columns = project_columns.get(proj.id, [])
        
        if not columns:
            print(f"No columns found for project '{proj.name}', skipping tasks...")
            continue
        
        print(f"Creating tasks for project: {proj.name}")
        for idx, title in enumerate(proj_titles):
            column = random.choice(columns)
            now = datetime.now(timezone.utc)
            due_date = now + timedelta(days=random.randint(7, 30))
            
            task_obj = task.create_task(db, TaskCreate(
                project_id=proj.id,
                title=title,
                description=fake.paragraph(),
                status=column.name.lower().replace(" ", "_"),
                priority=random.choice(["low", "medium", "high"]),
                reporter_id=random.choice(user_ids),
                assignee_id=random.choice(user_ids) if random.random() > 0.3 else None,
                due_date=due_date,
                estimated_hours=random.uniform(2, 8),
                column_id=column.id,
                position=idx
            ))
            tasks.append(task_obj)
        db.flush()
    return tasks

def seed_resources(db: Session, projects: List) -> List:
    """Seed project resources (people, equipment, materials)"""
    resources = []
    
    for proj in projects:
        print(f"Creating resources for project: {proj.name}")
        
        # People resources
        for _ in range(3):
            resources.append(resource.create_resource(db, ResourceCreate(
                project_id=proj.id,
                name=fake.name(),
                type="person",
                cost_rate=random.uniform(50, 150),
                availability=random.choice([50.0, 75.0, 100.0]),
                skills=[fake.job(), fake.job()],  # Send as list
                email=fake.email(),
                phone=fake.phone_number()[:20]
            )))
        
        # Equipment resources
        for equip in ["Design Workstation", "Testing Device", "Server"]:
            resources.append(resource.create_resource(db, ResourceCreate(
                project_id=proj.id,
                name=equip,
                type="equipment",
                cost_rate=random.uniform(10, 50),
                availability=100.0
            )))
    
    return resources

def seed_resource_assignments(db: Session, projects: List, tasks: List, resources: List) -> List:
    """Assign resources to tasks"""
    assignments = []
    
    for proj in projects:
        # Convert UUIDs to strings for comparison
        proj_tasks = [t for t in tasks if str(t.project_id) == str(proj.id)]
        proj_resources = [r for r in resources if str(r.project_id) == str(proj.id)]
        
        if not proj_tasks or not proj_resources:
            continue
        
        print(f"Creating resource assignments for project: {proj.name}")
        for t in proj_tasks:  # Changed variable name from 'task' to 't'
            if random.random() > 0.5:
                res = random.choice(proj_resources)
                assignments.append(resource.create_resource_assignment(
                    db,
                    ResourceAssignmentCreate(
                        project_id=str(proj.id),
                        task_id=str(t.id),  # Explicit string conversion
                        resource_id=str(res.id),
                        allocation_percentage=random.choice([50.0, 75.0, 100.0]),
                        role=random.choice(["Developer", "Tester", "Designer"])
                    )
                ))
    
    return assignments

def seed_issues(db: Session, projects: List, user_ids: List[str]) -> List:
    """Seed issues with attachments and comments"""
    issues = []
    issue_types = ["BUG", "ENHANCEMENT", "TASK"]
    priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    statuses = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]
    
    for proj in projects:
        # Create 3-7 issues per project
        for _ in range(random.randint(3, 7)):
            issue_data = IssueCreate(
                title=fake.sentence(),
                description=fake.paragraph(),
                project_id=proj.id,
                status=random.choice(statuses),
                priority=random.choice(priorities),
                issue_type=random.choice(issue_types),
                assignee_id=random.choice(user_ids),
                reporter_id=random.choice(user_ids)
            )
            
            try:
                issue = qa.create_issue(db, issue_data)
                issues.append(issue)
                
                # Add 0-3 comments
                for _ in range(random.randint(0, 3)):
                    comment_data = IssueCommentCreate(
                        issue_id=issue.id,
                        content=fake.paragraph(),
                        author_id=random.choice(user_ids)
                    )
                    qa.create_issue_comment(db, comment_data)
                
                # Add 0-2 attachments
                for _ in range(random.randint(0, 2)):
                    attachment_data = IssueAttachmentCreate(
                        issue_id=issue.id,
                        file_name=f"attachment_{fake.word()}.{random.choice(['pdf', 'png', 'doc'])}",
                        file_path=f"/uploads/issues/{issue.id}/{uuid.uuid4()}",
                        file_type=random.choice(['application/pdf', 'image/png', 'application/msword']),
                        file_size=random.randint(1000, 5000000),
                        uploaded_by=random.choice(user_ids)
                    )
                    qa.create_issue_attachment(db, attachment_data)
                
            except Exception as e:
                print(f"Error creating issue for project {proj.id}: {str(e)}")
                db.rollback()
                continue
            
        print(f"Created issues for project: {proj.name}")
    return issues

def seed_test_cases(db: Session, projects: List, user_ids: List[str]) -> List:
    """Seed test cases for projects"""
    test_cases = []
    categories = ["Functional", "Security", "Performance", "Integration"]
    priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    statuses = ["ACTIVE", "DRAFT", "DEPRECATED"]
    
    for proj in projects:
        # Create 5-10 test cases per project
        for _ in range(random.randint(5, 10)):
            steps = [
                {"step": f"Step {i+1}", "description": fake.sentence()}
                for i in range(random.randint(3, 6))
            ]
            
            test_case_data = TestCaseCreate(
                title=fake.sentence(),
                description=fake.paragraph(),
                project_id=proj.id,
                steps=steps,
                expected_results=fake.paragraph(),
                category=random.choice(categories),
                priority=random.choice(priorities),
                status=random.choice(statuses),
                prerequisites=fake.paragraph() if random.random() > 0.5 else None,
                created_by=random.choice(user_ids),
                automated=random.random() > 0.7,
                automation_script_path=f"/scripts/test_{uuid.uuid4()}.py" if random.random() > 0.7 else None
            )
            
            try:
                test_case = qa.create_test_case(db, test_case_data)
                test_cases.append(test_case)
            except Exception as e:
                print(f"Error creating test case for project {proj.id}: {str(e)}")
                db.rollback()
                continue
            
        print(f"Created test cases for project: {proj.name}")
    return test_cases

def seed_test_runs(db: Session, projects: List, test_cases: List, user_ids: List[str]) -> (List, List):
    """Seed test runs and their results"""
    test_runs = []
    test_results = []
    environments = ["DEV", "QA", "STAGING", "PROD"]
    run_statuses = ["PLANNED", "IN_PROGRESS", "COMPLETED", "ABORTED"]
    result_statuses = ["PASSED", "FAILED", "BLOCKED", "SKIPPED"]
    
    for proj in projects:
        # Get test cases for this project
        project_test_cases = [tc for tc in test_cases if tc.project_id == proj.id]
        if not project_test_cases:
            continue
        
        # Create 2-4 test runs per project
        for _ in range(random.randint(2, 4)):
            # Select random subset of test cases
            selected_test_cases = random.sample(
                project_test_cases,
                min(len(project_test_cases), random.randint(2, len(project_test_cases)))
            )
            
            test_run_data = TestRunCreate(
                name=f"Test Run {fake.word()}",
                description=fake.paragraph(),
                project_id=proj.id,
                environment=random.choice(environments),
                test_cases=[tc.id for tc in selected_test_cases],
                status=random.choice(run_statuses),
                executor_id=random.choice(user_ids),
                created_by=random.choice(user_ids)
            )
            
            try:
                test_run = qa.create_test_run(db, test_run_data)
                test_runs.append(test_run)
                
                # Create results for each test case in the run
                for tc in selected_test_cases:
                    result_data = TestRunResultCreate(
                        test_run_id=test_run.id,
                        test_case_id=tc.id,
                        status=random.choice(result_statuses),
                        notes=fake.paragraph() if random.random() > 0.5 else None,
                        execution_time=random.uniform(0.5, 10.0),
                        executor_id=test_run.executor_id,
                        defects=[] if random.random() > 0.3 else [str(uuid.uuid4()) for _ in range(random.randint(1, 3))]
                    )
                    
                    result = qa.create_test_run_result(db, result_data)
                    test_results.append(result)
                    
            except Exception as e:
                print(f"Error creating test run for project {proj.id}: {str(e)}")
                db.rollback()
                continue
            
        print(f"Created test runs for project: {proj.name}")
    return test_runs, test_results

def main():
    """Main function to seed all data"""
    db = SessionLocal()
    try:
        print("Starting database seeding...")
        
        # Generate some user IDs for reference
        user_ids = generate_user_ids(10)
        
        # Seed core project data
        projects = seed_projects(db)
        settings = seed_project_settings(db, projects)
        members = seed_project_members(db, projects, user_ids)
        
        # Seed project management data
        columns = seed_board_columns(db, projects)
        tasks = seed_tasks(db, projects, columns, user_ids)
        
        # Seed resource management data
        resources = seed_resources(db, projects)
        assignments = seed_resource_assignments(db, projects, tasks, resources)
        
        # Seed QA data
        issues = seed_issues(db, projects, user_ids)
        test_cases = seed_test_cases(db, projects, user_ids)
        test_runs, test_results = seed_test_runs(db, projects, test_cases, user_ids)
        
        db.commit()
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error during seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()