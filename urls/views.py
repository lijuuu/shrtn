"""
URL views layer for handling HTTP requests with serializers.
"""
import uuid
from typing import Dict, Any, Optional
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
import json
import secrets

from core.dependencies.service_registry import service_registry
from core.permissions.decorators import require_organization_permission, require_namespace_access
from core.utils.response import APIResponse
from .serializers import (
    ShortUrlSerializer,
    ShortUrlWithPermissionsSerializer,
    ShortUrlCreateSerializer,
    ShortUrlUpdateSerializer,
    BulkCreateSerializer
)


class UrlView:
    """
    URL views for HTTP endpoints.
    """
    
    def __init__(self):
        self._service = None
    
    @property
    def service(self):
        """lazy service initialization."""
        if self._service is None:
            self._service = service_registry.get_url_service()
        return self._service
    
    @require_namespace_access()
    def list_urls(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """List URLs in namespace."""
        try:
            # Get namespace ID from namespace name
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return JsonResponse({
                    'message': 'Namespace not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            namespace_id = namespace_obj.namespace_id
            
            # Get user ID from request (would come from JWT in real implementation)
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None
            if not user_id:
                return JsonResponse({
                    'message': 'Authentication required',
                    'status_code': 401,
                    'success': False,
                    'payload': None
                }, status=401)
            
            filters = {'namespace_id': namespace_id}
            urls = self.service.list(filters)
            
            # Use enhanced serializer with permissions
            serializer = ShortUrlWithPermissionsSerializer(
                urls, 
                many=True, 
                context={'request': request}
            )
            
            return APIResponse.success(
                message="URLs retrieved successfully",
                data=serializer.data,
                meta={
                    "namespace": namespace,
                    "namespace_id": str(namespace_id),
                    "count": len(urls)
                }
            )
            
        except Exception as e:
            return APIResponse.error(
                message="Failed to retrieve URLs",
                status_code=500
            )
    
    @require_organization_permission('can_update')
    @require_namespace_access()
    def create_url(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Create new short URL."""
        try:
            data = json.loads(request.body)
            
            # Get user ID from request (would come from JWT in real implementation)
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None
            if not user_id:
                return JsonResponse({
                    'message': 'Authentication required',
                    'status_code': 401,
                    'success': False,
                    'payload': None
                }, status=401)
            
            # Get namespace ID from namespace name
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return JsonResponse({
                    'message': 'Namespace not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            namespace_id = namespace_obj.namespace_id
            
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
    
    @require_namespace_access()
    def get_url(self, request: HttpRequest, org_id: uuid.UUID, namespace: str, shortcode: str) -> JsonResponse:
        """Get URL details."""
        try:
            # Get namespace ID from namespace name
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return JsonResponse({
                    'message': 'Namespace not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            namespace_id = namespace_obj.namespace_id
            
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
    
    @require_organization_permission('can_update')
    @require_namespace_access()
    def update_url(self, request: HttpRequest, org_id: uuid.UUID, namespace: str, shortcode: str) -> JsonResponse:
        """Update URL."""
        try:
            data = json.loads(request.body)
            
            # Get namespace ID from namespace name
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return JsonResponse({
                    'message': 'Namespace not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            namespace_id = namespace_obj.namespace_id
            
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
    
    @require_organization_permission('can_update')
    @require_namespace_access()
    def delete_url(self, request: HttpRequest, org_id: uuid.UUID, namespace: str, shortcode: str) -> JsonResponse:
        """Delete URL."""
        try:
            # Get namespace ID from namespace name
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return JsonResponse({
                    'message': 'Namespace not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            namespace_id = namespace_obj.namespace_id
            
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
        """Resolve short URL to original URL with analytics tracking."""
        try:
            # Get namespace ID from namespace name
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return JsonResponse({
                    'message': 'Namespace not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            namespace_id = namespace_obj.namespace_id
            
            # Prepare request metadata for analytics
            request_meta = {
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referer': request.META.get('HTTP_REFERER', '')
            }
            
            original_url = self.service.resolve_url(namespace_id, shortcode, request_meta)
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
            logger.error("Failed to resolve URL: %s", e)
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'
    
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
    
    def get_hot_urls(self, request: HttpRequest) -> JsonResponse:
        """Get hot URLs (most accessed)."""
        try:
            limit = int(request.GET.get('limit', 100))
            hot_urls = self.service.get_hot_urls(limit)
            
            return JsonResponse({
                'message': 'Hot URLs retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': {
                    'hot_urls': hot_urls,
                    'count': len(hot_urls),
                    'limit': limit
                }
            })
            
        except ValueError as e:
            return JsonResponse({
                'message': 'Invalid limit parameter',
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
    
    def get_cache_stats(self, request: HttpRequest) -> JsonResponse:
        """Get cache statistics."""
        try:
            stats = self.service.get_cache_stats()
            
            return JsonResponse({
                'message': 'Cache statistics retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': {
                    'cache_stats': stats
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    def clear_cache(self, request: HttpRequest) -> JsonResponse:
        """Clear all URL cache."""
        try:
            success = self.service.clear_cache()
            
            if success:
                return JsonResponse({
                    'message': 'Cache cleared successfully',
                    'status_code': 200,
                    'success': True,
                    'payload': None
                })
            else:
                return JsonResponse({
                    'message': 'Failed to clear cache',
                    'status_code': 500,
                    'success': False,
                    'payload': None
                }, status=500)
            
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    def test_cache(self, request: HttpRequest) -> JsonResponse:
        """Test cache functionality."""
        try:
            # Test cache stats
            stats = self.service.get_cache_stats()
            
            # Test hot URLs
            hot_urls = self.service.get_hot_urls(10)
            
            return JsonResponse({
                'message': 'Cache test successful',
                'status_code': 200,
                'success': True,
                'payload': {
                    'cache_stats': stats,
                    'hot_urls': hot_urls,
                    'cache_working': True
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'message': f'Cache test failed: {str(e)}',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    def _generate_shortcode(self, length: int = 6) -> str:
        """Generate a random shortcode."""
        import string
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def get_url_analytics(self, request: HttpRequest, org_id: uuid.UUID, namespace: str, shortcode: str) -> JsonResponse:
        """Get analytics for a specific URL."""
        try:
            # Get namespace ID from namespace name
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return APIResponse.error(
                    message="Namespace not found",
                    status_code=404
                )
            
            namespace_id = namespace_obj.namespace_id
            
            # Get analytics service
            analytics_service = service_registry.get_analytics_service()
            if not analytics_service:
                return APIResponse.error(
                    message="Analytics service not available",
                    status_code=503
                )
            
            # Get days parameter (default 30)
            days = int(request.GET.get('days', 30))
            
            # Get analytics data
            analytics_data = analytics_service.get_url_analytics(namespace_id, shortcode, days)
            
            return APIResponse.success(
                message="URL analytics retrieved successfully",
                data=analytics_data
            )
            
        except ValueError as e:
            return APIResponse.error(
                message="Invalid days parameter",
                status_code=400
            )
        except Exception as e:
            logger.error("Failed to get URL analytics: %s", e)
            return APIResponse.error(
                message="Failed to retrieve analytics",
                status_code=500
            )
    
    def get_namespace_analytics(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Get analytics for all URLs in a namespace."""
        try:
            # Get namespace ID from namespace name
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return APIResponse.error(
                    message="Namespace not found",
                    status_code=404
                )
            
            namespace_id = namespace_obj.namespace_id
            
            # Get analytics service
            analytics_service = service_registry.get_analytics_service()
            if not analytics_service:
                return APIResponse.error(
                    message="Analytics service not available",
                    status_code=503
                )
            
            # Get days parameter (default 30)
            days = int(request.GET.get('days', 30))
            
            # Get analytics data
            analytics_data = analytics_service.get_namespace_analytics(namespace_id, days)
            
            return APIResponse.success(
                message="Namespace analytics retrieved successfully",
                data=analytics_data
            )
            
        except ValueError as e:
            return APIResponse.error(
                message="Invalid days parameter",
                status_code=400
            )
        except Exception as e:
            logger.error("Failed to get namespace analytics: %s", e)
            return APIResponse.error(
                message="Failed to retrieve analytics",
                status_code=500
            )
    
    def get_realtime_stats(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Get real-time statistics for a namespace."""
        try:
            # Get namespace ID from namespace name
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return APIResponse.error(
                    message="Namespace not found",
                    status_code=404
                )
            
            namespace_id = namespace_obj.namespace_id
            
            # Get analytics service
            analytics_service = service_registry.get_analytics_service()
            if not analytics_service:
                return APIResponse.error(
                    message="Analytics service not available",
                    status_code=503
                )
            
            # Get real-time stats
            stats_data = analytics_service.get_realtime_stats(namespace_id)
            
            return APIResponse.success(
                message="Real-time statistics retrieved successfully",
                data=stats_data
            )
            
        except Exception as e:
            logger.error("Failed to get real-time stats: %s", e)
            return APIResponse.error(
                message="Failed to retrieve real-time statistics",
                status_code=500
            )
