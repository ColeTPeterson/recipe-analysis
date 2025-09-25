"""Provides data access operations for ingredient entities stored in MariaDB;
handles fetching ingredient information, mapping database records to domain objects,
and managing ingredient symbols, measurements, and properties.
"""

import logging
from typing import List, Optional, Dict, Any

from .symbol_repository import SymbolRepository
from models.ingredient import Ingredient
from models.symbol import SymbolType, Symbol

logger = logging.getLogger(__name__)


class IngredientRepository(SymbolRepository):
    """Provides data access methods for ingredient-related operations,
    handles database operations, entity mapping, and domain object creation.
    """
    
    def __init__(self):
        """Creates a MariaDBConnectionManager instance to handle database connections."""
        super().__init__()
        self.symbol_type = SymbolType.INGREDIENT
    
    # Read Operations
    def get_all(self) -> List[Ingredient]:
        return self.get_symbols_by_type(self.symbol_type)

    def get_by_id(self, entity_id: int) -> Optional[Ingredient]:
        return self._get_symbol_by_id_and_type(entity_id, self.symbol_type)

    def get_all_ingredient_identities(self) -> List[str]:
        """Get all ingredient identities.
        
        Returns:
            List[str]: List of all ingredient identity names
        """
        return self.get_all_identities(self.symbol_type)
    
    def get_all_ingredient_properties(self) -> List[str]:
        """Get all ingredient property keys.
        
        Returns:
            List[str]: List of all ingredient property keys
        """
        return self.get_all_properties(self.symbol_type)

    def get_all_ingredient_property_values(self) -> Dict[str, List[str]]:
        """Get all ingredient property keys and their values.
        
        Returns:
            Dict[str, List[str]]: Dictionary with property keys as keys and list of values as values
        """
        return self.get_all_property_values(self.symbol_type)

    # Search Operations
    def find_by(self, criteria: Dict[str, Any]) -> List[Ingredient]:
        criteria['type'] = self.symbol_type
        return super().find_by(criteria)
     
    def find_by_name(self, name: str) -> List[Ingredient]:
        return self._search_symbols_in_tables(name, self.symbol_type)
    
    def find_ingredient_identities_by_name(self, name_pattern: str) -> List[str]:
        """Find ingredient identities by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching ingredient identity names
        """
        return self.find_identities_by_name(name_pattern, self.symbol_type)
    
    def find_ingredient_properties_by_name(self, name_pattern: str) -> List[str]:
        """Find ingredient property keys by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching ingredient property keys
        """
        return self.find_properties_by_name(name_pattern, self.symbol_type)

    # Create/Update/Delete Operations
    def create(self, entity: Ingredient) -> Optional[Ingredient]:
        return super().create(entity)

    def update(self, entity: Ingredient) -> Optional[Ingredient]:
        return super().update(entity)

    def delete(self, entity_id: int) -> bool:
        return super().delete(entity_id)
