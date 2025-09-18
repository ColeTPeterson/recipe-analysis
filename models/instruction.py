"""Defines classes for representing recipe instructions and how ingredients
and equipment are used within those instructions; models the relationships between
actions, ingredients, equipment, and produced items.
"""

from enum import Enum
from typing import Optional, Dict, Set

from .symbol import SymbolType, Symbol
from .item import Item
from .equipment import Equipment
from .ingredient import Ingredient
from .temperature import Temperature
from .duration import Duration


class ActionArity(Enum):
    """Represents the arity of actions - how many inputs/outputs they typically have."""
    UNARY = "unary"           # 1 input -> 1 output (e.g., chop, heat)
    BINARY = "binary"         # 2 inputs -> 1 output (e.g., mix, combine)
    TERNARY = "ternary"       # 3 inputs -> 1 output (e.g., complex combinations)
    N_ARY = "n_ary"           # n inputs -> 1 output (e.g., assemble)
    SPLITTING = "splitting"   # 1 input -> n outputs (e.g., separate, divide)
    VARIABLE = "variable"     # variable inputs/outputs


class Action(Symbol):
    """Represents an action used in recipe analysis;
    Operations that transform ingredients and equipment

    Args:
        Symbol (_type_): _description_

    Attributes:
        arity Optional[ActionArity]: The input/output behavior of this action
    """
    def __init__(
        self,
        name: str,
        arity: Optional[ActionArity] = None,
        **kwargs
    ):
        """Initialize an action.

        Args:
            name (str): Name of the action
            arity (Optional[ActionArity]): Input/output behavior of the action. Defaults to None.
            **kwargs Additional Symbol parameters
        """
        super().__init__(
            type=SymbolType.ACTION,
            name=name,
            **kwargs
        )
        self.arity = arity
    
    # String Representations
    def __str__(self) -> str:
        """Get string representation of the action.
        
        Returns:
            str: Action name
        """
        return self.name
        
    def __repr__(self) -> str:
        """Get detailed string representation of the action for debugging.
        
        Returns:
            str: Detailed representation with arity info
        """
        return (f"Action(name='{self.name}', "
                f"type={self.type.value}, "
                f"arity={self.arity}, "
                f"entity_id={self.entity_id}, "
                f"identities={len(self.identities)}, "
                f"properties={len(self.properties)})")


class IngredientUsage:
    """Represents how an ingredient is used in a specific instruction.

    Attributes:
        count (Optional[int]): The number of units of the ingredient used.
        proportion (Optional[float]): The proportion of the ingredient used (0-1).
        quantity_value (Optional[float]): The numeric quantity value.
        quantity_unit (Optional[Symbol]): The unit symbol for the quantity.
        is_optional (bool): Whether this ingredient is optional.
    """
    def __init__(self,
                 count: Optional[int] = None,
                 proportion: Optional[float] = None,
                 quantity_value: Optional[float] = None,
                 quantity_unit: Optional[Symbol] = None,
                 is_optional: bool = False):
        self.count = count
        self.proportion = proportion
        self.quantity_value = quantity_value
        self.quantity_unit = quantity_unit
        self.is_optional = is_optional


class EquipmentUsage:
    """Represents how equipment is used in a specific instruction.

    Attributes:
        count (Optional[int]): The number of units of the equipment used.
    """
    def __init__(self, 
                 count: Optional[int] = None):
        self.count = count


