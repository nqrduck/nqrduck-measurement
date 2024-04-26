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

        self.duration = Decimal((measurement.tdx[-1] - measurement.tdx[0]) * 1e-6)

        function_selection_field = DuckFormFunctionSelectionField(
            False, False, functions, self.duration, parent=parent, default_function=0
        )

        self.add_field(function_selection_field)

    def get_function(self) -> Function:
        """Get the selected function.

        Returns:
            Function: The selected function.
        """
        return self.get_values()[0]
    
    def apodization(self, function : Function) -> None:
        """Apply the apodization function to the measurement the object has been created to.

        Args:
            function (Function): The apodization function.

        Returns:
            Measurement: The apodized measurement.
        """

        # Get the y data weights from the function
        resolution = (
            self.measurement.tdx[1]
            - self.measurement.tdx[0]
        ) * 1e-6

        logger.debug("Resolution: %s", resolution)
        logger.debug("Resolution (Dec): %s", Decimal(resolution))

        y_weight = function.get_pulse_amplitude(self.duration, Decimal(resolution))
        # Append the last value to the end of the array
        y_weight = np.append(y_weight, y_weight[-1])

        tdy_measurement = self.measurement.tdy * y_weight

        apodized_measurement = Measurement(
            self.measurement.tdx,
            tdy_measurement,
            target_frequency=self.measurement.target_frequency,
            IF_frequency=self.measurement.IF_frequency,
        )

        return apodized_measurement
