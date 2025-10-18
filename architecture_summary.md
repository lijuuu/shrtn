# Entity-Based Architecture with Dependency Injection

## 🏗️ Complete Architecture Overview

### **App Structure (Entity-Based)**

```
project/
├── users/                    # User entity (PostgreSQL)
├── organizations/           # Organization entity (PostgreSQL)  
├── shorturls/              # Legacy ScyllaDB integration
├── urls/                   # URL entity (ScyllaDB) - NEW
├── core/                   # Infrastructure layer
│   ├── database/           # Database connections
│   ├── dependencies/       # Dependency injection
│   └── exceptions/         # Custom exceptions
└── config/                 # Configuration
```

## 🎯 Entity Responsibilities

### **Users App (PostgreSQL)**
- **Database**: PostgreSQL
- **Models**: User
- **Repository**: UserRepository
- **Service**: UserService
- **Views**: UserView
- **Responsibility**: User management, authentication, profiles

### **Organizations App (PostgreSQL)**
- **Database**: PostgreSQL
- **Models**: Organization, OrganizationMember, Invite
- **Repository**: OrganizationRepository
- **Service**: OrganizationService
- **Views**: OrganizationView
- **Responsibility**: Organization management, members, invites

### **URLs App (ScyllaDB) - NEW**
- **Database**: ScyllaDB
- **Models**: ShortUrl (Python class)
- **Repository**: UrlRepository
- **Service**: UrlService
- **Views**: UrlView
- **Responsibility**: URL shortening, resolution, management

## 🔧 Dependency Injection Setup

### **Database Layer**
```python
# core/database/base.py
class DatabaseConnection(Protocol):
    def connect(self): ...
    def disconnect(self): ...
    def is_connected(self): ...

class Repository(ABC):
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
```

### **PostgreSQL Connection**
```python
# core/database/postgres.py
class PostgreSQLConnection:
    def connect(self) -> None:
        # Django handles connection automatically
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
```

### **ScyllaDB Connection**
```python
# core/database/scylla.py
class ScyllaDBConnection:
    def __init__(self):
        self.scylla_db = None
    
    def connect(self) -> None:
        self.scylla_db = ScyllaDB()
```

### **Dependency Container**
```python
# core/dependencies/database.py
class DatabaseDependency:
    def __init__(self):
        self._postgres = None
        self._scylla = None
    
    def get_postgres(self) -> PostgreSQLConnection:
        if self._postgres is None:
            self._postgres = PostgreSQLConnection()
            self._postgres.connect()
        return self._postgres
    
    def get_scylla(self) -> ScyllaDBConnection:
        if self._scylla is None:
            self._scylla = ScyllaDBConnection()
            self._scylla.connect()
        return self._scylla
```

### **Service Container**
```python
# core/dependencies/services.py
class ServiceDependency:
    def __init__(self):
        self._user_service = None
        self._url_service = None
    
    def get_user_service(self) -> UserService:
        if self._user_service is None:
            postgres = db_dependency.get_postgres()
            user_repository = UserRepository(postgres)
            self._user_service = UserService(user_repository)
        return self._user_service
    
    def get_url_service(self) -> UrlService:
        if self._url_service is None:
            scylla = db_dependency.get_scylla()
            url_repository = UrlRepository(scylla)
            self._url_service = UrlService(url_repository)
        return self._url_service
```

## 🎯 Usage in Views

### **Before (Tight Coupling)**
```python
# users/views.py - OLD WAY
class UserView:
    def __init__(self):
        self.service = UserService()  # Direct instantiation
```

### **After (Dependency Injection)**
```python
# users/views.py - NEW WAY
from core.dependencies.services import service_dependency

class UserView:
    def __init__(self):
        self.service = service_dependency.get_user_service()
    
    def create_user(self, request):
        # Service is injected with proper database connection
        user = self.service.create(request.data)
        return JsonResponse({
            'message': 'User created successfully',
            'status_code': 201,
            'success': True,
            'payload': user
        })
```

## 🗄️ Database Separation Strategy

### **PostgreSQL (Relational Data)**
- **Users**: User profiles, authentication
- **Organizations**: Organization management
- **Organization Members**: Role-based permissions
- **Invites**: Email invitations
- **Namespaces**: Global namespace management
- **Bulk Uploads**: File processing tracking

### **ScyllaDB (High-Performance Storage)**
- **Short URLs**: URL shortening, resolution
- **Click Analytics**: Click tracking (future)
- **Performance**: Optimized for high read/write throughput

## 🚀 Benefits of This Architecture

### **1. Clear Separation of Concerns**
- Each app handles one entity
- Database responsibilities are explicit
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
- Consistent patterns across apps
- Easy to understand and modify

### **5. Testability**
- Services can be easily mocked
- Database connections can be stubbed
- Unit tests are straightforward

## 🔄 Data Flow

### **URL Creation Flow**
```
1. UserView.create_url() 
   ↓
2. UrlService.create() (injected with UrlRepository)
   ↓
3. UrlRepository.create() (injected with ScyllaDBConnection)
   ↓
4. ScyllaDB.create_short_url()
   ↓
5. Return ShortUrl object
```

### **User Creation Flow**
```
1. UserView.create_user()
   ↓
2. UserService.create() (injected with UserRepository)
   ↓
3. UserRepository.create() (injected with PostgreSQLConnection)
   ↓
4. Django ORM User.objects.create()
   ↓
5. Return User object
```

## 🎯 Next Steps

### **1. Implement Missing Repositories**
- OrganizationRepository
- NamespaceRepository
- Update existing repositories to use dependency injection

### **2. Create Service Classes**
- OrganizationService
- NamespaceService
- Update existing services to use dependency injection

### **3. Update Views**
- Use dependency injection in all views
- Implement consistent JSON response structure

### **4. Add Tests**
- Unit tests for repositories
- Unit tests for services
- Integration tests for views

This architecture provides a solid foundation for your URL shortener platform with proper separation of concerns, dependency injection, and clear database responsibilities! 🎯
