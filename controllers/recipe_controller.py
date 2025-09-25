"""Provides controllers for managing recipes and recipe analysis;
mediates between recipe repositories and domain models.
"""

import logging
from typing import List, Dict, Optional, Any, Union
from bson import ObjectId

from repositories.mongodb.recipe_repository import RecipeRepository

logger = logging.getLogger(__name__)

class RecipeController:
    """Mediates between recipe repositories and application logic,
    providing a higher-level interface for recipe-related operations.
    """
    
    def __init__(self):
        """Initialize the recipe controller with required dependencies."""
        self.recipe_repository = RecipeRepository()
    
    # Read Operations
    def get_all_recipes(self) -> List[Dict[str, Any]]:
        """Get all recipes in the system.

        Returns:
            List[Dict[str, Any]]: List of all available recipes
        """
        try:
            return self.recipe_repository.get_all()
        except Exception as e:
            logger.error(f"Error retrieving all recipes: {e}")
            return []

    def get_recipe_by_id(self, recipe_id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        """Get a recipe by MongoDB ObjectId.
        
        Args:
            recipe_id (Union[str, ObjectId]): Recipe ObjectId
            
        Returns:
            Optional[Dict[str, Any]]: The recipe if found, None otherwise
        """
        try:
            return self.recipe_repository.get_by_id(recipe_id)
        except Exception as e:
            logger.error(f"Error retrieving recipe {recipe_id}: {e}")
            return None

    def get_recipe_by_relational_id(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """Get a recipe by its relational database ID.
        
        Args:
            recipe_id (int): The relational database ID
            
        Returns:
            Optional[Dict[str, Any]]: The recipe if found, None otherwise
        """
        try:
            return self.recipe_repository.get_by_relational_id(recipe_id)
        except Exception as e:
            logger.error(f"Error retrieving recipe by relational ID {recipe_id}: {e}")
            return None

    # Search Operations
    def find_recipes_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find recipes by MongoDB criteria.
        
        Args:
            criteria (Dict[str, Any]): MongoDB query criteria
            
        Returns:
            List[Dict[str, Any]]: List of matching recipes
        """
        try:
            return self.recipe_repository.find_by(criteria)
        except Exception as e:
            logger.error(f"Error finding recipes by criteria: {e}")
            return []

    def find_recipes_by_relational_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find recipes by relational database criteria.
        
        Args:
            criteria (Dict[str, Any]): Search criteria for recipes table
            
        Returns:
            List[Dict[str, Any]]: List of matching recipe documents
        """
        try:
            return self.recipe_repository.find_by_relational_criteria(criteria)
        except Exception as e:
            logger.error(f"Error finding recipes by relational criteria: {e}")
            return []
        
    def find_recipes_by_title(self, title: str) -> List[Dict[str, Any]]:
        """Find recipes by title.
        
        Args:
            title (str): Title or partial title to search for
            
        Returns:
            List[Dict[str, Any]]: List of matching recipes
        """
        try:
            return self.recipe_repository.find_by_name(title)
        except Exception as e:
            logger.error(f"Error searching recipes by title '{title}': {e}")
            return []

    def find_recipes_by_ingredient(self, ingredient_name: str) -> List[Dict[str, Any]]:
        """Find recipes that use a specific ingredient.
        
        Args:
            ingredient_name (str): Name of the ingredient
            
        Returns:
            List[Dict[str, Any]]: List of matching recipes
        """
        try:
            logger.info(f"Searching for recipes with ingredient: '{ingredient_name}'")
            
            # Try structured ingredient search first
            query = {
                "ingredients.name": {"$regex": f".*{ingredient_name}.*", "$options": "i"}
            }
            logger.info(f"Using query: {query}")
            results = self.recipe_repository.find_by(query)
            
            if results:
                logger.info(f"Found {len(results)} recipes")
                return results
                
            # Fallback to broader search
            logger.info("No results with first query, trying alternative search")
            query = {
                "$or": [
                    {"ingredients": {"$regex": f".*{ingredient_name}.*", "$options": "i"}},
                    {"ingredients.name": {"$regex": f".*{ingredient_name}.*", "$options": "i"}}
                ]
            }
            return self.recipe_repository.find_by(query)
                
        except Exception as e:
            logger.error(f"Error searching for recipes with ingredient '{ingredient_name}': {e}")
            return []
            
    # Create/Update/Delete Operations
    def create(self, recipe_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new recipe in both MongoDB and MariaDB.
        
        Args:
            recipe_data (Dict[str, Any]): Recipe data
            
        Returns:
            Optional[Dict[str, Any]]: The created recipe with ID assigned, None if failed
        """
        try:
            return self.recipe_repository.create(recipe_data)
        except Exception as e:
            logger.error(f"Error creating recipe: {e}")
            return None
        
    def update(self, recipe_data: Dict[str, Any]) -> bool:
        """Update an existing recipe in both MongoDB and MariaDB.
        
        Args:
            recipe_data (Dict[str, Any]): Recipe data with _id field
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if '_id' not in recipe_data:
            logger.error("Cannot update recipe without MongoDB _id")
            return False
            
        try:
            updated = self.recipe_repository.update(recipe_data)
            return updated is not None
        except Exception as e:
            logger.error(f"Error updating recipe: {e}")
            return False
        
    def delete(self, recipe_id: Union[str, ObjectId]) -> bool:
        """Delete a recipe from both MongoDB and MariaDB.
        
        Args:
            recipe_id (Union[str, ObjectId]): MongoDB ObjectId of the recipe to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            return self.recipe_repository.delete(recipe_id)
        except Exception as e:
            logger.error(f"Error deleting recipe {recipe_id}: {e}")
            return False

    def delete_by_relational_id(self, recipe_id: int) -> bool:
        """Delete a recipe by its relational database ID.
        
        Args:
            recipe_id (int): The relational database ID
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            return self.recipe_repository.delete_by_relational_id(recipe_id)
        except Exception as e:
            logger.error(f"Error deleting recipe by relational ID {recipe_id}: {e}")
            return False
    
    # Metadata Operations
    def get_relational_metadata(self, recipe_id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        """Get relational metadata for a recipe.
        
        Args:
            recipe_id (Union[str, ObjectId]): MongoDB ObjectId
            
        Returns:
            Optional[Dict[str, Any]]: Relational metadata or None if not found
        """
        try:
            return self.recipe_repository.get_relational_metadata(recipe_id)
        except Exception as e:
            logger.error(f"Error getting relational metadata for {recipe_id}: {e}")
            return None

    def sync_metadata_to_relational(self, recipe_data: Dict[str, Any]) -> bool:
        """Sync recipe metadata from MongoDB to MariaDB.
        
        Args:
            recipe_data (Dict[str, Any]): MongoDB recipe document
            
        Returns:
            bool: True if sync was successful, False otherwise
        """
        try:
            return self.recipe_repository.sync_metadata_to_relational(recipe_data)
        except Exception as e:
            logger.error(f"Error syncing metadata to relational: {e}")
            return False
    
    # Analysis Methods
    def analyze_recipe_complexity(self, recipe_id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        """Calculates various complexity metrics for a recipe,
        including number of ingredients, steps, and an overall complexity score.
        
        Args:
            recipe_id (Union[str, ObjectId]): Recipe ID
            
        Returns:
            Optional[Dict[str, Any]]: Complexity analysis results, or None if recipe not found
        """
        try:
            recipe = self.get_recipe_by_id(recipe_id)
            if not recipe:
                logger.warning(f"Recipe with ID {recipe_id} not found for complexity analysis")
                return None
                
            ingredient_count = len(recipe.get('ingredients', []))
            
            # Count steps by analyzing instructions
            instructions = recipe.get('instructions', '')
            if isinstance(instructions, str):
                # Split by newlines or periods to estimate steps
                steps = [s.strip() for s in instructions.replace('\n', '.').split('.') if s.strip()]
            elif isinstance(instructions, list):
                steps = instructions
            else:
                steps = []
                
            step_count = len(steps)
            
            # Calculate complexity score: 0.6 * ingredient_count + 0.4 * step_count
            complexity_score = 0.6 * ingredient_count + 0.4 * step_count
            
            return {
                'recipe_id': str(recipe_id),
                'title': recipe.get('title', 'Untitled'),
                'complexity_metrics': {
                    'ingredient_count': ingredient_count,
                    'step_count': step_count,
                    'complexity_score': round(complexity_score, 1)
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing recipe complexity for {recipe_id}: {e}")
            return None
        
    def export_recipe_as_json(self, recipe_id: Union[str, ObjectId]) -> Optional[str]:
        """Export a recipe as a JSON string.
        
        Args:
            recipe_id (Union[str, ObjectId]): Recipe ID
            
        Returns:
            str: JSON representation of the recipe, or None if recipe not found
        """
        try:
            return self.recipe_repository.serialize(recipe_id)
        except ValueError as e:
            logger.warning(f"Recipe not found for export: {e}")
            return None
        except Exception as e:
            logger.error(f"Error exporting recipe {recipe_id}: {e}")
            return None
