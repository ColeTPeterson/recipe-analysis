from typing import Set, TYPE_CHECKING
from .instruction import Instruction

if TYPE_CHECKING:
    from .symbol import Symbol
    from .item import Item

class Recipe:
    """Represents a recipe, a collection of instructions that form a directed acyclic graph (DAG).

    Attributes:
        recipe_id (int): The unique identifier for this recipe.
        title (str): The title of the recipe.
        root_instructions (Set[Instruction]): The set of root instructions in the DAG (no prerequisites).
        all_instructions (Set[Instruction]): The set of all instructions in the DAG.
    """
    def __init__(self,
                 recipe_id: int,
                 title: str,
                 root_instructions: Set['Instruction'],
                 all_instructions: Set['Instruction']):
        self.recipe_id = recipe_id
        self.title = title
        self.root_instructions = root_instructions
        self.all_instructions = all_instructions
        
        # DAG container properties
        self._action_nodes: Set['Symbol'] = set()  # All action nodes in the DAG
        self._item_nodes: Set['Item'] = set()      # All item nodes in the DAG
    
    @property
    def recipe_id(self) -> int:
        """Get the recipe ID."""
        return self._recipe_id
    
    @recipe_id.setter
    def recipe_id(self, value: int) -> None:
        """Set the recipe ID."""
        if not isinstance(value, int):
            raise TypeError("Recipe ID must be an integer")
        self._recipe_id = value
    
    @property
    def title(self) -> str:
        """Get the recipe title."""
        return self._title
    
    @title.setter
    def title(self, value: str) -> None:
        """Set the recipe title."""
        if not isinstance(value, str):
            raise TypeError("Title must be a string")
        self._title = value
    
    @property
    def root_instructions(self) -> Set['Instruction']:
        """Get the set of root instructions."""
        return self._root_instructions.copy()
    
    @root_instructions.setter
    def root_instructions(self, value: Set['Instruction']) -> None:
        """Set the root instructions."""
        if not isinstance(value, set):
            raise TypeError("Root instructions must be a set")
        self._root_instructions = value
    
    @property
    def all_instructions(self) -> Set['Instruction']:
        """Get the set of all instructions."""
        return self._all_instructions.copy()
    
    @all_instructions.setter
    def all_instructions(self, value: Set['Instruction']) -> None:
        """Set all instructions."""
        if not isinstance(value, set):
            raise TypeError("All instructions must be a set")
        self._all_instructions = value
    
    # DAG properties
    @property
    def action_nodes(self) -> Set['Symbol']:
        """Get all action nodes in the DAG."""
        return self._action_nodes.copy()
    
    @property
    def item_nodes(self) -> Set['Item']:
        """Get all item nodes in the DAG."""
        return self._item_nodes.copy()
    
    # DAG management methods
    def add_action_node(self, action: 'Symbol') -> None:
        """Add an action node to the DAG."""
        if not action.is_operator():
            raise ValueError("Only ACTION symbols can be added as action nodes")
        self._action_nodes.add(action)
    
    def add_item_node(self, item: 'Item') -> None:
        """Add an item node to the DAG."""
        from .item import Item
        if not isinstance(item, Item):
            raise TypeError("Only Item instances can be added as item nodes")
        self._item_nodes.add(item)
    
    def remove_action_node(self, action: 'Symbol') -> None:
        """Remove an action node from the DAG."""
        self._action_nodes.discard(action)
    
    def remove_item_node(self, item: 'Item') -> None:
        """Remove an item node from the DAG."""
        self._item_nodes.discard(item)
    
    def get_root_action_nodes(self) -> Set['Symbol']:
        """Get action nodes that have no input items (recipe entry points)."""
        return {action for action in self._action_nodes if len(action.input_nodes) == 0}
    
    def get_leaf_action_nodes(self) -> Set['Symbol']:
        """Get action nodes that have no output items (recipe end points)."""
        return {action for action in self._action_nodes if len(action.output_nodes) == 0}
    
    def get_input_items(self) -> Set['Item']:
        """Get items that are inputs to the recipe (not produced by any action)."""
        return {item for item in self._item_nodes if item.is_input_operand()}
    
    def get_output_items(self) -> Set['Item']:
        """Get items that are outputs of the recipe (not consumed by any action)."""
        return {item for item in self._item_nodes if item.is_output_operand()}
    
    def validate_dag_structure(self) -> bool:
        """Validate that the action/item nodes form a valid DAG."""
        # Check that all action input/output nodes are in item_nodes
        for action in self._action_nodes:
            for input_item in action.input_nodes:
                if input_item not in self._item_nodes:
                    return False
            for output_item in action.output_nodes:
                if output_item not in self._item_nodes:
                    return False
        
        # Check that all item consuming/producing actions are in action_nodes
        for item in self._item_nodes:
            for action in item.consuming_actions:
                if action not in self._action_nodes:
                    return False
            for action in item.producing_actions:
                if action not in self._action_nodes:
                    return False
        
        return True
