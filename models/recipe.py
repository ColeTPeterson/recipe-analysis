"""Defines the Recipe class that represents a complete recipe as a
directed acyclic graph (DAG) of actions and items. Provides methods to build,
validate, and analyze recipe structures.
"""

from typing import Set, List

from .instruction import Action, Instruction
from .item import Item


class Recipe:
    """Represents a recipe, a collection of instructions that form a directed acyclic graph (DAG).

    Attributes:
        recipe_id (int): The unique identifier for this recipe.
        title (str): The title of the recipe.
        root_instructions (Set[Instruction]): The set of root instructions in the DAG (no prerequisites).
        all_instructions (Set[Instruction]): The set of all instructions in the DAG.
    """
    def __init__(self, recipe_id: int, title: str):
        self._recipe_id = recipe_id
        self._title = title
        self._root_instructions = set()
        self._all_instructions = set()
        
        # DAG container properties
        self._action_nodes: Set['Action'] = set()  # All action nodes in the DAG
        self._item_nodes: Set['Item'] = set()      # All item nodes in the DAG
        
        # Build DAG from instructions
        self._build_dag_from_instructions()

    # Properties and Accessor Methods
    @property
    def recipe_id(self) -> int:
        """Get the recipe ID."""
        return self._recipe_id
    
    @property
    def title(self) -> str:
        """Get the recipe title."""
        return self._title
    
    @property
    def root_instructions(self) -> Set['Instruction']:
        """Get the set of root instructions."""
        return self._root_instructions.copy()
    
    @property
    def all_instructions(self) -> Set['Instruction']:
        """Get the set of all instructions."""
        return self._all_instructions.copy()
    
    @property
    def action_nodes(self) -> Set['Action']:
        """Get all action nodes in the DAG."""
        return self._action_nodes.copy()
    
    @property
    def item_nodes(self) -> Set['Item']:
        """Get all item nodes in the DAG."""
        return self._item_nodes.copy()
    
    # Mutator Methods
    @recipe_id.setter
    def recipe_id(self, value: int) -> None:
        """Set the recipe ID."""
        if not isinstance(value, int):
            raise TypeError("Recipe ID must be an integer")
        self._recipe_id = value
    
    @title.setter
    def title(self, value: str) -> None:
        """Set the recipe title."""
        if not isinstance(value, str):
            raise TypeError("Title must be a string")
        self._title = value
    
    @root_instructions.setter
    def root_instructions(self, value: Set['Instruction']) -> None:
        """Set the root instructions."""
        if not isinstance(value, set):
            raise TypeError("Root instructions must be a set")
        self._root_instructions = value
    
    @all_instructions.setter
    def all_instructions(self, value: Set['Instruction']) -> None:
        """Set all instructions."""
        if not isinstance(value, set):
            raise TypeError("All instructions must be a set")
        self._all_instructions = value

    # DAG management methods
    def add_instruction(self, instruction: 'Instruction') -> None:
        """Add an instruction to the recipe and update DAG."""
        self._all_instructions.add(instruction)
        if instruction.is_root_instruction():
            self._root_instructions.add(instruction)
        else:
            self._root_instructions.discard(instruction)
        
        # Update DAG nodes based on instruction structure
        self._action_nodes.add(instruction.action)
        
        # Add input items (ingredients and equipment) to DAG
        for item in instruction.get_input_items():
            self._item_nodes.add(item)
        
        # Add output items to DAG
        for item in instruction.get_output_items():
            self._item_nodes.add(item)
    
    def remove_instruction(self, instruction: 'Instruction') -> None:
        """Remove an instruction from the recipe and update DAG."""
        self._all_instructions.discard(instruction)
        self._root_instructions.discard(instruction)
        
        # Remove action from DAG if no other instructions use it
        action_still_used = any(
            inst.action == instruction.action 
            for inst in self._all_instructions 
            if inst != instruction
        )
        if not action_still_used:
            self._action_nodes.discard(instruction.action)
    
    def _build_dag_from_instructions(self) -> None:
        """Build the DAG structure from current instructions."""
        self._action_nodes.clear()
        self._item_nodes.clear()
        
        for instruction in self._all_instructions:
            # Add action node
            self._action_nodes.add(instruction.action)
            
            # Add input items
            for item in instruction.get_input_items():
                self._item_nodes.add(item)
            
            # Add output items
            for item in instruction.get_output_items():
                self._item_nodes.add(item)
    
    # Analysis Methods
    def get_input_items(self) -> Set['Item']:
        """Get items that are inputs to the recipe (not produced by any instruction)."""
        produced_items = set()
        for instruction in self._all_instructions:
            produced_items.update(instruction.get_output_items())
        
        consumed_items = set()
        for instruction in self._all_instructions:
            consumed_items.update(instruction.get_consumed_items())
        
        return consumed_items - produced_items
    
    def get_output_items(self) -> Set['Item']:
        """Get items that are final outputs of the recipe (produced but not consumed)."""
        produced_items = set()
        for instruction in self._all_instructions:
            produced_items.update(instruction.get_output_items())
        
        consumed_items = set()
        for instruction in self._all_instructions:
            consumed_items.update(instruction.get_consumed_items())
        
        return produced_items - consumed_items
    
    def get_intermediate_items(self) -> Set['Item']:
        """Get items that are both produced and consumed (intermediate results)."""
        produced_items = set()
        consumed_items = set()
        
        for instruction in self._all_instructions:
            produced_items.update(instruction.get_output_items())
            consumed_items.update(instruction.get_consumed_items())
        
        return produced_items & consumed_items
    
    def validate_dag_structure(self) -> bool:
        """Check that instruction dependencies form a DAG (no cycles).

        Returns:
            bool: True if DAG structure is valid, False otherwise
        """
        for instruction in self._all_instructions:
            if instruction.has_cycle():
                return False
        return True
        
    def get_topological_order(self) -> List['Instruction']:
        """Get instructions in topological order (dependencies before dependents)."""
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(instruction: 'Instruction') -> bool:
            if instruction in temp_visited:
                return False  # Cycle detected
            if instruction in visited:
                return True
            
            temp_visited.add(instruction)
            for prereq in instruction.prerequisites:
                if not visit(prereq):
                    return False
            temp_visited.remove(instruction)
            visited.add(instruction)
            result.append(instruction)
            return True
        
        for instruction in self._all_instructions:
            if instruction not in visited:
                if not visit(instruction):
                    return []  # Cycle detected, return empty list
        
        return result

    def __str__(self) -> str:
        """Get string representation of the recipe.
        
        Returns:
            str: String representation with title and instruction count
        """
        return f"Recipe: {self.title} ({len(self._all_instructions)} instructions)"

    def __repr__(self) -> str:
        """Get detailed string representation of the recipe for debugging.
        
        Returns:
            str: Detailed representation with DAG structure info
        """
        return (f"Recipe(id={self.recipe_id}, "
                f"title='{self.title}', "
                f"instructions={len(self._all_instructions)}, "
                f"root_instructions={len(self._root_instructions)}, "
                f"action_nodes={len(self._action_nodes)}, "
                f"item_nodes={len(self._item_nodes)})")
