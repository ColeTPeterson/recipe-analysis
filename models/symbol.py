from enum import Enum
from typing import Set

class SymbolType(Enum):
    """Enumeration of symbol types used to classify symbolic descriptors."""
    ACTION = "ACTION"
    EQUIPMENT_IDENTITY = "EQUIPMENT_IDENTITY"
    INGREDIENT_IDENTITY = "INGREDIENT_IDENTITY"
    ITEM_PROPERTY = "ITEM_PROPERTY"
    UNIT = "UNIT"


class Symbol:
    """Represents a recognized term (unit, action, properties, identities, etc.)
    used as a symbolic descriptor in recipes.

    Attributes:
        symbol_type (SymbolType): The type of the symbol (e.g. ACTION, UNIT).
        categories (Set[str]): A set of hierarchical categories the symbol belongs to.
        canonical_form (str): The canonical name of a symbol.
        aliases (Set[str]): Alternative names or aliases for the symbol.
        description (str): A textual description of the symbol.
    """
    def __init__(self,
                 symbol_type: SymbolType,
                 categories: Set[str],
                 canonical_form: str,
                 aliases: Set[str],
                 description: str):
        self.symbol_type = symbol_type
        self.categories = categories
        self.canonical_form = canonical_form
        self.aliases = aliases
        self.description = description
