# Namespaces API Documentation

## Overview
Namespace management endpoints for organizing URLs into folders within organizations.

## Base URL
```
/api/v1/
```

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## Endpoints

### 1. List Namespaces
**GET** `/api/v1/organizations/{org_id}/namespaces/`

List all namespaces in an organization.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID

**Query Parameters:**
- `page` (integer, optional) - Page number (default: 1)
- `limit` (integer, optional) - Items per page (default: 20)
- `search` (string, optional) - Search by namespace name

**Response:**
```json
{
  "success": true,
  "payload": [
    {
      "id": "uuid",
      "name": "namespace-name",
      "description": "Namespace description",
      "organization": {
        "id": "uuid",
        "name": "Organization Name"
      },
      "created_by": {
        "id": "uuid",
        "name": "Creator Name",
        "email": "creator@example.com"
      },
      "created_at": "2024-01-01T00:00:00Z",
      "url_count": 25,
      "is_active": true
    }
  ],
  "meta": {
    "count": 10,
    "page": 1,
    "total_pages": 1
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `403` - Access denied
- `404` - Organization not found

---

### 2. Create Namespace
**POST** `/api/v1/organizations/{org_id}/namespaces/create/`

Create a new namespace in an organization.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID

**Request Body:**
```json
{
  "name": "new-namespace",
  "description": "Namespace description"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "name": "new-namespace",
    "description": "Namespace description",
    "organization": {
      "id": "uuid",
      "name": "Organization Name"
    },
    "created_by": {
      "id": "uuid",
      "name": "Creator Name",
      "email": "creator@example.com"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "url_count": 0,
    "is_active": true
  }
}
```

**Status Codes:**
- `201` - Created
- `400` - Bad Request (validation errors)
- `403` - Insufficient permissions
- `409` - Namespace name already exists

---

### 3. Get Namespace
**GET** `/api/v1/namespaces/{namespace}/`

Get namespace details by name.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `namespace` (string, required) - Namespace name

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "name": "namespace-name",
    "description": "Namespace description",
    "organization": {
      "id": "uuid",
      "name": "Organization Name"
    },
    "created_by": {
      "id": "uuid",
      "name": "Creator Name",
      "email": "creator@example.com"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "url_count": 25,
    "is_active": true,
    "permissions": {
      "can_view": true,
      "can_update": true,
      "can_delete": true,
      "can_create_urls": true
    }
  }
}
```

**Status Codes:**
- `200` - Success
- `404` - Namespace not found
- `403` - Access denied

---

### 4. Update Namespace
**PUT** `/api/v1/organizations/{org_id}/namespaces/{namespace}/update/`

Update namespace details.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID
- `namespace` (string, required) - Namespace name

**Request Body:**
```json
{
  "description": "Updated namespace description"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "name": "namespace-name",
    "description": "Updated namespace description",
    "organization": {
      "id": "uuid",
      "name": "Organization Name"
    },
    "created_by": {
      "id": "uuid",
      "name": "Creator Name",
      "email": "creator@example.com"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "url_count": 25,
    "is_active": true
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request
- `403` - Insufficient permissions
- `404` - Namespace not found

---

### 5. Delete Namespace
**DELETE** `/api/v1/organizations/{org_id}/namespaces/{namespace}/delete/`

Delete a namespace and all its URLs.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID
- `namespace` (string, required) - Namespace name

**Request Body:**
```json
{
  "confirm": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Namespace and all associated URLs deleted successfully",
  "payload": {
    "deleted_urls": 25,
    "deleted_at": "2024-01-01T12:00:00Z"
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request (confirmation required)
- `403` - Insufficient permissions
- `404` - Namespace not found

---

### 6. Check Namespace Availability
**GET** `/api/v1/namespaces/check/{namespace}/`

Check if a namespace name is available.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `namespace` (string, required) - Namespace name to check

**Response:**
```json
{
  "success": true,
  "payload": {
    "namespace": "proposed-namespace",
    "available": true,
    "suggestions": [
      "proposed-namespace-1",
      "proposed-namespace-2"
    ]
  }
}
```

**Response (if not available):**
```json
{
  "success": true,
  "payload": {
    "namespace": "taken-namespace",
    "available": false,
    "suggestions": [
      "taken-namespace-1",
      "taken-namespace-2",
      "my-taken-namespace"
    ]
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid namespace name)

---

## Namespace Validation Rules

### Namespace Name Requirements:
- Must be 3-50 characters long
- Can contain lowercase letters, numbers, and hyphens
- Must start and end with a letter or number
- Cannot contain consecutive hyphens
- Cannot start or end with a hyphen
- Must be unique within the organization

### Valid Examples:
- `my-namespace`
- `project-2024`
- `api-v1`
- `user-dashboard`

### Invalid Examples:
- `My-Namespace` (uppercase not allowed)
- `my_namespace` (underscores not allowed)
- `-my-namespace` (cannot start with hyphen)
- `my-namespace-` (cannot end with hyphen)
- `my--namespace` (consecutive hyphens not allowed)
- `a` (too short)
- `very-long-namespace-name-that-exceeds-fifty-characters` (too long)

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Validation error",
  "errors": [
    "Namespace name must be 3-50 characters long",
    "Namespace name can only contain lowercase letters, numbers, and hyphens",
    "Namespace name cannot start or end with a hyphen"
  ]
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "message": "Authentication required",
  "status_code": 401
}
```

### 403 Forbidden
```json
{
  "success": false,
  "message": "Insufficient permissions",
  "status_code": 403
}
```

### 404 Not Found
```json
{
  "success": false,
  "message": "Namespace not found",
  "status_code": 404
}
```

### 409 Conflict
```json
{
  "success": false,
  "message": "Namespace name already exists",
  "status_code": 409
}
```

---

## Permissions

### Namespace Permissions:
- **can_view**: View namespace and its URLs
- **can_update**: Update namespace details
- **can_delete**: Delete namespace and all URLs
- **can_create_urls**: Create new URLs in the namespace

### Role-based Access:
- **Organization Admin**: All permissions
- **Organization Member**: Can view and create URLs
- **Namespace Creator**: All permissions for their namespaces

---

## Rate Limiting

- Namespace creation: 10 requests per hour per user
- Namespace updates: 50 requests per hour per user
- Namespace deletion: 5 requests per hour per user
- Availability checks: 100 requests per hour per user

---

## Notes

- Namespace names are case-sensitive
- Namespace names are unique within an organization
- Deleting a namespace permanently removes all associated URLs
- Namespace names cannot be changed after creation
- All timestamps are in ISO 8601 format (UTC)
- Namespace IDs are UUIDs
