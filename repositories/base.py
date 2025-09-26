"""Defines the abstract base class that all repository implementations must follow;
provides a consistent interface for data access operations across different data sources.
"""

import abc
from typing import Generic, TypeVar, List, Optional, Dict, Any, Union


T = TypeVar('T')
class BaseRepository(Generic[T], abc.ABC):
    """Abstract base repository defining the interface for data access.
    
    This class serves as a contract for all repository implementations,
    ensuring a consistent API across different data stores.
    """
    
    # Read Operations
    @abc.abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all entities from the data store.
        
        Returns:
            List[T]: List of all entities
        """
        pass
        
    @abc.abstractmethod
    def get_by_id(self, entity_id: Union[int, str]) -> Optional[T]:
        """Retrieve an entity by ID.
        
        Args:
            entity_id (Union[int, str]): ID of the entity
            
        Returns:
            Optional[T]: Entity if found, None otherwise
        """
        pass
    
    # Search Operations
    def find_by(self, criteria: Dict[str, Any]) -> List[T]:
        """Find entities matching the specified criteria.
        
        Args:
            criteria (Dict[str, Any]): Search criteria
            
        Returns:
            List[T]: List of matching entities
        """
        raise NotImplementedError("find_by method not implemented")

    # Create/Update/Delete Operations
    @abc.abstractmethod
    def create(self, entity: T) -> Optional[T]:
        """Create a new entity in the data store.
        
        Args:
            entity (T): Entity to create
            
        Returns:
            Optional[T]: Created entity with ID assigned, or None if failed
        """
        pass

    @abc.abstractmethod
    def update(self, entity: T) -> Optional[T]:
        """Update an existing entity in the data store.
        
        Args:
            entity (T): Entity to update
            
        Returns:
            Optional[T]: Updated entity, or None if failed
        """
        pass
        
    @abc.abstractmethod
    def delete(self, entity_id: Union[int, str]) -> bool:
        """Delete an entity.
        
        Args:
            entity_id (Union[int, str]): ID of the entity to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass
