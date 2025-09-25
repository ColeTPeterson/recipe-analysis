"""Provides data access operations for equipment entities stored in MariaDB.
Handles fetching equipment information, mapping database records to domain objects,
and managing equipment symbols and their properties.
"""

import logging
from typing import List, Optional, Dict, Any

from .symbol_repository import SymbolRepository
from models.equipment import Equipment
from models.symbol import SymbolType, Symbol

logger = logging.getLogger(__name__)


class EquipmentRepository(SymbolRepository):
    """Provides data access methods for equipment-related operations, 
    handles database operations, entity mapping, and domain object creation.
    """
    
    def __init__(self):
        """Creates a MariaDBConnectionManager instance to handle database connections."""
        super().__init__()
        self.symbol_type = SymbolType.EQUIPMENT

    # Read Operations 
    def get_all(self) -> List[Equipment]:
        return self.get_symbols_by_type(self.symbol_type)

    def get_by_id(self, entity_id: int) -> Optional[Equipment]:
        return self._get_symbol_by_id_and_type(entity_id, self.symbol_type)
    
    def get_all_equipment_identities(self) -> List[str]:
        """Get all equipment identities.
        
        Returns:
            List[str]: List of all equipment identity names
        """
        return self.get_all_identities(self.symbol_type)
    
    def get_all_equipment_properties(self) -> List[str]:
        """Get all equipment property keys.
        
        Returns:
            List[str]: List of all equipment property keys
        """
        return self.get_all_properties(self.symbol_type)

    def get_all_equipment_property_values(self) -> Dict[str, List[str]]:
        """Get all equipment property keys and their values.
        
        Returns:
            Dict[str, List[str]]: Dictionary with property keys as keys and list of values as values
        """
        return self.get_all_property_values(self.symbol_type)

    # Search Operations
    def find_by(self, criteria: Dict[str, Any]) -> List[Equipment]:
        criteria['type'] = self.symbol_type
        return super().find_by(criteria)

    def find_by_name(self, name: str) -> List[Equipment]:
        return self._search_symbols_in_tables(name, self.symbol_type)

    def find_equipment_identities_by_name(self, name_pattern: str) -> List[str]:
        """Find equipment identities by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching equipment identity names
        """
        return self.find_identities_by_name(name_pattern, self.symbol_type)
    
    def find_equipment_properties_by_name(self, name_pattern: str) -> List[str]:
        """Find equipment property keys by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching equipment property keys
        """
        return self.find_properties_by_name(name_pattern, self.symbol_type)

    # Create/Update/Delete Operations
    def create(self, entity: Equipment) -> Optional[Equipment]:
        return super().create(entity)

    def update(self, entity: Equipment) -> Optional[Equipment]:
        return super().update(entity)

    def delete(self, entity_id: int) -> bool:
        return super().delete(entity_id)