# JSON Response Structure - URL Shortener Platform

## 🎯 Standard Response Format

All API endpoints follow this consistent JSON response structure:

```json
{
    "message": "string",           // Human-readable message
    "status_code": number,         // HTTP status code
    "success": boolean,           // Success/failure indicator
    "payload": object | null      // Actual data or null
}
```

## 📊 Response Examples

### **✅ Success Responses**

#### **1. User Registration Success**
```json
POST /api/auth/register/
{
    "message": "User created successfully",
    "status_code": 201,
    "success": true,
    "payload": {
        "id": 1,
        "email": "john@example.com",
        "name": "John Doe",
        "username": "johndoe",
        "verified": false,
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

#### **2. Organization Creation Success**
```json
POST /api/organizations/
{
    "message": "Organization created successfully",
    "status_code": 201,
    "success": true,
    "payload": {
        "id": 1,
        "name": "Acme Corp",
        "slug": "acme-corp",
        "created_by": 1,
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

#### **3. URL Creation Success**
```json
POST /api/organizations/1/namespaces/acme/urls/
{
    "message": "Short URL created successfully",
    "status_code": 201,
    "success": true,
    "payload": {
        "id": "uuid-here",
        "namespace": "acme",
        "shortcode": "abc123",
        "original_url": "https://example.com",
        "short_url": "https://short.ly/acme/abc123",
        "created_by": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "expires_at": null,
        "is_private": false,
        "tags": ["marketing", "campaign"]
    }
}
```

#### **4. List Success**
```json
GET /api/organizations/1/namespaces/acme/urls/
{
    "message": "URLs retrieved successfully",
    "status_code": 200,
    "success": true,
    "payload": {
        "urls": [
            {
                "id": "uuid-1",
                "shortcode": "abc123",
                "original_url": "https://example.com",
                "click_count": 42,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "count": 1,
        "page": 1,
        "total_pages": 1
    }
}
```

### **❌ Error Responses**

#### **1. Validation Error**
```json
POST /api/auth/register/
{
    "message": "Validation failed",
    "status_code": 400,
    "success": false,
    "payload": {
        "errors": {
            "email": ["A user with this email already exists"],
            "password": ["Password must contain at least one uppercase letter"]
        }
    }
}
```

#### **2. Not Found Error**
```json
GET /api/organizations/999/namespaces/invalid/urls/abc123/
{
    "message": "URL not found",
    "status_code": 404,
    "success": false,
    "payload": null
}
```

#### **3. Permission Denied**
```json
DELETE /api/organizations/1/namespaces/acme/urls/abc123/
{
    "message": "Permission denied. You need Editor or Admin role",
    "status_code": 403,
    "success": false,
    "payload": null
}
```

#### **4. Server Error**
```json
POST /api/organizations/1/namespaces/acme/urls/
{
    "message": "Internal server error",
    "status_code": 500,
    "success": false,
    "payload": null
}
```

## 🔍 Specific Endpoint Examples

### **Authentication Endpoints**

#### **Login Success**
```json
POST /api/auth/login/
{
    "message": "Login successful",
    "status_code": 200,
    "success": true,
    "payload": {
        "user": {
            "id": 1,
            "email": "john@example.com",
            "name": "John Doe",
            "username": "johndoe"
        },
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "expires_in": 3600
        }
    }
}
```

#### **Token Refresh**
```json
POST /api/auth/refresh/
{
    "message": "Token refreshed successfully",
    "status_code": 200,
    "success": true,
    "payload": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "expires_in": 3600
    }
}
```

### **Organization Endpoints**

#### **Organization List**
```json
GET /api/organizations/
{
    "message": "Organizations retrieved successfully",
    "status_code": 200,
    "success": true,
    "payload": {
        "organizations": [
            {
                "id": 1,
                "name": "Acme Corp",
                "slug": "acme-corp",
                "role": "admin",
                "member_count": 5,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "count": 1
    }
}
```

#### **Organization Members**
```json
GET /api/organizations/1/members/
{
    "message": "Members retrieved successfully",
    "status_code": 200,
    "success": true,
    "payload": {
        "members": [
            {
                "id": 1,
                "user": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com"
                },
                "role": "admin",
                "joined_at": "2024-01-01T00:00:00Z"
            }
        ],
        "count": 1
    }
}
```

### **URL Management Endpoints**

#### **URL Analytics**
```json
GET /api/organizations/1/namespaces/acme/urls/abc123/analytics/
{
    "message": "Analytics retrieved successfully",
    "status_code": 200,
    "success": true,
    "payload": {
        "url": {
            "id": "uuid-here",
            "shortcode": "abc123",
            "original_url": "https://example.com",
            "click_count": 42,
            "unique_clicks": 38,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "analytics": {
            "total_clicks": 42,
            "unique_clicks": 38,
            "click_rate": 0.85,
            "top_countries": [
                {"country": "US", "clicks": 20},
                {"country": "CA", "clicks": 15}
            ],
            "top_browsers": [
                {"browser": "Chrome", "clicks": 25},
                {"browser": "Firefox", "clicks": 10}
            ],
            "daily_clicks": [
                {"date": "2024-01-01", "clicks": 10},
                {"date": "2024-01-02", "clicks": 15}
            ]
        }
    }
}
```

#### **Bulk URL Creation**
```json
POST /api/organizations/1/namespaces/acme/urls/bulk/
{
    "message": "Bulk URL creation started",
    "status_code": 202,
    "success": true,
    "payload": {
        "task_id": "task-uuid-here",
        "status": "processing",
        "total_urls": 100,
        "processed": 0,
        "estimated_completion": "2024-01-01T00:05:00Z"
    }
}
```

#### **Bulk Status Check**
```json
GET /api/organizations/1/namespaces/acme/urls/bulk/task-uuid-here/
{
    "message": "Bulk task status retrieved",
    "status_code": 200,
    "success": true,
    "payload": {
        "task_id": "task-uuid-here",
        "status": "completed",
        "total_urls": 100,
        "processed": 100,
        "successful": 95,
        "failed": 5,
        "download_url": "https://s3.amazonaws.com/bucket/results.xlsx",
        "completed_at": "2024-01-01T00:05:00Z"
    }
}
```

### **Search Endpoints**

#### **URL Search**
```json
GET /api/organizations/1/namespaces/acme/urls/search/?q=marketing
{
    "message": "Search completed successfully",
    "status_code": 200,
    "success": true,
    "payload": {
        "results": [
            {
                "id": "uuid-1",
                "shortcode": "abc123",
                "original_url": "https://marketing.example.com",
                "click_count": 42,
                "tags": ["marketing", "campaign"]
            }
        ],
        "count": 1,
        "query": "marketing",
        "search_time": 0.05
    }
}
```

## 🎯 Response Status Codes

| Status Code | Description | Success | Example |
|-------------|-------------|----------|---------|
| **200** | OK | ✅ | Successful GET, PUT |
| **201** | Created | ✅ | Successful POST |
| **202** | Accepted | ✅ | Async operation started |
| **400** | Bad Request | ❌ | Validation error |
| **401** | Unauthorized | ❌ | Invalid/expired token |
| **403** | Forbidden | ❌ | Insufficient permissions |
| **404** | Not Found | ❌ | Resource not found |
| **409** | Conflict | ❌ | Duplicate resource |
| **422** | Unprocessable Entity | ❌ | Business logic error |
| **429** | Too Many Requests | ❌ | Rate limit exceeded |
| **500** | Internal Server Error | ❌ | Server error |

## 🔧 Implementation Notes

### **Consistent Error Handling**
```python
# All views return this structure
return JsonResponse({
    'message': 'Human readable message',
    'status_code': 200,
    'success': True,
    'payload': data_or_null
})
```

### **Validation Errors**
```python
# Serializer validation errors
return JsonResponse({
    'message': 'Validation failed',
    'status_code': 400,
    'success': False,
    'payload': {
        'errors': serializer.errors
    }
})
```

### **Permission Errors**
```python
# Role-based access control
return JsonResponse({
    'message': 'Permission denied. Admin role required',
    'status_code': 403,
    'success': False,
    'payload': None
})
```

This consistent JSON response structure ensures a uniform API experience across all endpoints! 🚀
