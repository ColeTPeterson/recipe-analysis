"""Provides data access methods for recipe-related operations;
Handles document storage in MongoDB for recipe data while
maintaining relational metadata in MariaDB for efficient querying and indexing.
"""

import logging
import json
from typing import List, Optional, Dict, Any, Union
from bson import ObjectId

from repositories.base import BaseRepository
from repositories.connection import MariaDBConnectionManager, MongoDBConnectionManager

logger = logging.getLogger(__name__)


class RecipeRepository(BaseRepository[Dict[str, Any]]):
    """Provides data access methods for recipe-related operations,
    handles document storage in MongoDB and relational metadata in MariaDB.
    """
    
    def __init__(self):
        """Initialize the recipe repository with required dependencies."""
        self.mariadb_connection_manager = MariaDBConnectionManager()        
        self.mongo_connection_manager = MongoDBConnectionManager()

    # Read Operations  
    def get_all(self) -> List[Dict[str, Any]]:
        """Retrieve all recipes from MongoDB.
        
        Returns:
            List[Dict[str, Any]]: List of all recipes
        """
        try:
            collection = self.mongo_connection_manager.get_collection('recipes')
            return list(collection.find())
        except ConnectionError as e:
            logger.error(f"MongoDB connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving all recipes: {e}")
            return []
        
    def get_by_id(self, entity_id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        """Retrieve a recipe by MongoDB ObjectId.
        
        Args:
            entity_id (Union[str, ObjectId]): Recipe ObjectId
            
        Returns:
            Optional[Dict[str, Any]]: The recipe if found, None otherwise
        """
        try:
            if isinstance(entity_id, str):
                entity_id = ObjectId(entity_id)
                
            collection = self.mongo_connection_manager.get_collection('recipes')
            return collection.find_one({'_id': entity_id})
        except ConnectionError as e:
            logger.error(f"MongoDB connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving recipe with ID {entity_id}: {e}")
            return None
    
    def get_by_relational_id(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a recipe by its relational database ID.
        
        Args:
            recipe_id (int): The relational database ID
            
        Returns:
            Optional[Dict[str, Any]]: The recipe if found, None otherwise
        """
        try:
            # First get the ObjectId from MariaDB
            with self.mariadb_connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    query = "SELECT object_id FROM recipes WHERE id = %s"
                    cursor.execute(query, (recipe_id,))
                    row = cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    object_id = row['object_id']
            
            # Then get the full document from MongoDB
            return self.get_by_id(ObjectId(object_id))
        except Exception as e:
            logger.error(f"Error retrieving recipe with relational ID {recipe_id}: {e}")
            return None
    
    # Search Operations
    def find_by(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find recipes matching specified criteria in MongoDB.
        
        Args:
            criteria (Dict[str, Any]): MongoDB query criteria
            
        Returns:
            List[Dict[str, Any]]: Matching recipes
            
        Raises:
            ConnectionError: If MongoDB connection fails
        """
        try:
            logger.info(f"MongoDB query: {criteria}")
            
            collection = self.mongo_connection_manager.get_collection('recipes')
            
            if collection is None:
                logger.error("Recipe collection is None")
                return []
                
            results = list(collection.find(criteria))
            logger.info(f"MongoDB query returned {len(results)} results for criteria: {str(criteria)[:100]}")
            
            if results:
                first_result = results[0]
                title = first_result.get('title', 'Untitled')
                recipe_id = str(first_result.get('_id', 'unknown'))
                logger.info(f"First match: {title} (ID: {recipe_id})")
                
                ingredients = first_result.get('ingredients', [])
                if ingredients and isinstance(ingredients, list):
                    ingredient_names = [i.get('name', 'Unknown') if isinstance(i, dict) else str(i) 
                                      for i in ingredients[:3]]
                    logger.info(f"Sample ingredients: {ingredient_names}")
            else:
                logger.info(f"No recipes matched the criteria: {str(criteria)[:100]}")
                
            return results
            
        except ConnectionError as e:
            logger.error(f"MongoDB connection error: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Error finding recipes by criteria {str(criteria)[:100]}: {e}")
            return []

    def find_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Find recipes by name or partial name.

        Args:
            name (str): Name or partial name to search for

        Returns:
            List[Dict[str, Any]]: List of matching recipes
        """
        try:
            query = {"title": {"$regex": f".*{name}.*", "$options": "i"}}
            return self.find_by(query)
        except Exception as e:
            logger.error(f"Error searching recipes by name '{name}': {e}")
            return []

    def find_by_relational_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find recipes using relational database criteria.
        
        Args:
            criteria (Dict[str, Any]): Search criteria for recipes table
            
        Returns:
            List[Dict[str, Any]]: List of matching recipe documents
        """
        recipes = []
        
        try:
            where_parts = []
            query_params = []
            for key, value in criteria.items():
                where_parts.append(f"{key} = %s")
                query_params.append(value)
            
            where_clause = " AND ".join(where_parts) if where_parts else "1=1"
            
            with self.mariadb_connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    query = f"SELECT object_id FROM recipes WHERE {where_clause}"
                    cursor.execute(query, query_params)
                    
                    for row in cursor.fetchall():
                        recipe_doc = self.get_by_id(ObjectId(row['object_id']))
                        if recipe_doc:
                            recipes.append(recipe_doc)
        except Exception as e:
            logger.error(f"Error finding recipes by relational criteria: {e}")
        
        return recipes

    # Create/Update/Delete Operations
    def create(self, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new recipe document in MongoDB and metadata in MariaDB.

        Args:
            entity (Dict[str, Any]): Recipe data to create
            
        Returns:
            Optional[Dict[str, Any]]: The created recipe with ID assigned, or None if failed
        """
        try:
            # Insert into MongoDB first
            collection = self.mongo_connection_manager.get_collection('recipes')
            result = collection.insert_one(entity)
            entity['_id'] = result.inserted_id
            
            # Insert metadata into MariaDB
            try:
                with self.mariadb_connection_manager.get_connection() as connection:
                    with connection.cursor() as cursor:
                        query = """
                            INSERT INTO recipes (object_id, title, name)
                            VALUES (%s, %s, %s)
                        """
                        cursor.execute(query, (
                            str(result.inserted_id),
                            entity.get('title', 'Untitled'),
                            entity.get('name', entity.get('title', 'Untitled'))
                        ))
                        
                        # Store the relational ID in the entity
                        entity['relational_id'] = cursor.lastrowid
                        connection.commit()
                        
            except Exception as mariadb_error:
                # If MariaDB insert fails, remove from MongoDB to maintain consistency
                collection.delete_one({'_id': result.inserted_id})
                logger.error(f"MariaDB insert failed, rolled back MongoDB insert: {mariadb_error}")
                return None
            
            logger.info(f"Created recipe '{entity.get('title', 'Untitled')}' with MongoDB ID {result.inserted_id}")
            return entity
            
        except Exception as e:
            logger.error(f"Error creating recipe: {e}")
            return None

    def update(self, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing recipe in both MongoDB and MariaDB.
        
        Args:
            entity (Dict[str, Any]): Recipe data to update
            
        Returns:
            Optional[Dict[str, Any]]: The updated recipe, or None if failed
            
        Raises:
            ValueError: If recipe ID is not set
        """
        if '_id' not in entity:
            raise ValueError("Cannot update recipe without MongoDB _id")
            
        try:
            entity_id = entity['_id']
            
            # Update MongoDB document
            collection = self.mongo_connection_manager.get_collection('recipes')
            update_data = entity.copy()
            if '_id' in update_data:
                del update_data['_id']
            if 'relational_id' in update_data:
                del update_data['relational_id']
                
            mongo_result = collection.update_one({'_id': entity_id}, {'$set': update_data})
            
            # Update MariaDB metadata
            try:
                with self.mariadb_connection_manager.get_connection() as connection:
                    with connection.cursor() as cursor:
                        query = """
                            UPDATE recipes 
                            SET title = %s, name = %s 
                            WHERE object_id = %s
                        """
                        cursor.execute(query, (
                            entity.get('title', 'Untitled'),
                            entity.get('name', entity.get('title', 'Untitled')),
                            str(entity_id)
                        ))
                        connection.commit()
            except Exception as mariadb_error:
                logger.warning(f"MariaDB update failed for recipe {entity_id}: {mariadb_error}")
            
            if mongo_result.modified_count > 0:
                logger.info(f"Updated recipe with ID {entity_id}")
                return entity
            else:
                logger.warning(f"No recipe found with ID {entity_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating recipe: {e}")
            return None
    
    def delete(self, entity_id: Union[str, ObjectId]) -> bool:
        """Delete a recipe from both MongoDB and MariaDB.
        
        Args:
            entity_id (Union[str, ObjectId]): ID of the recipe to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            if isinstance(entity_id, str):
                entity_id = ObjectId(entity_id)
            
            # Delete from MariaDB first (due to foreign key constraints)
            try:
                with self.mariadb_connection_manager.get_connection() as connection:
                    with connection.cursor() as cursor:
                        query = "DELETE FROM recipes WHERE object_id = %s"
                        cursor.execute(query, (str(entity_id),))
                        connection.commit()
            except Exception as mariadb_error:
                logger.warning(f"MariaDB delete failed for recipe {entity_id}: {mariadb_error}")
            
            # Delete from MongoDB
            collection = self.mongo_connection_manager.get_collection('recipes')
            result = collection.delete_one({'_id': entity_id})
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted recipe {entity_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error deleting recipe with ID {entity_id}: {e}")
            return False
    
    def delete_by_relational_id(self, recipe_id: int) -> bool:
        """Delete a recipe by its relational database ID.
        
        Args:
            recipe_id (int): The relational database ID
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # First get the ObjectId from MariaDB
            object_id_str = None
            with self.mariadb_connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    query = "SELECT object_id FROM recipes WHERE id = %s"
                    cursor.execute(query, (recipe_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        object_id_str = row['object_id']
            
            if object_id_str:
                return self.delete(ObjectId(object_id_str))
            else:
                logger.warning(f"No recipe found with relational ID {recipe_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting recipe with relational ID {recipe_id}: {e}")
            return False
    
    # Helper Methods
    def get_relational_metadata(self, object_id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        """Get relational metadata for a recipe by its MongoDB ObjectId.
        
        Args:
            object_id (Union[str, ObjectId]): MongoDB ObjectId
            
        Returns:
            Optional[Dict[str, Any]]: Relational metadata or None if not found
        """
        try:
            with self.mariadb_connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM recipes WHERE object_id = %s"
                    cursor.execute(query, (str(object_id),))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting relational metadata for {object_id}: {e}")
            return None
    
    def sync_metadata_to_relational(self, recipe_doc: Dict[str, Any]) -> bool:
        """Sync recipe metadata from MongoDB document to MariaDB.
        
        Args:
            recipe_doc (Dict[str, Any]): MongoDB recipe document
            
        Returns:
            bool: True if sync was successful, False otherwise
        """
        if '_id' not in recipe_doc:
            return False
            
        try:
            with self.mariadb_connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    # Check if record exists
                    query = "SELECT id FROM recipes WHERE object_id = %s"
                    cursor.execute(query, (str(recipe_doc['_id']),))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existing record
                        query = """
                            UPDATE recipes 
                            SET title = %s, name = %s 
                            WHERE object_id = %s
                        """
                        cursor.execute(query, (
                            recipe_doc.get('title', 'Untitled'),
                            recipe_doc.get('name', recipe_doc.get('title', 'Untitled')),
                            str(recipe_doc['_id'])
                        ))
                    else:
                        # Insert new record
                        query = """
                            INSERT INTO recipes (object_id, title, name)
                            VALUES (%s, %s, %s)
                        """
                        cursor.execute(query, (
                            str(recipe_doc['_id']),
                            recipe_doc.get('title', 'Untitled'),
                            recipe_doc.get('name', recipe_doc.get('title', 'Untitled'))
                        ))
                    
                    connection.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error syncing metadata for recipe {recipe_doc['_id']}: {e}")
            return False
            
    def serialize(self, recipe_id: Union[str, ObjectId]) -> str:
        """Export a recipe as JSON string.
        
        Args:
            recipe_id (Union[str, ObjectId]): Recipe ID
            
        Returns:
            str: JSON representation of the recipe
            
        Raises:
            ValueError: If recipe not found
        """
        recipe = self.get_by_id(recipe_id)
        if not recipe:
            raise ValueError(f"Recipe with ID {recipe_id} not found")
            
        recipe_copy = recipe.copy()
        recipe_copy['_id'] = str(recipe_copy['_id'])
        
        return json.dumps(recipe_copy, indent=2)
