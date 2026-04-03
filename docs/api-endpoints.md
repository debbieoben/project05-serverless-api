# API Endpoints Documentation

## Base URL

```
https://[api-id].execute-api.us-east-1.amazonaws.com/dev
```

## Endpoints

### 1. Create Task

**Method:** `POST`  
**Path:** `/tasks`  
**Lambda:** CreateTask  

**Request Body:**
```json
{
  "userId": "string (required)",
  "title": "string (required)",
  "description": "string (optional)",
  "status": "string (optional: pending, in-progress, completed)",
  "priority": "string (optional: low, medium, high)",
  "dueDate": "number (optional: Unix timestamp)"
}
```

**Response (201 Created):**
```json
{
  "message": "Task created successfully",
  "task": {
    "taskId": "uuid",
    "userId": "alice",
    "title": "Deploy API",
    "description": "Deploy to production",
    "status": "pending",
    "priority": "high",
    "dueDate": 0,
    "createdAt": 1712160000,
    "updatedAt": 1712160000
  }
}
```

**Additional Behavior:**
- Sends SNS email notification
- Generates UUID for taskId
- Sets timestamps automatically

---

### 2. Get Task

**Method:** `GET`  
**Path:** `/tasks/{id}`  
**Lambda:** GetTask  

**Path Parameters:**
- `id` - Task UUID

**Response (200 OK):**
```json
{
  "task": {
    "taskId": "uuid",
    "userId": "alice",
    "title": "Deploy API",
    ...
  }
}
```

**Response (404 Not Found):**
```json
{
  "error": "Task not found"
}
```

---

### 3. List Tasks

**Method:** `GET`  
**Path:** `/tasks`  
**Lambda:** ListTasks  

**Query Parameters:**
- `limit` - Number of tasks to return (optional, default: 20)

**Example:** `GET /tasks?limit=10`

**Response (200 OK):**
```json
{
  "tasks": [
    {
      "taskId": "uuid1",
      "userId": "alice",
      "title": "Task 1",
      ...
    },
    {
      "taskId": "uuid2",
      "userId": "bob",
      "title": "Task 2",
      ...
    }
  ],
  "count": 2
}
```

---

### 4. Update Task

**Method:** `PUT`  
**Path:** `/tasks/{id}`  
**Lambda:** UpdateTask  

**Path Parameters:**
- `id` - Task UUID

**Request Body (all fields optional):**
```json
{
  "title": "string",
  "description": "string",
  "status": "string",
  "priority": "string"
}
```

**Response (200 OK):**
```json
{
  "message": "Task updated successfully",
  "task": {
    "taskId": "uuid",
    "userId": "alice",
    "title": "Updated Title",
    "updatedAt": 1712163600,
    ...
  }
}
```

**Response (404 Not Found):**
```json
{
  "error": "Task not found"
}
```

---

### 5. Delete Task

**Method:** `DELETE`  
**Path:** `/tasks/{id}`  
**Lambda:** DeleteTask  

**Path Parameters:**
- `id` - Task UUID

**Response (200 OK):**
```json
{
  "message": "Task deleted successfully"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Task not found"
}
```

---

## Common Response Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST |
| 400 | Bad Request | Missing required fields or invalid input |
| 404 | Not Found | Task ID doesn't exist |
| 500 | Internal Server Error | Lambda exception or DynamoDB error |

---

## CORS

All endpoints include CORS headers:
```
Access-Control-Allow-Origin: *
```

OPTIONS methods are auto-configured by API Gateway for preflight requests.

---

## Authentication

Currently using API Key (optional). For production:
- Implement Amazon Cognito authorizer
- Use custom Lambda authorizer
- Add request validation schemas

---

## Rate Limiting

Configured via API Gateway Usage Plans:
- Rate: 100 requests/second
- Burst: 200 requests
- Quota: 10,000 requests/month

---

## Error Format

All errors return JSON with `error` field:
```json
{
  "error": "Description of what went wrong"
}
```
