# Devflow Project Management Service API Documentation

## Overview
The Project Management Service provides APIs to manage projects, tasks, and related functionality within the Devflow platform. This documentation covers all available endpoints, request/response formats, and authentication requirements.

## Base URL
```
/api/pm
```

## Authentication
Most endpoints require authentication via JWT token. Include the token in the request headers:

```
Authorization: Bearer <token>
```

## Error Handling
The API returns standard HTTP status codes:
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication failure
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

Error responses follow this format:
```json
{
  "success": false,
  "message": "Error description"
}
```

## Endpoints

### Projects

#### Create Project
Creates a new project.

- **URL**: `/projects`
- **Method**: `POST`
- **Auth required**: Yes
- **Request Body**:
  ```json
  {
    "name": "Project Name",
    "description": "Project Description",
    "startDate": "2023-01-01T00:00:00.000Z",
    "endDate": "2023-12-31T00:00:00.000Z",
    "teamId": "team-uuid"
  }
  ```
- **Response**: 
  ```json
  {
    "success": true,
    "data": {
      "id": "project-uuid",
      "name": "Project Name",
      "description": "Project Description",
      "startDate": "2023-01-01T00:00:00.000Z",
      "endDate": "2023-12-31T00:00:00.000Z",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z",
      "teamId": "team-uuid",
      "createdBy": "user-uuid"
    }
  }
  ```

#### Get All Projects
Retrieves all projects the authenticated user has access to.

- **URL**: `/projects`
- **Method**: `GET`
- **Auth required**: Yes
- **Query Parameters**:
  - `page` (optional): Page number for pagination (default: 1)
  - `limit` (optional): Items per page (default: 10)
  - `teamId` (optional): Filter by team ID
- **Response**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "project-uuid",
        "name": "Project Name",
        "description": "Project Description",
        "startDate": "2023-01-01T00:00:00.000Z",
        "endDate": "2023-12-31T00:00:00.000Z",
        "createdAt": "2023-01-01T00:00:00.000Z",
        "updatedAt": "2023-01-01T00:00:00.000Z",
        "teamId": "team-uuid",
        "createdBy": "user-uuid"
      }
    ],
    "pagination": {
      "totalItems": 25,
      "totalPages": 3,
      "currentPage": 1,
      "itemsPerPage": 10
    }
  }
  ```

#### Get Project by ID
Retrieves a specific project by ID.

- **URL**: `/projects/:projectId`
- **Method**: `GET`
- **Auth required**: Yes
- **Path Parameters**:
  - `projectId`: UUID of the project
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "id": "project-uuid",
      "name": "Project Name",
      "description": "Project Description",
      "startDate": "2023-01-01T00:00:00.000Z",
      "endDate": "2023-12-31T00:00:00.000Z",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z",
      "teamId": "team-uuid",
      "createdBy": "user-uuid"
    }
  }
  ```

#### Update Project
Updates an existing project.

- **URL**: `/projects/:projectId`
- **Method**: `PUT`
- **Auth required**: Yes
- **Path Parameters**:
  - `projectId`: UUID of the project
- **Request Body**:
  ```json
  {
    "name": "Updated Project Name",
    "description": "Updated Project Description",
    "startDate": "2023-01-01T00:00:00.000Z",
    "endDate": "2023-12-31T00:00:00.000Z"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "id": "project-uuid",
      "name": "Updated Project Name",
      "description": "Updated Project Description",
      "startDate": "2023-01-01T00:00:00.000Z",
      "endDate": "2023-12-31T00:00:00.000Z",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z",
      "teamId": "team-uuid",
      "createdBy": "user-uuid"
    }
  }
  ```

#### Delete Project
Deletes a project.

- **URL**: `/projects/:projectId`
- **Method**: `DELETE`
- **Auth required**: Yes
- **Path Parameters**:
  - `projectId`: UUID of the project
- **Response**:
  ```json
  {
    "success": true,
    "message": "Project deleted successfully"
  }
  ```

### Tasks

#### Create Task
Creates a new task within a project.

- **URL**: `/tasks`
- **Method**: `POST`
- **Auth required**: Yes
- **Request Body**:
  ```json
  {
    "title": "Task Title",
    "description": "Task Description",
    "projectId": "project-uuid",
    "priority": "HIGH", // HIGH, MEDIUM, LOW
    "status": "TODO", // TODO, IN_PROGRESS, COMPLETED
    "dueDate": "2023-06-30T00:00:00.000Z",
    "assigneeId": "user-uuid"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "id": "task-uuid",
      "title": "Task Title",
      "description": "Task Description",
      "projectId": "project-uuid",
      "priority": "HIGH",
      "status": "TODO",
      "dueDate": "2023-06-30T00:00:00.000Z",
      "assigneeId": "user-uuid",
      "createdBy": "user-uuid",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Get All Tasks
Retrieves all tasks based on filters.

- **URL**: `/tasks`
- **Method**: `GET`
- **Auth required**: Yes
- **Query Parameters**:
  - `projectId` (optional): Filter by project ID
  - `status` (optional): Filter by status (TODO, IN_PROGRESS, COMPLETED)
  - `priority` (optional): Filter by priority (HIGH, MEDIUM, LOW)
  - `assigneeId` (optional): Filter by assignee ID
  - `page` (optional): Page number for pagination (default: 1)
  - `limit` (optional): Items per page (default: 10)
- **Response**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "task-uuid",
        "title": "Task Title",
        "description": "Task Description",
        "projectId": "project-uuid",
        "priority": "HIGH",
        "status": "TODO",
        "dueDate": "2023-06-30T00:00:00.000Z",
        "assigneeId": "user-uuid",
        "createdBy": "user-uuid",
        "createdAt": "2023-01-01T00:00:00.000Z",
        "updatedAt": "2023-01-01T00:00:00.000Z"
      }
    ],
    "pagination": {
      "totalItems": 25,
      "totalPages": 3,
      "currentPage": 1,
      "itemsPerPage": 10
    }
  }
  ```

