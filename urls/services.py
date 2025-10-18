"""
URL service for business logic.
"""
import logging
from typing import List, Optional, Dict, Any
from core.database.base import Service
from .repositories import UrlRepository
from .models import ShortUrl

logger = logging.getLogger(__name__)


class UrlService(Service):
    """Service for URL business logic."""
    
    def __init__(self, repository: UrlRepository):
        super().__init__(repository)
        self.repository = repository
    
    def create(self, data: Dict[str, Any]) -> ShortUrl:
        """Create a new short URL with business logic validation."""
        try:
            # Business logic validation
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
            
            # Create the short URL
            return self.repository.create(data)
            
        except Exception as e:
            logger.error("Failed to create short URL: %s", e)
            raise
    
    def get_by_id(self, id: tuple) -> Optional[ShortUrl]:
        """Get short URL by ID."""
        try:
            return self.repository.get_by_id(id)
        except Exception as e:
            logger.error("Failed to get short URL: %s", e)
            raise
    
    def update(self, id: tuple, data: Dict[str, Any]) -> Optional[ShortUrl]:
        """Update short URL."""
        try:
            return self.repository.update(id, data)
        except Exception as e:
            logger.error("Failed to update short URL: %s", e)
            raise
    
    def delete(self, id: tuple) -> bool:
        """Delete short URL."""
        try:
            return self.repository.delete(id)
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
    
    def resolve_url(self, namespace_id: int, shortcode: str) -> Optional[str]:
        """Resolve short URL to original URL."""
        try:
            short_url = self.repository.get_by_id((namespace_id, shortcode))
            if short_url:
                # Increment click count
                self.repository.increment_click_count(namespace_id, shortcode)
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
    
    def get_by_user(self, user_id: int) -> List[ShortUrl]:
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
