# Management API Documentation

## Authentication
All API endpoints require authentication using JWT tokens.

### Obtaining a Token 

## Endpoints

### Withdrawal Management

#### List Withdrawals 

Parameters:
- `status` - Filter by status (pending, approved, rejected)
- `from_date` - Filter by date range start
- `to_date` - Filter by date range end

Response: 

#### Get Withdrawal Status

#### Approve Withdrawal

Common Error Codes:
- `AUTH_REQUIRED`: Authentication required
- `INVALID_TOKEN`: Invalid or expired token
- `PERMISSION_DENIED`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `VALIDATION_ERROR`: Invalid input data

## Rate Limits

- Authentication: 5 requests per minute
- API endpoints: 60 requests per minute per user
- WebSocket: 1 connection per user

## Support

For API support:
- Email: api-support@juryim.com
- Status page: status.juryim.com
- Developer forum: forum.juryim.com