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
    
    @require_organization_permission('can_view')
    def list_namespaces(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """List organization namespaces."""
        try:
            filters = {'org_id': org_id}
            namespaces = self.service.list(filters)
            
            serializer = NamespaceSerializer(namespaces, many=True)
            return JsonResponse({
                'message': 'Namespaces retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': {
                    'namespaces': serializer.data,
                    'count': len(serializer.data)
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    @require_organization_permission('can_admin')
    def create_namespace(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Create new namespace."""
        try:
            data = json.loads(request.body)
            data['org_id'] = org_id
            
            # Get user ID from request (would come from JWT in real implementation)
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 1
            data['created_by_user_id'] = user_id
            
            serializer = NamespaceCreateSerializer(data=data)
            if serializer.is_valid():
                namespace = self.service.create(serializer.validated_data)
                
                response_serializer = NamespaceSerializer(namespace)
                return JsonResponse({
                    'message': 'Namespace created successfully',
                    'status_code': 201,
                    'success': True,
                    'payload': response_serializer.data
                }, status=201)
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
