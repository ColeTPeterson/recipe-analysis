"""Defines the abstract base class that all repository implementations must follow;
provides a consistent interface for data access operations across different data sources.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any, Dict

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    """Abstract base repository providing a consistent interface for data access.
    
    Type Parameters:
        T: The entity type that the repository manages
    """
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity in the data store.
        
        Args:
            entity: The entity to create
            
        Returns:
            T: The created entity, typically with generated IDs or timestamps
            
        Raises:
            Exception: If entity creation fails
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all entities from the data store.
        
        Returns:
            List[T]: A list of all entities
            
        Raises:
            Exception: If retrieval fails
        """
        pass

    @abstractmethod
    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Retrieve a single entity by its unique identifier.
        
        Args:
            entity_id: The unique identifier of the entity
            
        Returns:
            Optional[T]: The entity if found, None otherwise
            
        Raises:
            Exception: If retrieval fails
        """
        pass

    @abstractmethod
    def find_by(self, criteria: Dict[str, Any]) -> List[T]:
        """Find entities matching the specified criteria.
        
        Args:
            criteria: Dictionary of field names and values to match
            
        Returns:
            List[T]: A list of entities matching the criteria
            
        Raises:
            Exception: If the search operation fails
        """
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an existing entity in the data store.
        
        Args:
            entity: The entity with updated values
            
        Returns:
            T: The updated entity
            
        Raises:
            Exception: If entity update fails
            ValueError: If the entity doesn't exist
        """
        pass

    @abstractmethod
    def delete(self, entity_id: Any) -> bool:
        """Delete an entity from the data store.
        
        Args:
            entity_id: The unique identifier of the entity to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            Exception: If deletion operation fails
        """
        pass
