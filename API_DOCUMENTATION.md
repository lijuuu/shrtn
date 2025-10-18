# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All API endpoints (except health checks and public URL resolution) require JWT authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Response Format
All API responses follow a consistent format:
```json
{
  "success": true/false,
  "message": "Success/Error message",
  "status_code": 200,
  "payload": {
    // Response data
  },
  "meta": {
    // Additional metadata (pagination, counts, etc.)
  }
}
```

### Enhanced Response Features
- **Consistent structure** across all endpoints
- **Permission context** included in responses for conditional UI
- **User roles and permissions** for easy frontend integration
- **Rich metadata** with counts, pagination, and context information
- **Formatted data** ready for frontend consumption

## Status Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (authentication required)
- **404**: Not Found
- **500**: Internal Server Error

---

## Health Check Endpoints

### GET /health/
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### GET /health/detailed/
Detailed health check with service status.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "scylla": "healthy"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### GET /health/ready/
Readiness check for Kubernetes.

### GET /health/live/
Liveness check for Kubernetes.

---

## Authentication Endpoints

### POST /auth/register/
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe",
  "organization_name": "My Company" // optional
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "verified": false
  },
  "organization": {
    "id": "uuid",
    "name": "My Company"
  },
  "tokens": {
    "access": "jwt_token",
    "refresh": "jwt_token"
  }
}
```

**Error Responses:**
- **400**: Email already exists, invalid email format, weak password
- **500**: Registration failed

### POST /auth/login/
Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "verified": true
  },
  "tokens": {
    "access": "jwt_token",
    "refresh": "jwt_token"
  }
}
```

**Error Responses:**
- **400**: Missing email/password
- **401**: Invalid credentials, account disabled

### GET /auth/google/login/
Initiate Google OAuth login (redirects to Google).

### GET /auth/google/callback/
Handle Google OAuth callback.

**Response (200):**
```json
{
  "success": true,
  "message": "Authentication successful",
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "name": "John Doe",
    "verified": true
  },
  "tokens": {
    "access": "jwt_token"
  }
}
```

### GET /auth/status/
Check authentication status.

**Response (200):**
```json
{
  "authenticated": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "verified": true
  },
  "tokens": {
    "access": "jwt_token",
    "refresh": "jwt_token"
  }
}
```

### POST /auth/logout/
Logout user.

**Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### POST /auth/refresh/
Refresh JWT token.

**Request Body:**
```json
{
  "refresh_token": "jwt_refresh_token"
}
```

**Response (200):**
```json
{
  "success": true,
  "access_token": "new_jwt_token"
}
```

### POST /auth/change-password/
Change user password.

**Request Body:**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

### POST /auth/update-profile/
Update user profile.

**Request Body:**
```json
{
  "name": "John Smith"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Smith",
    "verified": true
  }
}
```

---

## User Management Endpoints

### GET /api/v1/users/
List all users.

**Query Parameters:**
- `verified_only` (boolean): Filter verified users only

**Response (200):**
```json
{
  "message": "Users retrieved successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "users": [
      {
        "id": "uuid",
        "email": "user@example.com",
        "name": "John Doe",
        "username": "johndoe",
        "verified": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "count": 1
  }
}
```