class Instruction:
    """Represents a single step in a recipe.

    Attributes:
        instruction_id (int): Unique identifier for this instruction.
        action (Action): The action performed in this instruction.
        ingredients (Dict[Ingredient, IngredientUsage]): Mapping of ingredients to their usage context.
        equipment (Dict[Equipment, EquipmentUsage]): Mapping of equipment to their usage context.
        produces (Optional[Item]): The item produced by this instruction.
        temperature (Optional[Temperature]): The temperature required to perform this instruction.
        duration (Optional[Duration]): The duration of this instruction.
        sequence_order (Optional[float]): The order of this instruction in the recipe.
        description (Optional[str]): Text description of this instruction.
        prerequisites (Optional[Set[Instruction]]): Instructions that must be completed before this one.
        next (Optional[Set[Instruction]]): Instructions that follow this one.
    """
    def __init__(self,
                 instruction_id: int,
                 action: Action,
                 ingredients: Optional[Dict[Ingredient, IngredientUsage]] = None,
                 equipment: Optional[Dict[Equipment, EquipmentUsage]] = None,
                 produces: Optional[Item] = None,
                 temperature: Optional[Temperature] = None,
                 duration: Optional[Duration] = None,
                 sequence_order: Optional[float] = None,
                 description: Optional[str] = None,
                 prerequisites: Optional[Set['Instruction']] = None,
                 next: Optional[Set['Instruction']] = None):
        self.instruction_id = instruction_id
        self.action = action
        self.ingredients = ingredients or {}
        self.equipment = equipment or {}
        self.produces = produces
        self.temperature = temperature
        self.duration = duration
        self.sequence_order = sequence_order
        self.description = description
        self.prerequisites = prerequisites or set()
        self.next = next or set()
    
    # Accessor Methods
    def get_input_ingredients(self) -> Dict[Ingredient, IngredientUsage]:
        """Get all ingredients used in this instruction.

        Returns:
            Dict[Ingredient, IngredientUsage]: Copy of ingredients mapping
        """
        return self.ingredients.copy()
    
    def get_equipment(self) -> Dict[Equipment, EquipmentUsage]:
        """Get all equipment used in this instruction.

        Returns:
            Dict[Equipment, EquipmentUsage]: Copy of equipment mapping
        """
        return self.equipment.copy()
    
    def get_input_items(self) -> Set[Item]:
        """Get all input items (ingredients + equipment) for this instruction."""
        input_items = set(self.ingredients.keys())
        input_items.update(self.equipment.keys())
        return input_items
    
    def get_output_items(self) -> Set[Item]:
        """Get all output items produced by this instruction."""
        if self.produces:
            return {self.produces}
        return set()
    
    def get_consumed_items(self) -> Set[Item]:
        """Get items that are consumed (ingredients only, equipment is reused)."""
        return set(self.ingredients.keys())
    
    # Mutator Methods
    def add_ingredient(self, ingredient: Ingredient, usage: IngredientUsage) -> None:
        """Add an ingredient usage to this instruction."""
        self.ingredients[ingredient] = usage
    
    def add_equipment(self, equipment: Equipment, usage: EquipmentUsage) -> None:
        """Add an equipment usage to this instruction."""
        self.equipment[equipment] = usage
    
    def add_prerequisite(self, instruction: 'Instruction') -> None:
        """Add a prerequisite instruction."""
        self.prerequisites.add(instruction)
        instruction.next.add(self)
    
    def remove_prerequisite(self, instruction: 'Instruction') -> None:
        """Remove a prerequisite instruction."""
        self.prerequisites.discard(instruction)
        instruction.next.discard(self)

    # DAG Analysis Methods
    def is_root_instruction(self) -> bool:
        """Check if this instruction has no prerequisites (is a root node)."""
        return len(self.prerequisites) == 0
    
    def is_leaf_instruction(self) -> bool:
        """Check if this instruction has no following instructions (is a leaf node)."""
        return len(self.next) == 0
    
    def get_all_prerequisites(self) -> Set['Instruction']:
        """Get all instructions that must be completed before this one (transitive closure)."""
        visited = set()
        to_visit = list(self.prerequisites)
        
        while to_visit:
            current = to_visit.pop()
            if current not in visited:
                visited.add(current)
                to_visit.extend(current.prerequisites)
        
        return visited
    
    def get_all_dependents(self) -> Set['Instruction']:
        """Get all instructions that depend on this one (transitive closure)."""
        visited = set()
        to_visit = list(self.next)
        
        while to_visit:
            current = to_visit.pop()
            if current not in visited:
                visited.add(current)
                to_visit.extend(current.next)
        
        return visited
    
    def has_cycle(self) -> bool:
        """Check if adding this instruction would create a cycle in the DAG."""
        return self in self.get_all_prerequisites()

    # String Representations
    def __str__(self) -> str:
        """Get string representation of the instruction."""
        return f"Instruction {self.instruction_id}: {self.action.name}"
    
    def __repr__(self) -> str:
        """Get detailed string representation of the instruction for debugging.
        
        Returns:
            str: Detailed representation with action and usage context
        """
        return (f"Instruction(id={self.instruction_id}, "
                f"action='{self.action.name}', "
                f"ingredients={len(self.ingredients)}, "
                f"equipment={len(self.equipment)}, "
                f"prerequisites={len(self.prerequisites)}, "
                f"next={len(self.next)}, "
                f"produces={self.produces.name if self.produces else None})")
