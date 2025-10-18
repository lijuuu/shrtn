"""
Permission decorators for role-based access control.
"""
import functools
import logging
from typing import List, Optional
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from core.dependencies.service_registry import service_registry

logger = logging.getLogger(__name__)

# Role definitions
ROLE_ADMIN = 'admin'
ROLE_EDITOR = 'editor'
ROLE_VIEWER = 'viewer'

# Permission definitions
PERMISSION_VIEW = 'can_view'
PERMISSION_UPDATE = 'can_update'
PERMISSION_ADMIN = 'can_admin'

def require_organization_permission(permission: str, org_id_param: str = 'org_id'):
    """
    Decorator to check if user has specific permission in organization.
    
    Args:
        permission: The permission to check (can_view, can_update, can_admin)
        org_id_param: The parameter name containing organization ID
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                # Get user from request
                if not hasattr(request, 'user') or not request.user.is_authenticated:
                    return JsonResponse({
                        'message': 'Authentication required',
                        'status_code': 401,
                        'success': False,
                        'payload': None
                    }, status=401)
                
                # Get organization ID from kwargs
                org_id = kwargs.get(org_id_param)
                if not org_id:
                    return JsonResponse({
                        'message': 'Organization ID not found in request',
                        'status_code': 400,
                        'success': False,
                        'payload': None
                    }, status=400)
                
                # Check user permissions in organization
                organization_service = service_registry.get_organization_service()
                user_permissions = organization_service.get_user_permissions(org_id, request.user.id)
                
                if not user_permissions:
                    return JsonResponse({
                        'message': 'You are not a member of this organization',
                        'status_code': 403,
                        'success': False,
                        'payload': None
                    }, status=403)
                
                # Check specific permission
                if not user_permissions.get(permission, False):
                    return JsonResponse({
                        'message': f'Insufficient permissions. Required: {permission}',
                        'status_code': 403,
                        'success': False,
                        'payload': None
                    }, status=403)
                
                # Permission granted, proceed with view
                return view_func(request, *args, **kwargs)
                
            except Exception as e:
                logger.error("Permission check failed: %s", e)
                return JsonResponse({
                    'message': 'Permission check failed',
                    'status_code': 500,
                    'success': False,
                    'payload': None
                }, status=500)
        
        return wrapper
    return decorator

def require_organization_role(role: str, org_id_param: str = 'org_id'):
    """
    Decorator to check if user has specific role in organization.
    
    Args:
        role: The role to check (admin, editor, viewer)
        org_id_param: The parameter name containing organization ID
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                # Get user from request
                if not hasattr(request, 'user') or not request.user.is_authenticated:
                    return JsonResponse({
                        'message': 'Authentication required',
                        'status_code': 401,
                        'success': False,
                        'payload': None
                    }, status=401)
                
                # Get organization ID from kwargs
                org_id = kwargs.get(org_id_param)
                if not org_id:
                    return JsonResponse({
                        'message': 'Organization ID not found in request',
                        'status_code': 400,
                        'success': False,
                        'payload': None
                    }, status=400)
                
                # Check user permissions in organization
                organization_service = service_registry.get_organization_service()
                user_permissions = organization_service.get_user_permissions(org_id, request.user.id)
                
                if not user_permissions:
                    return JsonResponse({
                        'message': 'You are not a member of this organization',
                        'status_code': 403,
                        'success': False,
                        'payload': None
                    }, status=403)
                
                # Check role-based permissions
                if role == ROLE_ADMIN:
                    if not user_permissions.get(PERMISSION_ADMIN, False):
                        return JsonResponse({
                            'message': 'Admin role required',
                            'status_code': 403,
                            'success': False,
                            'payload': None
                        }, status=403)
                elif role == ROLE_EDITOR:
                    if not (user_permissions.get(PERMISSION_UPDATE, False) or user_permissions.get(PERMISSION_ADMIN, False)):
                        return JsonResponse({
                            'message': 'Editor role required',
                            'status_code': 403,
                            'success': False,
                            'payload': None
                        }, status=403)
                elif role == ROLE_VIEWER:
                    if not (user_permissions.get(PERMISSION_VIEW, False) or user_permissions.get(PERMISSION_UPDATE, False) or user_permissions.get(PERMISSION_ADMIN, False)):
                        return JsonResponse({
                            'message': 'Viewer role required',
                            'status_code': 403,
                            'success': False,
                            'payload': None
                        }, status=403)
                
                # Permission granted, proceed with view
                return view_func(request, *args, **kwargs)
                
            except Exception as e:
                logger.error("Role check failed: %s", e)
                return JsonResponse({
                    'message': 'Role check failed',
                    'status_code': 500,
                    'success': False,
                    'payload': None
                }, status=500)
        
        return wrapper
    return decorator

def require_namespace_access(org_id_param: str = 'org_id', namespace_param: str = 'namespace'):
    """
    Decorator to check if user has access to namespace.
    
    Args:
        org_id_param: The parameter name containing organization ID
        namespace_param: The parameter name containing namespace name
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                # Get user from request
                if not hasattr(request, 'user') or not request.user.is_authenticated:
                    return JsonResponse({
                        'message': 'Authentication required',
                        'status_code': 401,
                        'success': False,
                        'payload': None
                    }, status=401)
                
                # Get organization ID and namespace from kwargs
                org_id = kwargs.get(org_id_param)
                namespace = kwargs.get(namespace_param)
                
                if not org_id or not namespace:
                    return JsonResponse({
                        'message': 'Organization ID and namespace required',
                        'status_code': 400,
                        'success': False,
                        'payload': None
                    }, status=400)
                
                # Check if namespace belongs to organization
                namespace_service = service_registry.get_namespace_service()
                namespace_obj = namespace_service.get_by_name(namespace)
                
                if not namespace_obj:
                    return JsonResponse({
                        'message': 'Namespace not found',
                        'status_code': 404,
                        'success': False,
                        'payload': None
                    }, status=404)
                
                if namespace_obj.organization_id != org_id:
                    return JsonResponse({
                        'message': 'Namespace does not belong to this organization',
                        'status_code': 403,
                        'success': False,
                        'payload': None
                    }, status=403)
                
                # Check user permissions in organization
                organization_service = service_registry.get_organization_service()
                user_permissions = organization_service.get_user_permissions(org_id, request.user.id)
                
                if not user_permissions:
                    return JsonResponse({
                        'message': 'You are not a member of this organization',
                        'status_code': 403,
                        'success': False,
                        'payload': None
                    }, status=403)
                
                # Check if user has view permission
                if not user_permissions.get(PERMISSION_VIEW, False):
                    return JsonResponse({
                        'message': 'Insufficient permissions to access this namespace',
                        'status_code': 403,
                        'success': False,
                        'payload': None
                    }, status=403)
                
                # Permission granted, proceed with view
                return view_func(request, *args, **kwargs)
                
            except Exception as e:
                logger.error("Namespace access check failed: %s", e)
                return JsonResponse({
                    'message': 'Namespace access check failed',
                    'status_code': 500,
                    'success': False,
                    'payload': None
                }, status=500)
        
        return wrapper
    return decorator
