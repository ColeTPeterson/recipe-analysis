"""Provides data access operations for recipe documents stored in MongoDB;
handles CRUD operations for recipes, including querying by various criteria,.
"""

import logging
from typing import List, Optional, Dict, Any

from bson import ObjectId

from models.recipe import Recipe
from repositories.base import BaseRepository
from repositories.mongodb.connection import MongoDBConnectionManager

logger = logging.getLogger(__name__)

class RecipeRepository(BaseRepository[Dict[str, Any]]):
    """Provides data access methods for recipe-related operations,
    handles document storage, retrieval, and manipulation with MongoDB-specific functionality.
    """
    
    def __init__(self):
        """Initialize the recipe repository with required dependencies."""
        self.db_manager = MongoDBConnectionManager()
        self.collection_name = 'recipes'

    def create(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new recipe document in the MongoDB collection.

        Args:
            entity (Dict[str, Any]): Recipe document to create
            
        Returns:
            Dict[str, Any]: The created recipe document with _id field added
            
        Raises:
            Exception: If document creation fails
        """
        try:
            with self.db_manager.get_collection(self.collection_name) as collection:
                result = collection.insert_one(entity)
                entity['_id'] = result.inserted_id
                return entity
        except Exception as e:
            logger.error(f"Error creating recipe: {e}")
            raise

    def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a recipe document by its MongoDB ID.
        
        Args:
            entity_id (str): The MongoDB ObjectId of the recipe as a string
            
        Returns:
            Optional[Dict[str, Any]]: The recipe document if found, None otherwise
        """
        try:
            with self.db_manager.get_collection(self.collection_name) as collection:
                result = collection.find_one({'_id': ObjectId(entity_id)})
                return result
        except Exception as e:
            logger.error(f"Error getting recipe {entity_id}: {e}")
            return None
    
    def get_by_sql_id(self, sql_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a recipe document by its SQL database ID reference.
                
        Args:
            sql_id (int): The SQL database ID referenced in the recipe document
            
        Returns:
            Optional[Dict[str, Any]]: The recipe document if found, None otherwise
        """
        try:
            with self.db_manager.get_collection(self.collection_name) as collection:
                result = collection.find_one({'id': sql_id})
                return result
        except Exception as e:
            logger.error(f"Error getting recipe with SQL ID {sql_id}: {e}")
            return None
    
    def find_by(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find recipe documents matching the specified criteria.
        
        Args:
            criteria (Dict[str, Any]): MongoDB query criteria
            
        Returns:
            List[Dict[str, Any]]: List of matching recipe documents
            
        Examples:
            Find recipes by cuisine:
            ```
            repo.find_by({"cuisine": "Italian"})
            ```
            
            Find recipes with specific ingredients:
            ```
            repo.find_by({"ingredients.name": "tomato"})
            ```
        """
        try:
            with self.db_manager.get_collection(self.collection_name) as collection:
                return list(collection.find(criteria))
        except Exception as e:
            logger.error(f"Error finding recipes with criteria {criteria}: {e}")
            return []
    
    def update(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing recipe document in the MongoDB collection.
        
        Args:
            entity (Dict[str, Any]): Recipe document with updated values
                                    (must include _id field)
            
        Returns:
            Dict[str, Any]: The updated recipe document
            
        Raises:
            ValueError: If the entity doesn't contain an _id field
            Exception: If document update fails
        """
        try:
            with self.db_manager.get_collection(self.collection_name) as collection:
                entity_id = entity.get('_id')
                if not entity_id:
                    raise ValueError("Recipe must have an _id key to be updated")
                
                update_data = {k: v for k, v in entity.items() if k != '_id'}
                collection.update_one({'_id': entity_id}, {'$set': update_data})
            return entity
        except Exception as e:
            logger.error(f"Error updating recipe {entity.get('_id')}: {e}")
            raise
            
    def delete(self, entity_id: str) -> bool:
        """Delete a recipe document from the MongoDB collection.
        
        Args:
            entity_id (str): The MongoDB ObjectId of the recipe to delete as a string
            
        Returns:
            bool: True if deletion was successful (document found and deleted),
                  False otherwise
        """
        try:
            with self.db_manager.get_collection(self.collection_name) as collection:
                result = collection.delete_one({'_id': ObjectId(entity_id)})
                return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting recipe {entity_id}: {e}")
            return False
