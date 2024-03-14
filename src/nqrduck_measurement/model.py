import logging
from PyQt6.QtCore import pyqtSignal
from nqrduck_spectrometer.measurement import Measurement
from nqrduck.module.module_model import ModuleModel
from nqrduck.helpers.validators import DuckFloatValidator, DuckIntValidator

logger = logging.getLogger(__name__)

class MeasurementModel(ModuleModel):

    FILE_EXTENSION = "meas"
    # This constants are used to determine which view is currently displayed.
    FFT_VIEW = "fft"
    TIME_VIEW = "time"

    displayed_measurement_changed = pyqtSignal(Measurement)
    measurements_changed = pyqtSignal(list)
    view_mode_changed = pyqtSignal(str)

    measurement_frequency_changed = pyqtSignal(float)
    averages_changed = pyqtSignal(int)

    def __init__(self, module) -> None:
        super().__init__(module)
        self.view_mode = self.TIME_VIEW
        self.measurements = []
        self._displayed_measurement = None

        self.validator_measurement_frequency = DuckFloatValidator(self, min_value=20.0, max_value=1000.0)
        self.validator_averages = DuckIntValidator(self, min_value=1, max_value=1e6)

        self.measurement_frequency = 100.0 # MHz
        self.averages = 1

    @property
    def view_mode(self):
        """View mode of the measurement view.
        Can be either "time" or "fft"."""
        return self._view_mode
    
    @view_mode.setter
    def view_mode(self, value : str):
        self._view_mode = value
        self.view_mode_changed.emit(value)

    @property
    def measurements(self):
        """List of measurements."""
        return self._measurements
    
    @measurements.setter
    def measurements(self, value : list[Measurement]):
        self._measurements = value
        self.measurements_changed.emit(value)
    
    def add_measurement(self, measurement : Measurement):
        """Add a measurement to the list of measurements."""
        self.measurements.append(measurement)
        self.measurements_changed.emit(self.measurements)

    @property
    def displayed_measurement(self):
        """Displayed measurement data.
        This is the data that is displayed in the view.
        It can be data in time domain or frequency domain."""
        return self._displayed_measurement
    
    @displayed_measurement.setter
    def displayed_measurement(self, value : Measurement):
        self._displayed_measurement = value
        self.displayed_measurement_changed.emit(value)

    @property
    def measurement_frequency(self):
        """Measurement frequency."""
        return self._measurement_frequency
    
    @measurement_frequency.setter
    def measurement_frequency(self, value : float):
        # Validator is used to check if the value is in the correct range.
        self._measurement_frequency = value
        self.measurement_frequency_changed.emit(value)
    
    @property
    def averages(self):
        """Number of averages."""
        return self._averages
    
    @averages.setter
    def averages(self, value : int):
        self._averages = value
        self.averages_changed.emit(value)