### POST /api/v1/users/create/
Create a new user.

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "name": "Jane Doe",
  "username": "janedoe",
  "password": "SecurePass123!"
}
```

**Response (201):**
```json
{
  "message": "User created successfully",
  "status_code": 201,
  "success": true,
  "payload": {
    "id": "uuid",
    "email": "newuser@example.com",
    "name": "Jane Doe",
    "username": "janedoe",
    "verified": false,
    "is_active": true,
    "is_staff": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /api/v1/users/{user_id}/
Get user by ID.

**Response (200):**
```json
{
  "message": "User retrieved successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "username": "johndoe",
    "verified": true,
    "is_active": true,
    "is_staff": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### PUT /api/v1/users/{user_id}/update/
Update user.

**Request Body:**
```json
{
  "name": "John Smith",
  "email": "johnsmith@example.com",
  "verified": true
}
```

**Response (200):**
```json
{
  "message": "User updated successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "id": "uuid",
    "email": "johnsmith@example.com",
    "name": "John Smith",
    "username": "johndoe",
    "verified": true,
    "is_active": true,
    "is_staff": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### DELETE /api/v1/users/{user_id}/delete/
Delete user.

**Response (200):**
```json
{
  "message": "User deleted successfully",
  "status_code": 200,
  "success": true,
  "payload": null
}
```

### GET /api/v1/users/email/{email}/
Get user by email.

**Response (200):**
```json
{
  "message": "User retrieved successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "username": "johndoe",
    "verified": true,
    "is_active": true,
    "is_staff": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /api/v1/users/search/
Search users by name.

**Query Parameters:**
- `q` (string): Search query

**Response (200):**
```json
{
  "message": "Search completed successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "users": [
      {
        "id": "uuid",
        "email": "user@example.com",
        "name": "John Doe",
        "username": "johndoe",
        "verified": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "count": 1,
    "query": "john"
  }
}
```

### GET /api/v1/users/{user_id}/stats/
Get user statistics.

**Response (200):**
```json
{
  "message": "User statistics retrieved successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "stats": {
      "total_urls": 150,
      "total_clicks": 2500,
      "organizations": 2,
      "namespaces": 5
    }
  }
}
```

---

## Organization Management Endpoints

### GET /api/v1/organizations/
List user's organizations with permissions and rich context.

**Response (200):**
```json
{
  "success": true,
  "message": "Organizations retrieved successfully",
  "status_code": 200,
  "payload": [
    {
      "org_id": "uuid",
      "name": "My Company",
      "description": "Company description",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "user_permissions": {
        "can_view": true,
        "can_admin": true,
        "can_update": true
      },
      "user_role": "admin",
      "member_count": 5,
      "namespace_count": 3
    },
    {
      "org_id": "uuid-2",
      "name": "Client Company",
      "description": "Client company description",
      "created_at": "2024-01-02T00:00:00Z",
      "updated_at": "2024-01-02T00:00:00Z",
      "user_permissions": {
        "can_view": true,
        "can_admin": false,
        "can_update": true
      },
      "user_role": "editor",
      "member_count": 12,
      "namespace_count": 8
    }
  ],
  "meta": {
    "count": 2,
    "user_id": "uuid"
  }
}
```

**Enhanced Permission Fields:**
- **`user_role`**: User's role in the organization (`admin`, `editor`, `viewer`, `none`)
- **`user_permissions`**: Object containing permission flags for conditional UI
  - **`can_view`**: Can view organization content, URLs, namespaces
  - **`can_admin`**: Can manage organization settings, members, invites
  - **`can_update`**: Can edit URLs, create/update namespaces
- **`member_count`**: Number of members in the organization
- **`namespace_count`**: Number of namespaces in the organization

### POST /api/v1/organizations/create/
Create new organization.

**Request Body:**
```json
{
  "name": "New Company",
  "description": "Company description" // optional
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Organization created successfully",
  "status_code": 201,
  "payload": {
    "org_id": "uuid",
    "name": "New Company",
    "description": "Company description",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "user_permissions": {
      "can_view": true,
      "can_admin": true,
      "can_update": true
    },
    "user_role": "admin",
    "member_count": 1,
    "namespace_count": 0
  },
  "meta": {
    "user_role": "admin",
    "user_permissions": {
      "can_view": true,
      "can_update": true,
      "can_admin": true
    }
  }
}
```

### GET /api/v1/organizations/{org_id}/
Get organization by ID with full details including members and permissions.

**Response (200):**
```json
{
  "success": true,
  "message": "Organization retrieved successfully",
  "status_code": 200,
  "payload": {
    "org_id": "uuid",
    "name": "My Company",
    "description": "Company description",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "user_permissions": {
      "can_view": true,
      "can_admin": true,
      "can_update": true
    },
    "user_role": "admin",
    "members": [
      {
        "user_id": "uuid",
        "user_email": "admin@company.com",
        "user_username": "admin",
        "user_first_name": "John",
        "user_last_name": "Doe",
        "can_view": true,
        "can_update": true,
        "can_admin": true,
        "joined_at": "2024-01-01T00:00:00Z"
      }
    ],
    "member_count": 5,
    "namespace_count": 3
  }
}
```

### PUT /api/v1/organizations/{org_id}/update/
Update organization.

**Request Body:**
```json
{
  "name": "Updated Company Name"
}
```

**Response (200):**
```json
{
  "message": "Organization updated successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "org_id": "uuid",
    "name": "Updated Company Name",
    "owner": "uuid",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### DELETE /api/v1/organizations/{org_id}/delete/
Delete organization.

**Response (200):**
```json
{
  "message": "Organization deleted successfully",
  "status_code": 200,
  "success": true,
  "payload": null
}
```

### GET /api/v1/organizations/{org_id}/members/
Get organization members.

**Response (200):**
```json
{
  "message": "Members retrieved successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "members": [
      {
        "user": "uuid",
        "user_email": "member@example.com",
        "user_name": "Member Name",
        "can_view": true,
        "can_admin": false,
        "can_update": true,
        "joined_at": "2024-01-01T00:00:00Z"
      }
    ],
    "count": 1
  }
}
```

### POST /api/v1/organizations/{org_id}/members/add/
Add member to organization.

**Request Body:**
```json
{
  "user": "uuid",
  "can_view": true,
  "can_admin": false,
  "can_update": true
}
```

**Response (201):**
```json
{
  "message": "Member added successfully",
  "status_code": 201,
  "success": true,
  "payload": {
    "user": "uuid",
    "user_email": "member@example.com",
    "user_name": "Member Name",
    "can_view": true,
    "can_admin": false,
    "can_update": true,
    "joined_at": "2024-01-01T00:00:00Z"
  }
}
```

### DELETE /api/v1/organizations/{org_id}/members/{user_id}/remove/
Remove member from organization.

**Response (200):**
```json
{
  "message": "Member removed successfully",
  "status_code": 200,
  "success": true,
  "payload": null
}
```

### POST /api/v1/organizations/{org_id}/invites/create/
Create organization invite.

**Request Body:**
```json
{
  "invitee_email": "newuser@example.com",
  "can_view": true,
  "can_admin": false,
  "can_update": true
}
```

**Response (201):**
```json
{
  "message": "Invite created successfully",
  "status_code": 201,
  "success": true,
  "payload": {
    "invite_id": "uuid",
    "invitee_email": "newuser@example.com",
    "organization": "uuid",
    "organization_name": "My Company",
    "inviter": "uuid",
    "inviter_name": "John Doe",
    "can_view": true,
    "can_admin": false,
    "can_update": true,
    "used": false,
    "created_at": "2024-01-01T00:00:00Z",
    "expires_at": "2024-01-08T00:00:00Z"
  }
}
```

### GET /api/v1/organizations/{org_id}/invites/
Get pending invites for organization.

**Response (200):**
```json
{
  "message": "Pending invites retrieved successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "invites": [
      {
        "invite_id": "uuid",
        "invitee_email": "newuser@example.com",
        "organization": "uuid",
        "organization_name": "My Company",
        "inviter": "uuid",
        "inviter_name": "John Doe",
        "can_view": true,
        "can_admin": false,
        "can_update": true,
        "used": false,
        "created_at": "2024-01-01T00:00:00Z",
        "expires_at": "2024-01-08T00:00:00Z"
      }
    ],
    "count": 1
  }
}
```

### GET /api/v1/invites/{token}/
Get invite details by token (public endpoint, no authentication required).

**Response (200):**
```json
{
  "success": true,
  "message": "Invite details retrieved successfully",
  "status_code": 200,
  "payload": {
    "invite_id": "uuid",
    "invitee_email": "newuser@example.com",
    "organization": {
      "org_id": "uuid",
      "name": "My Company",
      "description": "Company description"
    },
    "inviter": {
      "user_id": "uuid",
      "name": "John Doe"
    },
    "expires_at": "2024-01-08T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "permissions": {
      "can_view": true,
      "can_update": true,
      "can_admin": false
    }
  }
}
```

**Error Responses:**
- **400**: Invalid invite token
- **404**: Invite not found
- **410**: Invite expired or already used

### POST /api/v1/invites/{token}/accept/
Accept organization invite by token (requires authentication).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
  "success": true,
  "message": "Invite accepted successfully",
  "status_code": 200,
  "payload": {
    "organization": {
      "org_id": "uuid",
      "name": "My Company",
      "description": "Company description"
    },
    "user_permissions": {
      "can_view": true,
      "can_update": true,
      "can_admin": false
    },
    "user_role": "editor"
  }
}
```

**Error Responses:**
- **400**: Invalid invite token or validation error
- **401**: Authentication required
- **404**: Invite not found
- **410**: Invite expired or already used
- **500**: Failed to accept invite

---

## Namespace Management Endpoints

### GET /api/v1/organizations/{org_id}/namespaces/
List organization namespaces.

**Response (200):**
```json
{
  "message": "Namespaces retrieved successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "namespaces": [
      {
        "namespace_id": "uuid",
        "organization": "uuid",
        "organization_name": "My Company",
        "created_by": "uuid",
        "creator_name": "John Doe",
        "name": "marketing",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "count": 1
  }
}
```

### POST /api/v1/organizations/{org_id}/namespaces/create/
Create new namespace.

**Request Body:**
```json
{
  "name": "sales"
}
```

**Response (201):**
```json
{
  "message": "Namespace created successfully",
  "status_code": 201,
  "success": true,
  "payload": {
    "namespace_id": "uuid",
    "organization": "uuid",
    "organization_name": "My Company",
    "created_by": "uuid",
    "creator_name": "John Doe",
    "name": "sales",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /api/v1/namespaces/{namespace}/
Get namespace by name.

**Response (200):**
```json
{
  "message": "Namespace retrieved successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "namespace_id": "uuid",
    "organization": "uuid",
    "organization_name": "My Company",
    "created_by": "uuid",
    "creator_name": "John Doe",
    "name": "marketing",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### PUT /api/v1/organizations/{org_id}/namespaces/{namespace}/update/
Update namespace.

**Request Body:**
```json
{
  "name": "updated-namespace"
}
```

**Response (200):**
```json
{
  "message": "Namespace updated successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "namespace_id": "uuid",
    "organization": "uuid",
    "organization_name": "My Company",
    "created_by": "uuid",
    "creator_name": "John Doe",
    "name": "updated-namespace",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### DELETE /api/v1/organizations/{org_id}/namespaces/{namespace}/delete/
Delete namespace.

**Response (200):**
```json
{
  "message": "Namespace deleted successfully",
  "status_code": 200,
  "success": true,
  "payload": null
}
```

### GET /api/v1/namespaces/check/{namespace}/
Check namespace availability.

**Response (200):**
```json
{
  "message": "Namespace availability checked",
  "status_code": 200,
  "success": true,
  "payload": {
    "name": "marketing",
    "available": true
  }
}
```

---

## URL Management Endpoints

### GET /api/v1/organizations/{org_id}/namespaces/{namespace}/urls/
List URLs in namespace with enhanced context and permissions.

**Response (200):**
```json
{
  "success": true,
  "message": "URLs retrieved successfully",
  "status_code": 200,
  "payload": [
    {
      "namespace_id": "uuid",
      "shortcode": "abc123",
      "original_url": "https://example.com",
      "title": "Example Page",
      "description": "Example description",
      "created_by_user_id": "uuid",
      "created_at": "2024-01-01T00:00:00Z",
      "created_at_formatted": "2024-01-01 00:00:00",
      "updated_at": "2024-01-01T00:00:00Z",
      "expires_at": null,
      "expires_at_formatted": null,
      "click_count": 150,
      "is_active": true,
      "user_permissions": {
        "can_view": true,
        "can_update": true,
        "can_admin": false
      },
      "user_role": "editor",
      "namespace_name": "marketing",
      "organization_name": "My Company",
      "short_url": "http://localhost:8000/marketing/abc123/"
    }
  ],
  "meta": {
    "namespace": "marketing",
    "namespace_id": "uuid",
    "count": 1
  }
}
```

### POST /api/v1/organizations/{org_id}/namespaces/{namespace}/urls/create/
Create new short URL.

**Request Body:**
```json
{
  "shortcode": "abc123", // optional, auto-generated if not provided
  "original_url": "https://example.com",
  "title": "Example Page", // optional
  "description": "Example description", // optional
  "expires_at": "2024-12-31T23:59:59Z" // optional
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "URL created successfully",
  "status_code": 201,
  "payload": {
    "namespace_id": "uuid",
    "shortcode": "abc123",
    "original_url": "https://example.com",
    "title": "Example Page",
    "description": "Example description",
    "created_by_user_id": "uuid",
    "created_at": "2024-01-01T00:00:00Z",
    "created_at_formatted": "2024-01-01 00:00:00",
    "updated_at": "2024-01-01T00:00:00Z",
    "expires_at": "2024-12-31T23:59:59Z",
    "expires_at_formatted": "2024-12-31 23:59:59",
    "click_count": 0,
    "is_active": true,
    "user_permissions": {
      "can_view": true,
      "can_update": true,
      "can_admin": false
    },
    "user_role": "editor",
    "namespace_name": "marketing",
    "organization_name": "My Company",
    "short_url": "http://localhost:8000/marketing/abc123/"
  }
}
```

### GET /api/v1/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/
Get URL details.

**Response (200):**
```json
{
  "message": "URL retrieved successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "namespace_id": "uuid",
    "shortcode": "abc123",
    "created_by_user_id": "uuid",
    "original_url": "https://example.com",
    "expiry": "2024-12-31T23:59:59Z",
    "click_count": 150,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "is_private": false,
    "tags": ["marketing", "campaign"]
  }
}
```

### PUT /api/v1/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/update/
Update URL.

**Request Body:**
```json
{
  "original_url": "https://updated-example.com",
  "expiry": "2025-12-31T23:59:59Z",
  "is_private": true,
  "tags": ["updated", "campaign"]
}
```

**Response (200):**
```json
{
  "message": "URL updated successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "namespace_id": "uuid",
    "shortcode": "abc123",
    "created_by_user_id": "uuid",
    "original_url": "https://updated-example.com",
    "expiry": "2025-12-31T23:59:59Z",
    "click_count": 150,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "is_private": true,
    "tags": ["updated", "campaign"]
  }
}
```

### DELETE /api/v1/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/delete/
Delete URL.

**Response (200):**
```json
{
  "message": "URL deleted successfully",
  "status_code": 200,
  "success": true,
  "payload": null
}
```

### GET /{namespace}/{shortcode}/
Resolve short URL to original URL (public endpoint, no authentication required).

**Response:** HTTP 302 Redirect to original URL

**Error Response (404):**
```json
{
  "message": "URL not found",
  "status_code": 404,
  "success": false,
  "payload": null
}
```

### POST /api/v1/organizations/{org_id}/namespaces/{namespace}/urls/bulk/
Bulk create URLs.

**Request Body:**
```json
{
  "urls": [
    {
      "shortcode": "bulk1",
      "original_url": "https://example1.com"
    },
    {
      "shortcode": "bulk2",
      "original_url": "https://example2.com"
    }
  ]
}
```

**Response (201):**
```json
{
  "message": "URLs created successfully",
  "status_code": 201,
  "success": true,
  "payload": {
    "urls": [
      {
        "namespace_id": "uuid",
        "shortcode": "bulk1",
        "created_by_user_id": "uuid",
        "original_url": "https://example1.com",
        "expiry": null,
        "click_count": 0,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "is_private": false,
        "tags": []
      }
    ],
    "count": 2
  }
}
```

---

## Cache Management Endpoints

### GET /api/v1/cache/hot-urls/
Get hot URLs (most accessed).

**Query Parameters:**
- `limit` (integer): Maximum number of URLs to return (default: 100)

**Response (200):**
```json
{
  "message": "Hot URLs retrieved successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "hot_urls": [
      {
        "shortcode": "abc123",
        "original_url": "https://example.com",
        "click_count": 1500
      }
    ],
    "count": 1,
    "limit": 100
  }
}
```

### GET /api/v1/cache/stats/
Get cache statistics.

**Response (200):**
```json
{
  "message": "Cache statistics retrieved successfully",
  "status_code": 200,
  "success": true,
  "payload": {
    "cache_stats": {
      "total_cached": 1000,
      "hit_rate": 0.95,
      "miss_rate": 0.05,
      "memory_usage": "50MB"
    }
  }
}
```

### POST /api/v1/cache/clear/
Clear all URL cache.

**Response (200):**
```json
{
  "message": "Cache cleared successfully",
  "status_code": 200,
  "success": true,
  "payload": null
}
```

### GET /api/v1/cache/test/
Test cache functionality.

**Response (200):**
```json
{
  "message": "Cache test successful",
  "status_code": 200,
  "success": true,
  "payload": {
    "cache_stats": {
      "total_cached": 1000,
      "hit_rate": 0.95,
      "miss_rate": 0.05,
      "memory_usage": "50MB"
    },
    "hot_urls": [
      {
        "shortcode": "abc123",
        "original_url": "https://example.com",
        "click_count": 1500
      }
    ],
    "cache_working": true
  }
}
```

---

## Frontend Integration Benefits

### Permission-Based Conditional UI
The API provides rich permission context for easy frontend conditional rendering:

```javascript
// Example: Conditional UI based on permissions
const organization = response.payload;
if (organization.user_permissions.can_admin) {
  // Show admin controls
  showDeleteButton();
  showInviteMembersButton();
  showNamespaceManagement();
}
if (organization.user_role === 'admin') {
  // Show admin-only features
  showAdvancedSettings();
}
```

### Consistent Data Structure
All responses follow the same pattern for predictable frontend handling:

```javascript
// All responses have the same structure
const response = await fetch('/api/v1/organizations/');
const data = response.payload;     // Main data
const meta = response.meta;        // Additional context
const permissions = data.user_permissions; // Always available
```

### Rich Context Information
Responses include all necessary data for UI components:

```javascript
// Organizations include member counts, namespace counts
const org = response.payload;
console.log(`${org.name} has ${org.member_count} members and ${org.namespace_count} namespaces`);

// URLs include full short URLs and namespace context
const url = response.payload;
console.log(`Short URL: ${url.short_url}`);
console.log(`Namespace: ${url.namespace_name}`);
```

### Formatted Data Ready for Display
- **Dates**: Both ISO format and human-readable format
- **URLs**: Full short URLs ready for display
- **Counts**: Member counts, namespace counts, URL counts
- **Permissions**: Boolean flags for conditional rendering
- **Roles**: String roles for role-based UI logic

### Organization Invite Flow
The API provides a complete invite system with email integration:

```javascript
// 1. User receives invite email with token
// 2. Frontend gets invite details (no auth required)
const getInviteDetails = async (token) => {
  const response = await fetch(`/api/v1/invites/${token}/`);
  return response.json();
};

// 3. User logs in and accepts invite
const acceptInvite = async (token, userToken) => {
  const response = await fetch(`/api/v1/invites/${token}/accept/`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${userToken}` }
  });
  return response.json();
};

