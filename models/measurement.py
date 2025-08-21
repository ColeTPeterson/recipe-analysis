"""Defines classes for representing measurements in recipes,
supporting both absolute measurements and relative (range-based) measurements.
"""

from abc import ABC
from typing import Optional
from .symbol import Symbol

class Measurement(ABC):
    """Abstract base for measurements.

    Attributes:
        unit (Optional[Symbol]): Unit of measurement (Symbol.type=UNIT).
                                 Optional if only value exists (Abs) or if only unit exists (Rel)
                                 as per diagram note, but class boxes imply required for subclasses.
    """
    def __init__(self, unit: Optional[Symbol]):
        self.unit = unit


class MeasurementAbs(Measurement):
    """Absolute measurement.

    Attributes:
        unit (Optional[Symbol]): Unit of measurement. Optional if only value exists.
        value (Optional[float]): Absolute value. Optional if only unit exists.
    """
    def __init__(self, unit: Optional[Symbol] = None, value: Optional[float] = None):
        super().__init__(unit)
        self.value = value


class MeasurementRel(Measurement):
    """Relative measurement (range).

    Attributes:
        value_min (Optional[float]): Minimum value. Optional if only unit exists.
        value_max (Optional[float]): Maximum value. Optional if only unit exists.
        unit (Optional[Symbol]): Unit of measurement. Optional if only min/max values exist.
    """
    def __init__(self,
                 unit: Optional[Symbol] = None,
                 value_min: Optional[float] = None,
                 value_max: Optional[float] = None):
        super().__init__(unit)
        self.value_min = value_min
        self.value_max = value_max
