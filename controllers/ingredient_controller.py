"""Controllers for managing ingredients in recipes;
mediates between ingredient repositories and domain models.
"""

import logging
from typing import List, Optional, Dict

from models.symbol import SymbolType
from models.ingredient import Ingredient
from repositories.symbol_repository import SymbolRepository

logger = logging.getLogger(__name__)


class IngredientController:
    """Provides business logic for handling ingredients,
    delegating data access to the appropriate repository.
    """
    
    def __init__(self):
        """Initialize the ingredient controller with required dependencies."""
        self.repository = SymbolRepository(SymbolType.INGREDIENT)

    # Read Operations
    def get_all_ingredients(self) -> List[Ingredient]:
        """Get all ingredients in the system.
        
        Returns:
            List[Ingredient]: List of all available ingredients
        """
        try:
            return self.repository.get_all()
        except Exception as e:
            logger.error(f"Error retrieving all ingredients: {e}")
            return []

    def get_ingredient_by_id(self, ingredient_id: int) -> Optional[Ingredient]:
        """Get an ingredient by ID.
        
        Args:
            ingredient_id (int): ID of the ingredient to retrieve
            
        Returns:
            Optional[Ingredient]: The ingredient if found, None otherwise
        """
        try:
            return self.repository.get_by_id(ingredient_id)
        except Exception as e:
            logger.error(f"Error retrieving ingredient {ingredient_id}: {e}")
            return None

    def get_all_ingredient_identities(self) -> List[str]:
        """Get all ingredient identities.
        
        Returns:
            List[str]: List of all ingredient identity names
        """
        return self.repository.get_all_identities()
    
    def get_all_ingredient_properties(self) -> List[str]:
        """Get all ingredient property keys.
        
        Returns:
            List[str]: List of all ingredient property keys
        """
        return self.repository.get_all_properties()

    def get_all_ingredient_property_values(self) -> Dict[str, List[str]]:
        """Get all ingredient property keys and their values.
        
        Returns:
            Dict[str, List[str]]: Dictionary with property keys as keys and list of values as values
        """
        return self.repository.get_all_property_values()

    # Search Operations
    def find_ingredients_by_name(self, name: str) -> List[Ingredient]:
        """Find ingredients by name.
        
        Args:
            name (str): Name or partial name to search for
            
        Returns:
            List[Ingredient]: List of matching ingredients
        """
        try:
            return self.repository.find_symbols_by_name(name)
        except Exception as e:
            logger.error(f"Error searching ingredients by name '{name}': {e}")
            return []
    
    def find_ingredient_identities_by_name(self, name_pattern: str) -> List[str]:
        """Find ingredient identities by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching ingredient identity names
        """
        return self.repository.find_identities_by_name(name_pattern)
    
    def find_ingredient_properties_by_name(self, name_pattern: str) -> List[str]:
        """Find ingredient property keys by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for
            
        Returns:
            List[str]: List of matching ingredient property keys
        """
        return self.repository.find_properties_by_name(name_pattern)

    # Create/Update/Delete Operations
    def create(self, ingredient: Ingredient) -> Optional[Ingredient]:
        """Add a new ingredient to the system.
        
        Args:
            ingredient (Ingredient): The ingredient to add
            
        Returns:
            Optional[Ingredient]: The added ingredient with ID assigned, or None if failed
        """
        try:
            return self.repository.create(ingredient)
        except Exception as e:
            logger.error(f"Error creating ingredient: {e}")
            return None

    def update(self, ingredient: Ingredient) -> bool:
        """Update an existing ingredient.
        
        Args:
            ingredient (Ingredient): The ingredient to update
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not ingredient.entity_id:
            logger.error("Cannot update ingredient without ID")
            return False
            
        try:
            updated = self.repository.update(ingredient)
            return updated is not None
        except Exception as e:
            logger.error(f"Error updating ingredient: {e}")
            return False
        
    def delete(self, ingredient_id: int) -> bool:
        """Delete an ingredient.
        
        Args:
            ingredient_id (int): ID of the ingredient to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            return self.repository.delete(ingredient_id)
        except Exception as e:
            logger.error(f"Error deleting ingredient {ingredient_id}: {e}")
            return False
