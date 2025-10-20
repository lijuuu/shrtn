"""
Base view classes for consistent implementation across all views.
"""
import logging
from typing import Any, Dict, Optional
from django.http import JsonResponse, HttpRequest
from django.contrib.auth import get_user_model
from core.utils.view_helpers import (
    get_service, 
    get_authenticated_user
)
from core.utils.response import (
    success_response,
    error_response,
    server_error_response,
    unauthorized_response
)

logger = logging.getLogger(__name__)
User = get_user_model()


class BaseView:
    """
    Base view class with common functionality for all views.
    """
    
    def __init__(self):
        """Initialize with cached service instances."""
        self._services = {}
    
    def get_service(self, service_name: str):
        """Get cached service instance."""
        if service_name not in self._services:
            self._services[service_name] = get_service(service_name)
        return self._services[service_name]
    
    def get_authenticated_user(self, request: HttpRequest) -> Optional[User]:
        """Get authenticated user from JWT token."""
        return get_authenticated_user(request)
    
    def require_auth(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Check authentication and return error if not authenticated."""
        user = self.get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        return None
    
    # Response methods removed - use core.utils.response directly
    
    def handle_exception(self, e: Exception, operation: str) -> JsonResponse:
        """Handle exceptions with standardized error responses."""
        return server_error_response(f"{operation} failed")


class AuthenticatedView(BaseView):
    """
    Base view class for endpoints that require authentication.
    """
    
    def __init__(self):
        super().__init__()
        self.require_auth = True
    
    def check_auth(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Check authentication for authenticated views."""
        return self.require_auth(request)


class AdminView(BaseView):
    """
    Base view class for admin-only endpoints.
    """
    
    def check_admin_auth(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Check admin authentication."""
        user = self.get_authenticated_user(request)
        if not user:
            return self.error_response(
                message='Authentication required',
                status_code=401
            )
        
        if not (user.is_superuser or user.is_staff):
            return self.error_response(
                message='Admin privileges required',
                status_code=403
            )
        
        return None


class PublicView(BaseView):
    """
    Base view class for public endpoints (no authentication required).
    """
    
    def __init__(self):
        super().__init__()
        self.require_auth = False
