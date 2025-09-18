"""Provides domain models for ingredients used in recipes;
includes hierarchical organization and categorization.
"""

from typing import Optional, Set, Any

from .item import Item
from .symbol import SymbolType


class Ingredient(Item):
    """Domain model representing an ingredient in recipe analysis,
    ingredients are foods or substances used in recipes, with support
    for hierarchical organization (e.g., vegetables > leafy greens > spinach)
    """
    def __init__(self, name: str, **kwargs):
        """Initialize an ingredient.
        
        Args:
            name: Name of the ingredient
            **kwargs Additional Item parameters
        """
        super().__init__(
            name=name,
            type=SymbolType.INGREDIENT,
            **kwargs
        )

    # String Representations
    def __str__(self) -> str:
        """Get string representation of the ingredient.
        
        Returns:
            str: String representation
        """
        return self.name
        
    def __repr__(self) -> str:
        """Get detailed string representation of the ingredient.
        
        Returns:
            str: Detailed string representation
        """
        return (f"Ingredient(name='{self.name}', "
            f"type={self.type.value}, "
            f"entity_id={self.entity_id}, "
            f"identities={len(self.identities)}, "
            f"properties={len(self.properties)})")


class IntermediateIngredient(Ingredient):
    """Represents an ingredient produced by an instruction.

    Attributes:
        name: Name of the intermediate ingredient
        produced_by: Instruction that produces this ingredient.
        source_ingredients: Source ingredients used to produce this.
        vessel: The vessel
    """
    def __init__(self,
                 name: str,
                 produced_by: Optional[Any] = None,
                 source_ingredients: Optional[Set['Ingredient']] = None,
                 vessel: Optional[Any] = None,
                 **kwargs):
        """Initialize an intermediate ingredient.

        Args:
            name (str): Name of the intermediate ingredient
            produced_by (Optional[Any], optional): Instruction that produces this ingredient. Defaults to None.
            source_ingredients (Optional[Set[Ingredient]]): Set of source ingredients used. Defaults to None.
            vessel (Optional[Any]): The vessel used as the source of the ingredients
        """
        super().__init__(name=name, **kwargs)
        self.produced_by = produced_by
        self.source_ingredients = source_ingredients or set()
        self.vessel = vessel
    
    # Mutator methods
    def add_source_ingredient(self, ingredient: 'Ingredient') -> None:
        """Add a source ingredient that contributes to this intermediate ingredient."""
        self.source_ingredients.add(ingredient)
    
    def remove_source_ingredient(self, ingredient: 'Ingredient') -> None:
        """Remove a source ingredient."""
        self.source_ingredients.discard(ingredient)

    # String Representations
    def __str__(self) -> str:
        """Get string representation of the intermediate ingredient.
        
        Returns:
            str: String representation
        """
        source_count = len(self.source_ingredients) if self.source_ingredients else 0
        vessel_info = f" (from {self.vessel.name})" if self.vessel else ""
        return f"{self.name}{vessel_info} [{source_count} sources]"

    def __repr__(self) -> str:
        """Get detailed string representation of the intermediate ingredient.
        
        Returns:
            str: Detailed string representation for debugging
        """
        return (f"IntermediateIngredient(name='{self.name}', "
                f"produced_by={self.produced_by}, "
                f"sources={len(self.source_ingredients) if self.source_ingredients else 0}, "
                f"vessel={self.vessel.name if self.vessel else None})")
