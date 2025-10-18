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
    
    def get_by_namespace(self, namespace_id: int) -> List[ShortUrl]:
        """Get all URLs in a namespace."""
        try:
            query = """
            SELECT * FROM short_urls
            WHERE namespace_id = ?
            """
            
            results = self.scylla.execute_query(query, [namespace_id])
            urls = []
            
            for row in results:
                url = ShortUrl(
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
                urls.append(url)
            
            return urls
        except Exception as e:
            logger.error("Failed to get URLs by namespace: %s", e)
            raise
    
    def migrate_namespace_name(self, old_namespace_name: str, new_namespace_name: str) -> bool:
        """Migrate all URLs from old namespace name to new namespace name."""
        try:
            # Get all URLs with the old namespace name
            query = """
            SELECT * FROM short_urls
            WHERE namespace_name = ?
            """
            
            results = self.scylla.execute_query(query, [old_namespace_name])
            
            if not results:
                logger.info("No URLs found for namespace %s", old_namespace_name)
                return True
            
            # For each URL, delete the old entry and create a new one with new namespace name
            for row in results:
                # Delete old entry
                delete_query = """
                DELETE FROM short_urls
                WHERE namespace_name = ? AND shortcode = ?
                """
                self.scylla.execute_delete(delete_query, [old_namespace_name, row.shortcode])
                
                # Insert new entry with new namespace name
                insert_query = """
                INSERT INTO short_urls (
                    namespace_name, shortcode, original_url, created_by_user_id,
                    expiry, click_count, created_at, updated_at, is_private, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                self.scylla.execute_insert(insert_query, [
                    new_namespace_name, row.shortcode, row.original_url, row.created_by_user_id,
                    row.expiry, row.click_count, row.created_at, row.updated_at, 
                    row.is_private, row.tags
                ])
                
                logger.info("Migrated URL %s from namespace %s to %s", 
                          row.shortcode, old_namespace_name, new_namespace_name)
            
            logger.info("Successfully migrated %d URLs from namespace %s to %s", 
                       len(results), old_namespace_name, new_namespace_name)
            return True
            
        except Exception as e:
            logger.error("Failed to migrate namespace name from %s to %s: %s", 
                        old_namespace_name, new_namespace_name, e)
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
            # First, get the full record to get all primary key components
            get_query = """
            SELECT * FROM short_urls
            WHERE namespace_id = ? AND shortcode = ?
            LIMIT 1
            """
            results = self.scylla.execute_query(get_query, [namespace_id, shortcode])
            if not results:
                return False
            
            row = results[0]
            current_count = row.click_count
            
            # Then update with the new count, including all clustering keys
            update_query = """
            UPDATE short_urls
            SET click_count = ?, updated_at = ?
            WHERE namespace_id = ? AND shortcode = ? AND id = ? AND created_at = ?
            """
            now = datetime.now(timezone.utc)
            self.scylla.execute_update(update_query, [
                current_count + 1, now, namespace_id, shortcode, row.id, row.created_at
            ])
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
