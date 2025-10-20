# URLs API Documentation

## Overview
URL management endpoints for creating, managing short URLs, bulk operations, and URL resolution.

## Base URL
```
/api/v1/
```

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## Endpoints

### 1. List URLs
**GET** `/api/v1/organizations/{org_id}/namespaces/{namespace}/urls/`

List all URLs in a namespace.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID
- `namespace` (string, required) - Namespace name

**Query Parameters:**
- `page` (integer, optional) - Page number (default: 1, minimum: 1)
- `limit` (integer, optional) - Items per page (default: 20, maximum: 100)
- `search` (string, optional) - Search by shortcode or original URL
- `status` (string, optional) - Filter by status (active, inactive, expired)
- `sort` (string, optional) - Sort by field (created_at, click_count, shortcode) (default: created_at)
- `order` (string, optional) - Sort order (asc, desc) (default: desc)

**Response:**
```json
{
  "success": true,
  "payload": [
    {
      "id": "uuid",
      "shortcode": "abc123",
      "original_url": "https://www.example.com",
      "short_url": "https://short.ly/namespace/abc123",
      "title": "Example Website",
      "description": "A sample website",
      "tags": ["example", "demo"],
      "click_count": 42,
      "is_active": true,
      "is_private": false,
      "expiry": "2024-12-31T23:59:59Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "meta": {
    "namespace": "namespace-name",
    "namespace_id": "uuid",
    "pagination": {
      "count": 25,
      "page": 1,
      "limit": 20,
      "total_pages": 2,
      "has_next": true,
      "has_previous": false,
      "next_page": 2,
      "previous_page": null
    },
    "filters": {
      "search": "",
      "status": "",
      "sort": "created_at",
      "order": "desc"
    }
  }
}
```

---

### 2. Create URL
**POST** `/api/v1/organizations/{org_id}/namespaces/{namespace}/urls/create/`

Create a new short URL.

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
  "original_url": "https://www.example.com",
  "shortcode": "abc123",
  "title": "Example Website",
  "description": "A sample website",
  "tags": ["example", "demo"],
  "is_private": false,
  "expiry": "2024-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "shortcode": "abc123",
    "original_url": "https://www.example.com",
    "short_url": "https://short.ly/namespace/abc123",
    "title": "Example Website",
    "description": "A sample website",
    "tags": ["example", "demo"],
    "click_count": 0,
    "is_active": true,
    "is_private": false,
    "expiry": "2024-12-31T23:59:59Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Status Codes:**
- `201` - Created
- `400` - Bad Request (validation errors)
- `403` - Insufficient permissions
- `409` - Shortcode already exists

---

### 3. Get URL
**GET** `/api/v1/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/`

Get URL details by shortcode.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID
- `namespace` (string, required) - Namespace name
- `shortcode` (string, required) - URL shortcode

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "shortcode": "abc123",
    "original_url": "https://www.example.com",
    "short_url": "https://short.ly/namespace/abc123",
    "title": "Example Website",
    "description": "A sample website",
    "tags": ["example", "demo"],
    "click_count": 42,
    "is_active": true,
    "is_private": false,
    "expiry": "2024-12-31T23:59:59Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

---

### 4. Update URL
**PUT** `/api/v1/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/update/`

Update URL details.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID
- `namespace` (string, required) - Namespace name
- `shortcode` (string, required) - URL shortcode

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "tags": ["updated", "tags"],
  "is_private": true,
  "expiry": "2025-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "shortcode": "abc123",
    "original_url": "https://www.example.com",
    "short_url": "https://short.ly/namespace/abc123",
    "title": "Updated Title",
    "description": "Updated description",
    "tags": ["updated", "tags"],
    "click_count": 42,
    "is_active": true,
    "is_private": true,
    "expiry": "2025-12-31T23:59:59Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T15:00:00Z"
  }
}
```

---

### 5. Delete URL
**DELETE** `/api/v1/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/delete/`

Delete a short URL.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID
- `namespace` (string, required) - Namespace name
- `shortcode` (string, required) - URL shortcode

**Response:**
```json
{
  "success": true,
  "message": "URL deleted successfully"
}
```

---

## Bulk Operations

### 6. Bulk Create URLs
**POST** `/api/v1/organizations/{org_id}/namespaces/{namespace}/urls/bulk/`

Create multiple URLs at once.

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
  "urls": [
    {
      "original_url": "https://www.example1.com",
      "shortcode": "ex1",
      "title": "Example 1"
    },
    {
      "original_url": "https://www.example2.com",
      "shortcode": "ex2",
      "title": "Example 2"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "created": 2,
    "failed": 0,
    "results": [
      {
        "shortcode": "ex1",
        "short_url": "https://short.ly/namespace/ex1",
        "status": "created"
      },
      {
        "shortcode": "ex2",
        "short_url": "https://short.ly/namespace/ex2",
        "status": "created"
      }
    ]
  }
}
```

---

