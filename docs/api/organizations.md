# Organizations API Documentation

## Overview
Organization management endpoints for creating, managing organizations, members, and invitations.

## Base URL
```
/api/v1/organizations/
```

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## Endpoints

### 1. List Organizations
**GET** `/api/v1/organizations/`

List all organizations the user has access to.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (integer, optional) - Page number (default: 1)
- `limit` (integer, optional) - Items per page (default: 20)
- `search` (string, optional) - Search by organization name

**Response:**
```json
{
  "success": true,
  "payload": [
    {
      "id": "uuid",
      "name": "Organization Name",
      "description": "Organization description",
      "owner": {
        "id": "uuid",
        "name": "Owner Name",
        "email": "owner@example.com"
      },
      "created_at": "2024-01-01T00:00:00Z",
      "member_count": 5,
      "role": "admin"
    }
  ],
  "meta": {
    "count": 10,
    "page": 1,
    "total_pages": 1
  }
}
```

---

### 2. Create Organization
**POST** `/api/v1/organizations/create/`

Create a new organization.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "New Organization",
  "description": "Organization description"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "name": "New Organization",
    "description": "Organization description",
    "owner": {
      "id": "uuid",
      "name": "Owner Name",
      "email": "owner@example.com"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "member_count": 1
  }
}
```

**Status Codes:**
- `201` - Created
- `400` - Bad Request (validation errors)
- `409` - Conflict (organization name already exists)

---

### 3. Get Organization
**GET** `/api/v1/organizations/{org_id}/`

Get organization details by ID.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "name": "Organization Name",
    "description": "Organization description",
    "owner": {
      "id": "uuid",
      "name": "Owner Name",
      "email": "owner@example.com"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "member_count": 5,
    "user_role": "admin",
    "permissions": {
      "can_view": true,
      "can_update": true,
      "can_delete": true,
      "can_manage_members": true
    }
  }
}
```

**Status Codes:**
- `200` - Success
- `404` - Organization not found
- `403` - Access denied

---

### 4. Update Organization
**PUT** `/api/v1/organizations/{org_id}/update/`

Update organization details.

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
  "name": "Updated Organization Name",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "name": "Updated Organization Name",
    "description": "Updated description",
    "owner": {
      "id": "uuid",
      "name": "Owner Name",
      "email": "owner@example.com"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request
- `403` - Insufficient permissions
- `404` - Organization not found

---

### 5. Delete Organization
**DELETE** `/api/v1/organizations/{org_id}/delete/`

Delete an organization (owner only).

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID

**Response:**
```json
{
  "success": true,
  "message": "Organization deleted successfully"
}
```

**Status Codes:**
- `200` - Success
- `403` - Only owner can delete organization
- `404` - Organization not found

---

## Member Management

### 6. Get Members
**GET** `/api/v1/organizations/{org_id}/members/`

Get organization members.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID

**Query Parameters:**
- `page` (integer, optional) - Page number
- `limit` (integer, optional) - Items per page
- `role` (string, optional) - Filter by role (admin, member)

**Response:**
```json
{
  "success": true,
  "payload": [
    {
      "id": "uuid",
      "user": {
        "id": "uuid",
        "name": "User Name",
        "email": "user@example.com",
        "username": "username"
      },
      "role": "admin",
      "joined_at": "2024-01-01T00:00:00Z",
      "permissions": {
        "can_view": true,
        "can_update": true,
        "can_delete": false,
        "can_manage_members": true
      }
    }
  ],
  "meta": {
    "count": 5,
    "page": 1,
    "total_pages": 1
  }
}
```

---

### 7. Remove Member
**DELETE** `/api/v1/organizations/{org_id}/members/{user_id}/remove/`

Remove a member from the organization.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID
- `user_id` (uuid, required) - User ID to remove

**Response:**
```json
{
  "success": true,
  "message": "Member removed successfully"
}
```

**Status Codes:**
- `200` - Success
- `403` - Insufficient permissions
- `404` - Member not found

---

## Invitation Management

### 8. Create Invite
**POST** `/api/v1/organizations/{org_id}/invites/create/`

Create an invitation for a user to join the organization.

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
  "email": "invitee@example.com",
  "role": "member",
  "message": "Welcome to our organization!"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "email": "invitee@example.com",
    "role": "member",
    "message": "Welcome to our organization!",
    "token": "invitation_token",
    "expires_at": "2024-01-08T00:00:00Z",
    "created_by": {
      "id": "uuid",
      "name": "Inviter Name",
      "email": "inviter@example.com"
    },
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Status Codes:**
- `201` - Created
- `400` - Bad Request
- `403` - Insufficient permissions
- `409` - User already a member

---

### 9. Get Pending Invites
**GET** `/api/v1/organizations/{org_id}/invites/`

Get pending invitations for an organization.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID

**Response:**
```json
{
  "success": true,
  "payload": [
    {
      "id": "uuid",
      "email": "invitee@example.com",
      "role": "member",
      "message": "Welcome to our organization!",
      "expires_at": "2024-01-08T00:00:00Z",
      "created_by": {
        "id": "uuid",
        "name": "Inviter Name",
        "email": "inviter@example.com"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "count": 3
  }
}
```

---

### 10. Get Sent Invites
**GET** `/api/v1/organizations/invites/sent/`

Get invitations sent by the current user.

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
      "email": "invitee@example.com",
      "role": "member",
      "organization": {
        "id": "uuid",
        "name": "Organization Name"
      },
      "expires_at": "2024-01-08T00:00:00Z",
      "status": "pending",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "count": 5
  }
}
```

---

### 11. Get Received Invites
**GET** `/api/v1/organizations/invites/received/`

Get invitations received by the current user.

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
      "role": "member",
      "organization": {
        "id": "uuid",
        "name": "Organization Name"
      },
      "message": "Welcome to our organization!",
      "expires_at": "2024-01-08T00:00:00Z",
      "created_by": {
        "id": "uuid",
        "name": "Inviter Name",
        "email": "inviter@example.com"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "count": 2
  }
}
```

