"""
redis connection for dependency injection.
"""
import logging
import redis
from typing import Optional, Any, Dict, List
from django.conf import settings

logger = logging.getLogger(__name__)


class RedisConnection:
    """redis connection with lru cache support."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.is_connected_flag = False
    
    def connect(self) -> None:
        """connect to redis server."""
        try:
            #get redis url from celery broker url or default
            redis_url = getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0')
            
            #create redis client with connection pooling
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            #test connection
            self.redis_client.ping()
            self.is_connected_flag = True
            logger.info("redis connection established")
            
        except Exception as e:
            logger.error("failed to connect to redis: %s", e)
            self.is_connected_flag = False
            raise
    
    def disconnect(self) -> None:
        """disconnect from redis server."""
        try:
            if self.redis_client:
                self.redis_client.close()
            self.is_connected_flag = False
            logger.info("redis connection closed")
        except Exception as e:
            logger.error("error closing redis connection: %s", e)
    
    def is_connected(self) -> bool:
        """check if connected to redis."""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except Exception:
            pass
        return False
    
    def get_connection(self) -> redis.Redis:
        """get redis client."""
        if not self.is_connected():
            self.connect()
        return self.redis_client
    
    #basic redis operations
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """set key-value pair with optional expiration."""
        try:
            client = self.get_connection()
            return client.set(key, value, ex=ex)
        except Exception as e:
            logger.error("redis set error: %s", e)
            return False
    
    def get(self, key: str) -> Optional[str]:
        """get value by key."""
        try:
            client = self.get_connection()
            return client.get(key)
        except Exception as e:
            logger.error("redis get error: %s", e)
            return None
    
    def delete(self, key: str) -> bool:
        """delete key."""
        try:
            client = self.get_connection()
            return bool(client.delete(key))
        except Exception as e:
            logger.error("redis delete error: %s", e)
            return False
    
    def exists(self, key: str) -> bool:
        """check if key exists."""
        try:
            client = self.get_connection()
            return bool(client.exists(key))
        except Exception as e:
            logger.error("redis exists error: %s", e)
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """set expiration for key."""
        try:
            client = self.get_connection()
            return bool(client.expire(key, seconds))
        except Exception as e:
            logger.error("redis expire error: %s", e)
            return False
    
    def ttl(self, key: str) -> int:
        """get time to live for key."""
        try:
            client = self.get_connection()
            return client.ttl(key)
        except Exception as e:
            logger.error("redis ttl error: %s", e)
            return -1
    
    #lru cache operations
    def lru_set(self, key: str, value: Any, max_size: int = 1000, ttl: int = 3600) -> bool:
        """set value with lru eviction policy."""
        try:
            client = self.get_connection()
            cache_key = f"lru:{key}"
            
            #use redis sorted set for lru tracking
            lru_key = "lru:tracker"
            current_time = client.time()[0]  #get current unix timestamp
            
            #add to cache
            client.setex(cache_key, ttl, value)
            
            #update lru tracker
            client.zadd(lru_key, {cache_key: current_time})
            
            #check if we need to evict
            cache_count = client.zcard(lru_key)
            if cache_count > max_size:
                #remove oldest entries
                oldest_keys = client.zrange(lru_key, 0, cache_count - max_size - 1)
                if oldest_keys:
                    #delete from cache
                    client.delete(*oldest_keys)
                    #remove from tracker
                    client.zrem(lru_key, *oldest_keys)
            
            return True
            
        except Exception as e:
            logger.error("redis lru_set error: %s", e)
            return False
    
    def lru_get(self, key: str) -> Optional[str]:
        """get value with lru update."""
        try:
            client = self.get_connection()
            cache_key = f"lru:{key}"
            lru_key = "lru:tracker"
            
            #get value
            value = client.get(cache_key)
            if value is not None:
                #update lru timestamp
                current_time = client.time()[0]
                client.zadd(lru_key, {cache_key: current_time})
            
            return value
            
        except Exception as e:
            logger.error("redis lru_get error: %s", e)
            return None
    
    def lru_delete(self, key: str) -> bool:
        """delete from lru cache."""
        try:
            client = self.get_connection()
            cache_key = f"lru:{key}"
            lru_key = "lru:tracker"
            
            #delete from cache
            client.delete(cache_key)
            #remove from tracker
            client.zrem(lru_key, cache_key)
            
            return True
            
        except Exception as e:
            logger.error("redis lru_delete error: %s", e)
            return False
    
    def lru_clear(self) -> bool:
        """clear all lru cache."""
        try:
            client = self.get_connection()
            lru_key = "lru:tracker"
            
            #get all lru keys
            all_keys = client.zrange(lru_key, 0, -1)
            if all_keys:
                #delete all cache entries
                client.delete(*all_keys)
                #clear tracker
                client.delete(lru_key)
            
            return True
            
        except Exception as e:
            logger.error("redis lru_clear error: %s", e)
            return False
    
    def lru_stats(self) -> Dict[str, Any]:
        """get lru cache statistics."""
        try:
            client = self.get_connection()
            lru_key = "lru:tracker"
            
            total_keys = client.zcard(lru_key)
            memory_usage = client.memory_usage(lru_key) if hasattr(client, 'memory_usage') else 0
            
            return {
                'total_keys': total_keys,
                'memory_usage': memory_usage,
                'oldest_key': client.zrange(lru_key, 0, 0)[0] if total_keys > 0 else None,
                'newest_key': client.zrange(lru_key, -1, -1)[0] if total_keys > 0 else None
            }
            
        except Exception as e:
            logger.error("redis lru_stats error: %s", e)
            return {'error': str(e)}
