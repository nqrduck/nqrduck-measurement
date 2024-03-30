"""Signal processing options."""
import sympy
from nqrduck_spectrometer.base_spectrometer_model import BaseSpectrometerModel
from nqrduck_spectrometer.pulseparameters import FunctionOption, GaussianFunction, CustomFunction, Function

# We implement the signal processing options as PulseParamterOptions because we can then easily use the automatic UI generation

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


class Apodization(BaseSpectrometerModel.PulseParameter):
    """Apodization parameter.
    
    This parameter is used to apply apodization functions to the signal.
    The apodization functions are used to reduce the noise in the signal.
    
    Attributes:
        APODIZATION_FUNCTIONS (str): The name of the apodization functions option.
    """
    APODIZATION_FUNCTIONS = "Apodization functions"

    def __init__(self):
        """Apodization parameter."""
        super().__init__("Apodization")

        self.add_option(
            FunctionOption(
                self.APODIZATION_FUNCTIONS,
                [FIDFunction(), GaussianFunction(), CustomFunction()],
            ),
        )


