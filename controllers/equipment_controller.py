"""Provides controllers for managing cooking equipment in recipes;
mediates between equipment repositories and domain models.
"""

import logging
from typing import List, Optional, Dict

from models.symbol import SymbolType
from models.equipment import Equipment
from repositories.symbol_repository import SymbolRepository

logger = logging.getLogger(__name__)


class EquipmentController:
    """This controller mediates between equipment repositories and domain models,
    providing a higher-level interface for equipment-related operations.
    """
    
    def __init__(self):
        """Initialize the equipment controller with required dependencies."""
        self.repository = SymbolRepository(SymbolType.EQUIPMENT)

    # Read Operations
    def get_all_equipment(self) -> List[Equipment]:
        """Get all equipment items in the system.
        
        Returns:
            List[Equipment]: List of all available equipment items
        """
        try:
            return self.repository.get_all()
        except Exception as e:
            logger.error(f"Error retrieving all equipment: {e}")
            return []

    def get_equipment_by_id(self, entity_id: int) -> Optional[Equipment]:
        """Get an equipment item by ID.
        
        Args:
            entity_id (int): ID of the equipment to retrieve
            
        Returns:
            Optional[Equipment]: The equipment if found, None otherwise
        """
        try:
            return self.repository.get_by_id(entity_id)
        except Exception as e:
            logger.error(f"Error retrieving equipment {entity_id}: {e}")
            return None

    def get_all_equipment_identities(self) -> List[str]:
        """Get all equipment identities.
        
        Returns:
            List[str]: List of all equipment identity names
        """
        return self.repository.get_all_identities()
    
    def get_all_equipment_properties(self) -> List[str]:
        """Get all equipment property keys.
        
        Returns:
            List[str]: List of all equipment property keys
        """
        return self.repository.get_all_properties()

    def get_all_equipment_property_values(self) -> Dict[str, List[str]]:
        """Get all equipment property keys and their values.
        
        Returns:
            Dict[str, List[str]]: Dictionary with property keys as keys and list of values as values
        """
        return self.repository.get_all_property_values()

    # Search Operations
    def find_equipment_by_name(self, name: str) -> List[Equipment]:
        """Find equipment by name.
        
        Args:
            name (str): Name or partial name to search for
            
        Returns:
            List[Equipment]: List of matching equipment items
        """
        try:
            return self.repository.find_symbols_by_name(name)
        except Exception as e:
            logger.error(f"Error searching equipment by name '{name}': {e}")
            return []
        
    def find_equipment_identities_by_name(self, name_pattern: str) -> List[str]:
        """Find equipment identities by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching equipment identity names
        """
        return self.repository.find_identities_by_name(name_pattern)
    
    def find_equipment_properties_by_name(self, name_pattern: str) -> List[str]:
        """Find equipment property keys by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching equipment property keys
        """
        return self.repository.find_properties_by_name(name_pattern)

    # Create/Update/Delete Operations             
    def create(self, equipment: Equipment) -> Optional[Equipment]:
        """Add a new equipment item to the system.
        
        Args:
            equipment (Equipment): The equipment to add
            
        Returns:
            Optional[Equipment]: The added equipment with ID assigned, or None if failed
        """
        try:
            return self.repository.create(equipment)
        except Exception as e:
            logger.error(f"Error creating equipment: {e}")
            return None

    def update(self, equipment: Equipment) -> bool:
        """Update an existing equipment item.
        
        Args:
            equipment (Equipment): The equipment to update
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not equipment.entity_id:
            logger.error("Cannot update equipment without ID")
            return False
            
        try:
            updated = self.repository.update(equipment)
            return updated is not None
        except Exception as e:
            logger.error(f"Error updating equipment: {e}")
            return False
        
    def delete(self, entity_id: int) -> bool:
        """Delete an equipment item.
        
        Args:
            entity_id (int): ID of the equipment to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            return self.repository.delete(entity_id)
        except Exception as e:
            logger.error(f"Error deleting equipment {entity_id}: {e}")
            return False
