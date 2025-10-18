"""
redis-based url cache service with lru eviction.
"""
import logging
import json
from typing import Optional, Dict, Any
from .connection import RedisConnection

logger = logging.getLogger(__name__)


class UrlCacheService:
    """redis-based url cache with lru eviction policy."""
    
    def __init__(self, redis_connection: RedisConnection):
        self.redis = redis_connection
        self.cache_prefix = "url_cache"
        self.max_cache_size = 10000  #max number of cached urls
        self.default_ttl = 3600  #1 hour default ttl
    
    def _get_cache_key(self, namespace_id: int, shortcode: str) -> str:
        """generate cache key for url."""
        return f"{self.cache_prefix}:{namespace_id}:{shortcode}"
    
    def _get_hot_urls_key(self) -> str:
        """get key for hot urls tracking."""
        return f"{self.cache_prefix}:hot_urls"
    
    def cache_url(self, namespace_id: int, shortcode: str, url_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """cache url data with lru eviction."""
        try:
            cache_key = self._get_cache_key(namespace_id, shortcode)
            cache_data = json.dumps(url_data)
            
            #use lru cache with custom ttl
            cache_ttl = ttl or self.default_ttl
            success = self.redis.lru_set(cache_key, cache_data, self.max_cache_size, cache_ttl)
            
            if success:
                logger.debug("cached url: %s:%s", namespace_id, shortcode)
            
            return success
            
        except Exception as e:
            logger.error("failed to cache url %s:%s: %s", namespace_id, shortcode, e)
            return False
    
    def get_cached_url(self, namespace_id: int, shortcode: str) -> Optional[Dict[str, Any]]:
        """get cached url data."""
        try:
            cache_key = self._get_cache_key(namespace_id, shortcode)
            cached_data = self.redis.lru_get(cache_key)
            
            if cached_data:
                url_data = json.loads(cached_data)
                logger.debug("cache hit for url: %s:%s", namespace_id, shortcode)
                return url_data
            
            logger.debug("cache miss for url: %s:%s", namespace_id, shortcode)
            return None
            
        except Exception as e:
            logger.error("failed to get cached url %s:%s: %s", namespace_id, shortcode, e)
            return None
    
    def invalidate_url(self, namespace_id: int, shortcode: str) -> bool:
        """invalidate cached url."""
        try:
            cache_key = self._get_cache_key(namespace_id, shortcode)
            success = self.redis.lru_delete(cache_key)
            
            if success:
                logger.debug("invalidated cached url: %s:%s", namespace_id, shortcode)
            
            return success
            
        except Exception as e:
            logger.error("failed to invalidate cached url %s:%s: %s", namespace_id, shortcode, e)
            return False
    
    def track_hot_url(self, namespace_id: int, shortcode: str) -> bool:
        """track url as hot (frequently accessed)."""
        try:
            hot_urls_key = self._get_hot_urls_key()
            url_identifier = f"{namespace_id}:{shortcode}"
            
            #increment access count
            self.redis.get_connection().zincrby(hot_urls_key, 1, url_identifier)
            
            #set expiration for hot urls tracking (24 hours)
            self.redis.expire(hot_urls_key, 86400)
            
            logger.debug("tracked hot url: %s", url_identifier)
            return True
            
        except Exception as e:
            logger.error("failed to track hot url %s:%s: %s", namespace_id, shortcode, e)
            return False
    
    def get_hot_urls(self, limit: int = 100) -> list:
        """get list of hot urls (most accessed)."""
        try:
            hot_urls_key = self._get_hot_urls_key()
            client = self.redis.get_connection()
            
            #get top accessed urls
            hot_urls = client.zrevrange(hot_urls_key, 0, limit - 1, withscores=True)
            
            result = []
            for url_identifier, score in hot_urls:
                namespace_id, shortcode = url_identifier.split(':', 1)
                result.append({
                    'namespace_id': int(namespace_id),
                    'shortcode': shortcode,
                    'access_count': int(score)
                })
            
            logger.debug("retrieved %d hot urls", len(result))
            return result
            
        except Exception as e:
            logger.error("failed to get hot urls: %s", e)
            return []
    
    def cache_url_resolution(self, namespace_id: int, shortcode: str, original_url: str, ttl: Optional[int] = None) -> bool:
        """cache url resolution for fast redirects."""
        try:
            resolution_key = f"{self.cache_prefix}:resolve:{namespace_id}:{shortcode}"
            cache_ttl = ttl or 7200  #2 hours for resolution cache
            
            success = self.redis.set(resolution_key, original_url, ex=cache_ttl)
            
            if success:
                logger.debug("cached url resolution: %s:%s -> %s", namespace_id, shortcode, original_url)
            
            return success
            
        except Exception as e:
            logger.error("failed to cache url resolution %s:%s: %s", namespace_id, shortcode, e)
            return False
    
    def get_cached_resolution(self, namespace_id: int, shortcode: str) -> Optional[str]:
        """get cached url resolution."""
        try:
            resolution_key = f"{self.cache_prefix}:resolve:{namespace_id}:{shortcode}"
            original_url = self.redis.get(resolution_key)
            
            if original_url:
                logger.debug("cache hit for url resolution: %s:%s", namespace_id, shortcode)
                return original_url
            
            logger.debug("cache miss for url resolution: %s:%s", namespace_id, shortcode)
            return None
            
        except Exception as e:
            logger.error("failed to get cached resolution %s:%s: %s", namespace_id, shortcode, e)
            return None
    
    def invalidate_resolution(self, namespace_id: int, shortcode: str) -> bool:
        """invalidate cached url resolution."""
        try:
            resolution_key = f"{self.cache_prefix}:resolve:{namespace_id}:{shortcode}"
            success = self.redis.delete(resolution_key)
            
            if success:
                logger.debug("invalidated cached resolution: %s:%s", namespace_id, shortcode)
            
            return success
            
        except Exception as e:
            logger.error("failed to invalidate cached resolution %s:%s: %s", namespace_id, shortcode, e)
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """get cache statistics."""
        try:
            stats = self.redis.lru_stats()
            stats['cache_prefix'] = self.cache_prefix
            stats['max_cache_size'] = self.max_cache_size
            stats['default_ttl'] = self.default_ttl
            
            #get hot urls count
            hot_urls_key = self._get_hot_urls_key()
            hot_urls_count = self.redis.get_connection().zcard(hot_urls_key)
            stats['hot_urls_count'] = hot_urls_count
            
            return stats
            
        except Exception as e:
            logger.error("failed to get cache stats: %s", e)
            return {'error': str(e)}
    
    def clear_all_cache(self) -> bool:
        """clear all url cache."""
        try:
            #clear lru cache
            self.redis.lru_clear()
            
            #clear hot urls tracking
            hot_urls_key = self._get_hot_urls_key()
            self.redis.delete(hot_urls_key)
            
            #clear resolution cache (pattern matching)
            client = self.redis.get_connection()
            resolution_keys = client.keys(f"{self.cache_prefix}:resolve:*")
            if resolution_keys:
                client.delete(*resolution_keys)
            
            logger.info("cleared all url cache")
            return True
            
        except Exception as e:
            logger.error("failed to clear all cache: %s", e)
            return False

