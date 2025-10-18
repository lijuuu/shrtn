"""
PostgreSQL database connection for dependency injection.
"""
import os
import logging
from typing import Optional
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)


class PostgreSQLConnection:
    """PostgreSQL database connection."""
    
    def __init__(self):
        self.connection = None
        self.is_connected_flag = False
    
    def connect(self) -> None:
        """Connect to PostgreSQL database."""
        try:
            # Django handles the connection automatically
            # We just need to ensure it's available
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.is_connected_flag = True
            logger.info("PostgreSQL connection established")
        except Exception as e:
            logger.error("Failed to connect to PostgreSQL: %s", e)
            self.is_connected_flag = False
            raise
    
    def disconnect(self) -> None:
        """Disconnect from PostgreSQL database."""
        try:
            connection.close()
            self.is_connected_flag = False
            logger.info("PostgreSQL connection closed")
        except Exception as e:
            logger.error("Error closing PostgreSQL connection: %s", e)
    
    def is_connected(self) -> bool:
        """Check if connected to PostgreSQL."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def get_connection(self):
        """Get Django database connection."""
        return connection
    
    def execute_query(self, query: str, params: Optional[list] = None) -> list:
        """Execute a raw SQL query."""
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or [])
                return cursor.fetchall()
        except Exception as e:
            logger.error("Error executing PostgreSQL query: %s", e)
            raise
    
    def execute_update(self, query: str, params: Optional[list] = None) -> int:
        """Execute an update/insert/delete query."""
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or [])
                return cursor.rowcount
        except Exception as e:
            logger.error("Error executing PostgreSQL update: %s", e)
            raise
