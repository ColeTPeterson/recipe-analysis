from abc import ABC
from .symbol import Symbol

class Duration(ABC):
    """Abstract base for durations.

    Attributes:
        unit (Symbol): Unit of time (Symbol.type=UNIT, category from UnitCategory.TIME).
    """
    def __init__(self, unit: Symbol):
        self.unit = unit


class DurationAbs(Duration):
    """Absolute duration.

    Attributes:
        value (float): Absolute duration value.
        unit (Symbol): Unit of time.
    """
    def __init__(self, unit: Symbol,  value: float):
        super().__init__(unit)
        self.value = value


class DurationRel(Duration):
    """Relative duration (range).

    Attributes:
        value_min (float): Minimum duration value.
        value_max (float): Maximum duration value.
        unit (Symbol): Unit of time.
    """
    def __init__(self, unit: Symbol, value_min: float, value_max: float):
        super().__init__(unit)
        self.value_min = value_min
        self.value_max = value_max
