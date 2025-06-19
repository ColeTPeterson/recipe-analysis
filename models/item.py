from abc import ABC
from typing import Set, Optional, TYPE_CHECKING
from .symbol import Symbol
from .dimensions import Dimensions
from .measurement import Measurement

if TYPE_CHECKING:
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
        
        # DAG node properties (for operand nodes)
        self._consuming_actions: Set[Symbol] = set()  # Actions that consume this item
        self._producing_actions: Set[Symbol] = set()  # Actions that produce this item
    
    @property
    def name(self) -> str:
        """Get the item name."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Set the item name."""
        if not isinstance(value, str):
            raise TypeError("Name must be a string")
        self._name = value
    
    @property
    def identity(self) -> Set[Symbol]:
        """Get the identity symbols."""
        return self._identity.copy()
    
    @identity.setter
    def identity(self, value: Set[Symbol]) -> None:
        """Set the identity symbols."""
        if not isinstance(value, set):
            raise TypeError("Identity must be a set")
        self._identity = value
    
    @property
    def state(self) -> Optional[Set[Symbol]]:
        """Get the state symbols."""
        return self._state.copy() if self._state else None
    
    @state.setter
    def state(self, value: Optional[Set[Symbol]]) -> None:
        """Set the state symbols."""
        if value is not None and not isinstance(value, set):
            raise TypeError("State must be a set or None")
        self._state = value
    
    @property
    def preparation(self) -> Optional[Set[Symbol]]:
        """Get the preparation symbols."""
        return self._preparation.copy() if self._preparation else None
    
    @preparation.setter
    def preparation(self, value: Optional[Set[Symbol]]) -> None:
        """Set the preparation symbols."""
        if value is not None and not isinstance(value, set):
            raise TypeError("Preparation must be a set or None")
        self._preparation = value
    
    @property
    def size(self) -> Optional[Symbol]:
        """Get the size symbol."""
        return self._size
    
    @size.setter
    def size(self, value: Optional[Symbol]) -> None:
        """Set the size symbol."""
        if value is not None and not isinstance(value, Symbol):
            raise TypeError("Size must be a Symbol or None")
        self._size = value
    
    @property
    def dimensions(self) -> Optional[Dimensions]:
        """Get the dimensions."""
        return self._dimensions
    
    @dimensions.setter
    def dimensions(self, value: Optional[Dimensions]) -> None:
        """Set the dimensions."""
        if value is not None and not hasattr(value, '__class__'):
            raise TypeError("Dimensions must be a Dimensions instance or None")
        self._dimensions = value
    
    # DAG node properties (for operand nodes)
    @property
    def consuming_actions(self) -> Set[Symbol]:
        """Get actions that consume this item as input."""
        return self._consuming_actions.copy()
    
    @property
    def producing_actions(self) -> Set[Symbol]:
        """Get actions that produce this item as output."""
        return self._producing_actions.copy()
    
    # DAG node management methods
    def add_consuming_action(self, action: Symbol) -> None:
        """Add an action that consumes this item."""
        if not action.is_operator():
            raise ValueError("Only ACTION symbols can consume items")
        self._consuming_actions.add(action)
        action.add_input_node(self)
    
    def add_producing_action(self, action: Symbol) -> None:
        """Add an action that produces this item."""
        if not action.is_operator():
            raise ValueError("Only ACTION symbols can produce items")
        self._producing_actions.add(action)
        action.add_output_node(self)
    
    def remove_consuming_action(self, action: Symbol) -> None:
        """Remove an action that consumes this item."""
        self._consuming_actions.discard(action)
        action.remove_input_node(self)
    
    def remove_producing_action(self, action: Symbol) -> None:
        """Remove an action that produces this item."""
        self._producing_actions.discard(action)
        action.remove_output_node(self)
    
    # Operand analysis methods
    def is_operand(self) -> bool:
        """Check if this item serves as an operand (has consuming or producing actions)."""
        return len(self._consuming_actions) > 0 or len(self._producing_actions) > 0
    
    def is_input_operand(self) -> bool:
        """Check if this item is an input operand (no producing actions)."""
        return len(self._producing_actions) == 0 and len(self._consuming_actions) > 0
    
    def is_output_operand(self) -> bool:
        """Check if this item is an output operand (no consuming actions)."""
        return len(self._consuming_actions) == 0 and len(self._producing_actions) > 0
    
    def is_intermediate_operand(self) -> bool:
        """Check if this item is intermediate (both produced and consumed)."""
        return len(self._consuming_actions) > 0 and len(self._producing_actions) > 0
    
    def __hash__(self) -> int:
        """Hash method for using items in sets."""
        return hash(self.name)
    
    def __eq__(self, other) -> bool:
        """Equality comparison based on name."""
        if not isinstance(other, Item):
            return False
        return self.name == other.name


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
                 produced_by: 'Instruction',
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
                 produced_by: 'Instruction',
                 source_equipment: Set['Equipment'],
                 source_ingredients: Set['Ingredient'],
                 description: str):
        super().__init__(name, identity, state, preparation, size, dimensions)
        self.produced_by = produced_by
        self.source_equipment = source_equipment
        self.source_ingredients = source_ingredients
        self.description = description