---

### 12. Revoke Invite
**DELETE** `/api/v1/organizations/invites/{invite_id}/revoke/`

Revoke a sent invitation.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `invite_id` (uuid, required) - Invitation ID

**Response:**
```json
{
  "success": true,
  "message": "Invitation revoked successfully"
}
```

---

### 13. Reject Invite
**POST** `/api/v1/organizations/invites/{invite_id}/reject/`

Reject a received invitation.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `invite_id` (uuid, required) - Invitation ID

**Response:**
```json
{
  "success": true,
  "message": "Invitation rejected successfully"
}
```

---

### 14. Get Invite Details
**GET** `/api/v1/organizations/invites/{token}/details/`

Get invitation details by token (public endpoint).

**Path Parameters:**
- `token` (string, required) - Invitation token

**Response:**
```json
{
  "success": true,
  "payload": {
    "id": "uuid",
    "email": "invitee@example.com",
    "role": "member",
    "organization": {
      "id": "uuid",
      "name": "Organization Name",
      "description": "Organization description"
    },
    "message": "Welcome to our organization!",
    "expires_at": "2024-01-08T00:00:00Z",
    "created_by": {
      "id": "uuid",
      "name": "Inviter Name",
      "email": "inviter@example.com"
    },
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### 15. Accept Invite
**POST** `/api/v1/organizations/invites/{org_id}/accept/`

Accept an invitation to join an organization.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID

**Request Body:**
```json
{
  "token": "invitation_token"
}
```

**Response:**
```json
{
  "success": true,
  "payload": {
    "organization": {
      "id": "uuid",
      "name": "Organization Name"
    },
    "role": "member",
    "permissions": {
      "can_view": true,
      "can_update": false,
      "can_delete": false,
      "can_manage_members": false
    }
  },
  "message": "Successfully joined the organization"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Validation error",
  "errors": [
    "Field 'name' is required",
    "Field 'email' must be a valid email address"
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
  "message": "Organization not found",
  "status_code": 404
}
```

### 409 Conflict
```json
{
  "success": false,
  "message": "Organization name already exists",
  "status_code": 409
}
```

---

## Rate Limiting

- Organization creation: 5 requests per hour per user
- Member management: 50 requests per hour per user
- Invitation management: 20 requests per hour per user

---

## Notes

- Organization names must be unique
- Only organization owners can delete organizations
- Invitations expire after 7 days
- Users can only be invited once per organization
- Member roles: `admin`, `member`
- All timestamps are in ISO 8601 format (UTC)
