"""
JWT Authentication Middleware for Django.
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from core.utils.view_helpers import authenticate_user_jwt

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate users using JWT tokens.
    Sets request.user for authenticated requests.
    """
    
    def process_request(self, request):
        """Process JWT authentication for each request."""
        try:
            # Skip authentication for certain paths
            if self._should_skip_auth(request.path):
                return None
            
            # Debug: Log the authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            logger.info("JWT Middleware - Authorization header: %s", auth_header)
            
            # Try to authenticate using JWT
            auth_result = authenticate_user_jwt(request)
            
            if auth_result:
                user, token = auth_result
                request.user = user
                request.jwt_token = token
                logger.info("JWT authentication successful for user %s", user.id)
            else:
                # Set anonymous user if no valid JWT
                from django.contrib.auth.models import AnonymousUser
                request.user = AnonymousUser()
                logger.info("JWT authentication failed - setting anonymous user")
                
        except Exception as e:
            logger.error("JWT middleware error: %s", e)
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
        
        return None
    
    def _should_skip_auth(self, path: str) -> bool:
        """Check if authentication should be skipped for this path."""
        skip_paths = [
            '/health/',
            '/admin/',
            '/static/',
            '/media/',
            '/api/v1/organizations/invites/',  # Public invite endpoints
            '/api/v1/namespaces/check/',  # Public namespace check
            '/api/v1/urls/resolve/',  # Public URL resolution endpoint
        ]
        
        # Skip JWT auth for short URL resolution (public access)
        # Pattern: /<namespace>/<shortcode>/ (e.g., /myorg/abc123/)
        # This allows public access to short URLs without authentication
        if self._is_short_url_path(path):
            return True
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def _is_short_url_path(self, path: str) -> bool:
        """Check if the path is a short URL resolution request."""
        # Remove leading slash and split by '/'
        path_parts = path.strip('/').split('/')
        
        # Short URL pattern: /<namespace>/<shortcode>/
        # Should have exactly 2 parts and not start with 'api'
        if len(path_parts) == 2 and not path_parts[0].startswith('api'):
            return True
        
        return False
