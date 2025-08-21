"""Defines classes for representing temperatures in recipes;
provides both absolute and relative temperature specifications with appropriate units.
"""

from abc import ABC
from typing import Optional
from .symbol import Symbol

class Temperature(ABC):
    """Abstract base for temperatures.

    Attributes:
        unit (Optional[Symbol]): Unit of temperature (Symbol.type=UNIT, category from UnitCategory.TEMPERATURE).
                                 Optional based on subclass constraints.
    """
    def __init__(self, unit: Optional[Symbol]):
        self.unit = unit


class TemperatureAbs(Temperature):
    """Absolute temperature.

    Attributes:
        unit (Symbol): Unit of temperature.
        value (float): Absolute temperature value.
    """
    def __init__(self, unit: Symbol, value: float):
        super().__init__(unit)
        self.value = value


class TemperatureRel(Temperature):
    """Relative temperature (range or level).

    Attributes:
        unit (Optional[Symbol]): Unit of temperature. Optional if only level exists.
        value_min (Optional[float]): Minimum temperature value.
        value_max (Optional[float]): Maximum temperature value.
        level (Optional[Symbol]): Relative temperature level (Symbol.type=ITEM_PROPERTY, category from ItemPropertyCategory.RELATIVE_TEMPERATURE).
    """
    def __init__(self,
                 unit: Optional[Symbol] = None,
                 value_min: Optional[float] = None,
                 value_max: Optional[float] = None,
                 level: Optional[Symbol] = None):
        super().__init__(unit)
        self.value_min = value_min
        self.value_max = value_max
        self.level = level
