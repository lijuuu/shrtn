"""
Base database interface for dependency injection.
"""
from abc import ABC, abstractmethod
from typing import Protocol, Any, Dict, List, Optional


class DatabaseConnection(Protocol):
    """Protocol for database connections."""
    
    def connect(self) -> None:
        """Connect to the database."""
        ...
    
    def disconnect(self) -> None:
        """Disconnect from the database."""
        ...
    
    def is_connected(self) -> bool:
        """Check if connected to the database."""
        ...


class Repository(ABC):
    """Base repository interface."""
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Any:
        """Create a new record."""
        pass
    
    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[Any]:
        """Get record by ID."""
        pass
    
    @abstractmethod
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[Any]:
        """Update record by ID."""
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Delete record by ID."""
        pass
    
    @abstractmethod
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """List records with optional filters."""
        pass


class Service(ABC):
    """Base service interface."""
    
    def __init__(self, repository: Repository):
        self.repository = repository
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Any:
        """Create a new entity."""
        pass
    
    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[Any]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[Any]:
        """Update entity by ID."""
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """List entities with optional filters."""
        pass
