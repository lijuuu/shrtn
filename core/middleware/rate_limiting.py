"""
Rate limiting middleware for global request rate limiting.
"""
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
import time
import hashlib

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Global rate limiting middleware that applies different limits based on endpoint patterns.
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        
        # Get rate limiting configuration from settings
        from django.conf import settings
        self.rate_limits = getattr(settings, 'RATE_LIMIT_CONFIG', {
            'auth': {'requests': 10, 'window': 60, 'burst': 5},
            'api': {'requests': 100, 'window': 60, 'burst': 20},
            'health': {'requests': 1000, 'window': 60, 'burst': 100},
            'default': {'requests': 50, 'window': 60, 'burst': 10}
        })
    
    def get_rate_limit_config(self, path):
        """
        Determine rate limit configuration based on request path.
        """
        if path.startswith('/auth/'):
            return self.rate_limits['auth']
        elif path.startswith('/api/'):
            return self.rate_limits['api']
        elif path.startswith('/health/'):
            return self.rate_limits['health']
        else:
            return self.rate_limits['default']
    
    def get_client_identifier(self, request):
        """
        Get a unique identifier for the client (IP + User-Agent hash).
        """
        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create a hash of IP + User-Agent for better identification
        identifier = f"{ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
        return identifier
    
    def get_client_ip(self, request):
        """
        Get the real IP address of the client.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def check_rate_limit(self, identifier, path):
        """
        Check if the client has exceeded the rate limit.
        """
        config = self.get_rate_limit_config(path)
        current_time = int(time.time())
        window_start = current_time - config['window']
        
        # Create cache keys
        request_key = f"rate_limit:requests:{identifier}:{path}"
        burst_key = f"rate_limit:burst:{identifier}:{path}"
        
        # Get current request count in the window
        request_count = cache.get(request_key, 0)
        
        # Get burst count (requests in last 10 seconds)
        burst_count = cache.get(burst_key, 0)
        
        # Check if limits are exceeded
        if request_count >= config['requests']:
            logger.warning(f"Rate limit exceeded for {identifier} on {path}: {request_count}/{config['requests']}")
            return False, "Rate limit exceeded. Too many requests."
        
        if burst_count >= config['burst']:
            logger.warning(f"Burst rate limit exceeded for {identifier} on {path}: {burst_count}/{config['burst']}")
            return False, "Rate limit exceeded. Too many requests in short time."
        
        return True, None
    
    def update_rate_limit_counters(self, identifier, path):
        """
        Update rate limit counters for the client.
        """
        config = self.get_rate_limit_config(path)
        current_time = int(time.time())
        
        # Request counter (sliding window)
        request_key = f"rate_limit:requests:{identifier}:{path}"
        cache.set(request_key, cache.get(request_key, 0) + 1, config['window'])
        
        # Burst counter (last 10 seconds)
        burst_key = f"rate_limit:burst:{identifier}:{path}"
        cache.set(burst_key, cache.get(burst_key, 0) + 1, 10)
    
    def process_request(self, request):
        """
        Process the request and check rate limits.
        """
        # Skip rate limiting for certain paths
        skip_paths = ['/admin/', '/static/', '/media/', '/__debug__/']
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Get client identifier
        identifier = self.get_client_identifier(request)
        
        # Check rate limit
        allowed, error_message = self.check_rate_limit(identifier, request.path)
        
        if not allowed:
            return JsonResponse({
                'success': False,
                'message': error_message,
                'status_code': 429,
                'payload': None,
                'error': 'RATE_LIMIT_EXCEEDED'
            }, status=429)
        
        # Update counters
        self.update_rate_limit_counters(identifier, request.path)
        
        return None
    
    def process_response(self, request, response):
        """
        Add rate limit headers to the response.
        """
        if hasattr(request, 'path') and not any(request.path.startswith(path) for path in ['/admin/', '/static/', '/media/', '/__debug__/']):
            identifier = self.get_client_identifier(request)
            config = self.get_rate_limit_config(request.path)
            
            # Add rate limit headers
            response['X-RateLimit-Limit'] = str(config['requests'])
            response['X-RateLimit-Window'] = str(config['window'])
            response['X-RateLimit-Remaining'] = str(max(0, config['requests'] - cache.get(f"rate_limit:requests:{identifier}:{request.path}", 0)))
        
        return response
