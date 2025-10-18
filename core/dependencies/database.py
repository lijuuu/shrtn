"""
database dependency injection container with connection pooling.
"""
import logging
import threading
from typing import Optional
from core.database.postgres import PostgreSQLConnection
from core.database.scylla import ScyllaDBConnection
from core.redis.connection import RedisConnection
from core.s3.connection import S3Connection

logger = logging.getLogger(__name__)


class DatabaseDependency:
    """database dependency injection container with singleton pattern."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """initialize database connections only once."""
        if hasattr(self, '_initialized'):
            return
        
        self._postgres: Optional[PostgreSQLConnection] = None
        self._scylla: Optional[ScyllaDBConnection] = None
        self._redis: Optional[RedisConnection] = None
        self._s3: Optional[S3Connection] = None
        self._initialized = False
        self._lock = threading.Lock()
    
    def initialize_connections(self) -> None:
        """initialize all database connections at startup."""
        if self._initialized:
            return
        
        with self._lock:
            if self._initialized:
                return
            
            try:
                logger.info("initializing database connections...")
                
                #initialize postgresql connection (required)
                self._postgres = PostgreSQLConnection()
                self._postgres.connect()
                logger.info("postgresql connection initialized")
                
                #initialize redis connection (required for caching)
                self._redis = RedisConnection()
                self._redis.connect()
                logger.info("redis connection initialized")
                
                #initialize s3 connection (required for file storage)
                self._s3 = S3Connection()
                self._s3.connect()
                logger.info("s3 connection initialized")
                
                #try to initialize scylladb connection (optional)
                try:
                    self._scylla = ScyllaDBConnection()
                    self._scylla.connect()
                    logger.info("scylladb connection initialized")
                except Exception as scylla_error:
                    logger.warning("scylladb connection failed during startup: %s", scylla_error)
                    logger.info("scylladb will be initialized on first use")
                    self._scylla = None
                
                self._initialized = True
                logger.info("database connections initialized successfully")
                
            except Exception as e:
                logger.error("failed to initialize database connections: %s", e)
                #don't raise here to avoid breaking django startup
                logger.warning("database connections will be initialized on first use")
    
    def get_postgres(self) -> PostgreSQLConnection:
        """get postgresql connection."""
        if not self._initialized:
            self.initialize_connections()
        return self._postgres
    
    def get_redis(self) -> RedisConnection:
        """get redis connection."""
        if not self._initialized:
            self.initialize_connections()
        return self._redis
    
    def get_s3(self) -> S3Connection:
        """get s3 connection."""
        if not self._initialized:
            self.initialize_connections()
        return self._s3
    
    def get_scylla(self) -> ScyllaDBConnection:
        """get scylladb connection."""
        if not self._initialized:
            self.initialize_connections()
        
        #if scylladb wasn't initialized at startup, try to initialize it now
        if self._scylla is None:
            try:
                self._scylla = ScyllaDBConnection()
                self._scylla.connect()
                logger.info("scylladb connection initialized on first use")
            except Exception as e:
                logger.error("failed to initialize scylladb connection: %s", e)
                raise
        
        return self._scylla
    
    def close_all(self) -> None:
        """close all database connections."""
        with self._lock:
            if self._postgres:
                try:
                    self._postgres.disconnect()
                except Exception as e:
                    logger.error("error closing postgresql connection: %s", e)
            
            if self._redis:
                try:
                    self._redis.disconnect()
                except Exception as e:
                    logger.error("error closing redis connection: %s", e)
            
            if self._scylla:
                try:
                    self._scylla.disconnect()
                except Exception as e:
                    logger.error("error closing scylladb connection: %s", e)
            
            if self._s3:
                try:
                    self._s3.disconnect()
                except Exception as e:
                    logger.error("error closing s3 connection: %s", e)
            
            self._initialized = False
    
    def is_initialized(self) -> bool:
        """check if connections are initialized."""
        return self._initialized


#global database dependency instance
db_dependency = DatabaseDependency()
