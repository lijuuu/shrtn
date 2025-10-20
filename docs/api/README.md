# API Documentation

## Overview
Complete API documentation for the Hirethon Django Template - a comprehensive URL shortening service with organization management, analytics, and more.

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Module Documentation

### 1. [Users API](./users.md)
User management, authentication, and profile operations.
- User registration and login
- Profile management
- Google OAuth integration
- Password management

### 2. [Organizations API](./organizations.md)
Organization management, member administration, and invitations.
- Organization CRUD operations
- Member management
- Invitation system
- Role-based permissions

### 3. [Namespaces API](./namespaces.md)
Namespace management for organizing URLs.
- Namespace CRUD operations
- Availability checking
- Permission management

### 4. [URLs API](./urls.md)
URL shortening, management, and bulk operations.
- URL CRUD operations
- Bulk URL creation
- Excel upload/download
- URL resolution
- **Pagination support**

### 5. [Analytics API](./analytics.md)
Comprehensive analytics and reporting.
- URL analytics
- Namespace analytics
- Real-time statistics
- Geographic analytics
- Tier analytics

## Health Endpoints

### Basic Health Check
**GET** `/health/`
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Detailed Health Check
**GET** `/health/detailed/`
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "scylla": "healthy",
    "s3": "healthy"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Readiness Check
**GET** `/health/ready/`
Returns 200 if the service is ready to accept requests.

### Liveness Check
**GET** `/health/live/`
Returns 200 if the service is alive.

## Common Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "payload": {
    // Response data
  },
  "meta": {
    // Metadata (pagination, filters, etc.)
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "errors": [
    "Detailed error messages"
  ],
  "status_code": 400
}
```

## Pagination

Most list endpoints support pagination with the following parameters:
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)
- `search` (string): Search query
- `sort` (string): Sort field
- `order` (string): Sort order (asc, desc)

### Pagination Response
```json
{
  "meta": {
    "pagination": {
      "count": 100,
      "page": 1,
      "limit": 20,
      "total_pages": 5,
      "has_next": true,
      "has_previous": false,
      "next_page": 2,
      "previous_page": null
    }
  }
}
```

## Rate Limiting

- **Authentication endpoints**: 5 requests/minute per IP
- **User management**: 100 requests/hour per user
- **Organization management**: 50 requests/hour per user
- **URL operations**: 100 requests/hour per user
- **Analytics**: 100 requests/hour per user
- **Bulk operations**: 10 requests/hour per user

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `410` - Gone (expired URLs)
- `500` - Internal Server Error

## Data Types

### UUIDs
All IDs are UUIDs in string format:
```
"550e8400-e29b-41d4-a716-446655440000"
```

### Timestamps
All timestamps are in ISO 8601 format (UTC):
```
"2024-01-01T00:00:00Z"
```

### URLs
- Original URLs must be valid HTTP/HTTPS URLs
- Short URLs follow the pattern: `https://short.ly/{namespace}/{shortcode}`
- Shortcodes are 3-20 characters, alphanumeric with hyphens/underscores

## Testing

### Run Tests
```bash
pytest tests/ -v
```

### Generate Test Data
```bash
python manage.py generate_bulk_data --users 100 --organizations 50 --namespaces 100 --urls 200 --clicks 500
```

## Environment Setup

### Required Environment Variables
```bash
DATABASE_URL=postgres://user:password@localhost:5433/shrtn
CELERY_BROKER_URL=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=us-east-1
```

### Start Services
```bash
docker-compose -f local.yml up postgres redis scylla -d
```

## Support

For questions or issues:
- Check the interactive documentation at `/api/docs/`
- Review the module-specific documentation
- Run the test suite to verify functionality
