import logging
from PyQt6.QtCore import pyqtSignal
from nqrduck_spectrometer.measurement import Measurement
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)

class MeasurementModel(ModuleModel):

    FILE_EXTENSION = ".meas"
    # This constants are used to determine which view is currently displayed.
    FFT_VIEW = "fft"
    TIME_VIEW = "time"

    displayed_measurement_changed = pyqtSignal(Measurement)
    measurements_changed = pyqtSignal(list)
    view_mode_changed = pyqtSignal(str)

    def __init__(self, module) -> None:
        super().__init__(module)
        self.view_mode = self.TIME_VIEW
        self.measurements = []

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
