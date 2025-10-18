# App Structure - Entity-Based Architecture

## 🏗️ Recommended App Structure

```
project/
├── apps/
│   ├── users/                    # User entity
│   │   ├── models.py            # User model (PostgreSQL)
│   │   ├── repositories.py      # User data access
│   │   ├── services.py          # User business logic
│   │   ├── views.py             # User HTTP endpoints
│   │   ├── serializers.py       # User data transformation
│   │   └── urls.py              # User routing
│   │
│   ├── organizations/           # Organization entity
│   │   ├── models.py            # Organization, Member, Invite models (PostgreSQL)
│   │   ├── repositories.py      # Organization data access
│   │   ├── services.py          # Organization business logic
│   │   ├── views.py             # Organization HTTP endpoints
│   │   ├── serializers.py       # Organization data transformation
│   │   └── urls.py              # Organization routing
│   │
│   ├── namespaces/              # Namespace entity
│   │   ├── models.py            # Namespace model (PostgreSQL)
│   │   ├── repositories.py      # Namespace data access
│   │   ├── services.py          # Namespace business logic
│   │   ├── views.py             # Namespace HTTP endpoints
│   │   ├── serializers.py       # Namespace data transformation
│   │   └── urls.py              # Namespace routing
│   │
│   ├── urls/                    # URL entity (Short URLs)
│   │   ├── models.py            # ShortUrl model (ScyllaDB representation)
│   │   ├── repositories.py      # ScyllaDB data access
│   │   ├── services.py          # URL business logic
│   │   ├── views.py             # URL HTTP endpoints
│   │   ├── serializers.py       # URL data transformation
│   │   └── urls.py              # URL routing
│   │
│   └── analytics/               # Analytics entity
│       ├── models.py            # Analytics models
│       ├── repositories.py      # Analytics data access
│       ├── services.py          # Analytics business logic
│       ├── views.py             # Analytics HTTP endpoints
│       ├── serializers.py       # Analytics data transformation
│       └── urls.py              # Analytics routing
│
├── core/                        # Core infrastructure
│   ├── database/                # Database configurations
│   │   ├── postgres.py          # PostgreSQL connection
│   │   ├── scylla.py            # ScyllaDB connection
│   │   └── base.py              # Base database interface
│   │
│   ├── dependencies/            # Dependency injection
│   │   ├── __init__.py
│   │   ├── database.py          # Database dependency injection
│   │   └── services.py          # Service dependency injection
│   │
│   └── exceptions/              # Custom exceptions
│       ├── __init__.py
│       ├── database.py          # Database exceptions
│       └── business.py          # Business logic exceptions
│
└── config/                      # Configuration
    ├── settings/
    └── urls.py
```

## 🎯 Entity Responsibilities

### **Users App**
- **Database**: PostgreSQL
- **Responsibility**: User management, authentication, profiles
- **Models**: User
- **Operations**: CRUD, authentication, profile management

### **Organizations App**
- **Database**: PostgreSQL
- **Responsibility**: Organization management, members, invites
- **Models**: Organization, OrganizationMember, Invite
- **Operations**: CRUD, member management, invite system

### **Namespaces App**
- **Database**: PostgreSQL
- **Responsibility**: Namespace management, global uniqueness
- **Models**: Namespace
- **Operations**: CRUD, uniqueness validation

### **URLs App**
- **Database**: ScyllaDB
- **Responsibility**: URL shortening, resolution, management
- **Models**: ShortUrl (ScyllaDB representation)
- **Operations**: CRUD, resolution, analytics

### **Analytics App**
- **Database**: ScyllaDB + PostgreSQL
- **Responsibility**: Click tracking, reporting, statistics
- **Models**: ClickEvent, Analytics
- **Operations**: Tracking, reporting, statistics

## 🔧 Dependency Injection Setup

### **Database Dependencies**
```python
# core/dependencies/database.py
from abc import ABC, abstractmethod
from typing import Protocol

class DatabaseConnection(Protocol):
    def connect(self): ...
    def disconnect(self): ...

class PostgreSQLConnection:
    def connect(self): ...
    def disconnect(self): ...

class ScyllaDBConnection:
    def connect(self): ...
    def disconnect(self): ...

class DatabaseDependency:
    def __init__(self):
        self.postgres = PostgreSQLConnection()
        self.scylla = ScyllaDBConnection()
    
    def get_postgres(self) -> PostgreSQLConnection:
        return self.postgres
    
    def get_scylla(self) -> ScyllaDBConnection:
        return self.scylla
```

### **Service Dependencies**
```python
# core/dependencies/services.py
from users.services import UserService
from organizations.services import OrganizationService
from namespaces.services import NamespaceService
from urls.services import UrlService
from analytics.services import AnalyticsService

class ServiceDependency:
    def __init__(self, db_dependency):
        self.db = db_dependency
        
        # Initialize services with database dependencies
        self.user_service = UserService(self.db.get_postgres())
        self.org_service = OrganizationService(self.db.get_postgres())
        self.namespace_service = NamespaceService(self.db.get_postgres())
        self.url_service = UrlService(self.db.get_scylla())
        self.analytics_service = AnalyticsService(self.db.get_scylla())
    
    def get_user_service(self) -> UserService:
        return self.user_service
    
    def get_org_service(self) -> OrganizationService:
        return self.org_service
    
    def get_namespace_service(self) -> NamespaceService:
        return self.namespace_service
    
    def get_url_service(self) -> UrlService:
        return self.url_service
    
    def get_analytics_service(self) -> AnalyticsService:
        return self.analytics_service
```

## 🎯 Benefits of This Structure

### **1. Clear Separation of Concerns**
- Each app handles one entity
- Database responsibilities are clear
- Business logic is isolated

### **2. Dependency Injection**
- Services are injected with database connections
- Easy to test and mock
- Loose coupling between layers

### **3. Scalability**
- Each app can be scaled independently
- Database connections are managed centrally
- Easy to add new entities

### **4. Maintainability**
- Clear boundaries between entities
- Easy to understand and modify
- Consistent patterns across apps
