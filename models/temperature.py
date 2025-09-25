"""Defines classes for representing temperatures in recipes;
provides both absolute and relative temperature specifications with appropriate units.
"""

from typing import Optional

from models.measurement import Unit, Quantification


class Temperature(Quantification):
    """Abstract base class for temperature measurements."""
    pass


class TemperatureAbs(Temperature):
    """Absolute temperature with exact value."""
    
    def __init__(self, value: float, unit: Unit):
        """Initialize a TemperatureAbs instance.
        
        Args:
            value: Exact temperature value
            unit: Temperature unit
        """
        super().__init__(unit)
        self.value = value


class TemperatureRel(Temperature):
    """Relative temperature with a range or level."""
    
    def __init__(self, value_min: Optional[float] = None, value_max: Optional[float] = None, 
                 unit: Optional[Unit] = None, level: Optional[str] = None):
        """Initialize a TemperatureRel instance.
        
        Args:
            value_min: Minimum temperature value (optional)
            value_max: Maximum temperature value (optional)
            unit: Temperature unit (optional)
            level: Temperature level description (e.g., "low", "medium", "high")
        """
        super().__init__(unit)
        self.value_min = value_min
        self.value_max = value_max
        self.level = level
