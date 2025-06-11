from abc import ABC
from typing import Set, Optional
from .symbol import Symbol
from .dimensions import Dimensions
from .measurement import Measurement
from .instruction import Instruction

class Item(ABC):
    """Abstract class representing an item in a recipe (ingredient/equipment).

    Attributes:
        name (str): The name of the item.
        identity (Set[Symbol]): A set of symbols representing the identity of an item.
        state (Optional[Set[Symbol]]): A set of symbols representing the state of the item.
        preparation (Optional[Set[Symbol]]): A set of symbols representing the states an item can be prepared.
        size (Optional[Symbol]): A symbol representing the relative physical size of the item.
        dimensions (Optional[Dimensions]): The physical dimensions of an item.
    """
    def __init__(self,
                 name: str,
                 identity: Set[Symbol],
                 state: Optional[Set[Symbol]],
                 preparation: Optional[Set[Symbol]],
                 size: Optional[Symbol],
                 dimensions: Optional[Dimensions]):
        self.name = name
        self.identity = identity
        self.state = state
        self.preparation = preparation
        self.size = size
        self.dimensions = dimensions


class Ingredient(Item):
    """Represents an ingredient in the recipe.

    Attributes:
        name (str): The name of ingredient.
        identity (Set[Symbol]): A set of symbols of descriptive terms relating to the ingredient's identity.
        state (Optional[Set[Symbol]]): A set of symbols representing the state of the ingredient.
        preparation (Optional[Set[Symbol]]): A set of symbols representing the states an ingredient can be prepared.
        size (Optional[Symbol]): A symbol representing the relative physical size of the ingredients.
        dimensions (Optional[Dimensions]): The physical dimensions of an ingredient.
        ingredient_id (int): Unique identifier for this ingredient.
        parent_id (Optional[int]): The ID of the parent ingredient.
        cut_style (Optional[Symbol]): A symbol representing the style of cut of the ingredient.
        measurement (Optional[Measurement]): The measurement for an ingredient.
        is_category (bool): Marks whether the ingredient is categorical (e.g. 'cheese': {'cheddar', 'swiss', ...})
        is_optional (bool): Marks whether the ingredient is not explicitly required.
    """
    def __init__(self,
                 name: str,
                 identity: Set[Symbol],
                 state: Optional[Set[Symbol]],
                 preparation: Optional[Set[Symbol]],
                 size: Optional[Symbol],
                 dimensions: Optional[Dimensions],
                 ingredient_id: int,
                 parent_id: Optional[int],
                 cut_style: Optional[Symbol],
                 measurement: Optional[Measurement],
                 is_category: bool,
                 is_optional: bool):
        super().__init__(name, identity, state, preparation, size, dimensions)
        self.ingredient_id = ingredient_id
        self.parent_id = parent_id
        self.cut_style = cut_style
        self.measurement = measurement
        self.is_category = is_category
        self.is_optional = is_optional


class IntermediateIngredient(Item):
    """Represents an ingredient produced by an instruction.

    Attributes:
        name (str): The name of the product.
        identity (Set[Symbol]): Symbols defining the product's identity.
        state (Optional[Set[Symbol]]): Symbols defining the product's current state.
        preparation (Optional[Set[Symbol]]): Symbols defining preparation styles for the product.
        size (Optional[Symbol]): Symbol representing the product's relative size.
        dimensions (Optional[Dimensions]): Physical dimensions of the product.
        produced_by (Instruction): Instruction that produces this ingredient.
        source_ingredients (Set['Ingredient']): Source ingredients used.
        description (str): Textual description of this intermediate ingredient.
    """
    def __init__(self,
                 name: str,
                 identity: Set[Symbol],
                 state: Optional[Set[Symbol]],
                 preparation: Optional[Set[Symbol]],
                 size: Optional[Symbol],
                 dimensions: Optional[Dimensions],
                 produced_by: Instruction,
                 source_ingredients: Set['Ingredient'],
                 description: str):
        super().__init__(name, identity, state, preparation, size, dimensions)
        self.produced_by = produced_by
        self.source_ingredients = source_ingredients
        self.description = description


class Equipment(Item):
    """Represents a piece of equipment.

    Attributes:
        name (str): The name of the equipment.
        identity (Set[Symbol]): Symbols defining the equipment's identity.
        state (Optional[Set[Symbol]]): Symbols defining the equipment's current state.
        preparation (Optional[Set[Symbol]]): Symbols defining preparation styles for the equipment.
        size (Optional[Symbol]): Symbol representing the equipment's relative size.
        dimensions (Optional[Dimensions]): Physical dimensions of the equipment.
        equipment_id (int): Unique identifier for this equipment.
    """
    def __init__(self,
                 name: str,
                 identity: Set[Symbol],
                 state: Optional[Set[Symbol]],
                 preparation: Optional[Set[Symbol]],
                 size: Optional[Symbol],
                 dimensions: Optional[Dimensions],
                 equipment_id: int):
        super().__init__(name, identity, state, preparation, size, dimensions)
        self.equipment_id = equipment_id


class IntermediateEquipment(Item):
    """Represents equipment produced or modified by an instruction.

    Attributes:
        name (str): The name of the intermediate equipment.
        identity (Set[Symbol]): Symbols defining its identity.
        state (Optional[Set[Symbol]]): Symbols defining its current state.
        preparation (Optional[Set[Symbol]]): Symbols defining its preparation.
        size (Optional[Symbol]): Symbol representing its relative size.
        dimensions (Optional[Dimensions]): Physical dimensions.
        produced_by (Instruction): Instruction that produces/modifies this equipment.
        source_equipment (Set['Equipment']): Source equipment used.
        source_ingredients (Set['Ingredient']): Source ingredients used (if any).
        description (str): Textual description of this intermediate equipment.
    """
    def __init__(self,
                 name: str,
                 identity: Set[Symbol],
                 state: Optional[Set[Symbol]],
                 preparation: Optional[Set[Symbol]],
                 size: Optional[Symbol],
                 dimensions: Optional[Dimensions],
                 produced_by: Instruction,
                 source_equipment: Set['Equipment'],
                 source_ingredients: Set['Ingredient'],
                 description: str):
        super().__init__(name, identity, state, preparation, size, dimensions)
        self.produced_by = produced_by
        self.source_equipment = source_equipment
        self.source_ingredients = source_ingredients
        self.description = description
