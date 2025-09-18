"""Provides the base Item class for recipe elements,
with physical attributes for recipe modeling.
Item inherits from Symbol and adds physical attributes.
"""

from typing import Optional

from .symbol import Symbol, SymbolType
from .dimensions import Dimensions


class Item(Symbol):
    """Base class representing an item in a recipe (ingredient/equipment).
    Inherits from Symbol and adds physical attributes specific to recipe components.

    Attributes:
        dimensions (Optional[Dimensions]): The physical dimensions of an item.
    """
    def __init__(self,
                 name: str,
                 type: SymbolType,
                 dimensions: Optional[Dimensions] = None,
                 **kwargs):
        """Initialize an item.

        Args:
            type (SymbolType): The type of the item (INGREDIENT or EQUIPMENT)
            name (str): The name of the item
            dimensions (Optional[Dimensions], optional): The physical dimensions of the item. Defaults to None.
            **kwargs Additional Symbol parameters
        """
        super().__init__(
            type=type,
            name=name,
            **kwargs
        )
        self.dimensions = dimensions

    @property
    def dimensions(self) -> Optional[Dimensions]:
        """Get the dimensions."""
        return self._dimensions
    
    @dimensions.setter
    def dimensions(self, value: Optional[Dimensions]) -> None:
        """Set the dimensions.

        Args:
            value (Optional[Dimensions]): Dimensions instance or None

        Raises:
            TypeError: If value is not a Dimensions instance or None
        """
        if value is not None and not hasattr(value, '__class__'):
            raise TypeError("Dimensions must be a Dimensions instance or None")
        self._dimensions = value
    
    # Equality and Hashing
    def __eq__(self, other) -> bool:
        """Equality comparison based on name."""
        if not isinstance(other, Item):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        """Hash method for using items in sets."""
        return hash(self.name)
    
    # String Representations
    def __str__(self) -> str:
        """Get string representation of the item.
        
        Returns:
            str: String representation showing name and type
        """
        return f"{self.name} ({self.type.value})"

    def __repr__(self) -> str:
        """Get detailed string representation of the item for debugging.
        
        Returns:
            str: Detailed string representation
        """
        dims_info = f", dimensions={self.dimensions}" if self.dimensions else ""
        return f"Item(name='{self.name}', type={self.type.value}{dims_info})"
        
