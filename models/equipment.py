"""Provides domain models for equipment used in recipes;
includes hierarchical organization and categorization.
"""

from typing import Optional, Set, Any, List

from .item import Item
from .ingredient import Ingredient, IntermediateIngredient
from .symbol import SymbolType


class Equipment(Item):
    """Domain model representing equipment in recipe analysis,
    equipment items are tools or devices used in food preparation,
    with support for hierarchical organization (e.g., cookware > pots > stockpot)
    """
    def __init__(self,
                 name: str,
                 contents: Optional[Set[Any]] = None,
                 **kwargs):
        """Initialize equipment.
        
        Args:
            name: Name of the equipment
            contents: Set of ingredients stored in this equipment (for vessels)
            **kwargs Additional Symbol parameters
        """
        super().__init__(
            name=name,
            type=SymbolType.EQUIPMENT,
            **kwargs
        )
        self.contents = contents or set()

    # Predicate Methods
    def is_vessel(self) -> bool:
        """Check if this equipment is a vessel that can store ingredients.

        Returns:
            bool: True if equipment has VESSEL identity (or parent chain resolving to VESSEL)
        """
        return "VESSEL" in self.identities

    # Vessel Methods
    def get_contents(self) -> List[Any]:
        """Get list of contents in this vessel.

        Raises:
            ValueError: If the equipment is not a vessel

        Returns:
            List[Any]: List of ingredients and/or intermediate ingredients in vessel
        """
        if not self.is_vessel():
            raise ValueError(f"Equipment '{self.name}' is not a vessel and has no contents")
        return list(self.contents)

    def add_ingredient(self, ingredient: Any) -> None:
        """Add an ingredient to this equipment's contents (for vessels).
        
        Args:
            ingredient: Ingredient to add to contents
            
        Raises:
            ValueError: If this equipment is not a vessel
        """
        if not self.is_vessel():
            raise ValueError(f"Equipment '{self.name}' is not a vessel and cannot store ingredients")
        self.contents.add(ingredient)

    def combine_contents(self) -> None:
        """Combine all contents into one IntermediateIngredient

        Raises:
            ValueError: If this equipment is not a vessel
            ValueError: If this equipment is a vessel but has no contents to combine
        """
        if not self.is_vessel():
            raise ValueError(f"Equipment '{self.name}' is not a vessel and cannot combine contents")
        if not self.contents:
            raise ValueError(f"Vessel '{self.name}' has no contents to combine")
        
        combined_identities = set()
        combined_properties = {}
        
        for item in self.contents:
            combined_identities.update(item.identities)
            combined_properties.update(item.properties)

        name = "mixture"

        combined = IntermediateIngredient(
            name=name,
            source_ingredients=self.contents.copy(),
            vessel=self,
            identities=combined_identities,
            properties=combined_properties
        )

        self.contents.clear()
        self.contents.add(combined)

    def empty_contents(self) -> None:
        """Empty and return all ingredients from this equipment.
        
        Raises:
            ValueError: If this equipment is not a vessel
        """
        if not self.is_vessel():
            raise ValueError(f"Equipment '{self.name}' is not a vessel and cannot empty its contents")
        self.contents.clear()

    # String Representations
    def __str__(self) -> str:
        """Get string representation of the equipment.
        
        Returns:
            str: String representation
        """
        if self.is_vessel() and self.contents:
            return f"{self.name} (containing {len(self.contents)} items)"
        return self.name
        
    def __repr__(self) -> str:
        """Get detailed string representation of the equipment.
        
        Returns:
            str: Detailed string representation
        """
        return (f"Equipment(name='{self.name}', "
                f"is_vessel={self.is_vessel()}, "
                f"contents={len(self.contents)})")
       

class IntermediateEquipment(Equipment):
    """Represents equipment produced or modified by an instruction.

    Attributes:
        produced_by: Instruction that produces/modifies this equipment.
        source_equipment: Source equipment used to produce this.
        source_ingredients: Source ingredients used in the modification (if any).
    """
    def __init__(self,
                 name: str,
                 produced_by: Optional[Any] = None,
                 source_equipment: Optional[Set['Equipment']] = None,
                 source_ingredients: Optional[Set[Any]] = None,
                 **kwargs):
        """Initialize intermediate equipment.

        Args:
            name (str): Name of the intermediate equipment
            produced_by (Optional[Any]): Instruction that produces/modifies this equipment. Defaults to None.
            source_equipment (Optional[Set[Equipment]]): Set of source equipment used. Defaults to None.
            source_ingredients (Optional[Set[Any]]): Set of source ingredients used. Defaults to None.
            **kwargs Additional Item parameters
        """
        super().__init__(name=name, **kwargs)
        self.produced_by = produced_by
        self.source_equipment = source_equipment or set()
        self.source_ingredients = source_ingredients or set()

    # Mutator Methods
    def add_source_equipment(self, equipment: Equipment) -> None:
        """Add source equipment that contributes to this intermediate equipment.

        Args:
            equipment (Equipment): Equipment instance to add as a source
        """
        self.source_equipment.add(equipment)
    
    def remove_source_equipment(self, equipment: Equipment) -> None:
        """Remove source equipment.

        Args:
            equipment (Equipment): Equipment instance to remove from sources
        """
        self.source_equipment.discard(equipment)
    
    def add_source_ingredient(self, ingredient: Ingredient) -> None:
        """Add a source ingredient used in equipment modification.

        Args:
            ingredient (Ingredient): Ingredient instance to add as a source
        """
        self.source_ingredients.add(ingredient)
    
    def remove_source_ingredient(self, ingredient: Ingredient) -> None:
        """Remove a source ingredient.

        Args:
            ingredient (Ingredient): Ingredient instance to remove from sources.
        """
        self.source_ingredients.discard(ingredient)

    # String Representations
    def __str__(self) -> str:
        """Get string representation of the intermediate equipment.
        
        Returns:
            str: String representation showing name and source context
        """
        source_count = len(self.source_equipment) + len(self.source_ingredients)
        if source_count > 0:
            return f"{self.name} (from {source_count} sources)"
        return f"{self.name} (intermediate)"
    
    def __repr__(self) -> str:
        """Get detailed string representation of the intermediate equipment for debugging.
        
        Returns:
            str: Detailed representation with production context
        """
        produced_by_info = f"instruction_{self.produced_by.instruction_id}" if self.produced_by else None
        return (f"IntermediateEquipment(name='{self.name}', "
                f"type={self.type.value}, "
                f"produced_by={produced_by_info}, "
                f"source_equipment={len(self.source_equipment)}, "
                f"source_ingredients={len(self.source_ingredients)}, "
                f"is_vessel={self.is_vessel()}, "
                f"contents={len(self.contents)})")
