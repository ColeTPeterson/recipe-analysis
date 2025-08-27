"""Provides data access operations for symbol entities stored in MariaDB;
handles fetching symbols of different types (actions, units, properties, etc.),
mapping database records to domain objects, and managing symbol categories and aliases.
"""

import logging
from typing import List, Optional, Dict, Any, Set

from models.symbol import Symbol, SymbolType
from repositories.base import BaseRepository
from repositories.mariadb.connection import MariaDBConnectionManager

logger = logging.getLogger(__name__)

class SymbolRepository(BaseRepository[Symbol]):
    """Provides data access methods for symbol-related operations,
    handles database operations across different symbol types (actions, units, 
    properties, ingredients, equipment) and manages relationships between symbols,
    categories, and aliases.
    """
    
    def __init__(self):
        """Initialize the symbol repository with a database connection manager."""
        self.db_manager = MariaDBConnectionManager()

    def create(self, entity: Symbol) -> Symbol:
        """Create a new symbol entity in the database.
        
        Args:
            entity (Symbol): The symbol entity to create
            
        Returns:
            Symbol: The created symbol with updated ID
            
        Raises:
            NotImplementedError: This method is not yet implemented
        """
        raise NotImplementedError("Symbol creation is not yet implemented")
    
    def get_all(self) -> List[Symbol]:
        """Retrieve all symbol entities from the database.
        
        Returns:
            List[Symbol]: A list of all symbol entities
            
        Raises:
            NotImplementedError: This method is not implemented due to the 
                potentially large number of symbols that would be returned
        """
        raise NotImplementedError("Getting all symbols is not implemented due to potential size")
    
    def get_by_id(self, entity_id: int) -> Optional[Symbol]:
        """Retrieve a symbol entity by its ID.
        
        Searches across all symbol type tables for the given ID.
        
        Args:
            entity_id (int): The database ID of the symbol
            
        Returns:
            Optional[Symbol]: The symbol entity if found, None otherwise
        """
        with self.db_manager.get_cursor() as cursor:
            for table in ['actions_canonical', 'units_canonical', 'item_properties_canonical',
                          'ingredients_canonical', 'equipment_canonical']:
                cursor.execute(f"SELECT * FROM {table} WHERE id = %s", (entity_id,))
                result = cursor.fetchone()
                if result:
                    return self._map_to_symbol(result, table)
        return None
    
    def find_by(self, criteria: Dict[str, Any]) -> List[Symbol]:
        """Searches for symbols based on the provided criteria, focusing on a specific
        symbol type table. Requires at minimum a symbol_type in the criteria.
        
        Args:
            criteria (Dict[str, Any]): Search criteria with supported keys:
                - symbol_type: Required SymbolType enum value
                - canonical_form or name: Optional exact match for symbol name
            
        Returns:
            List[Symbol]: List of matching symbol entities
        """
        results = []

        symbol_type = criteria.get('symbol_type')
        if not symbol_type:
            return []
        
        table_name = self._get_table_for_symbol_type(symbol_type)
        if not table_name:
            return []
        
        with self.db_manager.get_cursor() as cursor:
            query_parts = []
            query_params = []

            if 'canonical_form' in criteria or 'name' in criteria:
                name_value = criteria.get('canonical_form', criteria.get('name'))
                query_parts.append("name = %s")
                query_params.append(name_value)

            if not query_parts:
                return []
            
            query = f"SELECT * FROM {table_name} WHERE {' AND '.join(query_parts)}"
            cursor.execute(query, query_params)
            for row in cursor.fetchall():
                results.append(self._map_to_symbol(row, table_name))

        return results
    
    def find_by_name(self, name: str, symbol_type: SymbolType) -> List[Symbol]:
        """Find symbols by name and type.
                
        Args:
            name (str): The canonical form/name to search for
            symbol_type (SymbolType): The type of symbol to search for
            
        Returns:
            List[Symbol]: List of matching symbol entities
        """
        return self.find_by({'canonical_form': name, 'symbol_type': symbol_type})
    
    def update(self, entity: Symbol) -> Symbol:
        """Update an existing symbol entity in the database.
        
        Args:
            entity (Symbol): The symbol entity with updated values
            
        Returns:
            Symbol: The updated symbol entity
            
        Raises:
            NotImplementedError: This method is not yet implemented
        """
        raise NotImplementedError("Symbol updating is not yet implemented")
    
    def delete(self, entity_id: int) -> bool:
        """Delete a symbol entity from the database.
        
        Args:
            entity_id (int): The ID of the symbol to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            NotImplementedError: This method is not yet implemented
        """
        raise NotImplementedError("Symbol deletion is not yet implemented")
    
    def _get_table_for_symbol_type(self, symbol_type: SymbolType) -> str:
        """Get the corresponding database table name for a symbol type.
            
        Args:
            symbol_type (SymbolType): The symbol type to map
            
        Returns:
            str: Database table name or empty string if no mapping exists
        """
        mapping = {
            SymbolType.ACTION: 'actions_canonical',
            SymbolType.UNIT: 'units_canonical',
            SymbolType.ITEM_PROPERTY: 'item_properties_canonical',
            SymbolType.INGREDIENT_IDENTITY: 'ingredients_canonical',
            SymbolType.EQUIPMENT_IDENTITY: 'equipment_canonical'
        }
        return mapping.get(symbol_type, '')
    
    def _map_to_symbol(self, db_row: Dict[str, Any], table_name: str) -> Symbol:
        """Map a database row to a Symbol domain object.
        
        Args:
            db_row (Dict[str, Any]): Database row containing symbol data
            table_name (str): Name of the table the row was fetched from
            
        Returns:
            Symbol: The fully populated Symbol object
            
        Raises:
            ValueError: If the table name does not correspond to a known symbol type
        """
        
        # Determine the appropriate symbol type based on the table
        symbol_type_mapping = {
            'actions_canonical': SymbolType.ACTION,
            'units_canonical': SymbolType.UNIT,
            'item_properties_canonical': SymbolType.ITEM_PROPERTY,
            'ingredients_canonical': SymbolType.INGREDIENT_IDENTITY,
            'equipment_canonical': SymbolType.EQUIPMENT_IDENTITY
        }

        symbol_type = symbol_type_mapping.get(table_name)
        if not symbol_type:
            raise ValueError(f"Unknown table name: {table_name}")
        
        # Retrieve related categories and aliases
        categories = self._get_categories_for_symbol(db_row['id'], table_name)
        aliases = self._get_aliases_for_symbol(db_row['id'], table_name)

        # Create a complete Symbol object
        return Symbol(
            symbol_type=symbol_type,
            categories=categories,
            canonical_form=db_row['name'],
            aliases=aliases,
            description=db_row.get('description', '')
        )
    
    def _get_categories_for_symbol(self, symbol_id: int, table_name: str) -> Set[str]:
        """Retrieve all categories associated with a symbol.
        
        Args:
            symbol_id (int): The ID of the symbol
            table_name (str): The canonical table name for the symbol type
            
        Returns:
            Set[str]: Set of category names associated with the symbol
        """
        category_tables = {
            'actions_canonical': ('action_category_mapping', 'action_categories', 'action_canonical_id'),
            'units_canonical': ('unit_category_mapping', 'unit_categories', 'unit_canonical_id'),
            'item_properties_canonical': ('item_property_category_mapping', 'item_property_categories', 'item_property_canonical_id'),
            'ingredients_canonical': ('ingredient_identity_category_mapping', 'ingredient_identity_categories', 'ingredient_canonical_id'),
            'equipment_canonical': ('equipment_identity_category_mapping', 'equipment_identity_categories', 'equipment_canonical_id')
        }

        if table_name not in category_tables:
            return set()
        
        mapping_table, category_table, id_column = category_tables[table_name]
        categories = set()

        with self.db_manager.get_cursor() as cursor:
            query = f"""
                SELECT c.name
                FROM {mapping_table} m
                JOIN {category_table} c ON m.{id_column.replace('_id', '')}_category_id = c.id
                WHERE m.{id_column} = %s
            """
            cursor.execute(query, (symbol_id,))
            for row in cursor.fetchall():
                categories.add(row['name'])

        return categories
    
    def _get_aliases_for_symbol(self, symbol_id: int, table_name: str) -> Set[str]:
        """Retrieve all aliases associated with a symbol.
        
        Args:
            symbol_id (int): The ID of the symbol
            table_name (str): The canonical table name for the symbol type
            
        Returns:
            Set[str]: Set of alias strings associated with the symbol
        """
        alias_tables = {
            'actions_canonical': ('actions_recognized', 'action_canonical_id'),
            'units_canonical': ('units_recognized', 'unit_canonical_id'),
            'item_properties_canonical': ('item_properties_recognized', 'item_property_canonical_id'),
            'ingredients_canonical': ('ingredients_recognized', 'ingredient_canonical_id'),
            'equipment_canonical': ('equipment_recognized', 'equipment_canonical_id')
        }

        if table_name not in alias_tables:
            return set()
        
        recognized_table, id_column = alias_tables[table_name]
        aliases = set()

        with self.db_manager.get_cursor() as cursor:
            query = f"""
                SELECT alias
                FROM {recognized_table}
                WHERE {id_column} = %s
            """
            cursor.execute(query, (symbol_id,))
            for row in cursor.fetchall():
                aliases.add(row['alias'])

        return aliases
