from typing import Set
from .instruction import Instruction

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
