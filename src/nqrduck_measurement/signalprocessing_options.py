"""Signal processing options."""
import logging 
from decimal import Decimal
import numpy as np
import sympy
from nqrduck_spectrometer.measurement import Measurement
from nqrduck.helpers.functions import Function, GaussianFunction, CustomFunction
from nqrduck.helpers.formbuilder import DuckFormBuilder, DuckFormFunctionSelectionField

logger = logging.getLogger(__name__)

class FIDFunction(Function):
    """The exponetial FID function."""

    name = "FID"

    def __init__(self) -> None:
        """Exponential FID function."""
        expr = sympy.sympify("exp( -x / T2star )")
        super().__init__(expr)
        self.start_x = 0
        self.end_x = 30

        self.add_parameter(Function.Parameter("T2star (microseconds)", "T2star", 10))


class Apodization(DuckFormBuilder):
    """Apodization parameter.

    This parameter is used to apply apodization functions to the signal.
    The apodization functions are used to reduce the noise in the signal.
    """

    def __init__(self, measurement: Measurement, parent=None) -> None:
        """Apodization parameter."""
        super().__init__("Apodization", parent=parent)

        self.measurement = measurement
        functions = [
            FIDFunction(),
            GaussianFunction(),
            CustomFunction(),
        ]

        self.duration = (self.measurement.tdx[-1] - self.measurement.tdx[0]) * 1e-6

        function_selection_field = DuckFormFunctionSelectionField(
            text=None, tooltip=None, functions=functions, duration=self.duration, parent=parent, default_function=0
        )

        self.add_field(function_selection_field)

    def get_function(self) -> Function:
        """Get the selected function.

        Returns:
            Function: The selected function.
        """
        return self.get_values()[0]
    