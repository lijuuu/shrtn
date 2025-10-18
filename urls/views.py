"""
URL views layer for handling HTTP requests with serializers.
"""
from typing import Dict, Any, Optional
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
import json
import secrets

from core.dependencies.services import service_dependency
from .serializers import (
    ShortUrlSerializer,
    ShortUrlCreateSerializer,
    ShortUrlUpdateSerializer,
    BulkCreateSerializer
)


class UrlView:
    """
    URL views for HTTP endpoints.
    """
    
    def __init__(self):
        self.service = service_dependency.get_url_service()
    
    def list_urls(self, request: HttpRequest, org_id: int, namespace: str) -> JsonResponse:
        """List URLs in namespace."""
        try:
            # Get namespace ID (would need to query namespace service)
            # For now, we'll use a placeholder
            namespace_id = 1  # This should be resolved from namespace name
            
            # Get user ID from request (would come from JWT in real implementation)
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 1
            
            filters = {'created_by_user_id': user_id}
            urls = self.service.list(filters)
            
            # Convert to dict format for serializer
            url_data = [url.to_dict() for url in urls]
            serializer = ShortUrlSerializer(url_data, many=True)
            
            return JsonResponse({
                'message': 'URLs retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': {
                    'urls': serializer.data,
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
    
    def create_url(self, request: HttpRequest, org_id: int, namespace: str) -> JsonResponse:
        """Create new short URL."""
        try:
            data = json.loads(request.body)
            
            # Get user ID from request (would come from JWT in real implementation)
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 1
            
            # Get namespace ID (would need to query namespace service)
            namespace_id = 1  # This should be resolved from namespace name
            
            # Generate shortcode if not provided
            if not data.get('shortcode'):
                data['shortcode'] = self._generate_shortcode()
            
            data['namespace_id'] = namespace_id
            data['created_by_user_id'] = user_id
            
            serializer = ShortUrlCreateSerializer(data=data)
            if serializer.is_valid():
                url = self.service.create(serializer.validated_data)
                
                response_serializer = ShortUrlSerializer(url.to_dict())
                return JsonResponse({
                    'message': 'URL created successfully',
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
    
    def get_url(self, request: HttpRequest, org_id: int, namespace: str, shortcode: str) -> JsonResponse:
        """Get URL details."""
        try:
            # Get namespace ID (would need to query namespace service)
            namespace_id = 1  # This should be resolved from namespace name
            
            url = self.service.get_by_id((namespace_id, shortcode))
            if not url:
                return JsonResponse({
                    'message': 'URL not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            serializer = ShortUrlSerializer(url.to_dict())
            return JsonResponse({
                'message': 'URL retrieved successfully',
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
    
    def update_url(self, request: HttpRequest, org_id: int, namespace: str, shortcode: str) -> JsonResponse:
        """Update URL."""
        try:
            data = json.loads(request.body)
            
            # Get namespace ID (would need to query namespace service)
            namespace_id = 1  # This should be resolved from namespace name
            
            serializer = ShortUrlUpdateSerializer(data=data, partial=True)
            if serializer.is_valid():
                updated_url = self.service.update((namespace_id, shortcode), serializer.validated_data)
                if not updated_url:
                    return JsonResponse({
                        'message': 'URL not found',
                        'status_code': 404,
                        'success': False,
                        'payload': None
                    }, status=404)
                
                response_serializer = ShortUrlSerializer(updated_url.to_dict())
                return JsonResponse({
                    'message': 'URL updated successfully',
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
    
    def delete_url(self, request: HttpRequest, org_id: int, namespace: str, shortcode: str) -> JsonResponse:
        """Delete URL."""
        try:
            # Get namespace ID (would need to query namespace service)
            namespace_id = 1  # This should be resolved from namespace name
            
            success = self.service.delete((namespace_id, shortcode))
            if not success:
                return JsonResponse({
                    'message': 'URL not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            return JsonResponse({
                'message': 'URL deleted successfully',
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
    
    def resolve_url(self, request: HttpRequest, namespace: str, shortcode: str) -> HttpResponseRedirect:
        """Resolve short URL to original URL."""
        try:
            # Get namespace ID (would need to query namespace service)
            namespace_id = 1  # This should be resolved from namespace name
            
            original_url = self.service.resolve_url(namespace_id, shortcode)
            if not original_url:
                # Return 404 page or error
                return JsonResponse({
                    'message': 'URL not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            return HttpResponseRedirect(original_url)
            
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    def bulk_create_urls(self, request: HttpRequest, org_id: int, namespace: str) -> JsonResponse:
        """Bulk create URLs."""
        try:
            data = json.loads(request.body)
            
            # Get user ID from request (would come from JWT in real implementation)
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 1
            
            # Get namespace ID (would need to query namespace service)
            namespace_id = 1  # This should be resolved from namespace name
            
            # Add namespace_id and user_id to each URL
            for url_data in data.get('urls', []):
                url_data['namespace_id'] = namespace_id
                url_data['created_by_user_id'] = user_id
                if not url_data.get('shortcode'):
                    url_data['shortcode'] = self._generate_shortcode()
            
            serializer = BulkCreateSerializer(data=data)
            if serializer.is_valid():
                urls = self.service.batch_create(serializer.validated_data['urls'])
                
                url_data = [url.to_dict() for url in urls]
                response_serializer = ShortUrlSerializer(url_data, many=True)
                
                return JsonResponse({
                    'message': 'URLs created successfully',
                    'status_code': 201,
                    'success': True,
                    'payload': {
                        'urls': response_serializer.data,
                        'count': len(response_serializer.data)
                    }
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
    
    def _generate_shortcode(self, length: int = 6) -> str:
        """Generate a random shortcode."""
        import string
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
