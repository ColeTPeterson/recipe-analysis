"""Provides data access operations for unit entities stored in MariaDB.
Handles fetching unit information, mapping database records to domain objects,
and managing unit symbols and their properties for measurement systems.
"""

import logging
from typing import List, Optional, Dict, Any

from .symbol_repository import SymbolRepository
from models.symbol import SymbolType, Symbol
from models.measurement import Unit

logger = logging.getLogger(__name__)


class UnitRepository(SymbolRepository):
    """Provides data access methods for unit-related operations,
    handles database operations, entity mapping, and domain object creation.
    """
    
    def __init__(self):
        """Creates a MariaDBConnectionManager instance to handle database connections."""
        super().__init__()
        self.symbol_type = SymbolType.UNIT

    # Read Operations
    def get_all(self) -> List[Unit]:
        return self.get_symbols_by_type(self.symbol_type)

    def get_by_id(self, entity_id: int) -> Optional[Unit]:
        return self._get_symbol_by_id_and_type(entity_id, self.symbol_type)
    
    def get_all_unit_identities(self) -> List[str]:
        """Get all unit identities.
        
        Returns:
            List[str]: List of all unit identity names
        """
        return self.get_all_identities(self.symbol_type)
    
    def get_all_unit_properties(self) -> List[str]:
        """Get all unit property keys.
        
        Returns:
            List[str]: List of all unit property keys
        """
        return self.get_all_properties(self.symbol_type)
    
    def get_all_unit_property_values(self) -> Dict[str, List[str]]:
        """Get all unit property keys and their values.
        
        Returns:
            Dict[str, List[str]]: Dictionary with property keys as keys and list of values as values
        """
        return self.get_all_property_values(self.symbol_type)

    # Search Operations
    def find_by(self, criteria: Dict[str, Any]) -> List[Unit]:
        criteria['type'] = self.symbol_type
        return super().find_by(criteria)

    def find_by_name(self, name: str) -> List[Unit]:
        return self._search_symbols_in_tables(name, self.symbol_type)
    
    def find_by_identity(self, identity: str) -> List[Unit]:
        units = []
        
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    query = """
                        SELECT DISTINCT c.*
                        FROM units_canonical c
                        JOIN symbol_identity_mapping sim ON c.id = sim.symbol_id
                        JOIN symbol_identities si ON sim.identity_id = si.id
                        WHERE sim.symbol_type = 'UNIT' AND si.identity_name LIKE %s
                    """
                    cursor.execute(query, (f"%{identity}%",))
                    for row in cursor.fetchall():
                        unit = self._map_to_symbol(row, SymbolType.UNIT)
                        if unit:
                            units.append(unit)
        except Exception as e:
            logger.error(f"Error finding units by identity '{identity}': {e}")
        
        return units

    def find_unit_identities_by_name(self, name_pattern: str) -> List[str]:
        """Find unit identities by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching unit identity names
        """
        return self.find_identities_by_name(name_pattern, self.symbol_type)
    
    def find_unit_properties_by_name(self, name_pattern: str) -> List[str]:
        """Find unit property keys by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching unit property keys
        """
        return self.find_properties_by_name(name_pattern, self.symbol_type)

    # Create/Update/Delete Operations
    def create(self, entity: Unit) -> Optional[Unit]:
        return super().create(entity)

    def update(self, entity: Unit) -> Optional[Unit]:
        return super().update(entity)

    def delete(self, entity_id: int) -> bool:
        return super().delete(entity_id)
