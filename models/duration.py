"""Defines classes for representing durations in recipes,
supporting both absolute durations and relative (range-based) durations.
"""

from models.measurement import Unit, Quantification


class Duration(Quantification):
    """Abstract base class for duration measurements."""
    pass


class DurationAbs(Duration):
    """Absolute duration with exact value."""
    
    def __init__(self, value: float, unit: Unit):
        """Initialize a DurationAbs instance.
        
        Args:
            value: Exact duration value
            unit: Unit of time measurement
        """
        super().__init__(unit)
        self.value = value


class DurationRel(Duration):
    """Relative duration with min/max range."""
    
    def __init__(self, value_min: float, value_max: float, unit: Unit):
        """Initialize a DurationRel instance.
        
        Args:
            value_min: Minimum duration value
            value_max: Maximum duration value
            unit: Unit of time measurement
        """
        super().__init__(unit)
        self.value_min = value_min
        self.value_max = value_max
