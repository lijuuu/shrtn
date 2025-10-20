"""
URL views layer for handling HTTP requests with serializers.
"""
import uuid
import logging
from typing import Dict, Any, Optional
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
import json
import secrets
from django.utils import timezone

logger = logging.getLogger(__name__)

from core.utils.view_helpers import get_service, get_authenticated_user
from core.utils.response import (
    success_response, 
    error_response, 
    unauthorized_response,
    server_error_response,
    APIResponse
)
from core.dependencies.service_registry import service_registry
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
            self._service = get_service('url')
        return self._service
    
    def list_urls(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """List URLs in namespace with pagination."""
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
            
            # Get namespace ID from namespace name
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return error_response('Namespace not found', 404)
            
            namespace_id = namespace_obj.namespace_id
            
            # Get pagination parameters
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 20))
            search = request.GET.get('search', '')
            status = request.GET.get('status', '')
            sort = request.GET.get('sort', 'created_at')
            order = request.GET.get('order', 'desc')
            
            # Validate pagination parameters
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 20
            
            # Build filters
            filters = {'namespace_id': namespace_id}
            if search:
                filters['search'] = search
            if status:
                filters['status'] = status
            
            # Get total count for pagination
            all_urls = self.service.list(filters)
            total_count = len(all_urls)
            
            # Apply sorting
            if sort == 'created_at':
                all_urls.sort(key=lambda x: x.created_at, reverse=(order == 'desc'))
            elif sort == 'click_count':
                all_urls.sort(key=lambda x: x.click_count, reverse=(order == 'desc'))
            elif sort == 'shortcode':
                all_urls.sort(key=lambda x: x.shortcode, reverse=(order == 'desc'))
            
            # Apply pagination
            start_index = (page - 1) * limit
            end_index = start_index + limit
            paginated_urls = all_urls[start_index:end_index]
            
            # Calculate pagination metadata
            total_pages = (total_count + limit - 1) // limit
            has_next = page < total_pages
            has_previous = page > 1
            
            # Serialize the paginated results
            serializer = ShortUrlSerializer(
                paginated_urls, 
                many=True, 
                context={'request': request}
            )
            
            return success_response(
                message="URLs retrieved successfully",
                data=serializer.data,
                meta={
                    "namespace": namespace,
                    "namespace_id": str(namespace_id),
                    "pagination": {
                        "count": total_count,
                        "page": page,
                        "limit": limit,
                        "total_pages": total_pages,
                        "has_next": has_next,
                        "has_previous": has_previous,
                        "next_page": page + 1 if has_next else None,
                        "previous_page": page - 1 if has_previous else None
                    },
                    "filters": {
                        "search": search,
                        "status": status,
                        "sort": sort,
                        "order": order
                    }
                }
            )
            
        except Exception as e:
            return server_error_response('Failed to retrieve URLs')
    
    @method_decorator(csrf_exempt)
    def create_url(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Create new short URL."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Create URL method called")
        
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        # Check user permissions in organization
        try:
            import logging
            logger = logging.getLogger(__name__)
            logger.info("Creating URL - User: %s, Org: %s, Namespace: %s", user.id, org_id, namespace)
            
            organization_service = service_registry.get_organization_service()
            user_permissions = organization_service.get_user_permissions(org_id, user.id)
            
            if not user_permissions:
                return error_response('You are not a member of this organization', 403)
            
            # Check if user has update permission
            if not user_permissions.get('can_update', False):
                return error_response('Insufficient permissions. Required: can_update', 403)
            
            # Get namespace ID from namespace name
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return error_response('Namespace not found', 404)
            
            namespace_id = namespace_obj.namespace_id
            
            data = json.loads(request.body)
            
            # Handle shortcode generation/validation
            custom_shortcode = data.get('shortcode', '').strip()
            if custom_shortcode:
                # User provided a custom shortcode - validate it
                if not self._is_valid_shortcode(custom_shortcode):
                    return error_response('Invalid shortcode format. Use only letters, numbers, hyphens, and underscores.', 400)
                
                # Check if custom shortcode is available
                if not self._is_shortcode_available(namespace_id, custom_shortcode):
                    return error_response(f'Shortcode "{custom_shortcode}" is already taken in this namespace', 409)
                
                data['shortcode'] = custom_shortcode
            else:
                # Generate a unique shortcode
                data['shortcode'] = self._generate_shortcode()
            
            data['namespace_id'] = namespace_id
            data['created_by_user_id'] = user.id
            
            serializer = ShortUrlCreateSerializer(data=data)
            if serializer.is_valid():
                url = self.service.create(serializer.validated_data)
                
                response_serializer = ShortUrlSerializer(url)
                return success_response('URL created successfully', response_serializer.data, 201)
            else:
                return error_response('Validation failed', 400, {
                    'errors': serializer.errors
                })
            
        except json.JSONDecodeError:
            return error_response('Invalid JSON format', 400)
        except ValidationError as e:
            return error_response(str(e), 400)
        except ValueError as e:
            # Handle shortcode conflicts and validation errors
            error_message = str(e)
            if "already exists" in error_message:
                return error_response(error_message, 409)  # Conflict status
            else:
                return error_response(error_message, 400)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("URL creation error: %s", e)
            return server_error_response('Internal server error')
    
    def get_url(self, request: HttpRequest, org_id: uuid.UUID, namespace: str, shortcode: str) -> JsonResponse:
        """Get URL details."""
        try:
            # Get namespace ID from namespace name
            namespace_service = get_service('namespace')
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
    
    @method_decorator(csrf_exempt)
    def update_url(self, request: HttpRequest, org_id: uuid.UUID, namespace: str, shortcode: str) -> JsonResponse:
        """Update URL."""
        try:
            data = json.loads(request.body)
            
            # Get namespace ID from namespace name
            from core.utils.view_helpers import get_service
            namespace_service = get_service('namespace')
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
    
    @method_decorator(csrf_exempt)
    def delete_url(self, request: HttpRequest, org_id: uuid.UUID, namespace: str, shortcode: str) -> JsonResponse:
        """Delete URL."""
        try:
            # Get namespace ID from namespace name
            from core.utils.view_helpers import get_service
            namespace_service = get_service('namespace')
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
        """Resolve short URL to original URL with analytics tracking and proper HTTP redirects."""
        try:
            # Get namespace ID from namespace name
            from core.utils.view_helpers import get_service
            namespace_service = get_service('namespace')
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                # Check if this is an API request to return JSON instead of redirect
                if self._is_api_request(request):
                    return JsonResponse({
                        'error': 'Namespace not found',
                        'message': f'Namespace "{namespace}" does not exist'
                    }, status=200)
                # Return 404 redirect to a custom 404 page
                from django.shortcuts import redirect
                return redirect('/404/', permanent=False)
            
            namespace_id = namespace_obj.namespace_id
            
            # Prepare request metadata for analytics
            request_meta = {
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referer': request.META.get('HTTP_REFERER', ''),
                'timestamp': timezone.now().isoformat()
            }
            
            # Get URL details including redirect type
            url_details = self.service.resolve_url_with_details(namespace_id, shortcode, request_meta)
            if not url_details:
                # Check if this is an API request to return JSON instead of redirect
                if self._is_api_request(request):
                    return JsonResponse({
                        'error': 'Short URL not found',
                        'message': f'Short URL "{namespace}/{shortcode}" does not exist'
                    }, status=200)
                # Return 404 redirect
                from django.shortcuts import redirect
                return redirect('/404/', permanent=False)
            
            original_url = url_details.get('url')
            redirect_type = url_details.get('redirect_type', 'temporary')  # temporary or permanent
            is_active = url_details.get('is_active', True)
            
            # Check if URL is active
            if not is_active:
                if self._is_api_request(request):
                    return JsonResponse({
                        'error': 'URL inactive',
                        'message': f'Short URL "{namespace}/{shortcode}" is inactive'
                    }, status=200)
                from django.shortcuts import redirect
                return redirect('/inactive/', permanent=False)
            
            # Check if URL has expired
            expires_at = url_details.get('expires_at')
            if expires_at and timezone.now() > expires_at:
                if self._is_api_request(request):
                    return JsonResponse({
                        'error': 'URL expired',
                        'message': f'Short URL "{namespace}/{shortcode}" has expired'
                    }, status=200)
                from django.shortcuts import redirect
                return redirect('/expired/', permanent=False)
            
            # If this is an API request, return JSON with the long URL (always 200 status)
            if self._is_api_request(request):
                return JsonResponse({
                    'long_url': original_url
                }, status=200)
            
            # For direct access, perform redirect
            # Determine redirect status code
            if redirect_type == 'permanent':
                status_code = 301  # Moved Permanently
            else:
                status_code = 302  # Found (temporary redirect)
            
            # Create redirect response with proper status code
            response = HttpResponseRedirect(original_url, status=status_code)
            
            # Add custom headers for analytics and tracking
            response['X-Short-URL-Source'] = f"{namespace}/{shortcode}"
            response['X-Redirect-Type'] = redirect_type
            response['X-Click-Timestamp'] = request_meta['timestamp']
            
            # Add cache control headers
            if redirect_type == 'permanent':
                response['Cache-Control'] = 'public, max-age=31536000'  # 1 year
            else:
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            
            logger.info("URL resolved: %s -> %s (status: %d)", 
                       f"{namespace}/{shortcode}", original_url, status_code)
            
            return response
            
        except Exception as e:
            logger.error("Failed to resolve URL: %s", e)
            # Check if this is an API request to return JSON instead of redirect
            if self._is_api_request(request):
                return JsonResponse({
                    'error': 'Internal server error',
                    'message': 'Failed to resolve URL'
                }, status=200)
            # Return 500 redirect to error page
            from django.shortcuts import redirect
            return redirect('/500/', permanent=False)
    
    def _is_api_request(self, request: HttpRequest) -> bool:
        """Check if the request is coming from the API endpoint."""
        return request.path.startswith('/api/v1/urls/resolve/')
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'
    
    def bulk_create_urls(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Bulk create URLs."""
        return self._bulk_create_urls_impl(request, org_id, namespace)
    
    def _bulk_create_urls_impl(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Implementation of bulk create URLs."""
        try:
            # Check if request method is POST
            if request.method != 'POST':
                return error_response('Method not allowed. Use POST.', 405)
            
            # Check if request body is empty
            if not request.body:
                return error_response('Request body is required', 400)
            
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                return error_response(f'Invalid JSON format: {str(e)}', 400)
            
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
    
    @method_decorator(csrf_exempt)
    def bulk_upload_excel(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Bulk upload URLs from Excel file."""
        try:
            # Check authentication
            user = get_authenticated_user(request)
            if not user:
                return unauthorized_response('Authentication required')
            
            # Check user permissions in organization
            organization_service = service_registry.get_organization_service()
            user_permissions = organization_service.get_user_permissions(org_id, user.id)
            
            if not user_permissions:
                return error_response('You are not a member of this organization', 403)
            
            # Check if user has update permission
            if not user_permissions.get('can_update', False):
                return error_response('Insufficient permissions. Required: can_update', 403)
            
            # Get namespace ID from namespace name
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return error_response('Namespace not found', 404)
            
            namespace_id = namespace_obj.namespace_id
            
            # Check if file was uploaded
            if 'excel_file' not in request.FILES:
                return error_response('Excel file is required', 400)
            
            excel_file = request.FILES['excel_file']
            
            # Validate file type
            if not excel_file.name.endswith(('.xlsx', '.xls', '.csv')):
                return error_response('Only Excel files (.xlsx, .xls) or CSV files (.csv) are allowed', 400)
            
            # Process Excel file
            result = self.service.process_bulk_urls(
                excel_file=excel_file,
                namespace_id=namespace_id,
                user_id=user.id,
                method='random'
            )
            
            if result['success']:
                return success_response(
                    message='Bulk upload completed successfully',
                    data={
                        'processed_count': result['processed_count'],
                        'error_count': result['error_count'],
                        'results': result['results'][:10],  # Show first 10 results
                        'total_results': len(result['results'])
                    },
                    meta={
                        'namespace': namespace,
                        'namespace_id': str(namespace_id)
                    }
                )
            else:
                return error_response(
                    message='Bulk upload failed',
                    status_code=400,
                    data={
                        'errors': result['errors'],
                        'processed_count': result['processed_count'],
                        'error_count': result['error_count']
                    }
                )
                
        except Exception as e:
            logger.error("Excel bulk upload error: %s", e)
            return server_error_response('Internal server error')
    
    def get_excel_template(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Get Excel template for bulk upload."""
        try:
            # Check authentication
            user = get_authenticated_user(request)
            if not user:
                return unauthorized_response('Authentication required')
            
            # Check user permissions in organization
            organization_service = service_registry.get_organization_service()
            user_permissions = organization_service.get_user_permissions(org_id, user.id)
            
            if not user_permissions:
                return error_response('You are not a member of this organization', 403)
            
            # Check if user has view permission
            if not user_permissions.get('can_view', False):
                return error_response('Insufficient permissions. Required: can_view', 403)
            
            # Get template Excel file
            template_data = self.service.get_template_excel()
            
            from django.http import HttpResponse
            response = HttpResponse(
                template_data,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="url_bulk_upload_template.xlsx"'
            return response
                
        except Exception as e:
            logger.error("Excel template error: %s", e)
            return server_error_response('Internal server error')
    
    
    
    
    
    def _generate_shortcode(self, length: int = 6) -> str:
        """Generate a random shortcode."""
        import string
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def _is_valid_shortcode(self, shortcode: str) -> bool:
        """Validate shortcode format."""
        import re
        # Allow letters, numbers, hyphens, and underscores
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', shortcode)) and len(shortcode) >= 2
    
    def _is_shortcode_available(self, namespace_id: uuid.UUID, shortcode: str) -> bool:
        """Check if shortcode is available in namespace."""
        try:
            # Use the shortcode generator service
            from core.dependencies.service_registry import service_registry
            url_service = service_registry.get_url_service()
            return url_service.shortcode_generator.is_shortcode_available(namespace_id, shortcode)
        except Exception:
            # If check fails, assume available to avoid blocking
            return True
    
    def get_url_analytics(self, request: HttpRequest, org_id: uuid.UUID, namespace: str, shortcode: str) -> JsonResponse:
        """Get analytics for a specific URL."""
        try:
            # Get namespace ID from namespace name
            from core.utils.view_helpers import get_service
            namespace_service = get_service('namespace')
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return APIResponse.error(
                    message="Namespace not found",
                    status_code=404
                )
            
            namespace_id = namespace_obj.namespace_id
            
            # Get analytics service
            analytics_service = get_service('analytics')
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
            from core.utils.view_helpers import get_service
            namespace_service = get_service('namespace')
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return APIResponse.error(
                    message="Namespace not found",
                    status_code=404
                )
            
            namespace_id = namespace_obj.namespace_id
            
            # Get analytics service
            analytics_service = get_service('analytics')
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
    
    def get_simple_analytics(self, request: HttpRequest, org_id: uuid.UUID, namespace: str, shortcode: str) -> JsonResponse:
        """Get simple click count analytics for a specific shortcode."""
        try:
            # Check authentication
            user = get_authenticated_user(request)
            if not user:
                return unauthorized_response('Authentication required')
            
            # Get namespace ID from namespace name
            from core.utils.view_helpers import get_service
            namespace_service = get_service('namespace')
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return error_response('Namespace not found', 404)
            
            namespace_id = namespace_obj.namespace_id
            
            # Get the URL to get basic click count
            short_url = self.service.repository.get_by_id((namespace_id, shortcode))
            if not short_url:
                return error_response('URL not found', 404)
            
            # Get analytics service for detailed analytics
            analytics_service = get_service('analytics')
            analytics_data = {}
            
            if analytics_service:
                try:
                    # Get last 30 days of analytics
                    analytics_data = analytics_service.get_url_analytics(namespace_id, shortcode, 30)
                except Exception as e:
                    logger.warning("Failed to get detailed analytics: %s", e)
                    analytics_data = {
                        'period_days': 30,
                        'total_clicks': 0,
                        'analytics': {
                            'clicks_by_country': {},
                            'clicks_by_date': [],
                            'recent_clicks': []
                        },
                        'message': 'Analytics table not configured. ScyllaDB connection required for detailed analytics.'
                    }
            
            return success_response(
                message="Analytics retrieved successfully",
                data={
                    'shortcode': shortcode,
                    'namespace': namespace,
                    'original_url': short_url.original_url,
                    'total_clicks': short_url.click_count,
                    'created_at': short_url.created_at.isoformat(),
                    'last_updated': short_url.updated_at.isoformat(),
                    'is_active': short_url.is_active,
                    'detailed_analytics': analytics_data
                }
            )
            
        except Exception as e:
            logger.error("Failed to get simple analytics: %s", e)
            return error_response('Failed to retrieve analytics', 500)
    
    def get_public_analytics(self, request: HttpRequest, namespace: str, shortcode: str) -> JsonResponse:
        """Get public analytics for a specific shortcode (no auth required)."""
        try:
            # Get namespace ID from namespace name
            from core.utils.view_helpers import get_service
            namespace_service = get_service('namespace')
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return error_response('Namespace not found', 404)
            
            namespace_id = namespace_obj.namespace_id
            
            # Get the URL to get basic click count
            short_url = self.service.repository.get_by_id((namespace_id, shortcode))
            if not short_url:
                return error_response('URL not found', 404)
            
            return success_response(
                message="Analytics retrieved successfully",
                data={
                    'shortcode': shortcode,
                    'namespace': namespace,
                    'original_url': short_url.original_url,
                    'total_clicks': short_url.click_count,
                    'created_at': short_url.created_at.isoformat(),
                    'last_updated': short_url.updated_at.isoformat(),
                    'is_active': short_url.is_active
                }
            )
            
        except Exception as e:
            logger.error("Failed to get public analytics: %s", e)
            return error_response('Failed to retrieve analytics', 500)
    
    def get_realtime_stats(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Get real-time statistics for a namespace."""
        try:
            # Get namespace ID from namespace name
            from core.utils.view_helpers import get_service
            namespace_service = get_service('namespace')
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return APIResponse.error(
                    message="Namespace not found",
                    status_code=404
                )
            
            namespace_id = namespace_obj.namespace_id
            
            # Get analytics service
            analytics_service = get_service('analytics')
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