### 7. Bulk Upload Excel
**POST** `/api/v1/organizations/{org_id}/namespaces/{namespace}/urls/bulk/excel/`

Upload URLs from an Excel file.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID
- `namespace` (string, required) - Namespace name

**Request Body:**
```
excel_file: [Excel file]
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "processed_count": 10,
    "error_count": 2,
    "results": [
      {
        "shortcode": "url1",
        "short_url": "https://short.ly/namespace/url1",
        "status": "created"
      }
    ],
    "total_results": 10,
    "download_url": "https://s3.amazonaws.com/bucket/results.xlsx"
  },
  "meta": {
    "namespace": "namespace",
    "namespace_id": "uuid"
  }
}
```

---

### 8. Get Excel Template
**GET** `/api/v1/organizations/{org_id}/namespaces/{namespace}/urls/template/`

Download Excel template for bulk URL upload.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID
- `namespace` (string, required) - Namespace name

**Response:**
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
[Excel file content]
```

---

## URL Resolution

### 9. Resolve URL (API)
**GET** `/api/v1/urls/resolve/{namespace}/{shortcode}/`

Resolve a short URL to its original URL (API endpoint).

**Path Parameters:**
- `namespace` (string, required) - Namespace name
- `shortcode` (string, required) - URL shortcode

**Response:**
```json
{
  "success": true,
  "payload": {
    "original_url": "https://www.example.com",
    "title": "Example Website",
    "click_count": 42
  }
}
```

**Status Codes:**
- `200` - Success
- `404` - URL not found
- `410` - URL expired
- `403` - URL is private

---

### 10. Resolve URL (Redirect)
**GET** `/{namespace}/{shortcode}/`

Redirect to the original URL (public endpoint).

**Path Parameters:**
- `namespace` (string, required) - Namespace name
- `shortcode` (string, required) - URL shortcode

**Response:**
```
302 Redirect to original URL
```

**Status Codes:**
- `302` - Redirect to original URL
- `404` - URL not found
- `410` - URL expired
- `403` - URL is private

---

## Public Analytics

### 11. Get Public Analytics
**GET** `/api/v1/urls/{namespace}/{shortcode}/stats/`

Get public analytics for a URL (no authentication required).

**Path Parameters:**
- `namespace` (string, required) - Namespace name
- `shortcode` (string, required) - URL shortcode

**Response:**
```json
{
  "success": true,
  "payload": {
    "shortcode": "abc123",
    "click_count": 42,
    "last_clicked": "2024-01-01T12:00:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## URL Validation Rules

### Shortcode Requirements:
- Must be 3-20 characters long
- Can contain letters, numbers, hyphens, and underscores
- Must be unique within the namespace
- Cannot start or end with a hyphen or underscore

### URL Requirements:
- Must be a valid HTTP or HTTPS URL
- Must be accessible (not return 404)
- Cannot be a localhost URL (except in development)

### Valid Examples:
- `abc123`
- `my-link`
- `project_2024`
- `api-v1`

### Invalid Examples:
- `ab` (too short)
- `-abc123` (cannot start with hyphen)
- `abc123-` (cannot end with hyphen)
- `very-long-shortcode-name` (too long)

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Validation error",
  "errors": [
    "Shortcode must be 3-20 characters long",
    "URL must be a valid HTTP or HTTPS URL"
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
  "message": "URL not found",
  "status_code": 404
}
```

### 409 Conflict
```json
{
  "success": false,
  "message": "Shortcode already exists",
  "status_code": 409
}
```

---

## Rate Limiting

- URL creation: 100 requests per hour per user
- URL updates: 200 requests per hour per user
- URL deletion: 50 requests per hour per user
- Bulk operations: 10 requests per hour per user
- URL resolution: 1000 requests per hour per IP

---

## Pagination

### Pagination Parameters:
- **page**: Page number (starts from 1)
- **limit**: Number of items per page (1-100, default: 20)
- **search**: Search by shortcode or original URL
- **status**: Filter by status (active, inactive, expired)
- **sort**: Sort field (created_at, click_count, shortcode)
- **order**: Sort order (asc, desc)

### Pagination Response:
The pagination metadata includes:
- `count`: Total number of items
- `page`: Current page number
- `limit`: Items per page
- `total_pages`: Total number of pages
- `has_next`: Whether there's a next page
- `has_previous`: Whether there's a previous page
- `next_page`: Next page number (null if no next page)
- `previous_page`: Previous page number (null if no previous page)

### Example Pagination Usage:
```
GET /api/v1/organizations/{org_id}/namespaces/{namespace}/urls/?page=2&limit=10&sort=click_count&order=desc
```

## Notes

- Shortcodes are case-sensitive
- Shortcodes are unique within a namespace
- URLs are automatically validated for accessibility
- Private URLs require authentication to access
- Expired URLs return 410 Gone status
- All timestamps are in ISO 8601 format (UTC)
- URL IDs are UUIDs
- Pagination is applied after sorting and filtering
- Maximum limit is 100 items per page
