"""Represents a recognized term (action, equipment, ingredient, etc.) used
as symbolic descriptors in recipes. Each symbol has a 'type' and references
to hierarchical identities and properties stored separately.
"""

from enum import Enum
from typing import Optional, Tuple, Set, Dict, Any
from abc import ABC


class SymbolType(Enum):
    """Represents different kinds of symbols used in recipe analysis."""
    ACTION = "action"
    EQUIPMENT = "equipment"
    INGREDIENT = "ingredient"
    UNIT = "unit"


class Symbol(ABC):
    """Represents a symbol in recipe analysis;
    they are units that make up the recipe itself.
    
    This is an abstract base class that should be inherited by specific symbol types.
    """
    
    def __init__(
        self,
        type: SymbolType,
        name: str,
        entity_id: Optional[int] = None,
        canonical_form: Optional[Tuple[int, str]] = None,
        identities: Optional[Set[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        description: str = "",
    ):
        """Initialize a symbol instance.
        
        Args:
            type (SymbolType): Type of the symbol (action, equipment, ingredient, etc.)
            name (str): The name of the symbol
            entity_id (Optional[int], optional): Database ID of the symbol, if known. Defaults to None.
            canonical_form (Optional[Tuple[int, str]], optional): The standard form of the symbol. Defaults to None.
            identities (Optional[Set[str]]): Set of hierarchical identity strings. Defaults to None.
            properties (Optional[Dict[str, Any]], optional): Key-value pairs for symbol properties. Defaults to None.
            description (str, optional): Text description of the symbol. Defaults to "".
        """
        self.type = type
        self.name = name
        self.entity_id = entity_id
        self.canonical_form = canonical_form
        self.identities = identities or set()
        self.properties = properties or {}
        self.description = description

    @property
    def name(self) -> str:
        """Get the name of the symbol.
        
        Returns:
            str: The name of the symbol
        """
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Set the name of the symbol.

        Args:
            value (str): The new name of the symbol
        """
        self._name = value
    
    # Predicate Methods
    def is_operator(self) -> bool:
        """Check if this symbol represents an operation.
        
        Returns:
            bool: True for operation symbols (actions), False otherwise
        """
        return self.type == SymbolType.ACTION
        
    def is_operand(self) -> bool:
        """Check if this symbol represents an operand.
        
        Returns:
            bool: True for operand symbols (ingredients, equipment), False otherwise
        """
        return self.type in (SymbolType.INGREDIENT, SymbolType.EQUIPMENT)

    # Mutator Methods
    def add_identity(self, identity: str) -> None:
        """Add a hierarchical identity to this symbol.
        
        Args:
            identity (str): Hierarchical identity string to add
        """
        self.identities.add(identity)
        
    def remove_identity(self, identity: str) -> bool:
        """Remove a hierarchical identity from this symbol.
        
        Args:
            identity (str): Identity to remove
            
        Returns:
            bool: True if the identity was removed, False if it wasn't found
        """
        if identity in self.identities:
            self.identities.remove(identity)
            return True
        return False

    def set_property(self, key: str, value: str) -> None:
        """Set a property key-value pair for this symbol.
        
        Args:
            key (str): Property key
            value (str): Property value
        """
        self.properties[key] = value
        
    def remove_property(self, key: str) -> bool:
        """Remove a property from this symbol.
        
        Args:
            key (str): Property key to remove
            
        Returns:
            bool: True if the property was removed, False if it wasn't found
        """
        if key in self.properties:
            del self.properties[key]
            return True
        return False

    # Equality and Hashing
    def __eq__(self, other) -> bool:
        """Check equality based on type, canonical form, and entity_id."""
        if not isinstance(other, Symbol):
            return False
        return (self.type == other.type and 
                self.canonical_form == other.canonical_form and
                self.entity_id == other.entity_id)
    
    def __hash__(self) -> int:
        """Generate hash based on type and canonical form."""
        return hash((self.type, self.name, self.canonical_form))

    # String Representations
    def __str__(self) -> str:
        """Get string representation of this symbol.
        
        Returns:
            str: String representation of format: canonical_form (type)
        """
        return f"{self.name} ({self.type.value})"
        
    def __repr__(self) -> str:
        """Get detailed string representation of this symbol for debugging.
        
        Returns:
            str: Detailed string representation
        """
        return (f"{self.__class__.__name__}(type={self.type.value}, "
                f"name='{self.name}', "
                f"entity_id={self.entity_id}, "
                f"canonical_form={self.canonical_form}, "
                f"identities={len(self.identities)}, "
                f"properties={len(self.properties)})")
