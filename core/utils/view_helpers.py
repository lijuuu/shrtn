"""
Common view helpers for authentication, service access, and response formatting.
"""
import logging
from typing import Optional, Tuple, Any
from django.http import JsonResponse, HttpRequest
from django.contrib.auth import get_user_model
from core.utils.response import APIResponse
from core.dependencies.service_registry import service_registry

logger = logging.getLogger(__name__)
User = get_user_model()

# Global service instances for reuse
_services = {}


def get_service(service_name: str):
    """
    Get service instance with caching to avoid repeated initialization.
    """
    if service_name not in _services:
        _services[service_name] = getattr(service_registry, f'get_{service_name}_service')()
    return _services[service_name]


def authenticate_user_jwt(request: HttpRequest) -> Optional[Tuple[User, str]]:
    """
    Authenticate user using JWT token from Authorization header.
    Returns (user, token) tuple if authenticated, None if not.
    """
    try:
        from users.jwt_auth import JWTAuthentication
        auth = JWTAuthentication()
        return auth.authenticate(request)
    except Exception as e:
        logger.error("JWT authentication failed: %s", e)
        return None


def get_authenticated_user(request: HttpRequest) -> Optional[User]:
    """
    Get authenticated user from JWT token.
    Returns User object if authenticated, None if not.
    """
    auth_result = authenticate_user_jwt(request)
    if auth_result:
        user, token = auth_result
        return user
    return None


def require_jwt_auth(request: HttpRequest) -> Optional[JsonResponse]:
    """
    Check if request has valid JWT authentication.
    Returns error response if not authenticated, None if authenticated.
    """
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required',
            'status_code': 401,
            'payload': None
        }, status=401)
    return None


def get_namespace_by_name(namespace_name: str):
    """
    Get namespace object by name with caching.
    """
    namespace_service = get_service('namespace')
    return namespace_service.get_by_name(namespace_name)


def get_organization_by_id(org_id: str):
    """
    Get organization object by ID with caching.
    """
    organization_service = get_service('organization')
    return organization_service.get_by_id(org_id)


# Response functions moved to core.utils.response for consistency


def handle_view_exception(e: Exception, operation: str) -> JsonResponse:
    """
    Handle exceptions in views with standardized error responses.
    """
    logger.error(f"{operation} failed: %s", e)
    return standard_error_response(
        message=f"{operation} failed",
        status_code=500
    )


def validate_json_request(request: HttpRequest) -> Tuple[bool, dict, Optional[JsonResponse]]:
    """
    Validate and parse JSON request body.
    Returns (is_valid, data, error_response).
    """
    try:
        import json
        data = json.loads(request.body)
        return True, data, None
    except json.JSONDecodeError:
        return False, {}, standard_error_response(
            message="Invalid JSON format",
            status_code=400
        )
    except Exception as e:
        return False, {}, standard_error_response(
            message="Request parsing failed",
            status_code=400
        )
