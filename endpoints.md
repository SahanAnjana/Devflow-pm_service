# Projects Service APIs

Here's a comprehensive breakdown of the APIs needed for your Projects Service, organized by functional areas:

## Project Management APIs

### Project Core Operations
- `POST /api/projects` - Create a new project
- `GET /api/projects` - List all projects (with pagination and filtering)
- `GET /api/projects/{id}` - Get project details by ID
- `PUT /api/projects/{id}` - Update project details
- `DELETE /api/projects/{id}` - Delete a project

### Project Configuration
- `GET /api/projects/{id}/settings` - Get project settings
- `PUT /api/projects/{id}/settings` - Update project settings
- `POST /api/projects/{id}/members` - Add team members to project
- `DELETE /api/projects/{id}/members/{userId}` - Remove a team member
- `PUT /api/projects/{id}/members/{userId}/role` - Update member role in project

## Task Management APIs

### Task Operations
- `POST /api/projects/{id}/tasks` - Create a new task
- `GET /api/projects/{id}/tasks` - List all tasks in a project
- `GET /api/projects/{id}/tasks/{taskId}` - Get task details
- `PUT /api/projects/{id}/tasks/{taskId}` - Update task details
- `DELETE /api/projects/{id}/tasks/{taskId}` - Delete a task
- `PUT /api/projects/{id}/tasks/{taskId}/status` - Update task status
- `PUT /api/projects/{id}/tasks/{taskId}/assignee` - Assign task to team member

### Kanban Board
- `GET /api/projects/{id}/board` - Get Kanban board configuration
- `PUT /api/projects/{id}/board` - Update board configuration
- `POST /api/projects/{id}/board/columns` - Add a new column
- `PUT /api/projects/{id}/board/columns/{columnId}` - Update column
- `PUT /api/projects/{id}/tasks/{taskId}/position` - Reorder/move task

### Gantt Chart
- `GET /api/projects/{id}/gantt` - Get Gantt chart data
- `PUT /api/projects/{id}/tasks/{taskId}/schedule` - Update task schedule
- `GET /api/projects/{id}/critical-path` - Calculate critical path

## Resource Management APIs

### Resource Allocation
- `GET /api/resources` - List available resources
- `GET /api/projects/{id}/resources` - Get resources allocated to project
- `POST /api/projects/{id}/resources` - Allocate resources to project
- `DELETE /api/projects/{id}/resources/{resourceId}` - Remove resource
- `GET /api/resources/{resourceId}/availability` - Check resource availability
- `GET /api/resources/utilization` - Get resource utilization metrics

## Quality Assurance APIs

### Issue Tracking
- `POST /api/projects/{id}/issues` - Create a new issue/bug
- `GET /api/projects/{id}/issues` - List all issues
- `GET /api/projects/{id}/issues/{issueId}` - Get issue details
- `PUT /api/projects/{id}/issues/{issueId}` - Update issue
- `PUT /api/projects/{id}/issues/{issueId}/status` - Update issue status

### Test Management
- `POST /api/projects/{id}/test-cases` - Create test case
- `GET /api/projects/{id}/test-cases` - List test cases
- `POST /api/projects/{id}/test-runs` - Create test run
- `GET /api/projects/{id}/test-metrics` - Get QA metrics

## Collaboration APIs

### Document Management
- `POST /api/projects/{id}/documents` - Upload document
- `GET /api/projects/{id}/documents` - List documents
- `GET /api/projects/{id}/documents/{docId}` - Get document
- `DELETE /api/projects/{id}/documents/{docId}` - Delete document

### Comments & Discussions
- `POST /api/projects/{id}/tasks/{taskId}/comments` - Add comment
- `GET /api/projects/{id}/tasks/{taskId}/comments` - List comments
- `PUT /api/projects/{id}/tasks/{taskId}/comments/{commentId}` - Edit comment
- `DELETE /api/projects/{id}/tasks/{taskId}/comments/{commentId}` - Delete comment

## Event Publication Endpoints

### Webhooks & Events
- `POST /api/projects/{id}/webhooks` - Register webhook
- `GET /api/projects/{id}/activity` - Get project activity stream
- `GET /api/projects/{id}/events` - Get project events

## Reporting APIs

### Project Metrics
- `GET /api/projects/{id}/metrics/velocity` - Get team velocity
- `GET /api/projects/{id}/metrics/burndown` - Get burndown chart data
- `GET /api/projects/{id}/metrics/completion` - Get completion percentage
- `GET /api/projects/{id}/metrics/resource-utilization` - Get resource utilization
