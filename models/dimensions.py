"""Defines classes for representing physical dimensions in recipes,
supporting both absolute and relative dimensions with appropriate units.
"""

from typing import List

from models.measurement import Unit, Quantification


class Dimensions(Quantification):
    """Abstract base class for dimensional measurements."""
    pass


class DimensionsAbs(Dimensions):
    """Absolute dimensions with exact values."""
    
    def __init__(self, values: List[float], unit: Unit):
        """Initialize a DimensionsAbs instance.
        
        Args:
            values: List of dimension values (1-3 values for 1D, 2D, or 3D)
            unit: Length unit
        """
        super().__init__(unit)
        self.values = values


class DimensionsRel(Dimensions):
    """Relative dimensions with min/max ranges."""
    
    def __init__(self, values_min: List[float], values_max: List[float], unit: Unit):
        """Initialize a DimensionsRel instance.
        
        Args:
            values_min: List of minimum dimension values
            values_max: List of maximum dimension values
            unit: Length unit
        """
        super().__init__(unit)
        self.values_min = values_min
        self.values_max = values_max
