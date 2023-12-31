import logging
import json
from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QWidget
from nqrduck.module.module_controller import ModuleController
from nqrduck_spectrometer.measurement import Measurement

logger = logging.getLogger(__name__)


class MeasurementController(ModuleController):
    set_frequency_failure = pyqtSignal()
    set_averages_failure = pyqtSignal()

    def __init__(self, module):
        super().__init__(module)

    @pyqtSlot(str)
    def set_frequency(self, value: str) -> None:
        """Set frequency in MHz.

        Args:
            value (str): Frequency in MHz.

        Raises:
            ValueError: If value cannot be converted to float."""
        try:
            logger.debug("Setting frequency to: %s MHz" % value)
            self.module.nqrduck_signal.emit("set_frequency", float(value) * 1e6)
        except ValueError:
            self.set_averages_failure.emit()

    @pyqtSlot(str)
    def set_averages(self, value: str) -> None:
        """Set number of averages.

        Args:
            value (str): Number of averages.
        """
        logger.debug("Setting averages to: " + value)
        self.module.nqrduck_signal.emit("set_averages", value)

    @pyqtSlot()
    def change_view_mode(self) -> None:
        """Change view mode between time and frequency domain."""
        logger.debug("Changing view mode.")
        if self.module.model.view_mode == self.module.model.FFT_VIEW:
            self.module.model.view_mode = self.module.model.TIME_VIEW
        else:
            self.module.model.view_mode = self.module.model.FFT_VIEW

        logger.debug("View mode changed to: " + self.module.model.view_mode)

    def start_measurement(self) -> None:
        """Emmit the start measurement signal."""
        logger.debug("Start measurement clicked")
        self.module.view.measurement_dialog.show()
        self.module.nqrduck_signal.emit("start_measurement", None)

    def process_signals(self, key: str, value: object):
        """Process incoming signal from the nqrduck module.
        
        Arguments:
            key (str) -- The key of the signal.
            value (object) -- The value of the signal.
        """
        logger.debug(
            "Measurement Dialog is visible: "
            + str(self.module.view.measurement_dialog.isVisible())
        )

        if (
            key == "measurement_data"
            and self.module.view.measurement_dialog.isVisible()
        ):
            logger.debug("Received single measurement.")
            self.module.model.displayed_measurement = value
            self.module.model.add_measurement(value)
            self.module.view.measurement_dialog.hide()

        elif (
            key == "measurement_error"
            and self.module.view.measurement_dialog.isVisible()
        ):
            logger.debug("Received measurement error.")
            self.module.view.measurement_dialog.hide()
            self.module.nqrduck_signal.emit(
                "notification", ["Error", "Error during measurement."]
            )

        elif (
            key == "failure_set_frequency"
            and self.module.view._ui_form.frequencyEdit.text() == value
        ):
            logger.debug("Received set frequency failure.")
            self.set_frequency_failure.emit()

        elif (
            key == "failure_set_averages"
            and self.module.view._ui_form.averagesEdit.text() == value
        ):
            logger.debug("Received set averages failure.")
            self.set_averages_failure.emit()
        elif key == "active_spectrometer_changed":
            self.module.view._ui_form.spectrometerLabel.setText("Spectrometer: %s" % value)


    def save_measurement(self, file_name : str) -> None:
        """Save measurement to file.

        Args:
            file_name (str): Path to file.
        """
        logger.debug("Saving measurement.")
        if not self.module.model.measurements:
            logger.debug("No measurement to save.")
            return
        
        measurement = self.module.model.measurements[-1].to_json()

        with open(file_name, "w") as f:
            json.dump(measurement, f)

    def  load_measurement(self, file_name: str) -> None:
        """Load measurement from file.

        Args:
            file_name (str): Path to file.
        """
        logger.debug("Loading measurement.")

        try:
            with open(file_name, "r") as f:
                measurement = Measurement.from_json(json.load(f))
                self.module.model.add_measurement(measurement)
                self.module.model.displayed_measurement = measurement
        except FileNotFoundError:
            logger.debug("File not found.")
            self.module.nqrduck_signal.emit(
                "notification", ["Error", "File not found."]
            )
        except (json.JSONDecodeError, KeyError):
            logger.debug("File is not a valid measurement file.")
            self.module.nqrduck_signal.emit(
                "notification", ["Error", "File is not a valid measurement file."]
            )