#### Get Task by ID
Retrieves a specific task by ID.

- **URL**: `/tasks/:taskId`
- **Method**: `GET`
- **Auth required**: Yes
- **Path Parameters**:
  - `taskId`: UUID of the task
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "id": "task-uuid",
      "title": "Task Title",
      "description": "Task Description",
      "projectId": "project-uuid",
      "priority": "HIGH",
      "status": "TODO",
      "dueDate": "2023-06-30T00:00:00.000Z",
      "assigneeId": "user-uuid",
      "createdBy": "user-uuid",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Update Task
Updates an existing task.

- **URL**: `/tasks/:taskId`
- **Method**: `PUT`
- **Auth required**: Yes
- **Path Parameters**:
  - `taskId`: UUID of the task
- **Request Body**:
  ```json
  {
    "title": "Updated Task Title",
    "description": "Updated Task Description",
    "priority": "MEDIUM",
    "status": "IN_PROGRESS",
    "dueDate": "2023-07-15T00:00:00.000Z",
    "assigneeId": "user-uuid"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "id": "task-uuid",
      "title": "Updated Task Title",
      "description": "Updated Task Description",
      "projectId": "project-uuid",
      "priority": "MEDIUM",
      "status": "IN_PROGRESS",
      "dueDate": "2023-07-15T00:00:00.000Z",
      "assigneeId": "user-uuid",
      "createdBy": "user-uuid",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Delete Task
Deletes a task.

- **URL**: `/tasks/:taskId`
- **Method**: `DELETE`
- **Auth required**: Yes
- **Path Parameters**:
  - `taskId`: UUID of the task
- **Response**:
  ```json
  {
    "success": true,
    "message": "Task deleted successfully"
  }
  ```

### Task Comments

#### Add Comment to Task
Adds a comment to a task.

- **URL**: `/tasks/:taskId/comments`
- **Method**: `POST`
- **Auth required**: Yes
- **Path Parameters**:
  - `taskId`: UUID of the task
- **Request Body**:
  ```json
  {
    "content": "This is a comment on the task"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "id": "comment-uuid",
      "content": "This is a comment on the task",
      "taskId": "task-uuid",
      "createdBy": "user-uuid",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Get Task Comments
Retrieves all comments for a specific task.

- **URL**: `/tasks/:taskId/comments`
- **Method**: `GET`
- **Auth required**: Yes
- **Path Parameters**:
  - `taskId`: UUID of the task
- **Response**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "comment-uuid",
        "content": "This is a comment on the task",
        "taskId": "task-uuid",
        "createdBy": "user-uuid",
        "createdAt": "2023-01-01T00:00:00.000Z",
        "updatedAt": "2023-01-01T00:00:00.000Z"
      }
    ]
  }
  ```

#### Update Comment
Updates an existing comment.

- **URL**: `/comments/:commentId`
- **Method**: `PUT`
- **Auth required**: Yes
- **Path Parameters**:
  - `commentId`: UUID of the comment
- **Request Body**:
  ```json
  {
    "content": "Updated comment content"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "id": "comment-uuid",
      "content": "Updated comment content",
      "taskId": "task-uuid",
      "createdBy": "user-uuid",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Delete Comment
Deletes a comment.

- **URL**: `/comments/:commentId`
- **Method**: `DELETE`
- **Auth required**: Yes
- **Path Parameters**:
  - `commentId`: UUID of the comment
- **Response**:
  ```json
  {
    "success": true,
    "message": "Comment deleted successfully"
  }
  ```

### Project Members

#### Add Member to Project
Adds a user as a member to a project.

- **URL**: `/projects/:projectId/members`
- **Method**: `POST`
- **Auth required**: Yes
- **Path Parameters**:
  - `projectId`: UUID of the project
- **Request Body**:
  ```json
  {
    "userId": "user-uuid",
    "role": "MEMBER" // ADMIN, MEMBER
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "id": "membership-uuid",
      "projectId": "project-uuid",
      "userId": "user-uuid",
      "role": "MEMBER",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Get Project Members
Retrieves all members of a project.

- **URL**: `/projects/:projectId/members`
- **Method**: `GET`
- **Auth required**: Yes
- **Path Parameters**:
  - `projectId`: UUID of the project
- **Response**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "membership-uuid",
        "projectId": "project-uuid",
        "userId": "user-uuid",
        "role": "MEMBER",
        "user": {
          "id": "user-uuid",
          "name": "User Name",
          "email": "user@example.com"
        },
        "createdAt": "2023-01-01T00:00:00.000Z",
        "updatedAt": "2023-01-01T00:00:00.000Z"
      }
    ]
  }
  ```

#### Update Project Member Role
Updates a member's role in a project.

- **URL**: `/projects/:projectId/members/:userId`
- **Method**: `PUT`
- **Auth required**: Yes
- **Path Parameters**:
  - `projectId`: UUID of the project
  - `userId`: UUID of the user
- **Request Body**:
  ```json
  {
    "role": "ADMIN" // ADMIN, MEMBER
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "id": "membership-uuid",
      "projectId": "project-uuid",
      "userId": "user-uuid",
      "role": "ADMIN",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Remove Member from Project
Removes a user from a project.

- **URL**: `/projects/:projectId/members/:userId`
- **Method**: `DELETE`
- **Auth required**: Yes
- **Path Parameters**:
  - `projectId`: UUID of the project
  - `userId`: UUID of the user
- **Response**:
  ```json
  {
    "success": true,
    "message": "Member removed from project successfully"
  }
  ```

### Project Statistics

#### Get Project Statistics
Retrieves statistics for a specific project.

- **URL**: `/projects/:projectId/statistics`
- **Method**: `GET`
- **Auth required**: Yes
- **Path Parameters**:
  - `projectId`: UUID of the project
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "totalTasks": 25,
      "completedTasks": 10,
      "inProgressTasks": 8,
      "todoTasks": 7,
      "tasksByPriority": {
        "HIGH": 5,
        "MEDIUM": 12,
        "LOW": 8
      },
      "taskCompletionRate": 40, // percentage
      "recentActivity": [
        {
          "type": "TASK_CREATED",
          "taskId": "task-uuid",
          "userId": "user-uuid",
          "timestamp": "2023-01-01T00:00:00.000Z"
        }
      ]
    }
  }
  ```

### User Dashboard

#### Get User Dashboard
Retrieves dashboard information for the authenticated user.

- **URL**: `/dashboard`
- **Method**: `GET`
- **Auth required**: Yes
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "assignedTasks": {
        "total": 15,
        "completed": 5,
        "inProgress": 7,
        "todo": 3,
        "overdue": 2
      },
      "projects": [
        {
          "id": "project-uuid",
          "name": "Project Name",
          "progress": 65, // percentage
          "role": "MEMBER"
        }
      ],
      "recentActivity": [
        {
          "type": "COMMENT_ADDED",
          "taskId": "task-uuid",
          "projectId": "project-uuid",
          "timestamp": "2023-01-01T00:00:00.000Z"
        }
      ],
      "upcomingDeadlines": [
        {
          "taskId": "task-uuid",
          "title": "Task Title",
          "dueDate": "2023-01-10T00:00:00.000Z",
          "projectId": "project-uuid",
          "projectName": "Project Name"
        }
      ]
    }
  }
  ```

## Webhooks

The PM service supports webhooks for event notifications.

#### Register Webhook
Registers a new webhook for receiving notifications.

- **URL**: `/webhooks`
- **Method**: `POST`
- **Auth required**: Yes
- **Request Body**:
  ```json
  {
    "url": "https://example.com/webhook",
    "events": ["PROJECT_CREATED", "TASK_UPDATED", "COMMENT_ADDED"],
    "projectId": "project-uuid" // Optional, if not provided, subscribes to all projects
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "id": "webhook-uuid",
      "url": "https://example.com/webhook",
      "events": ["PROJECT_CREATED", "TASK_UPDATED", "COMMENT_ADDED"],
      "projectId": "project-uuid",
      "createdBy": "user-uuid",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Get Webhooks
Retrieves all webhooks registered by the authenticated user.

- **URL**: `/webhooks`
- **Method**: `GET`
- **Auth required**: Yes
- **Response**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "webhook-uuid",
        "url": "https://example.com/webhook",
        "events": ["PROJECT_CREATED", "TASK_UPDATED", "COMMENT_ADDED"],
        "projectId": "project-uuid",
        "createdBy": "user-uuid",
        "createdAt": "2023-01-01T00:00:00.000Z",
        "updatedAt": "2023-01-01T00:00:00.000Z"
      }
    ]
  }
  ```

#### Delete Webhook
Deletes a webhook.

- **URL**: `/webhooks/:webhookId`
- **Method**: `DELETE`
- **Auth required**: Yes
- **Path Parameters**:
  - `webhookId`: UUID of the webhook
- **Response**:
  ```json
  {
    "success": true,
    "message": "Webhook deleted successfully"
  }
  ```

## Rate Limiting

The API implements rate limiting to prevent abuse. When a rate limit is exceeded, the API returns a 429 Too Many Requests response.
