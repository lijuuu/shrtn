"""
Namespace views layer for handling HTTP requests with serializers.
"""
import uuid
from typing import Dict, Any, Optional
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
import json

from core.dependencies.service_registry import service_registry
from core.permissions.decorators import require_organization_permission
from core.utils.view_helpers import get_authenticated_user
from core.utils.response import (
    success_response, 
    error_response, 
    unauthorized_response,
    server_error_response
)
from .serializers import (
    NamespaceSerializer,
    NamespaceCreateSerializer,
    NamespaceUpdateSerializer,
    NamespaceAvailabilitySerializer
)


class NamespaceView:
    """
    Namespace views for HTTP endpoints.
    """
    
    def __init__(self):
        self.service = service_registry.get_namespace_service()
    
    def list_namespaces(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """List organization namespaces."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        # Check user permissions in organization
        try:
            organization_service = service_registry.get_organization_service()
            user_permissions = organization_service.get_user_permissions(org_id, user.id)
            
            if not user_permissions:
                return error_response('You are not a member of this organization', 403)
            
            # Check if user has view permission
            if not user_permissions.get('can_view', False):
                return error_response('Insufficient permissions. Required: can_view', 403)
            
            filters = {'org_id': org_id}
            namespaces = self.service.list(filters)
            
            serializer = NamespaceSerializer(namespaces, many=True)
            return success_response('Namespaces retrieved successfully', {
                'namespaces': serializer.data,
                'count': len(serializer.data)
            })
            
        except Exception as e:
            return server_error_response('Internal server error')
    
    @method_decorator(csrf_exempt)
    def create_namespace(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Create new namespace."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        # Check user permissions in organization
        try:
            organization_service = service_registry.get_organization_service()
            user_permissions = organization_service.get_user_permissions(org_id, user.id)
            
            if not user_permissions:
                return error_response('You are not a member of this organization', 403)
            
            # Check if user has admin permission
            if not user_permissions.get('can_admin', False):
                return error_response('Insufficient permissions. Required: can_admin', 403)
            
            data = json.loads(request.body)
            data['org_id'] = org_id
            data['created_by_user_id'] = user.id
            
            serializer = NamespaceCreateSerializer(data=data)
            if serializer.is_valid():
                # Pass the validated data along with org_id and created_by_user_id
                service_data = serializer.validated_data.copy()
                service_data['org_id'] = org_id
                service_data['created_by_user_id'] = user.id
                namespace = self.service.create(service_data)
                
                response_serializer = NamespaceSerializer(namespace)
                return success_response('Namespace created successfully', response_serializer.data, 201)
            else:
                return error_response('Validation failed', 400, {
                    'errors': serializer.errors
                })
            
        except json.JSONDecodeError:
            return error_response('Invalid JSON format', 400)
        except ValidationError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return server_error_response('Internal server error')
    
    def get_namespace(self, request: HttpRequest, namespace: str) -> JsonResponse:
        """Get namespace by name."""
        try:
            namespace_obj = self.service.get_by_name(namespace)
            if not namespace_obj:
                return JsonResponse({
                    'message': 'Namespace not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            serializer = NamespaceSerializer(namespace_obj)
            return JsonResponse({
                'message': 'Namespace retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': serializer.data
            })
            
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    @require_organization_permission('can_admin')
    def update_namespace(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Update namespace."""
        try:
            data = json.loads(request.body)
            
            # Get namespace by name first
            namespace_obj = self.service.get_by_name(namespace)
            if not namespace_obj:
                return JsonResponse({
                    'message': 'Namespace not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            serializer = NamespaceUpdateSerializer(data=data, partial=True)
            if serializer.is_valid():
                updated_namespace = self.service.update(namespace_obj.namespace_id, serializer.validated_data)
                if not updated_namespace:
                    return JsonResponse({
                        'message': 'Namespace not found',
                        'status_code': 404,
                        'success': False,
                        'payload': None
                    }, status=404)
                
                response_serializer = NamespaceSerializer(updated_namespace)
                return JsonResponse({
                    'message': 'Namespace updated successfully',
                    'status_code': 200,
                    'success': True,
                    'payload': response_serializer.data
                })
            else:
                return JsonResponse({
                    'message': 'Validation failed',
                    'status_code': 400,
                    'success': False,
                    'payload': {
                        'errors': serializer.errors
                    }
                }, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'message': 'Invalid JSON format',
                'status_code': 400,
                'success': False,
                'payload': None
            }, status=400)
        except ValidationError as e:
            return JsonResponse({
                'message': str(e),
                'status_code': 400,
                'success': False,
                'payload': None
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    @require_organization_permission('can_admin')
    def delete_namespace(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Delete namespace."""
        try:
            # Get namespace by name first
            namespace_obj = self.service.get_by_name(namespace)
            if not namespace_obj:
                return JsonResponse({
                    'message': 'Namespace not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            success = self.service.delete(namespace_obj.namespace_id)
            if not success:
                return JsonResponse({
                    'message': 'Namespace not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            return JsonResponse({
                'message': 'Namespace deleted successfully',
                'status_code': 200,
                'success': True,
                'payload': None
            })
            
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    def check_namespace_availability(self, request: HttpRequest, namespace: str) -> JsonResponse:
        """Check if namespace name is available."""
        try:
            available = self.service.check_name_availability(namespace)
            
            return JsonResponse({
                'message': 'Namespace availability checked',
                'status_code': 200,
                'success': True,
                'payload': {
                    'name': namespace,
                    'available': available
                }
            })
            
        except ValidationError as e:
            return JsonResponse({
                'message': str(e),
                'status_code': 400,
                'success': False,
                'payload': None
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
