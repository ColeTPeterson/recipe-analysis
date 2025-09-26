"""Provides data access operations for symbols stored in MariaDB.
Handles CRUD operations for recipe symbols (actions, equipment, ingredients, etc.)
using the canonical/alias pattern.
"""

import logging
from typing import List, Optional, Set, Dict, Any, TypeVar

from repositories.base import BaseRepository
from repositories.connection import MariaDBConnectionManager
from models.symbol import Symbol, SymbolType
from models.instruction import ActionArity

S = TypeVar('S', bound=Symbol)

logger = logging.getLogger(__name__)


class SymbolRepository(BaseRepository[S]):
    """Provides data access methods for symbol-related operations in SQL."""
    
    def __init__(self, symbol_type: SymbolType = None):
        """Creates a MariaDBConnectionManager instance to handle database connections.
        
        Args:
            symbol_type (SymbolType, optional): The type of symbol this repository handles. Defaults to None.
        """
        self.connection_manager = MariaDBConnectionManager()
        self.symbol_type = symbol_type
    
        self._table_mapping = {
            SymbolType.ACTION: 'actions',
            SymbolType.EQUIPMENT: 'equipment',
            SymbolType.INGREDIENT: 'ingredients',
            SymbolType.UNIT: 'units'
        }

    # Read Operations 
    def get_all(self) -> List[Symbol]:
        """Retrieve all symbols of the repository's symbol type.
        If no symbol type is set, retrieves all symbols from all types.
                
        Returns:
            List[Symbol]: List of all Symbol instances
        """
        if not self.symbol_type:
            symbols = []
            for symbol_type in SymbolType:
                try:
                    symbols.extend(self._get_symbols_by_type(symbol_type))
                except Exception as e:
                    logger.warning(f"Error retrieving symbols of type {symbol_type}: {e}")
            return symbols
        else:
            return self._get_symbols_by_type(self.symbol_type)
        
    def get_by_id(self, symbol_id: int) -> Optional[Symbol]:
        """Retrieve a symbol by its database ID.
        
        Args:
            symbol_id (int): The database ID of the symbol
            
        Returns:
            Optional[Symbol]: Symbol if found, None otherwise
        """
        if self.symbol_type:
            return self._get_symbol_by_id_and_type(symbol_id, self.symbol_type)
            
        for symbol_type in SymbolType:
            symbol = self._get_symbol_by_id_and_type(symbol_id, symbol_type)
            if symbol:
                return symbol       
        return None
    
    def _get_symbols_by_type(self, symbol_type: SymbolType) -> List[Symbol]:
        """Retrieve all symbols of a specific type.

        Args:
            symbol_type (SymbolType): The type of the symbols to retrieve 

        Returns:
            List[Symbol]: List of Symbol instances of the specified type
        """
        table_name = self._get_table_name_for_type(symbol_type)
        if not table_name:
            logger.warning(f"No table mapping found for symbol type: {symbol_type}")
            return []
    
        symbols = []
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    query = f"SELECT * FROM {table_name}_canonical ORDER BY name"
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        symbol = self._map_to_symbol(row, symbol_type)
                        if symbol:
                            symbols.append(symbol)
                        
        except Exception as e:
            logger.error(f"Error retrieving symbols of type {symbol_type}: {e}")
        
        return symbols

    def get_all_identities(self) -> List[str]:
        """Get all identities for the repository's symbol type.
        If no symbol type is set, returns identities for all types.
        
        Returns:
            List[str]: List of all identity names
        """
        identities = []
        
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    if self.symbol_type:
                        query = """
                            SELECT DISTINCT si.identity_name
                            FROM symbol_identities si
                            WHERE si.symbol_type = %s
                            ORDER BY si.identity_name
                        """
                        cursor.execute(query, (self.symbol_type.value.upper(),))
                    else:
                        query = """
                            SELECT DISTINCT identity_name
                            FROM symbol_identities
                            ORDER BY identity_name
                        """
                        cursor.execute(query)
                    
                    for row in cursor.fetchall():
                        identities.append(row['identity_name'])
                        
        except Exception as e:
            logger.error(f"Error retrieving identities for type {self.symbol_type}: {e}")
            
        return identities
    
    def get_all_properties(self) -> List[str]:
        """Get all property keys for the repository's symbol type.
        If no symbol type is set, returns properties for all types.
        
        Returns:
            List[str]: List of all property keys
        """
        properties = []
        
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    if self.symbol_type:
                        query = """
                            SELECT DISTINCT sp.property_key
                            FROM symbol_properties sp
                            WHERE sp.symbol_type = %s
                            ORDER BY sp.property_key
                        """
                        cursor.execute(query, (self.symbol_type.value.upper(),))
                    else:
                        query = """
                            SELECT DISTINCT property_key
                            FROM symbol_properties
                            ORDER BY property_key
                        """
                        cursor.execute(query)
                    
                    for row in cursor.fetchall():
                        properties.append(row['property_key'])
                        
        except Exception as e:
            logger.error(f"Error retrieving properties for type {self.symbol_type}: {e}")
            
        return properties

    def get_all_property_values(self) -> Dict[str, List[str]]:
        """Get all property keys and their values for the repository's symbol type.
        If no symbol type is set, returns property values for all types.
        
        Returns:
            Dict[str, List[str]]: Dictionary with property keys as keys and list of values as values
        """
        property_values = {}
        
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    if self.symbol_type:
                        query = """
                            SELECT DISTINCT property_key, property_value
                            FROM symbol_properties
                            WHERE symbol_type = %s
                            ORDER BY property_key, property_value
                        """
                        symbol_type_val = self.symbol_type.value.upper()
                        logger.debug(f"Executing query with symbol_type={symbol_type_val}: {query}")
                        cursor.execute(query, (symbol_type_val,))
                    else:
                        query = """
                            SELECT DISTINCT property_key, property_value
                            FROM symbol_properties
                            ORDER BY property_key, property_value
                        """
                        logger.debug(f"Executing query: {query}")
                        cursor.execute(query)
                    
                    for row in cursor.fetchall():
                        key = row['property_key']
                        value = row['property_value']
                        if key not in property_values:
                            property_values[key] = []
                        if value is not None:
                            property_values[key].append(value)
                        
            logger.debug(f"Retrieved property values: {property_values}")
                        
        except Exception as e:
            logger.error(f"Error retrieving property values for type {self.symbol_type}: {e}")
            
        return property_values

    # Search Operations
    def find_symbols_by_name(self, name: str) -> List[Symbol]:
        """Find symbols by name.
        Searches both canonical and alias tables for matching names.

        Args:
            name (str): The name to search for (partial matches supported)

        Returns:
            List[Symbol]: List of matching Symbol instances
        """
        symbols = []

        if self.symbol_type:
            try:
                symbols.extend(self._search_symbols_in_tables(name, self.symbol_type))
            except Exception as e:
                logger.warning(f"Error searching symbols of type {self.symbol_type}: {e}")
        else:
            for symbol_type in SymbolType:
                try:
                    symbols.extend(self._search_symbols_in_tables(name, symbol_type))
                except Exception as e:
                    logger.warning(f"Error searching symbols of type {symbol_type}: {e}")

        return symbols

    def find_identities_by_name(self, name_pattern: str) -> List[str]:
        """Find identities by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for in identity names
            
        Returns:
            List[str]: List of matching identity names
        """
        identities = []
        
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    if self.symbol_type:
                        query = """
                            SELECT DISTINCT si.identity_name
                            FROM symbol_identities si
                            WHERE si.symbol_type = %s AND si.identity_name LIKE %s
                            ORDER BY si.identity_name
                        """
                        cursor.execute(query, (self.symbol_type.value.upper(), f"%{name_pattern}%"))
                    else:
                        query = """
                            SELECT DISTINCT identity_name
                            FROM symbol_identities
                            WHERE identity_name LIKE %s
                            ORDER BY identity_name
                        """
                        cursor.execute(query, (f"%{name_pattern}%",))
                    
                    for row in cursor.fetchall():
                        identities.append(row['identity_name'])
                        
        except Exception as e:
            logger.error(f"Error finding identities by pattern '{name_pattern}' for type {self.symbol_type}: {e}")
            
        return identities
    
    def find_properties_by_name(self, name_pattern: str) -> List[str]:
        """Find property keys by name pattern.
        
        Args:
            name_pattern (str): Pattern to search for in property keys
            
        Returns:
            List[str]: List of matching property keys
        """
        properties = []
        
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    if self.symbol_type:
                        query = """
                            SELECT DISTINCT sp.property_key
                            FROM symbol_properties sp
                            WHERE sp.symbol_type = %s AND sp.property_key LIKE %s
                            ORDER BY sp.property_key
                        """
                        cursor.execute(query, (self.symbol_type.value.upper(), f"%{name_pattern}%"))
                    else:
                        query = """
                            SELECT DISTINCT property_key
                            FROM symbol_properties
                            WHERE property_key LIKE %s
                            ORDER BY property_key
                        """
                        cursor.execute(query, (f"%{name_pattern}%",))
                    
                    for row in cursor.fetchall():
                        properties.append(row['property_key'])
                        
        except Exception as e:
            logger.error(f"Error finding properties by pattern '{name_pattern}' for type {self.symbol_type}: {e}")
            
        return properties

    # Create/Update/Delete Operations
    def create(self, entity: Symbol) -> Optional[Symbol]:
        """Create a new symbol in the database.
        
        Args:
            entity (Symbol): Symbol entity to create
            
        Returns:
            Optional[Symbol]: The created symbol with ID assigned, or None if failed
        """
        if not self.symbol_type and not hasattr(entity, 'type'):
            raise ValueError("Cannot create symbol without a type")
            
        entity_type = self.symbol_type if self.symbol_type else entity.type
            
        try:        
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    table_name = self._get_table_name_for_type(entity_type)
                    
                    if not table_name:
                        raise ValueError(f"Unsupported symbol type: {entity_type}")
                        
                    # Insert into canonical table with type-specific columns
                    if entity_type == SymbolType.ACTION:
                        arity_value = None
                        if hasattr(entity, 'arity') and getattr(entity, 'arity'):
                            arity_value = getattr(entity, 'arity').value.upper()
                        
                        query = f"""
                            INSERT INTO {table_name}_canonical
                            (name, description, arity)
                            VALUES (%s, %s, %s)
                        """
                        cursor.execute(query, (entity.name, entity.description, arity_value))
                    else:
                        query = f"""
                            INSERT INTO {table_name}_canonical
                            (name, description)
                            VALUES (%s, %s)
                        """
                        cursor.execute(query, (entity.name, entity.description))
                    
                    entity.entity_id = cursor.lastrowid
                    connection.commit()
                    
                    # Add primary name to aliases table
                    alias_column = self._get_alias_column_name(table_name)
                    query = f"""
                        INSERT INTO {table_name}_aliases
                        (alias, {alias_column})
                        VALUES (%s, %s)
                    """
                    cursor.execute(query, (entity.name, entity.entity_id))
                    connection.commit()
                    
                    # Add identities and properties if present
                    self._create_identities_and_properties(entity)
                    
                    logger.info(f"Created symbol {entity.name} with ID {entity.entity_id}")
                    return entity
                    
        except Exception as e:
            logger.error(f"Error creating symbol {entity.name}: {e}")
            return None
    
    def update(self, entity: Symbol) -> Optional[Symbol]:
        """Update an existing symbol.
        
        Args:
            entity (Symbol): Symbol to update
            
        Returns:
            Optional[Symbol]: Updated symbol, or None if failed
            
        Raises:
            ValueError: If entity_id is not set
        """
        if not entity.entity_id:
            raise ValueError("Cannot update symbol without ID")
            
        if not self.symbol_type and not hasattr(entity, 'type'):
            raise ValueError("Cannot update symbol without a type")
            
        entity_type = self.symbol_type if self.symbol_type else entity.type
            
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    table_name = self._get_table_name_for_type(entity_type)
                    
                    if not table_name:
                        raise ValueError(f"Unsupported symbol type: {entity_type}")
                        
                    # Update canonical table with type-specific columns
                    if entity_type == SymbolType.ACTION:
                        arity_value = None
                        if hasattr(entity, 'arity') and getattr(entity, 'arity'):
                            arity_value = getattr(entity, 'arity').value.upper()
                        
                        query = f"""
                            UPDATE {table_name}_canonical
                            SET name = %s, description = %s, arity = %s
                            WHERE id = %s
                        """
                        cursor.execute(query, (entity.name, entity.description, arity_value, entity.entity_id))
                    else:
                        query = f"""
                            UPDATE {table_name}_canonical
                            SET name = %s, description = %s
                            WHERE id = %s
                        """
                        cursor.execute(query, (entity.name, entity.description, entity.entity_id))
                    
                    connection.commit()
                    
                    if cursor.rowcount > 0:
                        # Update identities and properties
                        self._update_identities_and_properties(entity)
                        logger.info(f"Updated symbol {entity.entity_id}")
                        return entity
                    else:
                        logger.warning(f"No symbol found with ID {entity.entity_id}")
                        return None
                    
        except Exception as e:
            logger.error(f"Error updating symbol {entity.entity_id}: {e}")
            return None
    
    def delete(self, entity_id: int) -> bool:
        """Delete a symbol.
        
        Args:
            entity_id (int): ID of the symbol to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if self.symbol_type:
            table_name = self._get_table_name_for_type(self.symbol_type)
            symbol_types = [self.symbol_type]
        else:
            symbol_types = list(SymbolType)
            
        success = False
        
        for symbol_type in symbol_types:
            table_name = self._get_table_name_for_type(symbol_type)
            
            try:
                with self.connection_manager.get_connection() as connection:
                    with connection.cursor() as cursor:
                        query = f"""
                            SELECT id FROM {table_name}_canonical
                            WHERE id = %s
                        """
                        cursor.execute(query, (entity_id,))
                        
                        if cursor.fetchone():
                            # Delete mappings first
                            self._delete_identities_and_properties(entity_id, symbol_type)
                            
                            # Delete from canonical table (cascading will handle aliases)
                            query = f"""
                                DELETE FROM {table_name}_canonical
                                WHERE id = %s
                            """
                            cursor.execute(query, (entity_id,))
                            
                            connection.commit()
                            if cursor.rowcount > 0:
                                success = True
                                logger.info(f"Deleted symbol {entity_id} of type {symbol_type.value}")
                                break
            except Exception as e:
                logger.error(f"Error deleting from {table_name}: {e}")
                
        return success

    # Helper Methods   
    def _find_in_table(self, criteria: Dict[str, Any], table_name: str, 
                      symbol_type: SymbolType) -> List[Symbol]:
        """Helper to find symbols in a specific table matching the given criteria.
            
        Args:
            criteria (Dict[str, Any]): Search criteria key-value pairs
            table_name (str): Name of the table to search in
            symbol_type (SymbolType): Type of symbol to map results to
            
        Returns:
            List[Symbol]: List of matching Symbol instances
            
        Raises:
            ValueError: If the table name is invalid or criteria contains unsupported fields
        """
        results = []
        
        try:
            where_parts = []
            query_params = []
            
            for key, value in criteria.items():
                # Handle special cases for specific symbol types
                if key == 'arity' and symbol_type == SymbolType.ACTION:
                    if isinstance(value, ActionArity):
                        where_parts.append("arity = %s")
                        query_params.append(value.value.upper())
                    else:
                        where_parts.append("arity = %s")
                        query_params.append(str(value).upper())
                else:
                    where_parts.append(f"{key} = %s")
                    query_params.append(value)
                
            where_clause = " AND ".join(where_parts) if where_parts else "1=1"
            
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    query = f"""
                        SELECT *
                        FROM {table_name}_canonical
                        WHERE {where_clause}
                    """
                    cursor.execute(query, query_params)
                    
                    for row in cursor.fetchall():
                        symbol = self._map_to_symbol(row, symbol_type)
                        if symbol:
                            results.append(symbol)
        except Exception as e:
            logger.error(f"Error finding symbols in table {table_name}: {e}")
                
        return results
        
    def _map_to_symbol(self, row: Dict[str, Any], symbol_type: SymbolType) -> Optional[Symbol]:
        """Map a database row to a Symbol object.
        
        Args:
            row (Dict[str, Any]): Database row
            symbol_type (SymbolType): Type of symbol
            
        Returns:
            Optional[Symbol]: Mapped concrete Symbol subclass instance
        """
        try:
            name = row['name']
            
            description = row.get('description')
            if description is None:
                description = ""
            elif not isinstance(description, str):
                description = str(description)
                
            # Get identities and properties from mapping tables
            identities = self._get_identities(row['id'], symbol_type)
            properties = self._get_properties(row['id'], symbol_type)
            
            # Create the appropriate symbol subclass based on type
            if symbol_type == SymbolType.ACTION:
                from models.instruction import Action, ActionArity
                arity = None
                if 'arity' in row and row['arity']:
                    try:
                        arity = ActionArity(row['arity'].lower())
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Invalid arity value '{row['arity']}': {e}")
                        # Try to recover with default
                        try:
                            arity = ActionArity.VARIABLE
                        except Exception:
                            pass
                
                return Action(
                    name=name,
                    entity_id=row['id'],
                    identities=identities,
                    properties=properties,
                    description=description,
                    arity=arity
                )
            elif symbol_type == SymbolType.EQUIPMENT:
                from models.equipment import Equipment
                return Equipment(
                    name=name,
                    entity_id=row['id'],
                    identities=identities,
                    properties=properties,
                    description=description
                )
            elif symbol_type == SymbolType.INGREDIENT:
                from models.ingredient import Ingredient
                return Ingredient(
                    name=name,
                    entity_id=row['id'],
                    identities=identities,
                    properties=properties,
                    description=description
                )
            elif symbol_type == SymbolType.UNIT:
                from models.measurement import Unit
                return Unit(
                    name=name,
                    entity_id=row['id'],
                    identities=identities,
                    properties=properties,
                    description=description
                )
            else:
                logger.error(f"Unknown symbol type: {symbol_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error mapping symbol row for {row.get('id', 'unknown')}: {e}")
            return None
    
    def _get_identities(self, symbol_id: int, symbol_type: SymbolType) -> Set[str]:
        """Get identities for a symbol from the mapping tables."""
        identities = set()
        
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    query = """
                        SELECT si.identity_name
                        FROM symbol_identity_mapping sim
                        JOIN symbol_identities si ON sim.identity_id = si.id
                        WHERE sim.symbol_id = %s AND sim.symbol_type = %s
                    """
                    cursor.execute(query, (symbol_id, symbol_type.value.upper()))
                    
                    for row in cursor.fetchall():
                        identities.add(row['identity_name'])
        except Exception as e:
            logger.debug(f"Error getting identities for symbol {symbol_id}: {e}")
                
        return identities
    
    def _get_properties(self, symbol_id: int, symbol_type: SymbolType) -> Dict[str, Any]:
        """Get properties for a symbol from the mapping tables."""
        properties = {}
        
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    query = """
                        SELECT sp.property_key, sp.property_value
                        FROM symbol_property_mapping spm
                        JOIN symbol_properties sp ON spm.property_id = sp.id
                        WHERE spm.symbol_id = %s AND sp.symbol_type = %s
                    """
                    cursor.execute(query, (symbol_id, symbol_type.value.upper()))
                    
                    for row in cursor.fetchall():
                        properties[row['property_key']] = row['property_value']
        except Exception as e:
            logger.debug(f"Error getting properties for symbol {symbol_id}: {e}")
            
        return properties

    def _create_identities_and_properties(self, entity: Symbol) -> None:
        """Create identity and property mappings for a symbol."""
        entity_type = self.symbol_type if self.symbol_type else entity.type
        
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    # Create identities
                    for identity in entity.identities:
                        # Insert or get identity
                        cursor.execute("""
                            INSERT IGNORE INTO symbol_identities (identity_name)
                            VALUES (%s)
                        """, (identity,))
                        
                        cursor.execute("""
                            SELECT id FROM symbol_identities WHERE identity_name = %s
                        """, (identity,))
                        identity_id = cursor.fetchone()['id']
                        
                        # Create mapping
                        cursor.execute("""
                            INSERT IGNORE INTO symbol_identity_mapping 
                            (symbol_id, symbol_type, identity_id)
                            VALUES (%s, %s, %s)
                        """, (entity.entity_id, entity_type.value.upper(), identity_id))
                    
                    # Create properties
                    for key, value in entity.properties.items():
                        # Insert or get property
                        cursor.execute("""
                            INSERT IGNORE INTO symbol_properties (property_key, property_value)
                            VALUES (%s, %s)
                        """, (key, value))
                        
                        cursor.execute("""
                            SELECT id FROM symbol_properties 
                            WHERE property_key = %s AND property_value = %s
                        """, (key, value))
                        property_id = cursor.fetchone()['id']
                        
                        # Create mapping
                        cursor.execute("""
                            INSERT IGNORE INTO symbol_property_mapping 
                            (symbol_id, symbol_type, property_id)
                            VALUES (%s, %s, %s)
                        """, (entity.entity_id, entity_type.value.upper(), property_id))
                    
                    connection.commit()
        except Exception as e:
            logger.error(f"Error creating identities and properties for symbol {entity.entity_id}: {e}")

    def _update_identities_and_properties(self, entity: Symbol) -> None:
        """Update identity and property mappings for a symbol."""
        entity_type = self.symbol_type if self.symbol_type else entity.type
        
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    # Delete existing mappings
                    cursor.execute("""
                        DELETE FROM symbol_identity_mapping 
                        WHERE symbol_id = %s AND symbol_type = %s
                    """, (entity.entity_id, entity_type.value.upper()))
                    
                    cursor.execute("""
                        DELETE FROM symbol_property_mapping 
                        WHERE symbol_id = %s AND symbol_type = %s
                    """, (entity.entity_id, entity_type.value.upper()))
                    
                    connection.commit()
                    
                    # Recreate mappings
                    self._create_identities_and_properties(entity)
                    
        except Exception as e:
            logger.error(f"Error updating identities and properties for symbol {entity.entity_id}: {e}")

    def _delete_identities_and_properties(self, symbol_id: int, symbol_type: SymbolType) -> None:
        """Delete identity and property mappings for a symbol."""
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM symbol_identity_mapping 
                        WHERE symbol_id = %s AND symbol_type = %s
                    """, (symbol_id, symbol_type.value.upper()))
                    
                    cursor.execute("""
                        DELETE FROM symbol_property_mapping 
                        WHERE symbol_id = %s AND symbol_type = %s
                    """, (symbol_id, symbol_type.value.upper()))
                    
        except Exception as e:
            logger.error(f"Error deleting identities and properties for symbol {symbol_id}: {e}")

    def _get_symbol_by_id_and_type(self, symbol_id: int, symbol_type: SymbolType) -> Optional[Symbol]:
        """Get a symbol by ID from a specific symbol type table."""
        table_name = self._get_table_name_for_type(symbol_type)
        if not table_name:
            return None
            
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    query = f"SELECT * FROM {table_name}_canonical WHERE id = %s"
                    cursor.execute(query, (symbol_id,))
                    row = cursor.fetchone()
                    return self._map_to_symbol(row, symbol_type) if row else None
                        
        except Exception as e:
            logger.error(f"Error retrieving symbol {symbol_id} of type {symbol_type}: {e}")
            return None
        
    def _get_table_name_for_type(self, symbol_type: SymbolType) -> str:
        """Convert symbol type enum to corresponding database table name.
            
        Args:
            symbol_type (SymbolType): The symbol type to map
            
        Returns:
            str: Table name corresponding to the symbol type, or empty string if not found
        """
        return self._table_mapping.get(symbol_type, '')

    def _get_alias_column_name(self, table_name: str) -> str:
        """Get the correct alias column name for the table."""
        if table_name == 'actions':
            return 'action_canonical_id'
        elif table_name == 'ingredients':
            return 'ingredient_canonical_id'
        elif table_name == 'equipment':
            return 'equipment_canonical_id'
        elif table_name == 'units':
            return 'unit_canonical_id'
        else:
            return f"{table_name}_canonical_id"

    def _search_symbols_in_tables(self, name: str, symbol_type: SymbolType) -> List[Symbol]:
        """Search for symbols in both canonical and alias tables.

        Args:
            name (str): The name of the symbol to search for
            symbol_type (SymbolType): The type of the symbol to search for

        Returns:
            List[Symbol]: A list of symbols matching the symbol's name and type
        """
        symbols = []
        table_name = self._get_table_name_for_type(symbol_type)
        
        if not table_name:
            return symbols
            
        try:
            with self.connection_manager.get_connection() as connection:
                with connection.cursor() as cursor:
                    # Search canonical table
                    query = f"SELECT * FROM {table_name}_canonical WHERE name LIKE %s ORDER BY name"
                    cursor.execute(query, (f"%{name}%",))
                    canonical_rows = cursor.fetchall()
                    
                    # Map canonical symbols
                    found_canonical_ids = set()
                    for row in canonical_rows:
                        symbol = self._map_to_symbol(row, symbol_type)
                        if symbol:
                            symbols.append(symbol)
                            found_canonical_ids.add(row['id'])
                    
                    # Search aliases table
                    alias_column = self._get_alias_column_name(table_name)
                    
                    if found_canonical_ids:
                        # Avoid duplicates with NOT IN clause
                        placeholders = ','.join(['%s'] * len(found_canonical_ids))
                        query = f"""
                            SELECT c.*
                            FROM {table_name}_aliases a
                            JOIN {table_name}_canonical c ON a.{alias_column} = c.id
                            WHERE a.alias LIKE %s AND a.{alias_column} NOT IN ({placeholders})
                            ORDER BY a.alias
                        """
                        params = [f"%{name}%"] + list(found_canonical_ids)
                        cursor.execute(query, params)
                    else:
                        query = f"""
                            SELECT c.*
                            FROM {table_name}_aliases a
                            JOIN {table_name}_canonical c ON a.{alias_column} = c.id
                            WHERE a.alias LIKE %s
                            ORDER BY a.alias
                        """
                        cursor.execute(query, (f"%{name}%",))
                    
                    aliases_rows = cursor.fetchall()
                    
                    for row in aliases_rows:
                        symbol = self._map_to_symbol(row, symbol_type)
                        if symbol:
                            symbols.append(symbol)
                            
        except Exception as e:
            logger.error(f"Error searching symbols for '{name}' of type {symbol_type}: {e}")
            
        return symbols
