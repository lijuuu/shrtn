"""
ScyllaDB database connection for dependency injection.
"""
import os
import logging
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import acsylla
from django.conf import settings

logger = logging.getLogger(__name__)


class ScyllaDBConnection:
    """ScyllaDB database connection."""
    
    def __init__(self):
        self.cluster = None
        self.session = None
        self.keyspace = getattr(settings, 'SCYLLA_KEYSPACE', 'shrtn_keyspace')
        self.table = getattr(settings, 'SCYLLA_TABLE', 'short_urls')
        self._loop = None
        self.is_connected_flag = False
    
    def connect(self) -> None:
        """Connect to ScyllaDB."""
        try:
            # Get ScyllaDB hosts from Django settings
            use_docker = os.getenv('USE_DOCKER', 'no').lower()
            if use_docker in ['yes', 'true', '1']:
                hosts = ['scylla']
            else:
                # Parse hosts from settings
                scylla_hosts = getattr(settings, 'SCYLLA_HOSTS', '127.0.0.1:9042')
                hosts = [scylla_hosts.split(':')[0]]  # Remove port, acsylla handles it
            
            logger.info("Connecting to ScyllaDB hosts: %s", hosts)
            
            # Create event loop if none exists
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
            
            # Connect to ScyllaDB
            self._loop.run_until_complete(self._async_connect(hosts))
            self.is_connected_flag = True
            logger.info("ScyllaDB connection established")
        except Exception as e:
            logger.error("Failed to connect to ScyllaDB: %s", e)
            self.is_connected_flag = False
            raise
    
    async def _async_connect(self, hosts):
        """Async connection to ScyllaDB."""
        self.cluster = acsylla.create_cluster(hosts)
        self.session = await self.cluster.create_session(keyspace=self.keyspace)
    
    def disconnect(self) -> None:
        """Disconnect from ScyllaDB."""
        try:
            if self.cluster:
                self._loop.run_until_complete(self.cluster.close())
            self.is_connected_flag = False
            logger.info("ScyllaDB connection closed")
        except Exception as e:
            logger.error("Error closing ScyllaDB connection: %s", e)
    
    def is_connected(self) -> bool:
        """Check if connected to ScyllaDB."""
        return self.is_connected_flag and self.session is not None
    
    def get_connection(self):
        """Get ScyllaDB session."""
        if not self.is_connected():
            self.connect()
        return self.session
    
    def execute_query(self, query: str, params: Optional[list] = None) -> list:
        """Execute a CQL query and return results."""
        try:
            session = self.get_connection()
            prepared = self._loop.run_until_complete(session.create_prepared(query))
            statement = prepared.bind()
            
            if params:
                for i, param in enumerate(params):
                    statement.bind(i, param)
            
            result = self._loop.run_until_complete(session.execute(statement))
            return list(result)
        except Exception as e:
            logger.error("Error executing ScyllaDB query: %s", e)
            raise
    
    def execute_update(self, query: str, params: Optional[list] = None) -> int:
        """Execute an update/insert/delete query."""
        try:
            session = self.get_connection()
            prepared = self._loop.run_until_complete(session.create_prepared(query))
            statement = prepared.bind()
            
            if params:
                for i, param in enumerate(params):
                    statement.bind(i, param)
            
            self._loop.run_until_complete(session.execute(statement))
            return 1  # ScyllaDB doesn't return row count like PostgreSQL
        except Exception as e:
            logger.error("Error executing ScyllaDB update: %s", e)
            raise
    
    def execute_batch(self, queries: List[tuple]) -> int:
        """Execute multiple queries in a batch."""
        try:
            session = self.get_connection()
            
            # For now, execute queries sequentially since acsylla doesn't have batch support
            # In production, you might want to use a different approach or library
            for query, params in queries:
                prepared = self._loop.run_until_complete(session.create_prepared(query))
                statement = prepared.bind()
                
                if params:
                    for i, param in enumerate(params):
                        statement.bind(i, param)
                
                self._loop.run_until_complete(session.execute(statement))
            
            return len(queries)
        except Exception as e:
            logger.error("Error executing ScyllaDB batch: %s", e)
            raise