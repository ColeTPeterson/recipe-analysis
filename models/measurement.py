"""Defines classes for representing measurements in recipes,
supporting both absolute measurements and relative (range-based) measurements.
"""

from abc import ABC
from typing import Optional

from .symbol import SymbolType, Symbol


class Unit(Symbol):
    """Represents a unit of measurement used in recipe analysis.
    Units have canonical forms/aliases and dynamic properties.
    """
    def __init__(self, name: str, **kwargs):
        """Initialize a unit.

        Args:
            name (str): Name of the unit
            **kwargs: Additional Symbol parameters
        """
        super().__init__(
            type=SymbolType.UNIT,
            name=name,
            **kwargs
        )

    def __str__(self) -> str:
        """Get string representation of the unit.

        Returns:
            str: Unit name
        """
        return self.name
    
    def __repr__(self) -> str:
        """Get detailed string representation of the unit for debugging.
        
        Returns:
            str: Detailed representation with identities info
        """
        return (f"Unit(name='{self.name}', "
                f"entity_id={self.entity_id}, "
                f"identities={len(self.identities)}, "
                f"properties={len(self.properties)})")


class Quantification(ABC):
    """Abstract base class for all measurement types in recipes.
    
    All quantifications have at minimum a unit (which may be optional in some cases)
    and provide a get_unit method.
    """
    
    def __init__(self, unit: Optional[Symbol] = None):
        """Initialize a Quantification with a unit.
        
        Args:
            unit: Unit of measurement (can be None in some special cases)
        """
        self.unit = unit
    
    def get_unit(self) -> Optional[Symbol]:
        """Return the measurement unit.
        
        Returns:
            Optional[Symbol]: The unit used for this measurement
        """
        return self.unit


class Measurement(Quantification):
    """Abstract base class for measurements."""
    pass


class MeasurementAbs(Measurement):
    """Absolute measurement.

    Attributes:
        value (Optional[float]): Absolute value
    """
    def __init__(self, unit: Optional[Unit] = None, value: Optional[float] = None):
        """Initialize an absolute measurement.
        
        Args:
            unit: Unit of measurement (optional)
            value: Absolute value (optional)
        """
        super().__init__(unit)
        self.value = value


class MeasurementRel(Measurement):
    """Relative measurement (range).

    Attributes:
        value_min (Optional[float]): Minimum value
        value_max (Optional[float]): Maximum value
    """
    def __init__(self,
                 unit: Optional[Unit] = None,
                 value_min: Optional[float] = None,
                 value_max: Optional[float] = None):
        """Initialize a relative measurement.
        
        Args:
            unit: Unit of measurement (optional)
            value_min: Minimum value (optional)
            value_max: Maximum value (optional)
        """
        super().__init__(unit)
        self.value_min = value_min
        self.value_max = value_max
