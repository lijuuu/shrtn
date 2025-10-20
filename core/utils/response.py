"""
Consolidated response utilities - single source of truth for all API responses.
"""
from typing import Any, Dict, Optional, List, Callable
from django.http import JsonResponse, HttpRequest
from django.core.paginator import Paginator
import functools
import logging

logger = logging.getLogger(__name__)


class APIResponse:
    """
    Consolidated API response builder - single source of truth.
    Replaces all duplicate response utilities.
    """
    
    @staticmethod
    def success(
        message: str = "Success",
        data: Any = None,
        status_code: int = 200,
        meta: Optional[Dict[str, Any]] = None
    ) -> JsonResponse:
        """Create a successful API response."""
        response_data = {
            "success": True,
            "message": message,
            "status_code": status_code,
            "payload": data,
            "meta": meta or {}
        }
        return JsonResponse(response_data, status=status_code)
    
    @staticmethod
    def error(
        message: str = "Error occurred",
        data: Any = None,
        status_code: int = 400,
        errors: Optional[List[str]] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> JsonResponse:
        """Create an error API response."""
        response_data = {
            "success": False,
            "message": message,
            "status_code": status_code,
            "payload": data,
            "errors": errors or [],
            "meta": meta or {}
        }
        return JsonResponse(response_data, status=status_code)
    
    @staticmethod
    def validation_error(message: str, errors: Dict) -> JsonResponse:
        """Validation error response."""
        return APIResponse.error(
            message=message,
            status_code=400,
            errors=errors
        )
    
    @staticmethod
    def not_found(message: str = 'Resource not found') -> JsonResponse:
        """Not found response."""
        return APIResponse.error(
            message=message,
            status_code=404
        )
    
    @staticmethod
    def unauthorized(message: str = 'Authentication required') -> JsonResponse:
        """Unauthorized response."""
        return APIResponse.error(
            message=message,
            status_code=401
        )
    
    @staticmethod
    def forbidden(message: str = 'Access denied') -> JsonResponse:
        """Forbidden response."""
        return APIResponse.error(
            message=message,
            status_code=403
        )
    
    @staticmethod
    def server_error(message: str = 'Internal server error') -> JsonResponse:
        """Server error response."""
        return APIResponse.error(
            message=message,
            status_code=500
        )
    
    @staticmethod
    def created(message: str, data: Any = None) -> JsonResponse:
        """Created response."""
        return APIResponse.success(
            message=message,
            data=data,
            status_code=201
        )
    
    @staticmethod
    def no_content(message: str = 'Operation completed successfully') -> JsonResponse:
        """No content response."""
        return APIResponse.success(
            message=message,
            data=None,
            status_code=204
        )
    
    @staticmethod
    def paginated(
        queryset,
        page: int = 1,
        per_page: int = 20,
        serializer_class=None,
        message: str = "Data retrieved successfully",
        **serializer_kwargs
    ) -> JsonResponse:
        """Create a paginated response."""
        try:
            paginator = Paginator(queryset, per_page)
            page_obj = paginator.get_page(page)
            
            # Serialize data if serializer provided
            if serializer_class:
                serializer = serializer_class(page_obj.object_list, many=True, **serializer_kwargs)
                data = serializer.data
            else:
                data = list(page_obj.object_list)
            
            meta = {
                "pagination": {
                    "current_page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "total_items": paginator.count,
                    "per_page": per_page,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous()
                }
            }
            
            return APIResponse.success(
                message=message,
                data=data,
                meta=meta
            )
            
        except Exception as e:
            logger.error("Pagination error: %s", e)
            return APIResponse.error(
                message="Pagination failed",
                status_code=500
            )


# Convenience functions for quick access
def success_response(message: str, data: Any = None, status_code: int = 200, meta: Dict = None) -> JsonResponse:
    """Quick success response."""
    return APIResponse.success(message, data, status_code, meta)


def error_response(message: str, status_code: int = 400, data: Any = None, errors: List[str] = None, meta: Dict = None) -> JsonResponse:
    """Quick error response."""
    return APIResponse.error(message, data, status_code, errors, meta)


def validation_error_response(message: str, errors: Dict) -> JsonResponse:
    """Quick validation error response."""
    return APIResponse.validation_error(message, errors)


def not_found_response(message: str = 'Resource not found') -> JsonResponse:
    """Quick not found response."""
    return APIResponse.not_found(message)


def unauthorized_response(message: str = 'Authentication required') -> JsonResponse:
    """Quick unauthorized response."""
    return APIResponse.unauthorized(message)


def forbidden_response(message: str = 'Access denied') -> JsonResponse:
    """Quick forbidden response."""
    return APIResponse.forbidden(message)


def server_error_response(message: str = 'Internal server error') -> JsonResponse:
    """Quick server error response."""
    return APIResponse.server_error(message)


def created_response(message: str, data: Any = None) -> JsonResponse:
    """Quick created response."""
    return APIResponse.created(message, data)


def no_content_response(message: str = 'Operation completed successfully') -> JsonResponse:
    """Quick no content response."""
    return APIResponse.no_content(message)


# Authentication decorators
def require_jwt_auth(func: Callable) -> Callable:
    """Decorator to require JWT authentication for view methods."""
    @functools.wraps(func)
    def wrapper(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        try:
            from core.utils.view_helpers import get_authenticated_user
            user = get_authenticated_user(request)
            if not user:
                return APIResponse.unauthorized('Authentication required')
            
            kwargs['authenticated_user'] = user
            return func(self, request, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Authentication failed in {func.__name__}: %s", e)
            return APIResponse.unauthorized('Authentication failed')
    
    return wrapper


def optional_jwt_auth(func: Callable) -> Callable:
    """Decorator for optional JWT authentication."""
    @functools.wraps(func)
    def wrapper(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        try:
            from core.utils.view_helpers import get_authenticated_user
            user = get_authenticated_user(request)
            kwargs['authenticated_user'] = user
            return func(self, request, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Optional authentication failed in {func.__name__}: %s", e)
            kwargs['authenticated_user'] = None
            return func(self, request, *args, **kwargs)
    
    return wrapper


def admin_required(func: Callable) -> Callable:
    """Decorator to require admin user (superuser or staff)."""
    @functools.wraps(func)
    def wrapper(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        try:
            from core.utils.view_helpers import get_authenticated_user
            user = get_authenticated_user(request)
            if not user:
                return APIResponse.unauthorized('Authentication required')
            
            if not (user.is_superuser or user.is_staff):
                return APIResponse.forbidden('Admin privileges required')
            
            kwargs['authenticated_user'] = user
            return func(self, request, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Admin authentication failed in {func.__name__}: %s", e)
            return APIResponse.forbidden('Admin authentication failed')
    
    return wrapper


# Response decorators
def api_response(func: Callable) -> Callable:
    """Decorator to standardize API responses with consistent error handling."""
    @functools.wraps(func)
    def wrapper(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        try:
            result = func(self, request, *args, **kwargs)
            
            if isinstance(result, JsonResponse):
                return result
            
            if isinstance(result, dict):
                return APIResponse.success(
                    message=result.get('message', 'Operation successful'),
                    data=result.get('data'),
                    status_code=result.get('status_code', 200),
                    meta=result.get('meta')
                )
            
            return APIResponse.success(
                message='Operation successful',
                data=result
            )
            
        except Exception as e:
            logger.error(f"API response error in {func.__name__}: %s", e)
            return APIResponse.server_error(f"Error in {func.__name__}")
    
    return wrapper


def json_request(func: Callable) -> Callable:
    """Decorator to validate JSON request body and inject parsed data."""
    @functools.wraps(func)
    def wrapper(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        try:
            import json
            data = json.loads(request.body)
            kwargs['json_data'] = data
            return func(self, request, *args, **kwargs)
        except json.JSONDecodeError:
            return APIResponse.error('Invalid JSON format', 400)
        except Exception as e:
            logger.error(f"JSON request validation failed in {func.__name__}: %s", e)
            return APIResponse.error('Request validation failed', 400)
    
    return wrapper


def success_response_decorator(message: str = 'Operation successful', status_code: int = 200):
    """Decorator to wrap method result in standardized success response."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
            try:
                result = func(self, request, *args, **kwargs)
                return APIResponse.success(message, result, status_code)
            except Exception as e:
                logger.error(f"Success response error in {func.__name__}: %s", e)
                return APIResponse.server_error(f"Error in {func.__name__}")
        return wrapper
    return decorator


class PermissionContext:
    """Utility for adding permission context to responses."""
    
    @staticmethod
    def get_user_permissions_in_org(user_id, org_id, organization_service):
        """Get user permissions in organization."""
        try:
            return organization_service.get_user_permissions(org_id, user_id)
        except Exception:
            return None
    
    @staticmethod
    def add_permission_context(data, user_id, org_id, organization_service):
        """Add permission context to data."""
        if isinstance(data, list):
            for item in data:
                if hasattr(item, 'organization_id'):
                    permissions = PermissionContext.get_user_permissions_in_org(
                        user_id, item.organization_id, organization_service
                    )
                    item.user_permissions = permissions or {}
        elif hasattr(data, 'organization_id'):
            permissions = PermissionContext.get_user_permissions_in_org(
                user_id, data.organization_id, organization_service
            )
            data.user_permissions = permissions or {}
        
        return data