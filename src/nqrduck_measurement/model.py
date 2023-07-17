import logging
from PyQt6.QtCore import pyqtSignal
from nqrduck_spectrometer.measurement import Measurement
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)

class MeasurementModel(ModuleModel):

    single_measurement_changed = pyqtSignal(Measurement)

    def __init__(self, module) -> None:
        super().__init__(module)

    @property
    def single_measurement(self):
        """Single measurement data."""
        return self._single_measurement
    
    @single_measurement.setter
    def single_measurement(self, value : Measurement):
        self._single_measurement = value
        self.single_measurement_changed.emit(value)
