# Users API Documentation

## Overview
User management endpoints for registration, authentication, profile management, and user operations.

## Base URL
```
/api/v1/users/
```

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## Endpoints

### 1. List Users
**GET** `/api/v1/users/`

List all users in the system.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "payload": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "username": "username",
      "name": "Full Name",
      "is_active": true,
      "date_joined": "2024-01-01T00:00:00Z"
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
- `403` - Forbidden

---

### 2. Search Users
**GET** `/api/v1/users/search/`

Search for users by email, username, or name.

**Query Parameters:**
- `q` (string, required) - Search query
- `limit` (integer, optional) - Number of results (default: 20)

**Example:**
```
GET /api/v1/users/search/?q=john&limit=10
```

**Response:**
```json
{
  "success": true,
  "payload": [
    {
      "id": "uuid",
      "email": "john@example.com",
      "username": "john_doe",
      "name": "John Doe"
    }
  ],
  "meta": {
    "query": "john",
    "count": 1
  }
}
```

---

### 3. Google Login
**POST** `/api/v1/users/google-login/`

Initiate Google OAuth login.

**Request Body:**
```json
{
  "redirect_uri": "http://localhost:8000/auth/google/callback/"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "auth_url": "https://accounts.google.com/oauth/authorize?..."
  }
}
```

---

### 4. Get Profile
**GET** `/api/v1/users/profile/`

Get current user's profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "name": "Full Name",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z",
    "organizations": [
      {
        "id": "uuid",
        "name": "Organization Name",
        "role": "admin"
      }
    ]
  }
}
```

---

### 5. Update Profile
**PUT** `/api/v1/users/update-profile/`

Update current user's profile information.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "New Full Name",
  "username": "new_username"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "new_username",
    "name": "New Full Name",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z"
  }
}
```

---

## Authentication Endpoints

### 6. Register User
**POST** `/auth/register/`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "Full Name",
  "organization_name": "Company Name"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "username": "username",
      "name": "Full Name"
    },
    "tokens": {
      "access": "jwt_access_token",
      "refresh": "jwt_refresh_token"
    },
    "organization": {
      "id": "uuid",
      "name": "Company Name"
    }
  }
}
```

**Status Codes:**
- `201` - Created
- `400` - Bad Request (validation errors)
- `409` - Conflict (email already exists)

---

### 7. Login
**POST** `/auth/login/`

Authenticate user and get JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "tokens": {
      "access": "jwt_access_token",
      "refresh": "jwt_refresh_token"
    },
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "username": "username",
      "name": "Full Name"
    }
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid credentials
- `400` - Bad Request

---

### 8. Logout
**POST** `/auth/logout/`

Logout user and invalidate tokens.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

---

### 9. Change Password
**POST** `/auth/change-password/`

Change user password.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "current_password": "old_password",
  "new_password": "new_secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

### 10. Auth Status
**GET** `/auth/status/`

Check authentication status.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "authenticated": true,
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "username": "username",
      "name": "Full Name"
    }
  }
}
```

---

### 11. Google OAuth Login
**GET** `/auth/google/login/`

Redirect to Google OAuth login.

**Response:**
```
302 Redirect to Google OAuth URL
```

---

### 12. Google OAuth Callback
**GET** `/auth/google/callback/`

Handle Google OAuth callback.

**Query Parameters:**
- `code` - Authorization code from Google
- `state` - State parameter for security

**Response:**
```
302 Redirect to frontend with tokens
```

---

### 13. Google Login API
**POST** `/auth/google/login/api/`

Google OAuth login via API.

**Request Body:**
```json
{
  "code": "google_authorization_code",
  "redirect_uri": "http://localhost:8000/auth/google/callback/"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "tokens": {
      "access": "jwt_access_token",
      "refresh": "jwt_refresh_token"
    },
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "username": "username",
      "name": "Full Name"
    }
  }
}
```

---

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "success": false,
  "message": "Validation error",
  "errors": [
    "Field 'email' is required",
    "Field 'password' must be at least 8 characters"
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

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Internal server error",
  "status_code": 500
}
```

---

## Rate Limiting

- Authentication endpoints: 5 requests per minute per IP
- User management endpoints: 100 requests per minute per user
- Search endpoints: 20 requests per minute per user

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- User IDs are UUIDs
- Passwords must be at least 8 characters long
- Email addresses must be valid and unique
- Usernames must be unique and contain only alphanumeric characters and underscores
