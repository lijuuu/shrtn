"""
URL repository for ScyllaDB operations.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from core.database.base import Repository
from core.database.scylla import ScyllaDBConnection
from .models import ShortUrl

logger = logging.getLogger(__name__)


class UrlRepository(Repository):
    """Repository for URL operations using ScyllaDB."""
    
    def __init__(self, connection: ScyllaDBConnection):
        super().__init__(connection)
        self.scylla = connection
    
    def create(self, data: Dict[str, Any]) -> ShortUrl:
        """Create a new short URL."""
        try:
            url_id = uuid.uuid4()
            now = datetime.now(timezone.utc)
            tags_set = set(data.get('tags', []))
            
            query = """
            INSERT INTO short_urls (
                namespace_id, shortcode, id, created_at, created_by_user_id,
                original_url, expiry, click_count, updated_at, is_private, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = [
                data['namespace_id'],
                data['shortcode'],
                url_id,
                now,
                data['created_by_user_id'],
                data['original_url'],
                data.get('expiry'),
                0,  # click_count
                now,
                data.get('is_private', False),
                tags_set
            ]
            
            self.scylla.execute_update(query, params)
            
            # Return the created ShortUrl object
            return ShortUrl(
                id=url_id,
                namespace_id=data['namespace_id'],
                shortcode=data['shortcode'],
                original_url=data['original_url'],
                created_by_user_id=data['created_by_user_id'],
                expiry=data.get('expiry'),
                click_count=0,
                created_at=now,
                updated_at=now,
                is_private=data.get('is_private', False),
                tags=data.get('tags', [])
            )
        except Exception as e:
            logger.error("Failed to create short URL: %s", e)
            raise
    
    def get_by_id(self, id: tuple) -> Optional[ShortUrl]:
        """Get short URL by namespace_id and shortcode."""
        try:
            namespace_id, shortcode = id
            
            query = """
            SELECT * FROM short_urls
            WHERE namespace_id = ? AND shortcode = ?
            LIMIT 1
            """
            
            results = self.scylla.execute_query(query, [namespace_id, shortcode])
            if results:
                row = results[0]
                return ShortUrl(
                    id=row.id,
                    namespace_id=row.namespace_id,
                    shortcode=row.shortcode,
                    original_url=row.original_url,
                    created_by_user_id=row.created_by_user_id,
                    expiry=row.expiry,
                    click_count=row.click_count,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                    is_private=row.is_private,
                    tags=list(row.tags) if row.tags else []
                )
            return None
        except Exception as e:
            logger.error("Failed to get short URL: %s", e)
            raise
    
    def update(self, id: tuple, data: Dict[str, Any]) -> Optional[ShortUrl]:
        """Update short URL."""
        try:
            namespace_id, shortcode = id
            
            # For ScyllaDB, we need to update specific fields
            # This is a simplified version - in production you'd want more sophisticated updates
            if 'click_count' in data:
                # Increment click count
                query = """
                UPDATE short_urls
                SET click_count = click_count + 1, updated_at = ?
                WHERE namespace_id = ? AND shortcode = ?
                """
                now = datetime.now(timezone.utc)
                self.scylla.execute_update(query, [now, namespace_id, shortcode])
            
            return self.get_by_id(id)
        except Exception as e:
            logger.error("Failed to update short URL: %s", e)
            raise
    
    def delete(self, id: tuple) -> bool:
        """Delete short URL."""
        try:
            namespace_id, shortcode = id
            
            query = """
            DELETE FROM short_urls
            WHERE namespace_id = ? AND shortcode = ?
            """
            
            self.scylla.execute_update(query, [namespace_id, shortcode])
            return True
        except Exception as e:
            logger.error("Failed to delete short URL: %s", e)
            raise
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[ShortUrl]:
        """List short URLs with optional filters."""
        try:
            if filters and 'created_by_user_id' in filters:
                query = """
                SELECT * FROM short_urls
                WHERE created_by_user_id = ?
                ALLOW FILTERING
                """
                
                results = self.scylla.execute_query(query, [filters['created_by_user_id']])
                urls = []
                for row in results:
                    urls.append(ShortUrl(
                        id=row.id,
                        namespace_id=row.namespace_id,
                        shortcode=row.shortcode,
                        original_url=row.original_url,
                        created_by_user_id=row.created_by_user_id,
                        expiry=row.expiry,
                        click_count=row.click_count,
                        created_at=row.created_at,
                        updated_at=row.updated_at,
                        is_private=row.is_private,
                        tags=list(row.tags) if row.tags else []
                    ))
                return urls
            return []
        except Exception as e:
            logger.error("Failed to list short URLs: %s", e)
            raise
    
    def increment_click_count(self, namespace_id: int, shortcode: str) -> bool:
        """Increment click count for a short URL."""
        try:
            query = """
            UPDATE short_urls
            SET click_count = click_count + 1, updated_at = ?
            WHERE namespace_id = ? AND shortcode = ?
            """
            now = datetime.now(timezone.utc)
            self.scylla.execute_update(query, [now, namespace_id, shortcode])
            return True
        except Exception as e:
            logger.error("Failed to increment click count: %s", e)
            raise
    
    def batch_create(self, urls_data: List[Dict[str, Any]]) -> List[ShortUrl]:
        """Batch create short URLs."""
        try:
            queries = []
            created_urls = []
            
            for url_data in urls_data:
                url_id = uuid.uuid4()
                now = datetime.now(timezone.utc)
                tags_set = set(url_data.get('tags', []))
                
                query = """
                INSERT INTO short_urls (
                    namespace_id, shortcode, id, created_at, created_by_user_id,
                    original_url, expiry, click_count, updated_at, is_private, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                params = [
                    url_data['namespace_id'],
                    url_data['shortcode'],
                    url_id,
                    now,
                    url_data['created_by_user_id'],
                    url_data['original_url'],
                    url_data.get('expiry'),
                    0,  # click_count
                    now,
                    url_data.get('is_private', False),
                    tags_set
                ]
                
                queries.append((query, params))
                
                # Create ShortUrl object for return
                created_urls.append(ShortUrl(
                    id=url_id,
                    namespace_id=url_data['namespace_id'],
                    shortcode=url_data['shortcode'],
                    original_url=url_data['original_url'],
                    created_by_user_id=url_data['created_by_user_id'],
                    expiry=url_data.get('expiry'),
                    click_count=0,
                    created_at=now,
                    updated_at=now,
                    is_private=url_data.get('is_private', False),
                    tags=url_data.get('tags', [])
                ))
            
            # Execute batch
            self.scylla.execute_batch(queries)
            return created_urls
        except Exception as e:
            logger.error("Failed to batch create URLs: %s", e)
            raise
    
    def get_by_namespace(self, namespace_id: int) -> List[ShortUrl]:
        """Get all URLs in a namespace."""
        try:
            # This would require a secondary index or different query strategy
            # For now, we'll use the user-based query as a workaround
            # In production, you might want to add a namespace-based index
            return []
        except Exception as e:
            logger.error("Failed to get URLs by namespace: %s", e)
            raise
