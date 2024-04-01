"""Model for the measurement module."""

import logging
from PyQt6.QtCore import pyqtSignal
from nqrduck_spectrometer.measurement import Measurement
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)


class MeasurementModel(ModuleModel):
    """Model for the measurement module.

    This class is responsible for storing the data of the measurement module.

    Attributes:
        FILE_EXTENSION (str): The file extension of the measurement files.
        FFT_VIEW (str): The view mode for the FFT view.
        TIME_VIEW (str): The view mode for the time view.

        displayed_measurement_changed (pyqtSignal): Signal emitted when the displayed measurement changes.
        measurements_changed (pyqtSignal): Signal emitted when the list of measurements changes.
        view_mode_changed (pyqtSignal): Signal emitted when the view mode changes.

        measurement_frequency_changed (pyqtSignal): Signal emitted when the measurement frequency changes.
        averages_changed (pyqtSignal): Signal emitted when the number of averages changes.

        view_mode (str): The view mode of the measurement view.
        measurements (list): List of measurements.
        displayed_measurement (Measurement): The displayed measurement data.
        measurement_frequency (float): The measurement frequency.
        averages (int): The number of averages.

        validator_measurement_frequency (DuckFloatValidator): Validator for the measurement frequency.
        validator_averages (DuckIntValidator): Validator for the number of averages.
    """

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
        """Initialize the model."""
        super().__init__(module)
        self.view_mode = self.TIME_VIEW
        self.measurements = []
        self._displayed_measurement = None

        self.measurement_frequency = 100.0  # MHz
        self.averages = 1

        self.frequency_valid = False
        self.averages_valid = False

    @property
    def view_mode(self) -> str:
        """View mode of the measurement view.

        Can be either "time" or "fft".
        """
        return self._view_mode

    @view_mode.setter
    def view_mode(self, value: str):
        self._view_mode = value
        self.view_mode_changed.emit(value)

    @property
    def measurements(self):
        """List of measurements."""
        return self._measurements

    @measurements.setter
    def measurements(self, value: list[Measurement]):
        self._measurements = value
        self.measurements_changed.emit(value)

    def add_measurement(self, measurement: Measurement):
        """Add a measurement to the list of measurements."""
        self.measurements.append(measurement)
        self.measurements_changed.emit(self.measurements)

    @property
    def displayed_measurement(self):
        """Displayed measurement data.

        This is the data that is displayed in the view.
        It can be data in time domain or frequency domain.
        """
        return self._displayed_measurement

    @displayed_measurement.setter
    def displayed_measurement(self, value: Measurement):
        self._displayed_measurement = value
        self.displayed_measurement_changed.emit(value)

    @property
    def measurement_frequency(self):
        """Measurement frequency."""
        return self._measurement_frequency

    @measurement_frequency.setter
    def measurement_frequency(self, value: float):
        # Validator is used to check if the value is in the correct range.
        self._measurement_frequency = value
        self.measurement_frequency_changed.emit(value)

    @property
    def frequency_valid(self) -> bool:
        """Check if the frequency is valid."""
        return self._frequency_valid

    @frequency_valid.setter
    def frequency_valid(self, value: bool):
        logger.debug("Frequency valid: " + str(value))
        self._frequency_valid = value

    @property
    def averages(self):
        """Number of averages."""
        return self._averages

    @averages.setter
    def averages(self, value: int):
        self._averages = value
        self.averages_changed.emit(value)

    @property
    def averages_valid(self) -> bool:
        """Check if the number of averages is valid."""
        logger.debug("Averages valid: " + str(self._averages_valid))
        return self._averages_valid

    @averages_valid.setter
    def averages_valid(self, value: bool):
        self._averages_valid = value
