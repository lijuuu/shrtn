"""
Database dependency injection container.
"""
import logging
from typing import Optional
from core.database.postgres import PostgreSQLConnection
from core.database.scylla import ScyllaDBConnection

logger = logging.getLogger(__name__)


class DatabaseDependency:
    """Database dependency injection container."""
    
    def __init__(self):
        self._postgres: Optional[PostgreSQLConnection] = None
        self._scylla: Optional[ScyllaDBConnection] = None
    
    def get_postgres(self) -> PostgreSQLConnection:
        """Get PostgreSQL connection."""
        if self._postgres is None:
            self._postgres = PostgreSQLConnection()
            try:
                self._postgres.connect()
            except Exception as e:
                logger.error("Failed to initialize PostgreSQL connection: %s", e)
                raise
        return self._postgres
    
    def get_scylla(self) -> ScyllaDBConnection:
        """Get ScyllaDB connection."""
        if self._scylla is None:
            self._scylla = ScyllaDBConnection()
            try:
                self._scylla.connect()
            except Exception as e:
                logger.error("Failed to initialize ScyllaDB connection: %s", e)
                raise
        return self._scylla
    
    def close_all(self) -> None:
        """Close all database connections."""
        if self._postgres:
            try:
                self._postgres.disconnect()
            except Exception as e:
                logger.error("Error closing PostgreSQL connection: %s", e)
        
        if self._scylla:
            try:
                self._scylla.disconnect()
            except Exception as e:
                logger.error("Error closing ScyllaDB connection: %s", e)


# Global database dependency instance
db_dependency = DatabaseDependency()
