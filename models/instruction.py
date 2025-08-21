"""Defines classes for representing recipe instructions and how ingredients
and equipment are used within those instructions; models the relationships between
actions, ingredients, equipment, and produced items.
"""

from typing import Optional, Dict, Set
from .duration import Duration
from .item import Equipment, Ingredient, Item
from .measurement import Measurement
from .symbol import Symbol
from .temperature import Temperature

class IngredientUsage:
    """Represents how an ingredient is used in a specific instruction.

    Attributes:
        count (Optional[int]): The number of units of the ingredient used.
        proportion (Optional[float]): The proportion of the ingredient used (0-1).
        measurement (Optional[Measurement]): The measurement of the ingredient.
    """
    def __init__(self,
                 count: Optional[int],
                 proportion: Optional[float],
                 measurement: Optional[Measurement]):
        self.count = count
        self.proportion = proportion
        self.measurement = measurement


class EquipmentUsage:
    """Represents how equipment is used in a specific instruction.

    Attributes:
        count (Optional[int]): The number of units of the equipment used.
    """
    def __init__(self, count: Optional[int]):
        self.count = count


class Instruction:
    """Represents a single step in a recipe.

    Attributes:
        instruction_id (int): Unique identifier for this instruction.
        action (Symbol): The action performed in this instruction.
        ingredients (Dict[Ingredient, IngredientUsage]): Mapping of ingredients to their usage context.
        equipment (Dict[Equipment, EquipmentUsage]): Mapping of equipment to their usage context.
        produces (Optional[Item]): The item produced by this instruction.
        temperature (Optional[Temperature]): The temperature required to perform this instruction.
        duration (Optional[Duration]): The duration of this instruction.
        prerequisites (Optional[Set[Instruction]]): Instructions that must be completed before this one.
        next (Optional[Set[Instruction]]): Instructions that follow this one.
    """
    def __init__(self,
                 instruction_id: int,
                 action: Symbol,
                 ingredients: Dict[Ingredient, IngredientUsage],
                 equipment: Dict[Equipment, EquipmentUsage],
                 produces: Optional[Item],
                 temperature: Optional[Temperature],
                 duration: Optional[Duration],
                 prerequisites: Optional[Set['Instruction']],
                 next: Optional[Set['Instruction']]):
        self.instruction_id = instruction_id
        self.action = action
        self.ingredients = ingredients
        self.equipment = equipment
        self.produces = produces
        self.temperature = temperature
        self.duration = duration
        self.prerequisites = prerequisites
        self.next = next
