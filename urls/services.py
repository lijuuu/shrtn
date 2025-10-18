"""
URL service for business logic with redis caching.
"""
import logging
from typing import List, Optional, Dict, Any
from core.database.base import Service
from core.utils.shortcode_generator import ShortcodeGenerator
from .repositories import UrlRepository
from .models import ShortUrl

logger = logging.getLogger(__name__)


class UrlService(Service):
    """Service for URL business logic with caching."""
    
    def __init__(self, repository: UrlRepository, cache_service=None):
        super().__init__(repository)
        self.repository = repository
        self.cache_service = cache_service
        self.shortcode_generator = ShortcodeGenerator()
    
    def create(self, data: Dict[str, Any]) -> ShortUrl:
        """Create a new short URL with business logic validation."""
        try:
            # Basic validation
            if not data.get('namespace_id'):
                raise ValueError("Namespace ID is required")
            
            if not data.get('shortcode'):
                raise ValueError("Shortcode is required")
            
            if not data.get('original_url'):
                raise ValueError("Original URL is required")
            
            if not data.get('created_by_user_id'):
                raise ValueError("Created by user ID is required")
            
            # Validate URL format
            if not self._is_valid_url(data['original_url']):
                raise ValueError("Invalid URL format")
            
            # Validate shortcode format
            if not self._is_valid_shortcode(data['shortcode']):
                raise ValueError("Shortcode can only contain letters, numbers, hyphens, and underscores")
            
            namespace_id = data['namespace_id']
            shortcode = data['shortcode']
            
            # Handle custom shortcode or generate one
            if not shortcode or shortcode.strip() == '':
                # Generate random shortcode
                shortcode = self.shortcode_generator.generate_unique_shortcode(namespace_id)
            else:
                # Validate custom shortcode
                if not self.shortcode_generator.is_valid_shortcode(shortcode):
                    raise ValueError(f"Invalid shortcode format: {shortcode}")
                
                # Check if shortcode already exists in this namespace
                if not self.shortcode_generator.is_shortcode_available(namespace_id, shortcode):
                    raise ValueError(f"Shortcode '{shortcode}' already exists in this namespace")
            
            # Create the short URL
            short_url = self.repository.create(data)
            
            # Cache the new URL if cache service is available
            if self.cache_service:
                try:
                    url_data = short_url.to_dict()
                    self.cache_service.cache_url(
                        data['namespace_id'], 
                        data['shortcode'], 
                        url_data
                    )
                    # Also cache the resolution for fast redirects
                    self.cache_service.cache_url_resolution(
                        data['namespace_id'], 
                        data['shortcode'], 
                        data['original_url']
                    )
                except Exception as cache_error:
                    logger.warning("failed to cache new url: %s", cache_error)
            
            return short_url
            
        except Exception as e:
            logger.error("Failed to create short URL: %s", e)
            raise
    
    def get_by_id(self, id: tuple) -> Optional[ShortUrl]:
        """Get short URL by ID with caching."""
        try:
            namespace_id, shortcode = id
            
            # Try cache first if available
            if self.cache_service:
                try:
                    cached_data = self.cache_service.get_cached_url(namespace_id, shortcode)
                    if cached_data:
                        # Convert cached data back to ShortUrl object
                        from .models import ShortUrl
                        return ShortUrl.from_dict(cached_data)
                except Exception as cache_error:
                    logger.warning("cache read error: %s", cache_error)
            
            # Fallback to database
            short_url = self.repository.get_by_id(id)
            
            # Cache the result if found
            if short_url and self.cache_service:
                try:
                    url_data = short_url.to_dict()
                    self.cache_service.cache_url(namespace_id, shortcode, url_data)
                except Exception as cache_error:
                    logger.warning("failed to cache url: %s", cache_error)
            
            return short_url
            
        except Exception as e:
            logger.error("Failed to get short URL: %s", e)
            raise
    
    def get_by_namespace(self, namespace_id: int) -> List[ShortUrl]:
        """Get all URLs in a namespace."""
        try:
            return self.repository.get_by_namespace(namespace_id)
        except Exception as e:
            logger.error("Failed to get URLs by namespace: %s", e)
            raise
    
    def update(self, id: tuple, data: Dict[str, Any]) -> Optional[ShortUrl]:
        """Update short URL with cache invalidation."""
        try:
            namespace_id, shortcode = id
            updated_url = self.repository.update(id, data)
            
            # Invalidate cache if update was successful
            if updated_url and self.cache_service:
                try:
                    self.cache_service.invalidate_url(namespace_id, shortcode)
                    self.cache_service.invalidate_resolution(namespace_id, shortcode)
                    
                    # Re-cache the updated URL
                    url_data = updated_url.to_dict()
                    self.cache_service.cache_url(namespace_id, shortcode, url_data)
                    if 'original_url' in data:
                        self.cache_service.cache_url_resolution(
                            namespace_id, shortcode, data['original_url']
                        )
                except Exception as cache_error:
                    logger.warning("failed to update cache: %s", cache_error)
            
            return updated_url
            
        except Exception as e:
            logger.error("Failed to update short URL: %s", e)
            raise
    
    def delete(self, id: tuple) -> bool:
        """Delete short URL with cache invalidation."""
        try:
            namespace_id, shortcode = id
            success = self.repository.delete(id)
            
            # Invalidate cache if deletion was successful
            if success and self.cache_service:
                try:
                    self.cache_service.invalidate_url(namespace_id, shortcode)
                    self.cache_service.invalidate_resolution(namespace_id, shortcode)
                except Exception as cache_error:
                    logger.warning("failed to invalidate cache: %s", cache_error)
            
            return success
            
        except Exception as e:
            logger.error("Failed to delete short URL: %s", e)
            raise
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[ShortUrl]:
        """List short URLs with optional filters."""
        try:
            return self.repository.list(filters)
        except Exception as e:
            logger.error("Failed to list short URLs: %s", e)
            raise
    
    def resolve_url(self, namespace_id: int, shortcode: str, request_meta: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Resolve short URL to original URL with caching, hot url tracking, and analytics."""
        try:
            # Try cache first for fast resolution
            if self.cache_service:
                try:
                    cached_url = self.cache_service.get_cached_resolution(namespace_id, shortcode)
                    if cached_url:
                        # Track as hot URL
                        self.cache_service.track_hot_url(namespace_id, shortcode)
                        logger.debug("cache hit for url resolution: %s:%s", namespace_id, shortcode)
                        return cached_url
                except Exception as cache_error:
                    logger.warning("cache read error during resolution: %s", cache_error)
            
            # Fallback to database
            short_url = self.repository.get_by_id((namespace_id, shortcode))
            if short_url:
                # Increment click count
                self.repository.increment_click_count(namespace_id, shortcode)
                
                # Track analytics if request metadata is available
                if request_meta:
                    try:
                        from core.dependencies.service_registry import service_registry
                        analytics_service = service_registry.get_analytics_service()
                        if analytics_service:
                            analytics_service.track_click(
                                namespace_id=namespace_id,
                                shortcode=shortcode,
                                ip_address=request_meta.get('ip_address', ''),
                                user_agent=request_meta.get('user_agent', ''),
                                referer=request_meta.get('referer', '')
                            )
                    except Exception as analytics_error:
                        logger.warning("failed to track analytics: %s", analytics_error)
                
                # Cache the resolution for future requests
                if self.cache_service:
                    try:
                        self.cache_service.cache_url_resolution(
                            namespace_id, shortcode, short_url.original_url
                        )
                        # Track as hot URL
                        self.cache_service.track_hot_url(namespace_id, shortcode)
                    except Exception as cache_error:
                        logger.warning("failed to cache resolution: %s", cache_error)
                
                return short_url.original_url
            
            return None
            
        except Exception as e:
            logger.error("Failed to resolve URL: %s", e)
            raise
    
    def increment_click_count(self, namespace_id: int, shortcode: str) -> bool:
        """Increment click count for a short URL."""
        try:
            return self.repository.increment_click_count(namespace_id, shortcode)
        except Exception as e:
            logger.error("Failed to increment click count: %s", e)
            raise
    
    def batch_create(self, urls_data: List[Dict[str, Any]]) -> List[ShortUrl]:
        """Batch create short URLs."""
        try:
            # Validate all URLs before batch creation
            for url_data in urls_data:
                if not self._is_valid_url(url_data.get('original_url', '')):
                    raise ValueError(f"Invalid URL format: {url_data.get('original_url')}")
            
            return self.repository.batch_create(urls_data)
        except Exception as e:
            logger.error("Failed to batch create URLs: %s", e)
            raise
    
    def get_by_user(self, user_id: uuid.UUID) -> List[ShortUrl]:
        """Get all URLs created by a user."""
        try:
            return self.repository.list({'created_by_user_id': user_id})
        except Exception as e:
            logger.error("Failed to get URLs by user: %s", e)
            raise
    
    def get_by_namespace(self, namespace_id: int) -> List[ShortUrl]:
        """Get all URLs in a namespace."""
        try:
            return self.repository.get_by_namespace(namespace_id)
        except Exception as e:
            logger.error("Failed to get URLs by namespace: %s", e)
            raise
    
    def get_hot_urls(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of hot URLs (most accessed)."""
        try:
            if self.cache_service:
                return self.cache_service.get_hot_urls(limit)
            return []
        except Exception as e:
            logger.error("Failed to get hot URLs: %s", e)
            return []
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            if self.cache_service:
                return self.cache_service.get_cache_stats()
            return {'error': 'cache service not available'}
        except Exception as e:
            logger.error("Failed to get cache stats: %s", e)
            return {'error': str(e)}
    
    def clear_cache(self) -> bool:
        """Clear all URL cache."""
        try:
            if self.cache_service:
                return self.cache_service.clear_all_cache()
            return False
        except Exception as e:
            logger.error("Failed to clear cache: %s", e)
            return False
    
    def _is_valid_shortcode(self, shortcode: str) -> bool:
        """Validate shortcode format."""
        import re
        # Shortcode should be 3-50 characters, alphanumeric, hyphens, underscores only
        if not shortcode or len(shortcode) < 3 or len(shortcode) > 50:
            return False
        
        # Check format: letters, numbers, hyphens, underscores only
        if not re.match(r'^[a-zA-Z0-9_-]+$', shortcode):
            return False
        
        # Cannot start or end with hyphen or underscore
        if shortcode.startswith(('-', '_')) or shortcode.endswith(('-', '_')):
            return False
        
        return True
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    def migrate_namespace_name(self, old_namespace_name: str, new_namespace_name: str) -> bool:
        """Migrate all URLs from old namespace name to new namespace name."""
        try:
            # Use repository method to migrate URLs in ScyllaDB
            success = self.repository.migrate_namespace_name(old_namespace_name, new_namespace_name)
            
            if success and self.cache_service:
                # Clear cache for all URLs in the old namespace
                try:
                    # Get all URLs in the old namespace to clear their cache
                    old_urls = self.get_by_namespace_name(old_namespace_name)
                    for url in old_urls:
                        self.cache_service.invalidate_url(url.namespace_id, url.shortcode)
                        self.cache_service.invalidate_resolution(url.namespace_id, url.shortcode)
                    
                    logger.info("Cleared cache for migrated URLs from namespace %s", old_namespace_name)
                except Exception as cache_error:
                    logger.warning("Failed to clear cache during namespace migration: %s", cache_error)
            
            return success
            
        except Exception as e:
            logger.error("Failed to migrate namespace name: %s", e)
            raise
    
    def process_bulk_urls(self, excel_file, namespace_id: uuid.UUID, user_id: uuid.UUID, method: str = 'random') -> Dict[str, Any]:
        """Process bulk URLs from Excel file."""
        try:
            from core.bulk.excel_processor import ExcelProcessor
            
            processor = ExcelProcessor()
            return processor.process_bulk_urls(excel_file, namespace_id, user_id, method)
            
        except Exception as e:
            logger.error("Failed to process bulk URLs: %s", e)
            return {
                'success': False,
                'error': str(e),
                'processed_count': 0,
                'error_count': 0,
                'results': [],
                'errors': [str(e)]
            }
    
    def get_template_excel(self) -> bytes:
        """Get template Excel file for bulk URL upload."""
        try:
            from core.bulk.excel_processor import ExcelProcessor
            
            processor = ExcelProcessor()
            return processor.get_template_excel()
            
        except Exception as e:
            logger.error("Failed to get template Excel: %s", e)
            raise
