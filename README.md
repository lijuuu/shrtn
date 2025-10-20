# URL Shortener Service

A complete URL shortening service with user management, organizations, and analytics.

## What's Included

### ✅ Core Features
- **User Management**: Registration, login, profiles
- **Organizations**: Company management with user roles
- **Namespaces**: Organize URLs into folders
- **URL Shortening**: Create and manage short links
- **Analytics**: Track clicks and performance
- **API Documentation**: Complete Swagger/OpenAPI docs

### ✅ Testing System
- **Complete Test Suite**: Tests for all endpoints
- **Data Generation**: Create 1000+ test entries
- **Workflow Tests**: End-to-end testing
- **Health Checks**: Monitor system status

## Quick Start

### 1. Start Services
```bash
docker-compose -f local.yml up postgres redis scylla -d
```

### 2. Run Tests
```bash
pytest tests/ -v
```

### 3. Add Test Data
```bash
python manage.py generate_bulk_data --users 1000 --organizations 1000 --namespaces 1000 --urls 1000 --clicks 5000
```

### 4. View Documentation
Visit: http://localhost:8000/api/docs/

## Key Files

### Core Application
- `users/` - User management and authentication
- `organizations/` - Company and team management
- `namespaces/` - URL organization
- `urls/` - URL shortening service
- `analytics/` - Click tracking and analytics

### Testing
- `tests/` - Complete test suite
- `core/management/commands/generate_bulk_data.py` - Data generation tool

### Configuration
- `config/settings/` - Django settings
- `local.yml` - Docker services
- `.envs/` - Environment variables

## API Endpoints

### Health
- `GET /health/` - Basic health check
- `GET /health/detailed/` - Detailed system status

### Authentication
- `POST /auth/register/` - User registration
- `POST /auth/login/` - User login
- `POST /auth/refresh/` - Refresh token

### Users
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{id}/` - Get user details
- `PUT /api/v1/users/{id}/` - Update user

### Organizations
- `GET /api/v1/organizations/` - List organizations
- `POST /api/v1/organizations/` - Create organization
- `GET /api/v1/organizations/{id}/` - Get organization

### Namespaces
- `GET /api/v1/namespaces/` - List namespaces
- `POST /api/v1/namespaces/` - Create namespace

### URLs
- `GET /api/v1/urls/` - List short URLs
- `POST /api/v1/urls/` - Create short URL
- `GET /{shortcode}` - Redirect to original URL

### Analytics
- `GET /api/v1/analytics/` - Get analytics data
- `GET /api/v1/analytics/clicks/` - Click statistics

## Database

- **PostgreSQL**: Main database for users, organizations, namespaces
- **ScyllaDB**: High-performance storage for URLs and analytics
- **Redis**: Caching and session storage

## Environment Setup

Required environment variables in `.envs/.local/.django`:
```
DATABASE_URL=postgres://user:password@postgres:5432/shrtn
CELERY_BROKER_URL=redis://redis:6379/0
REDIS_URL=redis://redis:6379/0
```

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Tests
```bash
pytest tests/test_health_endpoints.py -v
pytest tests/test_auth_endpoints.py -v
```

### Generate Test Data
```bash
python manage.py generate_bulk_data --users 100 --organizations 50 --namespaces 100 --urls 200 --clicks 500
```

## Documentation

- **API Docs**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema**: http://localhost:8000/api/schema/

## Status

✅ **Complete and Working**
- All endpoints tested and working
- Data generation system ready
- Documentation available
- Ready for production use