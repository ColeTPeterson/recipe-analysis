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
        
        # DAG node properties (only used when symbol_type == ACTION)
        self._input_nodes: Set['Symbol'] = set()  # Items consumed by this action
        self._output_nodes: Set['Symbol'] = set()  # Items produced by this action
    
    @property
    def symbol_type(self) -> SymbolType:
        """Get the symbol type."""
        return self._symbol_type
    
    @symbol_type.setter
    def symbol_type(self, value: SymbolType) -> None:
        """Set the symbol type."""
        if not isinstance(value, SymbolType):
            raise TypeError("Symbol type must be a SymbolType enum")
        self._symbol_type = value
    
    @property
    def categories(self) -> Set[str]:
        """Get the categories set."""
        return self._categories.copy()
    
    @categories.setter
    def categories(self, value: Set[str]) -> None:
        """Set the categories."""
        if not isinstance(value, set):
            raise TypeError("Categories must be a set")
        self._categories = value
    
    @property
    def canonical_form(self) -> str:
        """Get the canonical form."""
        return self._canonical_form
    
    @canonical_form.setter
    def canonical_form(self, value: str) -> None:
        """Set the canonical form."""
        if not isinstance(value, str):
            raise TypeError("Canonical form must be a string")
        self._canonical_form = value
    
    @property
    def aliases(self) -> Set[str]:
        """Get the aliases set."""
        return self._aliases.copy()
    
    @aliases.setter
    def aliases(self, value: Set[str]) -> None:
        """Set the aliases."""
        if not isinstance(value, set):
            raise TypeError("Aliases must be a set")
        self._aliases = value
    
    @property
    def description(self) -> str:
        """Get the description."""
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        """Set the description."""
        if not isinstance(value, str):
            raise TypeError("Description must be a string")
        self._description = value
    
    # DAG node properties (for ACTION symbols)
    @property
    def input_nodes(self) -> Set['Symbol']:
        """Get input nodes (items consumed by this action)."""
        return self._input_nodes.copy()
    
    @property
    def output_nodes(self) -> Set['Symbol']:
        """Get output nodes (items produced by this action)."""
        return self._output_nodes.copy()
    
    # DAG node management methods (for ACTION symbols)
    def add_input_node(self, item: 'Symbol') -> None:
        """Add an input node (item consumed by this action)."""
        if self.symbol_type != SymbolType.ACTION:
            raise ValueError("Only ACTION symbols can have input/output nodes")
        from .item import Item
        if not isinstance(item, (Item, Symbol)):
            raise TypeError("Input node must be an Item or Symbol")
        self._input_nodes.add(item)
    
    def add_output_node(self, item: 'Symbol') -> None:
        """Add an output node (item produced by this action)."""
        if self.symbol_type != SymbolType.ACTION:
            raise ValueError("Only ACTION symbols can have input/output nodes")
        from .item import Item
        if not isinstance(item, (Item, Symbol)):
            raise TypeError("Output node must be an Item or Symbol")
        self._output_nodes.add(item)
    
    def remove_input_node(self, item: 'Symbol') -> None:
        """Remove an input node."""
        self._input_nodes.discard(item)
    
    def remove_output_node(self, item: 'Symbol') -> None:
        """Remove an output node."""
        self._output_nodes.discard(item)
    
    # Operator analysis methods (for ACTION symbols)
    def is_operator(self) -> bool:
        """Check if this symbol represents an operator (action)."""
        return self.symbol_type == SymbolType.ACTION
    
    def get_operator_arity(self) -> str:
        """Get the arity type of this operator based on its categories."""
        if not self.is_operator():
            return "not_operator"
        
        for category in self.categories:
            if category in ["COMBINATION"]:
                return "n-ary"                              # Multiple operands
            elif category in ["DIVISION", "SEPARATION"]:
                return "unary_multi_output"                 # One input, multiple outputs
            elif category in ["COOKING_METHOD", "PREPARATION_TASK", "TEMPERATURE_CHANGE"]:
                return "unary"                              # One input, one output
        
        return "unknown"
    
    def __hash__(self) -> int:
        """Hash method for using symbols in sets."""
        return hash((self.symbol_type, self.canonical_form))
    
    def __eq__(self, other) -> bool:
        """Equality comparison based on type and canonical form."""
        if not isinstance(other, Symbol):
            return False
        return (self.symbol_type == other.symbol_type and 
                self.canonical_form == other.canonical_form)
