# DynamoDB Schema - TaskManagementAPI

## Table Configuration

**Table Name:** TaskManagementAPI  
**Billing Mode:** On-Demand  
**Region:** us-east-1  

## Primary Key

- **Partition Key:** `taskId` (String) - UUID format
- **Sort Key:** `createdAt` (Number) - Unix timestamp

## Global Secondary Index (GSI)

**Index Name:** userId-createdAt-index

- **Partition Key:** `userId` (String)
- **Sort Key:** `createdAt` (Number)
- **Projection:** ALL

**Purpose:** Query all tasks for a specific user, sorted by creation time

## Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| taskId | String | Yes | Unique identifier (UUID) |
| createdAt | Number | Yes | Creation timestamp (Unix) |
| userId | String | Yes | Task owner/assignee |
| title | String | Yes | Task title |
| description | String | No | Task details (default: "") |
| status | String | No | Task status: pending, in-progress, completed (default: "pending") |
| priority | String | No | Task priority: low, medium, high (default: "medium") |
| dueDate | Number | No | Due date timestamp (default: 0) |
| updatedAt | Number | Yes | Last update timestamp |

## Access Patterns

1. **Get task by ID:** Query using taskId (primary key)
2. **List all tasks:** Scan table with optional limit
3. **Get user's tasks:** Query GSI with userId
4. **Get user's recent tasks:** Query GSI with userId and createdAt range

## Example Item

```json
{
  "taskId": "550e8400-e29b-41d4-a716-446655440000",
  "createdAt": 1712160000,
  "userId": "alice",
  "title": "Complete serverless project",
  "description": "Build REST API with Lambda and DynamoDB",
  "status": "in-progress",
  "priority": "high",
  "dueDate": 1712246400,
  "updatedAt": 1712163600
}
```

## Streams

**Status:** Enabled  
**View Type:** New and old images  
**Purpose:** Trigger downstream processing or auditing

## Cost Considerations

- On-demand capacity auto-scales with traffic
- GSI doubles write costs (writes to both table and index)
- Consider provisioned capacity for predictable workloads
