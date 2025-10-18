# Database Schema Summary - URL Shortener Platform

## 🗄️ Complete Table Structure

### **PostgreSQL Tables (Relational Data)**

#### **1. Users Table**
```sql
users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

#### **2. Organizations Table**
```sql
organizations (
    org_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

#### **3. Organization_Members Table**
```sql
organization_members (
    org_id INTEGER NOT NULL REFERENCES organizations(org_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    can_view BOOLEAN DEFAULT FALSE,
    can_admin BOOLEAN DEFAULT FALSE,
    can_update BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (org_id, user_id)
)
```

#### **4. Invites Table**
```sql
invites (
    invite_id SERIAL PRIMARY KEY,
    invitee_email VARCHAR(254) NOT NULL,
    org_id INTEGER NOT NULL REFERENCES organizations(org_id),
    inviter_user_id INTEGER NOT NULL REFERENCES users(user_id),
    can_view BOOLEAN DEFAULT FALSE,
    can_admin BOOLEAN DEFAULT FALSE,
    can_update BOOLEAN DEFAULT FALSE,
    used BOOLEAN DEFAULT FALSE,
    secret VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
)
```

#### **5. Namespaces Table**
```sql
namespaces (
    namespace_id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(org_id),
    created_by_user_id INTEGER NOT NULL REFERENCES users(user_id),
    name VARCHAR(255) UNIQUE NOT NULL,  -- Globally unique
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

#### **6. Bulk_Uploads Table**
```sql
bulk_uploads (
    upload_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    org_id INTEGER NOT NULL REFERENCES organizations(org_id),
    namespace_id INTEGER NOT NULL REFERENCES namespaces(namespace_id),
    s3_link VARCHAR(500) NOT NULL,
    status VARCHAR(20) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

### **ScyllaDB Tables (High-Performance URL Storage)**

#### **7. Short_Urls Table**
```sql
-- Keyspace: hirethon_keyspace
-- Table: short_urls
-- Partition Key: (namespace_id, shortcode)
-- Clustering Key: created_at

short_urls (
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
)
```

## 🔗 Relationships & Data Flow

### **User Registration Flow:**
```
1. User registers → users table
2. Auto-create organization → organizations table (owner_id = user_id)
3. Auto-add user as admin → organization_members table (can_admin = TRUE)
```

### **Organization Management:**
```
1. Admin creates namespace → namespaces table
2. Admin invites users → invites table
3. User accepts invite → organization_members table
4. Members get permissions based on invite role
```

### **URL Shortening Flow:**
```
1. User creates short URL → short_urls table (ScyllaDB)
2. Bulk operations → bulk_uploads table (PostgreSQL) + S3
3. URL resolution → Query ScyllaDB by (namespace_id, shortcode)
```

## 🎯 Key Design Principles

### **PostgreSQL (Relational Data):**
- **Users & Organizations**: User management, permissions, relationships
- **Invites & Members**: Role-based access control
- **Namespaces**: Globally unique namespace management
- **Bulk Operations**: Track file uploads and processing status

### **ScyllaDB (High-Performance Storage):**
- **Short URLs**: Optimized for fast reads/writes
- **Partition Key**: (namespace_id, shortcode) for even distribution
- **Clustering Key**: created_at for chronological ordering
- **Secondary Indexes**: For filtered queries (creator, expiry, privacy)

### **Permission Model:**
```python
# Role definitions
ADMIN = {"can_view": True, "can_admin": True, "can_update": True}
EDITOR = {"can_view": True, "can_admin": False, "can_update": True}  
VIEWER = {"can_view": True, "can_admin": False, "can_update": False}
```

## 📊 Data Distribution Strategy

### **PostgreSQL:**
- **Users**: ~10K-100K records
- **Organizations**: ~1K-10K records  
- **Namespaces**: ~1K-10K records
- **Bulk Uploads**: ~1K-100K records

### **ScyllaDB:**
- **Short URLs**: ~1M-100M records
- **Partition Key**: (namespace_id, shortcode) ensures even distribution
- **3 Shards**: Optimal for single-node setup
- **TTL Support**: For expiring URLs

## 🚀 Performance Optimizations

### **PostgreSQL Indexes:**
```sql
-- Critical indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_organizations_owner ON organizations(owner_id);
CREATE INDEX idx_org_members_user ON organization_members(user_id);
CREATE INDEX idx_namespaces_name_unique ON namespaces(name);
CREATE INDEX idx_invites_secret ON invites(secret);
```

### **ScyllaDB Optimizations:**
```sql
-- Secondary indexes for filtered queries
CREATE INDEX idx_short_urls_creator ON short_urls(created_by_user_id);
CREATE INDEX idx_short_urls_expiry ON short_urls(expiry);
CREATE INDEX idx_short_urls_private ON short_urls(is_private);
```

## 🔧 Django Model Integration

### **PostgreSQL Models:**
- `User` → `users` table
- `Organization` → `organizations` table
- `OrganizationMember` → `organization_members` table
- `Invite` → `invites` table
- `Namespace` → `namespaces` table
- `BulkUpload` → `bulk_uploads` table

### **ScyllaDB Integration:**
- `ShortUrl` → Python class for ScyllaDB operations
- `BulkMapping` → In-memory data structure for Excel processing
- Repository pattern for ScyllaDB operations

## 📈 Scalability Considerations

### **PostgreSQL:**
- **Vertical Scaling**: Increase CPU/RAM for better performance
- **Read Replicas**: For analytics and reporting queries
- **Connection Pooling**: For high-concurrency scenarios

### **ScyllaDB:**
- **Horizontal Scaling**: Add more nodes for linear scaling
- **3 Shards**: Current setup for single node
- **Consistency Levels**: Configurable for performance vs consistency

This schema provides a solid foundation for your URL shortener platform with proper separation of concerns and optimal performance characteristics! 🎯
