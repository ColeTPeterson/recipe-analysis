"""Provides controllers for managing measurement units in recipes;
mediates between unit repositories and domain models.
"""

import logging
from typing import List, Optional, Dict

from models.measurement import Unit
from repositories.mariadb.unit_repository import UnitRepository

logger = logging.getLogger(__name__)


class UnitController:
    """Mediates between unit repositories and domain models,
    providing a higher-level interface for unit-related operations.
    """
    
    def __init__(self):
        """Initialize the unit controller with required dependencies."""
        self.repository = UnitRepository()

    # Read Operations
    def get_all_units(self) -> List[Unit]:
        """Get all measurement units in the system.
        
        Returns:
            List[Unit]: List of all available units
        """
        try:
            return self.repository.get_all()
        except Exception as e:
            logger.error(f"Error retrieving all units: {e}")
            return []

    def get_unit_by_id(self, unit_id: int) -> Optional[Unit]:
        """Get a unit by ID.
        
        Args:
            unit_id (int): ID of the unit to retrieve
            
        Returns:
            Optional[Unit]: The unit if found, None otherwise
        """
        try:
            return self.repository.get_by_id(unit_id)
        except Exception as e:
            logger.error(f"Error retrieving unit {unit_id}: {e}")
            return None

    def get_all_unit_identities(self) -> List[str]:
        """Get all unit identities.
        
        Returns:
            List[str]: List of all unit identity names
        """
        return self.repository.get_all_unit_identities()
    
    def get_all_unit_properties(self) -> List[str]:
        """Get all unit property keys.
        
        Returns:
            List[str]: List of all unit property keys
        """
        return self.repository.get_all_unit_properties()

    def get_all_unit_property_values(self) -> Dict[str, List[str]]:
        """Get all unit property keys and their values.
        
        Returns:
            Dict[str, List[str]]: Dictionary with property keys as keys and list of values as values
        """
        return self.repository.get_all_unit_property_values()

    # Search Operations
    def find_units_by_name(self, name: str) -> List[Unit]:
        """Find units by name.
        
        Args:
            name (str): Name or partial name to search for
            
        Returns:
            List[Unit]: List of matching units
        """
        try:
            return self.repository.find_by_name(name)
        except Exception as e:
            logger.error(f"Error searching units by name '{name}': {e}")
            return []

    def find_units_by_identity(self, identity: str) -> List[Unit]:
        """Find units by their hierarchical identity.
        
        Args:
            identity (str): Identity to search for (e.g., "VOLUME", "MASS")
            
        Returns:
            List[Unit]: List of units with the specified identity
        """
        try:
            return self.repository.find_by_identity(identity)
        except Exception as e:
            logger.error(f"Error searching units by identity '{identity}': {e}")
            return []
    
    def find_unit_identities_by_name(self, name_pattern: str) -> List[str]:
        """Find unit identities by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching unit identity names
        """
        return self.repository.find_unit_identities_by_name(name_pattern)
    
    def find_unit_properties_by_name(self, name_pattern: str) -> List[str]:
        """Find unit property keys by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching unit property keys
        """
        return self.repository.find_unit_properties_by_name(name_pattern)

    # Create/Update/Delete Operations
    def create(self, unit: Unit) -> Optional[Unit]:
        """Add a new unit to the system.
        
        Args:
            unit (Unit): The unit to add
            
        Returns:
            Optional[Unit]: The added unit with ID assigned, or None if failed
        """
        try:
            return self.repository.create(unit)
        except Exception as e:
            logger.error(f"Error creating unit: {e}")
            return None

    def update(self, unit: Unit) -> bool:
        """Update an existing unit.
        
        Args:
            unit (Unit): The unit to update
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not unit.entity_id:
            logger.error("Cannot update unit without ID")
            return False
            
        try:
            updated = self.repository.update(unit)
            return updated is not None
        except Exception as e:
            logger.error(f"Error updating unit: {e}")
            return False
        
    def delete(self, unit_id: int) -> bool:
        """Delete a unit.
        
        Args:
            unit_id (int): ID of the unit to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            return self.repository.delete(unit_id)
        except Exception as e:
            logger.error(f"Error deleting unit {unit_id}: {e}")
            return False

    # Analysis and Categorization Methods
    def get_units_by_measurement_type(self) -> dict:
        """Get units grouped by their measurement type (identity).
        
        Returns:
            dict: Dictionary with measurement type as key and list of units as value
        """
        try:
            all_units = self.get_all_units()
            type_groups = {}
            
            for unit in all_units:
                # Group by primary identity (first one alphabetically if multiple)
                primary_identity = min(unit.identities) if unit.identities else "UNKNOWN"
                
                if primary_identity not in type_groups:
                    type_groups[primary_identity] = []
                type_groups[primary_identity].append(unit)
            
            return type_groups
        except Exception as e:
            logger.error(f"Error grouping units by measurement type: {e}")
            return {}

    def get_volume_units(self) -> List[Unit]:
        """Get all volume measurement units.
        
        Returns:
            List[Unit]: List of volume units
        """
        return self.find_units_by_identity("VOLUME")

    def get_mass_units(self) -> List[Unit]:
        """Get all mass/weight measurement units.
        
        Returns:
            List[Unit]: List of mass units
        """
        return self.find_units_by_identity("MASS")

    def get_temperature_units(self) -> List[Unit]:
        """Get all temperature measurement units.
        
        Returns:
            List[Unit]: List of temperature units
        """
        return self.find_units_by_identity("TEMPERATURE")

    def get_time_units(self) -> List[Unit]:
        """Get all time measurement units.
        
        Returns:
            List[Unit]: List of time units
        """
        return self.find_units_by_identity("TIME")

    def get_unit_statistics(self) -> dict:
        """Get statistics about units in the system.
        
        Returns:
            dict: Dictionary containing unit statistics
        """
        try:
            all_units = self.get_all_units()
            total_count = len(all_units)
            
            identity_counts = {}
            for unit in all_units:
                for identity in unit.identities:
                    identity_counts[identity] = identity_counts.get(identity, 0) + 1
            
            return {
                'total_units': total_count,
                'identity_distribution': identity_counts,
                'most_common_identity': max(identity_counts, key=identity_counts.get) if identity_counts else None,
                'units_without_identity': sum(1 for unit in all_units if not unit.identities)
            }
        except Exception as e:
            logger.error(f"Error getting unit statistics: {e}")
            return {}

    def validate_unit_for_measurement_type(self, unit: Unit, expected_identity: str) -> bool:
        """Validate that a unit is appropriate for a specific measurement type.
        
        Args:
            unit (Unit): The unit to validate
            expected_identity (str): Expected identity (e.g., "VOLUME", "MASS")
            
        Returns:
            bool: True if unit is valid for the measurement type, False otherwise
        """
        try:
            return expected_identity in unit.identities
        except Exception as e:
            logger.error(f"Error validating unit {unit.name} for identity {expected_identity}: {e}")
            return False
