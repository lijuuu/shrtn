# URL Shortener Platform - Complete API Endpoints Specification

## 🔐 Authentication & User Management

### **User Registration & Authentication**
```
POST   /api/auth/register/                    # User registration
POST   /api/auth/login/                       # User login (JWT)
POST   /api/auth/refresh/                     # Refresh JWT token
POST   /api/auth/logout/                      # User logout
POST   /api/auth/forgot-password/             # Forgot password
POST   /api/auth/reset-password/              # Reset password
GET    /api/auth/me/                         # Get current user profile
PUT    /api/auth/me/                        # Update current user profile
```

### **Social Authentication (Optional)**
```
POST   /api/auth/google/                      # Google OAuth login
POST   /api/auth/auth0/                       # Auth0 login
```

## 🏢 Organization Management

### **Organization CRUD**
```
GET    /api/organizations/                    # List user's organizations
POST   /api/organizations/                    # Create new organization
GET    /api/organizations/{id}/               # Get organization details
PUT    /api/organizations/{id}/               # Update organization
DELETE /api/organizations/{id}/               # Delete organization
```

### **Organization Members**
```
GET    /api/organizations/{id}/members/      # List organization members
POST   /api/organizations/{id}/members/       # Add member to organization
PUT    /api/organizations/{id}/members/{user_id}/  # Update member role
DELETE /api/organizations/{id}/members/{user_id}/  # Remove member
```

### **Organization Invites**
```
POST   /api/organizations/{id}/invites/      # Send email invite
GET    /api/organizations/{id}/invites/       # List pending invites
PUT    /api/organizations/{id}/invites/{token}/  # Accept/decline invite
DELETE /api/organizations/{id}/invites/{token}/  # Cancel invite
```

## 🏷️ Namespace Management

### **Namespace CRUD**
```
GET    /api/organizations/{org_id}/namespaces/  # List organization namespaces
POST   /api/organizations/{org_id}/namespaces/  # Create namespace
GET    /api/namespaces/{namespace}/             # Get namespace details (public)
PUT    /api/organizations/{org_id}/namespaces/{namespace}/  # Update namespace
DELETE /api/organizations/{org_id}/namespaces/{namespace}/  # Delete namespace
```

### **Namespace Validation**
```
GET    /api/namespaces/check/{namespace}/      # Check namespace availability
```

## 🔗 URL Shortening

### **URL Management**
```
GET    /api/organizations/{org_id}/namespaces/{namespace}/urls/  # List URLs in namespace
POST   /api/organizations/{org_id}/namespaces/{namespace}/urls/  # Create short URL
GET    /api/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/  # Get URL details
PUT    /api/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/  # Update URL
DELETE /api/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/  # Delete URL
```

### **URL Resolution**
```
GET    /{namespace}/{shortcode}               # Resolve short URL (public)
GET    /{namespace}/{shortcode}/qr            # Get QR code (public)
```

### **Bulk URL Operations**
```
POST   /api/organizations/{org_id}/namespaces/{namespace}/urls/bulk/  # Bulk create URLs
GET    /api/organizations/{org_id}/namespaces/{namespace}/urls/bulk/{task_id}/  # Get bulk status
GET    /api/organizations/{org_id}/namespaces/{namespace}/urls/bulk/{task_id}/download/  # Download result
```

### **URL Analytics**
```
GET    /api/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/analytics/  # Get URL analytics
GET    /api/organizations/{org_id}/namespaces/{namespace}/analytics/  # Get namespace analytics
GET    /api/organizations/{org_id}/analytics/  # Get organization analytics
```

## 🔍 Search & Discovery

### **URL Search**
```
GET    /api/organizations/{org_id}/namespaces/{namespace}/urls/search/  # Search URLs
GET    /api/organizations/{org_id}/urls/search/  # Search across organization
```

### **Tag Management**
```
GET    /api/organizations/{org_id}/namespaces/{namespace}/tags/  # List tags
GET    /api/organizations/{org_id}/namespaces/{namespace}/urls/tags/{tag}/  # Get URLs by tag
```

## 📊 Analytics & Reporting

### **Click Analytics**
```
GET    /api/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/clicks/  # Get click data
GET    /api/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/clicks/export/  # Export click data
```

### **Usage Statistics**
```
GET    /api/organizations/{org_id}/stats/     # Organization usage stats
GET    /api/organizations/{org_id}/namespaces/{namespace}/stats/  # Namespace stats
GET    /api/users/stats/                     # User stats across all organizations
```

