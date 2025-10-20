"""
Example usage of common view implementations.
This shows how to use decorators and base classes across all views.
"""
from django.http import JsonResponse, HttpRequest
from core.views.base import BaseView, AuthenticatedView, AdminView, PublicView
from core.utils.response import (
    api_response, 
    json_request, 
    success_response_decorator,
    require_jwt_auth, 
    optional_jwt_auth, 
    admin_required
)
from core.utils.view_helpers import get_service


# =============================================================================
# METHOD 1: Using Decorators (Recommended for simple views)
# =============================================================================

class ExampleView:
    """Example view using decorators for common functionality."""
    
    def __init__(self):
        self.service = get_service('user')
    
    @require_jwt_auth
    @api_response
    def list_users(self, request: HttpRequest, authenticated_user, **kwargs) -> JsonResponse:
        """List users - requires JWT auth, standardized response."""
        users = self.service.list()
        return {
            'message': 'Users retrieved successfully',
            'data': {'users': users, 'count': len(users)}
        }
    
    @require_jwt_auth
    @json_request
    @api_response
    def create_user(self, request: HttpRequest, authenticated_user, json_data, **kwargs) -> JsonResponse:
        """Create user - requires JWT auth, JSON validation, standardized response."""
        user = self.service.create(json_data)
        return {
            'message': 'User created successfully',
            'data': user,
            'status_code': 201
        }
    
    @optional_jwt_auth
    @api_response
    def public_endpoint(self, request: HttpRequest, authenticated_user=None, **kwargs) -> JsonResponse:
        """Public endpoint - optional auth, standardized response."""
        if authenticated_user:
            return {'message': f'Hello {authenticated_user.email}'}
        return {'message': 'Hello anonymous user'}
    
    @admin_required
    @api_response
    def admin_only(self, request: HttpRequest, authenticated_user, **kwargs) -> JsonResponse:
        """Admin only endpoint."""
        return {'message': 'Admin access granted'}


# =============================================================================
# METHOD 2: Using Base Classes (Recommended for complex views)
# =============================================================================

class UserView(AuthenticatedView):
    """User view using base class for authentication."""
    
    def __init__(self):
        super().__init__()
        self.user_service = self.get_service('user')
    
    def list_users(self, request: HttpRequest) -> JsonResponse:
        """List users using base class methods."""
        # Check authentication
        auth_error = self.check_auth(request)
        if auth_error:
            return auth_error
        
        try:
            users = self.user_service.list()
            return self.success_response(
                message='Users retrieved successfully',
                data={'users': users, 'count': len(users)}
            )
        except Exception as e:
            return self.handle_exception(e, "User listing")
    
    def create_user(self, request: HttpRequest) -> JsonResponse:
        """Create user with JSON validation."""
        # Check authentication
        auth_error = self.check_auth(request)
        if auth_error:
            return auth_error
        
        try:
            # Parse JSON data
            import json
            data = json.loads(request.body)
            
            user = self.user_service.create(data)
            return self.success_response(
                message='User created successfully',
                data=user,
                status_code=201
            )
        except json.JSONDecodeError:
            return self.error_response('Invalid JSON format', 400)
        except Exception as e:
            return self.handle_exception(e, "User creation")


class AdminUserView(AdminView):
    """Admin user view using admin base class."""
    
    def __init__(self):
        super().__init__()
        self.user_service = self.get_service('user')
    
    def delete_user(self, request: HttpRequest, user_id: str) -> JsonResponse:
        """Delete user - admin only."""
        # Check admin authentication
        auth_error = self.check_admin_auth(request)
        if auth_error:
            return auth_error
        
        try:
            success = self.user_service.delete(user_id)
            if success:
                return self.success_response('User deleted successfully')
            else:
                return self.error_response('User not found', 404)
        except Exception as e:
            return self.handle_exception(e, "User deletion")


class PublicUserView(PublicView):
    """Public user view - no authentication required."""
    
    def __init__(self):
        super().__init__()
        self.user_service = self.get_service('user')
    
    def get_public_info(self, request: HttpRequest) -> JsonResponse:
        """Public endpoint - no auth required."""
        try:
            # Get some public information
            public_data = {'message': 'This is public information'}
            return self.success_response(
                message='Public info retrieved',
                data=public_data
            )
        except Exception as e:
            return self.handle_exception(e, "Public info retrieval")


# =============================================================================
# METHOD 3: Hybrid Approach (Best of both worlds)
# =============================================================================

class HybridView(BaseView):
    """Hybrid view using both decorators and base class methods."""
    
    def __init__(self):
        super().__init__()
        self.user_service = self.get_service('user')
    
    @require_jwt_auth
    @api_response
    def quick_list(self, request: HttpRequest, authenticated_user, **kwargs) -> JsonResponse:
        """Quick list using decorators."""
        users = self.user_service.list()
        return {'data': {'users': users, 'count': len(users)}}
    
    def detailed_list(self, request: HttpRequest) -> JsonResponse:
        """Detailed list using base class methods."""
        auth_error = self.require_auth(request)
        if auth_error:
            return auth_error
        
        try:
            # Get user for additional context
            user = self.get_authenticated_user(request)
            
            users = self.user_service.list()
            return self.success_response(
                message='Detailed user list retrieved',
                data={
                    'users': users,
                    'count': len(users),
                    'requested_by': user.email if user else 'anonymous'
                },
                meta={'timestamp': '2024-01-01T00:00:00Z'}
            )
        except Exception as e:
            return self.handle_exception(e, "Detailed user listing")


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

"""
# In your views.py files, you can now use any of these patterns:

# Pattern 1: Decorators (simplest)
class MyView:
    @require_jwt_auth
    @api_response
    def my_method(self, request, authenticated_user, **kwargs):
        return {'data': 'some data'}

# Pattern 2: Base classes (most control)
class MyView(AuthenticatedView):
    def my_method(self, request):
        auth_error = self.check_auth(request)
        if auth_error:
            return auth_error
        return self.success_response('Success', {'data': 'some data'})

# Pattern 3: Hybrid (flexible)
class MyView(BaseView):
    @require_jwt_auth
    def quick_method(self, request, authenticated_user, **kwargs):
        return self.success_response('Quick success')
    
    def detailed_method(self, request):
        auth_error = self.require_auth(request)
        if auth_error:
            return auth_error
        return self.success_response('Detailed success')
"""
