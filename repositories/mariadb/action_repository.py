"""Provides data access operations for action entities stored in MariaDB.
Handles fetching action information, mapping database records to domain objects,
and managing action symbols and their properties including arity.
"""

import logging
from typing import List, Optional, Dict, Any

from .symbol_repository import SymbolRepository
from models.symbol import SymbolType, Symbol
from models.instruction import Action, ActionArity

logger = logging.getLogger(__name__)


class ActionRepository(SymbolRepository):
    """Provides data access methods for action-related operations,
    handles database operations, entity mapping, and domain object creation.
    """
    
    def __init__(self):
        """Creates a MariaDBConnectionManager instance to handle database connections."""
        super().__init__()
        self.symbol_type = SymbolType.ACTION

    # Read Operations
    def get_all(self) -> List[Action]:
        return self.get_symbols_by_type(self.symbol_type)

    def get_by_id(self, entity_id: int) -> Optional[Action]:
        return self._get_symbol_by_id_and_type(entity_id, self.symbol_type)
    
    def get_all_action_identities(self) -> List[str]:
        """Get all action identities.
        
        Returns:
            List[str]: List of all action identity names
        """
        return self.get_all_identities(self.symbol_type)
    
    def get_all_action_properties(self) -> List[str]:
        """Get all action property keys.
        
        Returns:
            List[str]: List of all action property keys
        """
        return self.get_all_properties(self.symbol_type)

    def get_all_action_property_values(self) -> Dict[str, List[str]]:
        """Get all action property keys and their values.
        
        Returns:
            Dict[str, List[str]]: Dictionary with property keys as keys and list of values as values
        """
        return self.get_all_property_values(self.symbol_type)

    # Search Operations
    def find_by(self, criteria: Dict[str, Any]) -> List[Action]:
        criteria['type'] = self.symbol_type
        return super().find_by(criteria)

    def find_by_name(self, name: str) -> List[Action]:
        return self._search_symbols_in_tables(name, self.symbol_type)

    def find_by_arity(self, arity: ActionArity) -> List[Action]:
        try:
            return self.find_by({'arity': arity})
        except Exception as e:
            logger.error(f"Error finding actions by arity {arity}: {e}")
            return []
        
    def find_action_identities_by_name(self, name_pattern: str) -> List[str]:
        """Find action identities by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching action identity names
        """
        return self.find_identities_by_name(name_pattern, self.symbol_type)
    
    def find_action_properties_by_name(self, name_pattern: str) -> List[str]:
        """Find action property keys by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching action property keys
        """
        return self.find_properties_by_name(name_pattern, self.symbol_type)
    
    # Create/Update/Delete Operations
    def create(self, entity: Action) -> Optional[Action]:
        return super().create(entity)

    def update(self, entity: Action) -> Optional[Action]:
        return super().update(entity)

    def delete(self, entity_id: int) -> bool:
        return super().delete(entity_id)