## 🔒 Security & Access Control

### **Private URL Management**
```
POST   /api/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/private/  # Make URL private
DELETE /api/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/private/  # Make URL public
```

### **Rate Limiting**
```
GET    /api/rate-limit/status/                # Get rate limit status
```

## 📁 File Management

### **S3 Integration**
```
POST   /api/files/upload/                     # Upload file to S3
GET    /api/files/{file_id}/                  # Get file details
DELETE /api/files/{file_id}/                  # Delete file
```

## 🎯 Role-Based Access Control

### **Permission Checks**
```
GET    /api/organizations/{org_id}/permissions/  # Check user permissions
GET    /api/namespaces/{namespace}/permissions/  # Check namespace permissions
```

## 📧 Email & Notifications

### **Email Management**
```
POST   /api/emails/send/                      # Send custom email
GET    /api/emails/templates/                 # List email templates
POST   /api/emails/templates/                 # Create email template
```

## 🔧 System & Health

### **Health Checks**
```
GET    /api/health/                           # System health check
GET    /api/health/detailed/                  # Detailed health check
GET    /api/health/ready/                     # Readiness check
GET    /api/health/live/                      # Liveness check
```

### **System Information**
```
GET    /api/system/info/                      # System information
GET    /api/system/stats/                     # System statistics
```

## 📱 Mobile & QR Code

### **QR Code Generation**
```
GET    /api/qr/{namespace}/{shortcode}         # Generate QR code
POST   /api/qr/bulk/                          # Generate multiple QR codes
```

## 🏷️ Advanced Features

### **URL Expiration**
```
POST   /api/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/expire/  # Set expiration
DELETE /api/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/expire/  # Remove expiration
```

### **URL Categories**
```
GET    /api/organizations/{org_id}/namespaces/{namespace}/categories/  # List categories
POST   /api/organizations/{org_id}/namespaces/{namespace}/categories/  # Create category
PUT    /api/organizations/{org_id}/namespaces/{namespace}/categories/{id}/  # Update category
DELETE /api/organizations/{org_id}/namespaces/{namespace}/categories/{id}/  # Delete category
```

## 🔄 Webhooks & Integrations

### **Webhook Management**
```
GET    /api/organizations/{org_id}/webhooks/  # List webhooks
POST   /api/organizations/{org_id}/webhooks/  # Create webhook
PUT    /api/organizations/{org_id}/webhooks/{id}/  # Update webhook
DELETE /api/organizations/{org_id}/webhooks/{id}/  # Delete webhook
```

## 📊 Admin & Monitoring

### **Admin Operations**
```
GET    /api/admin/users/                      # List all users (admin only)
GET    /api/admin/organizations/              # List all organizations (admin only)
GET    /api/admin/namespaces/                 # List all namespaces (admin only)
GET    /api/admin/urls/                       # List all URLs (admin only)
```

### **System Monitoring**
```
GET    /api/admin/metrics/                    # System metrics
GET    /api/admin/logs/                       # System logs
GET    /api/admin/errors/                     # Error logs
```

## 🎯 Summary of Endpoint Categories

| Category | Count | Description |
|----------|-------|-------------|
| **Authentication** | 8 | User registration, login, JWT management |
| **Organizations** | 12 | Organization CRUD, members, invites |
| **Namespaces** | 6 | Namespace management and validation |
| **URL Management** | 15 | URL CRUD, resolution, analytics |
| **Bulk Operations** | 3 | Bulk URL creation and management |
| **Analytics** | 8 | Click tracking, usage statistics |
| **Search & Discovery** | 4 | URL search and tag management |
| **Security** | 4 | Private URLs, rate limiting |
| **File Management** | 3 | S3 integration |
| **System** | 8 | Health checks, monitoring |
| **Advanced Features** | 8 | QR codes, expiration, categories |
| **Admin** | 8 | Administrative operations |

**Total Endpoints: ~85+**

## 🚀 Implementation Priority

### **Phase 1: Core Features**
1. Authentication & User Management
2. Organization Management
3. Namespace Management
4. Basic URL Shortening
5. URL Resolution

### **Phase 2: Advanced Features**
1. Bulk URL Operations
2. Analytics & Reporting
3. Search & Discovery
4. Security Features

### **Phase 3: Optional Features**
1. Social Authentication
2. Advanced Analytics
3. Webhooks & Integrations
4. Admin Operations

This comprehensive endpoint specification covers all the requirements for your URL Shortener platform! 🎯
