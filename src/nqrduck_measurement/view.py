"""View for the measurement module."""

import logging
import numpy as np
from PyQt6.QtWidgets import QWidget, QDialog, QLabel, QVBoxLayout
from PyQt6.QtCore import pyqtSlot, Qt
from nqrduck.module.module_view import ModuleView
from nqrduck.assets.icons import Logos
from nqrduck.assets.animations import DuckAnimations
from .widget import Ui_Form

logger = logging.getLogger(__name__)


class MeasurementView(ModuleView):
    """View for the measurement module.

    This class is responsible for displaying the measurement data and handling the user input.

    Args:
        module (Module): The module instance.

    Attributes:
        widget (QWidget): The widget of the view.
        _ui_form (Ui_Form): The form of the widget.
        measurement_dialog (MeasurementDialog): The dialog shown when the measurement is started.
    """

    def __init__(self, module):
        """Initialize the measurement view."""
        super().__init__(module)

        widget = QWidget()
        self._ui_form = Ui_Form()
        self._ui_form.setupUi(self)
        self.widget = widget

        # Initialize plotter
        self.init_plotter()
        logger.debug(
            "Facecolor %s" % str(self._ui_form.plotter.canvas.ax.get_facecolor())
        )

        # Measurement dialog
        self.measurement_dialog = self.MeasurementDialog()

        # Connect signals
        self.module.model.displayed_measurement_changed.connect(
            self.update_displayed_measurement
        )
        self.module.model.view_mode_changed.connect(self.update_displayed_measurement)

        self._ui_form.buttonStart.clicked.connect(
            self.on_measurement_start_button_clicked
        )
        self._ui_form.fftButton.clicked.connect(self.module.controller.change_view_mode)

        # Measurement settings controller
        self._ui_form.frequencyEdit.state_updated.connect(
            lambda state, text: self.module.controller.set_frequency(state, text)
        )
        self._ui_form.averagesEdit.state_updated.connect(
            lambda state, text: self.module.controller.set_averages(state, text)
        )

        self.module.controller.set_frequency_failure.connect(
            self.on_set_frequency_failure
        )
        self.module.controller.set_averages_failure.connect(
            self.on_set_averages_failure
        )

        self._ui_form.apodizationButton.clicked.connect(
            self.module.controller.show_apodization_dialog
        )

        # Add logos
        self._ui_form.buttonStart.setIcon(Logos.Play_16x16())
        self._ui_form.buttonStart.setIconSize(self._ui_form.buttonStart.size())
        self._ui_form.buttonStart.setEnabled(False)

        self._ui_form.exportButton.setIcon(Logos.Save16x16())
        self._ui_form.exportButton.setIconSize(self._ui_form.exportButton.size())

        self._ui_form.importButton.setIcon(Logos.Load16x16())
        self._ui_form.importButton.setIconSize(self._ui_form.importButton.size())

        # Connect measurement save  and load buttons
        self._ui_form.exportButton.clicked.connect(
            self.on_measurement_save_button_clicked
        )
        self._ui_form.importButton.clicked.connect(
            self.on_measurement_load_button_clicked
        )

        # Make title label bold
        self._ui_form.titleLabel.setStyleSheet("font-weight: bold;")

        self._ui_form.spLabel.setStyleSheet("font-weight: bold;")

        # Set Min Max Values for frequency and averages
        self._ui_form.frequencyEdit.set_min_value(20.0)
        self._ui_form.frequencyEdit.set_max_value(1000.0)

        self._ui_form.averagesEdit.set_min_value(1)
        self._ui_form.averagesEdit.set_max_value(1e6)

    def init_plotter(self) -> None:
        """Initialize plotter with the according units for time domain."""
        plotter = self._ui_form.plotter
        plotter.canvas.ax.clear()
        plotter.canvas.ax.set_xlim(0, 100)
        plotter.canvas.ax.set_ylim(0, 1)
        plotter.canvas.ax.set_xlabel("Time (µs)")
        plotter.canvas.ax.set_ylabel("Amplitude (a.u.)")
        plotter.canvas.ax.set_title("Measurement data - Time domain")
        plotter.canvas.ax.grid()

    def change_to_time_view(self) -> None:
        """Change plotter to time domain view."""
        plotter = self._ui_form.plotter
        self._ui_form.fftButton.setText("FFT")
        plotter.canvas.ax.clear()
        plotter.canvas.ax.set_xlabel("Time (µs)")
        plotter.canvas.ax.set_ylabel("Amplitude (a.u.)")
        plotter.canvas.ax.set_title("Measurement data - Time domain")
        plotter.canvas.ax.grid()

    def change_to_fft_view(self) -> None:
        """Change plotter to frequency domain view."""
        plotter = self._ui_form.plotter
        self._ui_form.fftButton.setText("iFFT")
        plotter.canvas.ax.clear()
        plotter.canvas.ax.set_xlabel("Frequency (MHz)")
        plotter.canvas.ax.set_ylabel("Amplitude (a.u.)")
        plotter.canvas.ax.set_title("Measurement data - Frequency domain")
        plotter.canvas.ax.grid()

    @pyqtSlot()
    def update_displayed_measurement(self) -> None:
        """Update displayed measurement data."""
        logger.debug("Updating displayed measurement view.")
        plotter = self._ui_form.plotter
        plotter.canvas.ax.clear()
        try:
            if self.module.model.view_mode == self.module.model.FFT_VIEW:
                self.change_to_fft_view()
                x = self.module.model.displayed_measurement.fdx
                y = self.module.model.displayed_measurement.fdy
                x += float(self.module.model.displayed_measurement.target_frequency - self.module.model.displayed_measurement.IF_frequency) * 1e-6
            else:
                self.change_to_time_view()
                x = self.module.model.displayed_measurement.tdx
                y = self.module.model.displayed_measurement.tdy

            self._ui_form.plotter.canvas.ax.plot(
                x, y.real, label="Real", linestyle="-", alpha=0.35, color="red"
            )
            self._ui_form.plotter.canvas.ax.plot(
                x, y.imag, label="Imaginary", linestyle="-", alpha=0.35, color="green"
            )
            # Magnitude
            self._ui_form.plotter.canvas.ax.plot(
                x, np.abs(y), label="Magnitude", color="blue"
            )

            # Add legend
            self._ui_form.plotter.canvas.ax.legend()

        except AttributeError:
            logger.debug("No measurement data to display.")
        self._ui_form.plotter.canvas.draw()

    @pyqtSlot()
    def on_measurement_start_button_clicked(self) -> None:
        """Slot for when the measurement start button is clicked."""
        logger.debug("Measurement start button clicked.")
        self.module.controller.start_measurement()

    @pyqtSlot()
    def on_set_frequency_failure(self) -> None:
        """Slot for when the set frequency signal fails."""
        logger.debug("Set frequency failure.")
        self._ui_form.frequencyEdit.setStyleSheet("border: 1px solid red;")

    @pyqtSlot()
    def on_set_averages_failure(self) -> None:
        """Slot for when the set averages signal fails."""
        logger.debug("Set averages failure.")
        self._ui_form.averagesEdit.setStyleSheet("border: 1px solid red;")

    @pyqtSlot()
    def on_measurement_save_button_clicked(self) -> None:
        """Slot for when the measurement save button is clicked."""
        logger.debug("Measurement save button clicked.")

        file_manager = self.QFileManager(
            self.module.model.FILE_EXTENSION, parent=self.widget
        )
        file_name = file_manager.saveFileDialog()
        if file_name:
            self.module.controller.save_measurement(file_name)

    @pyqtSlot()
    def on_measurement_load_button_clicked(self) -> None:
        """Slot for when the measurement load button is clicked."""
        logger.debug("Measurement load button clicked.")

        file_manager = self.QFileManager(
            self.module.model.FILE_EXTENSION, parent=self.widget
        )
        file_name = file_manager.loadFileDialog()
        if file_name:
            self.module.controller.load_measurement(file_name)

    class MeasurementDialog(QDialog):
        """This Dialog is shown when the measurement is started and therefore blocks the main window.

        It shows the duck animation and a message.

        Attributes:
            finished (bool): True if the spinner movie is finished.
        """

        def __init__(self):
            """Initialize the dialog."""
            super().__init__()
            self.finished = True
            self.setModal(True)
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            self.message_label = "Measuring..."
            self.spinner_movie = DuckAnimations.DuckKick128x128()
            self.spinner_label = QLabel(self)
            self.spinner_label.setMovie(self.spinner_movie)

            self.layout = QVBoxLayout(self)
            self.layout.addWidget(QLabel(self.message_label))
            self.layout.addWidget(self.spinner_label)

            self.spinner_movie.finished.connect(self.on_movie_finished)

            self.spinner_movie.start()

        def on_movie_finished(self) -> None:
            """Called when the spinner movie is finished."""
            self.finished = True

        def hide(self) -> None:
            """Hide the dialog and stop the spinner movie."""
            while not self.finished:
                continue
            self.spinner_movie.stop()
            super().hide()