// 4. User is now a member with specified permissions
const userRole = response.payload.user_role; // 'admin', 'editor', 'viewer'
const permissions = response.payload.user_permissions;
```

---

## Error Handling

### Validation Errors (400)
```json
{
  "success": false,
  "message": "Validation failed",
  "status_code": 400,
  "payload": {
    "email": ["Enter a valid email address"],
    "password": ["Password must be at least 8 characters long"]
  },
  "errors": [
    "Email format is invalid",
    "Password is too weak"
  ],
  "meta": {}
}
```

### Authentication Errors (401)
```json
{
  "success": false,
  "message": "Authentication required",
  "status_code": 401,
  "payload": null,
  "meta": {}
}
```

### Permission Errors (403)
```json
{
  "success": false,
  "message": "Insufficient permissions. Required: can_admin",
  "status_code": 403,
  "payload": null,
  "meta": {
    "required_permission": "can_admin",
    "user_role": "editor"
  }
}
```

### Not Found Errors (404)
```json
{
  "success": false,
  "message": "Organization not found",
  "status_code": 404,
  "payload": null,
  "meta": {}
}
```

### Server Errors (500)
```json
{
  "success": false,
  "message": "Failed to retrieve organization",
  "status_code": 500,
  "payload": null,
  "meta": {}
}
```

---

## Data Validation Rules

### User Registration/Update
- **Email**: Valid email format, unique
- **Password**: 8+ characters, uppercase, lowercase, number, special character
- **Name**: 2-255 characters, letters/spaces/hyphens/apostrophes/periods only
- **Username**: 3-150 characters, alphanumeric and underscores only

### Organization
- **Name**: 2+ characters

### Namespace
- **Name**: 2+ characters, alphanumeric/hyphens/underscores only, unique

### URL
- **Original URL**: Valid HTTP/HTTPS URL
- **Shortcode**: 3+ characters, alphanumeric/hyphens/underscores only
- **Tags**: Array of strings, max 100 characters each

---

## Rate Limiting
- Authentication endpoints: 5 requests per minute
- URL creation: 100 requests per hour
- Bulk operations: 10 requests per hour
- Cache operations: 50 requests per hour

---

## Analytics Endpoints

The analytics system provides comprehensive insights into URL performance with flexible time filtering and tier-based country analysis.

### Features
- **Time Filtering**: `1day`, `3days`, `7days`, `30days` or custom periods
- **Tier System**: Automatic country classification based on traffic levels
- **Real-time Stats**: Live monitoring of today's activity
- **Geographic Analysis**: Country-based traffic distribution
- **Performance Metrics**: Click counts, unique IPs, referer analysis

### Time Filter Options
- `1day` - Last 24 hours
- `3days` - Last 3 days
- `7days` - Last 7 days  
- `30days` - Last 30 days

### Tier Classification
- **Tier 1**: High-traffic countries (≥1000 clicks)
- **Tier 2**: Medium-traffic countries (500-999 clicks)
- **Tier 3**: Low-traffic countries (100-499 clicks)
- **Tier 4**: Minimal-traffic countries (<100 clicks)

---

### Get URL Analytics
Get detailed analytics for a specific short URL with time filtering support.

**Endpoint:** `GET /api/v1/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/analytics/`

**Parameters:**
- `days` (optional): Number of days to analyze (default: 30, max: 365)
- `time_filter` (optional): Time filter - `1day`, `3days`, `7days`, `30days`

**Time Filter Options:**
- `1day` - Last 24 hours
- `3days` - Last 3 days
- `7days` - Last 7 days  
- `30days` - Last 30 days

**Response:**
```json
{
  "success": true,
  "message": "URL analytics retrieved successfully",
  "payload": {
    "url": "namespace:shortcode",
    "period_days": 7,
    "time_filter": "7days",
    "total_clicks": 1250,
    "analytics": {
      "daily_clicks": [
        {"date": "2024-01-01", "clicks": 45},
        {"date": "2024-01-02", "clicks": 52}
      ],
      "country_distribution": {
        "United States of America": 450,
        "Canada": 200,
        "United Kingdom": 150
      },
      "referer_distribution": {
        "Direct": 300,
        "Google": 250,
        "Facebook": 100
      },
      "top_countries": [
        {"country": "United States of America", "clicks": 450},
        {"country": "Canada", "clicks": 200}
      ],
      "unique_ips": 850,
      "total_clicks": 1250
    }
  }
}
```

### Get Namespace Analytics
Get analytics for all URLs in a namespace with time filtering support.

**Endpoint:** `GET /api/v1/organizations/{org_id}/namespaces/{namespace}/analytics/`

**Parameters:**
- `days` (optional): Number of days to analyze (default: 30, max: 365)
- `time_filter` (optional): Time filter - `1day`, `3days`, `7days`, `30days`

**Time Filter Options:**
- `1day` - Last 24 hours
- `3days` - Last 3 days
- `7days` - Last 7 days  
- `30days` - Last 30 days

**Response:**
```json
{
  "success": true,
  "message": "Namespace analytics retrieved successfully",
  "payload": {
    "namespace_id": "uuid",
    "period_days": 7,
    "time_filter": "7days",
    "total_clicks": 5000,
    "unique_urls": 25,
    "analytics": {
      "daily_clicks": [
        {"date": "2024-01-01", "clicks": 45},
        {"date": "2024-01-02", "clicks": 52}
      ],
      "country_distribution": {
        "United States of America": 450,
        "Canada": 200,
        "United Kingdom": 150
      },
      "top_countries": [
        {"country": "United States of America", "clicks": 450},
        {"country": "Canada", "clicks": 200}
      ]
    },
    "url_stats": {
      "abc123": {
        "total_clicks": 200,
        "unique_ips": 150,
        "countries": ["United States of America", "Canada"],
        "top_countries": [
          {"country": "United States of America", "clicks": 120},
          {"country": "Canada", "clicks": 80}
        ]
      }
    }
  }
}
```

### Get Real-time Statistics
Get real-time statistics for a namespace (today's data only).

**Endpoint:** `GET /api/v1/organizations/{org_id}/namespaces/{namespace}/analytics/realtime/`

**Response:**
```json
{
  "success": true,
  "message": "Real-time statistics retrieved successfully",
  "payload": {
    "namespace_id": "uuid",
    "date": "2024-01-15",
    "total_clicks_today": 45,
    "recent_clicks": [
      {
        "shortcode": "abc123",
        "timestamp": "2024-01-15T14:30:00Z",
        "country": "United States of America"
      },
      {
        "shortcode": "def456",
        "timestamp": "2024-01-15T14:25:00Z",
        "country": "Canada"
      }
    ],
    "unique_countries_today": 8,
    "country_breakdown": {
      "United States of America": 25,
      "Canada": 15,
      "United Kingdom": 5
    }
  }
}
```

### Get Country Analytics
Get country-based analytics with tier information across all namespaces in an organization.

**Endpoint:** `GET /api/v1/organizations/{org_id}/analytics/countries/`

**Parameters:**
- `days` (optional): Number of days to analyze (default: 30, max: 365)
- `time_filter` (optional): Time filter - `1day`, `3days`, `7days`, `30days`

**Time Filter Options:**
- `1day` - Last 24 hours
- `3days` - Last 3 days
- `7days` - Last 7 days  
- `30days` - Last 30 days

**Tier System:**
- **Tier 1**: High-traffic countries (≥1000 clicks)
- **Tier 2**: Medium-traffic countries (500-999 clicks)
- **Tier 3**: Low-traffic countries (100-499 clicks)
- **Tier 4**: Minimal-traffic countries (<100 clicks)

**Response:**
```json
{
  "success": true,
  "message": "Country analytics retrieved successfully",
  "payload": {
    "total_clicks": 10000,
    "countries": ["United States of America", "Canada", "United Kingdom"],
    "country_distribution": {
      "United States of America": 4500,
      "Canada": 2000,
      "United Kingdom": 1500
    },
    "top_countries": [
      {
        "country": "United States of America",
        "clicks": 4500,
        "tier": "tier_1",
        "percentage": 45.0
      },
      {
        "country": "Canada",
        "clicks": 2000,
        "tier": "tier_2",
        "percentage": 20.0
      },
      {
        "country": "United Kingdom",
        "clicks": 1500,
        "tier": "tier_2",
        "percentage": 15.0
      }
    ],
    "tier_counts": {
      "tier_1": 1,
      "tier_2": 2,
      "tier_3": 0,
      "tier_4": 0
    },
    "period_days": 7,
    "time_filter": "7days",
    "namespaces_analyzed": 5
  }
}
```

### Get Tier Analytics
Get tier-based analytics breakdown for an organization.

**Endpoint:** `GET /api/v1/organizations/{org_id}/analytics/tiers/`

**Parameters:**
- `days` (optional): Number of days to analyze (default: 30, max: 365)
- `time_filter` (optional): Time filter - `1day`, `3days`, `7days`, `30days`

**Response:**
```json
{
  "success": true,
  "message": "Tier analytics retrieved successfully",
  "payload": {
    "tier_breakdown": {
      "tier_1": {
        "count": 1,
        "countries": [
          {
            "country": "United States of America",
            "clicks": 4500,
            "percentage": 45.0
          }
        ],
        "total_clicks": 4500
      },
      "tier_2": {
        "count": 1,
        "countries": [
          {
            "country": "Canada",
            "clicks": 2000,
            "percentage": 20.0
          }
        ],
        "total_clicks": 2000
      },
      "tier_3": {
        "count": 1,
        "countries": [
          {
            "country": "United Kingdom",
            "clicks": 1500,
            "percentage": 15.0
          }
        ],
        "total_clicks": 1500
      },
      "tier_4": {
        "count": 0,
        "countries": [],
        "total_clicks": 0
      }
    },
    "tier_counts": {
      "tier_1": 1,
      "tier_2": 1,
      "tier_3": 1,
      "tier_4": 0
    },
    "total_clicks": 10000,
    "period_days": 30,
    "time_filter": "30days",
    "namespaces_analyzed": 5
  }
}
```

## Analytics Usage Examples

### Time Filter Examples

#### Get Today's URL Analytics
```bash
GET /api/v1/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/analytics/?time_filter=1day
```

#### Get Last Week's Namespace Analytics
```bash
GET /api/v1/organizations/{org_id}/namespaces/{namespace}/analytics/?time_filter=7days
```

#### Get Last Month's Country Analytics with Tiers
```bash
GET /api/v1/organizations/{org_id}/analytics/countries/?time_filter=30days
```

#### Get Custom Period Analytics
```bash
GET /api/v1/organizations/{org_id}/analytics/tiers/?days=14&time_filter=7days
```

### Tier Analytics Examples

#### Get Tier Breakdown for Organization
```bash
GET /api/v1/organizations/{org_id}/analytics/tiers/?time_filter=7days
```

#### Get High-Traffic Countries (Tier 1)
```bash
GET /api/v1/organizations/{org_id}/analytics/countries/?time_filter=30days
# Filter results where tier = "tier_1"
```

### Real-time Monitoring

#### Get Today's Activity
```bash
GET /api/v1/organizations/{org_id}/namespaces/{namespace}/analytics/realtime/
```

#### Get Last 3 Days Performance
```bash
GET /api/v1/organizations/{org_id}/namespaces/{namespace}/analytics/?time_filter=3days
```

### Error Handling

#### Invalid Time Filter
```json
{
  "success": false,
  "message": "Invalid time_filter. Must be one of: 1day, 3days, 7days, 30days",
  "status_code": 400,
  "payload": null
}
```

#### No Analytics Data
```json
{
  "success": true,
  "message": "No analytics data available",
  "payload": {
    "total_clicks": 0,
    "countries": [],
    "country_distribution": {},
    "tier_counts": {"tier_1": 0, "tier_2": 0, "tier_3": 0, "tier_4": 0},
    "top_countries": [],
    "period_days": 7,
    "time_filter": "7days",
    "namespaces_analyzed": 0
  }
}
```

---

## Pagination
For list endpoints, use query parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

---

## Webhooks
The API supports webhooks for URL clicks and user events. Configure webhook URLs in organization settings.

---

## SDKs and Libraries
- JavaScript/Node.js SDK available
- Python SDK available
- cURL examples provided for all endpoints

---

## Support
For API support and questions:
- Documentation: [API Docs]
- Support Email: support@example.com
- Status Page: [Status Page]
