"""Handles operations related to symbols including retrieval, categorization,
and conversion between database records and domain models.
"""

import logging
from typing import List, Optional, TypeVar, Generic, Type

from models.symbol import Symbol, SymbolType
from repositories.symbol_repository import SymbolRepository

logger = logging.getLogger(__name__)

S = TypeVar('S', bound=Symbol)


class SymbolController(Generic[S]):
    """Mediates between the symbol repository and application logic,
    providing methods for retrieving and managing symbols.
    """
    
    def __init__(self, symbol_class: Type[S] = None, symbol_type: SymbolType = None):
        """Initialize the symbol controller with required repositories.
        
        Args:
            symbol_class (Type[S], optional): The symbol class this controller manages. Defaults to None.
            symbol_type (SymbolType, optional): The type of symbols this controller manages. Defaults to None.
        """
        self.repository = SymbolRepository()
        self.symbol_class = symbol_class
        self.symbol_type = symbol_type

    # Read Operations
    def get_all_symbols(self) -> List[Symbol]:
        """Retrieve all symbols from the repository.

        Returns:
            List[Symbol]: List of all Symbol instances across all types
        """
        try:
            return self.repository.get_all()
        except Exception as e:
            logger.error(f"Error retrieving all symbols: {e}")
            return []

    def get_symbol_by_id(self, symbol_id: int) -> Optional[Symbol]:
        """Retrieve a specific symbol by its database ID.
        
        Args:
            symbol_id (int): ID of the symbol to retrieve
            
        Returns:
            Optional[Symbol]: The symbol if found, None otherwise
        """
        try:
            return self.repository.get_by_id(symbol_id)
        except Exception as e:
            logger.error(f"Error retrieving symbol {symbol_id}: {e}")
            return None
    
    # Search Operations
    def find_symbols_by_name(self, name: str) -> List[Symbol]:
        """Find symbols by name and optionally by type.
        
        Args:
            name (str): Name or partial name to search for
            
        Returns:
            List[Symbol]: List of matching symbols
        """
        try:
            return self.repository.find_symbols_by_name(name)
        except Exception as e:
            logger.error(f"Error searching symbols by name '{name}': {e}")
            return []

    # Create/Update/Delete Operations
    def create_symbol(self, symbol: Symbol) -> Optional[Symbol]:
        """Create a new symbol in the database.

        Args:
            symbol (Symbol): The Symbol to be created

        Returns:
            Optional[Symbol]: The created symbol instance in the database
        """
        try:
            return self.repository.create(symbol)
        except Exception as e:
            logger.error(f"Error creating symbol: {e}")
            return None
        
    def update_symbol(self, symbol: Symbol) -> bool:
        """Update an existing symbol in the database.

        Args:
            symbol (Symbol): The Symbol to be updated

        Returns:
            bool: True if the Symbol has been updated, False otherwise
        """
        try:
            updated = self.repository.update(symbol)
            return updated is not None
        except Exception as e:
            logger.error(f"Error updating symbol: {e}")
            return False
        
    def delete_symbol(self, symbol_id: int) -> bool:
        """Delete a Symbol by its database ID.

        Args:
            symbol_id (int): The database ID of the Symbol to be deleted

        Returns:
            bool: True if the Symbol has been deleted, False otherwise
        """
        try:
            return self.repository.delete(symbol_id)
        except Exception as e:
            logger.error(f"Error deleting symbol {symbol_id}: {e}")
            return False