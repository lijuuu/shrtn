# Database Schema - URL Shortener Platform

## 🗄️ PostgreSQL Tables

### **1. Users Table**
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_verified ON users(verified);
```

### **2. Organizations Table**
```sql
CREATE TABLE organizations (
    org_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_organizations_owner ON organizations(owner_id);
CREATE INDEX idx_organizations_name ON organizations(name);
```

### **3. Organization_Members Table**
```sql
CREATE TABLE organization_members (
    org_id INTEGER NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    can_view BOOLEAN DEFAULT FALSE,
    can_admin BOOLEAN DEFAULT FALSE,
    can_update BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (org_id, user_id)
);

-- Indexes
CREATE INDEX idx_org_members_user ON organization_members(user_id);
CREATE INDEX idx_org_members_permissions ON organization_members(can_admin, can_update, can_view);
```

### **4. Invites Table**
```sql
CREATE TABLE invites (
    invite_id SERIAL PRIMARY KEY,
    invitee_email VARCHAR(254) NOT NULL,
    org_id INTEGER NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    inviter_user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    can_view BOOLEAN DEFAULT FALSE,
    can_admin BOOLEAN DEFAULT FALSE,
    can_update BOOLEAN DEFAULT FALSE,
    used BOOLEAN DEFAULT FALSE,
    secret VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Indexes
CREATE INDEX idx_invites_email ON invites(invitee_email);
CREATE INDEX idx_invites_org ON invites(org_id);
CREATE INDEX idx_invites_secret ON invites(secret);
CREATE INDEX idx_invites_expires ON invites(expires_at);
```

### **5. Namespaces Table**
```sql
CREATE TABLE namespaces (
    namespace_id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    created_by_user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(255) UNIQUE NOT NULL,  -- Globally unique
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_namespaces_org ON namespaces(org_id);
CREATE INDEX idx_namespaces_creator ON namespaces(created_by_user_id);
CREATE UNIQUE INDEX idx_namespaces_name_unique ON namespaces(name);
```

### **6. Bulk_Uploads Table**
```sql
CREATE TABLE bulk_uploads (
    upload_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    org_id INTEGER NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    namespace_id INTEGER NOT NULL REFERENCES namespaces(namespace_id) ON DELETE CASCADE,
    s3_link VARCHAR(500) NOT NULL,
    status VARCHAR(20) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_bulk_uploads_user ON bulk_uploads(user_id);
CREATE INDEX idx_bulk_uploads_org ON bulk_uploads(org_id);
CREATE INDEX idx_bulk_uploads_namespace ON bulk_uploads(namespace_id);
CREATE INDEX idx_bulk_uploads_status ON bulk_uploads(status);
```

## 🗄️ ScyllaDB Tables

### **7. Short_Urls Table (ScyllaDB)**
```sql
-- Keyspace: hirethon_keyspace
-- Table: short_urls
-- Partition Key: (namespace_id, shortcode)
-- Clustering Key: (created_at)

CREATE TABLE short_urls (
    namespace_id INT,
    shortcode TEXT,
    created_by_user_id INT,
    original_url TEXT,
    expiry TIMESTAMP,
    click_count INT DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_private BOOLEAN DEFAULT FALSE,
    tags SET<TEXT>,
    PRIMARY KEY ((namespace_id, shortcode), created_at)
) WITH CLUSTERING ORDER BY (created_at DESC)
  AND compaction = {'class': 'SizeTieredCompactionStrategy'}
  AND gc_grace_seconds = 864000;

-- Secondary Indexes
CREATE INDEX idx_short_urls_creator ON short_urls(created_by_user_id);
CREATE INDEX idx_short_urls_expiry ON short_urls(expiry);
CREATE INDEX idx_short_urls_private ON short_urls(is_private);
```

## 📊 In-App Data Structures

### **8. Excel/Bulk Mapping (In-Memory)**
```python
# Python data structure for bulk operations
bulk_mapping = [
    {
        "shortcode": "abc123",
        "original_url": "https://example.com/page1"
    },
    {
        "shortcode": "def456", 
        "original_url": "https://example.com/page2"
    }
]
```

## 🔗 Relationships Overview

```
Users (1) ──→ (M) Organizations (owner)
Users (M) ──→ (M) Organizations (via Organization_Members)
Users (1) ──→ (M) Namespaces (creator)
Users (1) ──→ (M) Invites (inviter)
Users (1) ──→ (M) Bulk_Uploads

Organizations (1) ──→ (M) Organization_Members
Organizations (1) ──→ (M) Invites
Organizations (1) ──→ (M) Namespaces
Organizations (1) ──→ (M) Bulk_Uploads

Namespaces (1) ──→ (M) Short_Urls (ScyllaDB)
Namespaces (1) ──→ (M) Bulk_Uploads
```

## 🎯 Key Design Decisions

### **PostgreSQL Tables:**
- **Users**: Core user data with authentication
- **Organizations**: Multi-tenant structure
- **Organization_Members**: Role-based permissions (can_view, can_admin, can_update)
- **Invites**: Email-based invitations with expiration
- **Namespaces**: Globally unique namespace management
- **Bulk_Uploads**: Track bulk operations and S3 file links

### **ScyllaDB Tables:**
- **Short_Urls**: High-performance URL storage with composite partition key
- **Partition Key**: (namespace_id, shortcode) for optimal sharding
- **Clustering Key**: created_at for time-based ordering
- **Secondary Indexes**: For querying by creator, expiry, privacy

### **Permission Model:**
```python
# Role definitions
ADMIN = {"can_view": True, "can_admin": True, "can_update": True}
EDITOR = {"can_view": True, "can_admin": False, "can_update": True}  
VIEWER = {"can_view": True, "can_admin": False, "can_update": False}
```

## 🚀 Performance Optimizations

### **PostgreSQL Indexes:**
- Email lookups (users, invites)
- Organization relationships
- Permission checks
- Namespace uniqueness

### **ScyllaDB Optimizations:**
- Composite partition key for even distribution
- Clustering by timestamp for chronological queries
- Secondary indexes for filtered queries
- TTL support for expiring URLs

This schema provides a solid foundation for your URL shortener platform with proper separation of concerns between PostgreSQL (relational data) and ScyllaDB (high-performance URL storage)! 🎯
