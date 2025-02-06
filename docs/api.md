# API Documentation

## Overview

The Juryim API provides programmatic access to platform functionality. This document covers authentication, endpoints, and common operations.

## Authentication

### JWT Authentication
All API requests require a JWT token in the Authorization header:

### Obtaining Tokens
```bash
Authorization: Bearer <your_token>
```

## API Endpoints

### 1. Financial API

#### List Accounts
```http
GET /api/v1/financial/accounts/
```

Response:
```json
{
    "count": 100,
    "next": "/api/v1/financial/accounts/?page=2",
    "results": [
        {
            "id": 1,
            "user": "username",
            "balance": "100.00",
            "frozen_balance": "0.00",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

#### Withdrawal Operations
```http
GET /api/v1/financial/withdrawals/
POST /api/v1/financial/withdrawals/{id}/approve/
POST /api/v1/financial/withdrawals/{id}/reject/
```

### 2. Task API

#### List Tasks
```http
GET /api/v1/tasks/
```

#### Create Task
```http
POST /api/v1/tasks/
Content-Type: application/json

{
    "title": "Task Title",
    "description": "Task Description",
    "reward": "10.00",
    "deadline": "2024-02-01T00:00:00Z"
}
```

### 3. Group API

#### List Groups
```http
GET /api/v1/groups/
```

#### Create Group
```http
POST /api/v1/groups/
Content-Type: application/json

{
    "name": "Group Name",
    "description": "Group Description"
}
```

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://juryim.com/ws/management/');
```

### Subscribe to Updates
```javascript
ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'withdrawals'
}));
```

### Message Types
1. Withdrawal Updates
```json
{
    "type": "withdrawal_update",
    "data": {
        "id": 1,
        "status": "approved",
        "timestamp": "2024-01-01T00:00:00Z"
    }
}
```

2. Task Updates
```json
{
    "type": "task_update",
    "data": {
        "id": 1,
        "status": "completed",
        "timestamp": "2024-01-01T00:00:00Z"
    }
}
```

## Rate Limits

- Authentication endpoints: 5 requests per minute
- General API endpoints: 60 requests per minute
- WebSocket connections: 1 connection per user

## Error Handling

### Common Error Codes
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests

### Error Response Format
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {}
    }
}
```

## Support

For API support:
- Email: api-support@juryim.com
- API Status: status.juryim.com
- Documentation: docs.juryim.com