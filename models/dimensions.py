from abc import ABC
from typing import List
from .symbol import Symbol

class Dimensions(ABC):
    """Abstract base for physical dimensions.

    Attributes:
        unit (Symbol): Unit of length (Symbol.type=UNIT, category from UnitCategory.LENGTH).
    """
    def __init__(self, unit: Symbol):
        self.unit = unit


class DimensionsAbs(Dimensions):
    """Absolute physical dimensions.

    Attributes:
        values (List[float]): List of exact dimension values (1 to 3 values).
        unit (Symbol): Unit of length.
    """
    def __init__(self, unit: Symbol, values: List[float]):
        super().__init__(unit)
        self.values = values


class DimensionsRel(Dimensions):
    """Relative physical dimensions (range).

    Attributes:
        values_min (List[float]): List of minimum dimension values (1 to 3 values).
        values_max (List[float]): List of maximum dimension values (1 to 3 values).
        unit (Symbol): Unit of length.
    """
    def __init__(self, unit: Symbol, values_min: List[float], values_max: List[float]):
        super().__init__(unit)
        self.values_min = values_min
        self.values_max = values_max
