# Projects Service APIs

Here's a comprehensive breakdown of the APIs needed for your Projects Service, organized by functional areas:

## Project Management APIs

### Project Core Operations
- `POST /projects` - Create a new project  
- `GET /projects` - List all projects (with pagination and filtering)  
- `GET /projects/{project_id}` - Get project details by ID  
- `PUT /projects/{project_id}` - Update project details  
- `DELETE /projects/{project_id}` - Delete a project  

### Project Configuration
- `GET /projects/{project_id}/settings` - Get project settings  
- `PUT /projects/{project_id}/settings` - Update project settings  
- `POST /projects/{project_id}/members` - Add team members to project  
- `DELETE /projects/{project_id}/members/{user_id}` - Remove a team member  
- `PUT /projects/{project_id}/members/{user_id}/role` - Update member role  

## Task Management APIs

### Task Operations
- `POST /tasks/projects/{project_id}/tasks` - Create a new task  
- `GET /tasks/projects/{project_id}/tasks` - List all tasks in a project  
- `GET /tasks/projects/{project_id}/tasks/{task_id}` - Get task details  
- `PUT /tasks/projects/{project_id}/tasks/{task_id}` - Update task details  
- `DELETE /tasks/projects/{project_id}/tasks/{task_id}` - Delete a task  
- `PUT /tasks/projects/{project_id}/tasks/{task_id}/status` - Update task status  
- `PUT /tasks/projects/{project_id}/tasks/{task_id}/assignee` - Assign task to team member 

### Kanban Board
- `GET /tasks/projects/{project_id}/board` - Get Kanban board configuration  
- `POST /tasks/projects/{project_id}/board/columns` - Add a new column  
- `PUT /tasks/projects/{project_id}/board/columns/{column_id}` - Update column  
- `PUT /tasks/projects/{project_id}/tasks/{task_id}/position` - Reorder/move task  

### Gantt Chart
- `GET /tasks/projects/{project_id}/gantt` - Get Gantt chart data  
- `PUT /tasks/projects/{project_id}/tasks/{task_id}/schedule` - Update task schedule  
- `GET /tasks/projects/{project_id}/critical-path` - Calculate critical path 

## Resource Management APIs

### Resource Allocation
- `POST /resources/projects/{project_id}/resources` - Allocate resources to project  
- `GET /resources/projects/{project_id}/resources` - List allocated resources  
- `GET /resources/projects/{project_id}/resources/{resource_id}` - Get resource details  
- `PUT /resources/projects/{project_id}/resources/{resource_id}` - Update resource  
- `DELETE /resources/projects/{project_id}/resources/{resource_id}` - Remove resource 

### Resource Assignments
- `POST /resources/projects/{project_id}/resource-assignments` - Create assignment  
- `GET /resources/projects/{project_id}/resource-assignments` - List assignments  
- `PUT /resources/projects/{project_id}/resource-assignments/{assignment_id}` - Update assignment  
- `DELETE /resources/projects/{project_id}/resource-assignments/{assignment_id}` - Delete assignment  

### Utilization
- `GET /resources/projects/{project_id}/resources/{resource_id}/utilization` - Get utilization metrics 

## Quality Assurance APIs

### Issue Tracking
- `POST /qa/projects/{project_id}/issues` - Create a new issue  
- `GET /qa/projects/{project_id}/issues` - List all issues  
- `GET /qa/projects/{project_id}/issues/{issue_id}` - Get issue details  
- `PUT /qa/projects/{project_id}/issues/{issue_id}` - Update issue  
- `DELETE /qa/projects/{project_id}/issues/{issue_id}` - Delete issue 

### Test Management
- `POST /qa/projects/{project_id}/test-cases` - Create test case  
- `GET /qa/projects/{project_id}/test-cases` - List test cases  
- `POST /qa/projects/{project_id}/test-runs` - Create test run  
- `GET /qa/projects/{project_id}/test-runs` - List test runs  
- `GET /qa/projects/{project_id}/test-metrics` - Get QA metrics  

### Test Run Results
- `POST /qa/projects/{project_id}/test-runs/{test_run_id}/results` - Add test result  
- `PUT /qa/projects/{project_id}/test-runs/{test_run_id}/results/{result_id}` - Update result  

## Collaboration APIs

### Document Management
- `POST /projects/{id}/documents` - Upload document
- `GET /projects/{id}/documents` - List documents
- `GET /projects/{id}/documents/{docId}` - Get document
- `DELETE /projects/{id}/documents/{docId}` - Delete document

### Comments & Discussions
- `POST /projects/{id}/tasks/{taskId}/comments` - Add comment
- `GET /projects/{id}/tasks/{taskId}/comments` - List comments
- `PUT /projects/{id}/tasks/{taskId}/comments/{commentId}` - Edit comment
- `DELETE /projects/{id}/tasks/{taskId}/comments/{commentId}` - Delete comment

## Event Publication Endpoints

### Webhooks & Events
- `POST /projects/{id}/webhooks` - Register webhook
- `GET /projects/{id}/activity` - Get project activity stream
- `GET /projects/{id}/events` - Get project events

## Reporting APIs

### Project Metrics
- `GET /projects/{id}/metrics/velocity` - Get team velocity
- `GET /projects/{id}/metrics/burndown` - Get burndown chart data
- `GET /projects/{id}/metrics/completion` - Get completion percentage
- `GET /projects/{id}/metrics/resource-utilization` - Get resource utilization
