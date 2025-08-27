"""Provides data access operations for ingredient entities stored in MariaDB;
handles fetching ingredient information, mapping database records to domain objects,
and managing ingredient symbols, measurements, and properties.
"""

import logging
from typing import List, Optional, Dict, Any, Set

from models.item import Ingredient
from models.symbol import Symbol, SymbolType
from models.measurement import Measurement, MeasurementAbs
from repositories.base import BaseRepository
from repositories.mariadb.connection import MariaDBConnectionManager
from repositories.mariadb.symbol import SymbolRepository

logger = logging.getLogger(__name__)

class IngredientRepository(BaseRepository[Ingredient]):
    """Provides data access methods for ingredient-related operations,
    handles database operations, entity mapping, and domain object creation.
    """
    
    def __init__(self):
        """Initialize the ingredient repository with required dependencies."""
        self.db_manager = MariaDBConnectionManager()
        self.symbol_repository = SymbolRepository()

    def create(self, entity: Ingredient) -> Ingredient:
        """Create a new ingredient entity in the database.
        
        Args:
            entity (Ingredient): The ingredient entity to create
            
        Returns:
            Ingredient: The created ingredient with updated ID
            
        Raises:
            NotImplementedError: This method is not yet implemented
        """
        raise NotImplementedError("Ingredient creation is not yet implemented")
    
    def get_all(self) -> List[Ingredient]:
        """Retrieve all ingredient entities from the database.
        
        Returns:
            List[Ingredient]: A list of all ingredient entities
        """
        results = []
        with self.db_manager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM ingredients")
            for row in cursor.fetchall():
                ingredient = self._map_to_ingredient(row)
                if ingredient:
                    results.append(ingredient)
        return results
    
    def get_by_id(self, entity_id: int) -> Optional[Ingredient]:
        """Retrieve an ingredient entity by its ID.
        
        Args:
            entity_id (int): The database ID of the ingredient
            
        Returns:
            Optional[Ingredient]: The ingredient entity if found, None otherwise
        """
        with self.db_manager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM ingredients WHERE id = %s", (entity_id,))
            result = cursor.fetchone()
            if result:
                return self._map_to_ingredient(result)
    
        return None
    
    def find_by(self, criteria: Dict[str, Any]) -> List[Ingredient]:
        """Find ingredient entities matching the specified criteria,
        supports filtering by name, parent_id, and is_category flags.
        
        Args:
            criteria (Dict[str, Any]): Search criteria with supported keys:
                - name: Exact match for ingredient name
                - parent_id: Filter by parent ingredient ID
                - is_category: Filter by category flag
            
        Returns:
            List[Ingredient]: List of matching ingredient entities
        """
        results = []
        query_parts = []
        query_params = []

        if 'name' in criteria:
            query_parts.append("name = %s")
            query_params.append(criteria['name'])
        if 'parent_id' in criteria:
            query_parts.append("parent_id = %s")
            query_params.append(criteria['parent_id'])
        if 'is_category' in criteria:
            query_parts.append("is_category = %s")
            query_params.append(1 if criteria['is_category'] else 0)

        if not query_parts:
            return []
        
        query = f"SELECT * FROM ingredients WHERE {' AND '.join(query_parts)}"

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(query, query_params)
            for row in cursor.fetchall():
                ingredient = self._map_to_ingredient(row)
                if ingredient:
                    results.append(ingredient)

        return results
    
    def update(self, entity: Ingredient) -> Ingredient:
        """Update an existing ingredient entity in the database.
        
        Args:
            entity (Ingredient): The ingredient entity with updated values
            
        Returns:
            Ingredient: The updated ingredient entity
            
        Raises:
            NotImplementedError: This method is not yet implemented
        """
        raise NotImplementedError("Ingredient updating is not yet implemented")

    def delete(self, entity_id: int) -> bool:
        """Delete an ingredient entity from the database.
        
        Args:
            entity_id (int): The ID of the ingredient to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            NotImplementedError: This method is not yet implemented
        """
        raise NotImplementedError("Ingredient deletion is not yet implemented")
    
    def _map_to_ingredient(self, db_row: Dict[str, Any]) -> Optional[Ingredient]:
        """Map a database row to an Ingredient domain object.
        
        Args:
            db_row (Dict[str, Any]): Database row containing ingredient data
            
        Returns:
            Optional[Ingredient]: The mapped Ingredient object or None if mapping fails
            
        Raises:
            Exception: Logged and converted to None return
        """
        try:
            identity_symbols = self._get_ingredient_identity_symbols(db_row['id'])

            return Ingredient(
                name=db_row['name'],
                identity=identity_symbols,
                state=None,
                preparation=None,
                size=None,
                dimensions=None,
                ingredient_id=db_row['id'],
                parent_id=db_row['parent_id'],
                cut_style=None,
                measurement=None,
                is_category=bool(db_row['is_category']),
                is_optional=False
            )
        except Exception as e:
            logger.error(f"Error mapping ingredient ID {db_row['id']}: {e}")
            return None
        
    def _get_ingredient_identity_symbols(self, ingredient_id: int) -> Set[Symbol]:
        """Retrieve identity symbols for an ingredient by ID.
        
        Args:
            ingredient_id (int): The database ID of the ingredient
            
        Returns:
            Set[Symbol]: A set containing the ingredient identity symbol
        """
        identity_symbols = set()

        with self.db_manager.get_cursor() as cursor:
            cursor.execute("SELECT name FROM ingredients WHERE id = %s", (ingredient_id,))
            result = cursor.fetchone()
            if result:
                identity_symbols.add(Symbol(
                    symbol_type=SymbolType.INGREDIENT_IDENTITY,
                    categories=set(),
                    canonical_form=result['name'],
                    aliases=set(),
                    description=""
                ))

        return identity_symbols
