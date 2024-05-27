"""View for the measurement module."""

import logging
import numpy as np
from functools import partial
from PyQt6.QtWidgets import (
    QWidget,
    QDialog,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidgetItem,
    QSizePolicy,
    QApplication,
    QLineEdit,
)
from PyQt6.QtGui import QFontMetrics
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
            f"Facecolor {str(self._ui_form.plotter.canvas.ax.get_facecolor())}"
        )

        # Measurement dialog
        self.measurement_dialog = self.MeasurementDialog(self)

        # Connect signals
        self.module.model.displayed_measurement_changed.connect(
            self.update_displayed_measurement
        )
        self.module.model.view_mode_changed.connect(self.update_displayed_measurement)

        self.module.model.measurements_changed.connect(self.on_measurements_changed)

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

        self._ui_form.fittingButton.clicked.connect(
            self.module.controller.show_fitting_dialog
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

        # Connect selectionBox signal for switching the displayed  measurement
        self._ui_form.selectionBox.valueChanged.connect(
            self.module.controller.change_displayed_measurement
        )

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

    @pyqtSlot()
    def on_settings_changed(self) -> None:
        """Redraw the plots in case the according settings have changed."""
        self.update_displayed_measurement()

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
            if self.module.model.displayed_measurement is None:
                logger.debug("No measurement data to display. Clearing plotter.")

                if self.module.model.view_mode == self.module.model.FFT_VIEW:
                    self.change_to_fft_view()
                else:
                    self.change_to_time_view()

                self._ui_form.plotter.canvas.draw()

                return

            if self.module.model.view_mode == self.module.model.FFT_VIEW:
                self.change_to_fft_view()
                y = self.module.model.displayed_measurement.fdy
                x = (
                    self.module.model.displayed_measurement.fdx
                    + float(
                        self.module.model.displayed_measurement.target_frequency
                        - self.module.model.displayed_measurement.IF_frequency
                    )
                    * 1e-6
                )
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

            # Plot fits
            self.plot_fits()

            # Add legend
            self._ui_form.plotter.canvas.ax.legend()

            # Highlight the displayed measurement in the measurementsList
            for i in range(self._ui_form.measurementsList.count()):
                item = self._ui_form.measurementsList.item(i)
                widget = self._ui_form.measurementsList.itemWidget(item)
                button = widget.layout().itemAt(0).widget()
                # Get the measurement by accessing measurement property
                measurement = button.property("measurement")
                if measurement == self.module.model.displayed_measurement:
                    item.setSelected(True)
                else:
                    item.setSelected(False)

            # Update the number of the selectionBox
            for measurement in self.module.model.measurements:
                if measurement.name == self.module.model.displayed_measurement.name:
                    self._ui_form.selectionBox.setValue(
                        self.module.model.measurements.index(measurement)
                    )
                    break

        except AttributeError as e:
            logger.debug(f"No measurement data to display: {e}")

        self._ui_form.plotter.canvas.draw()

    def plot_fits(self):
        """Plots the according fits to the displayed measurement if there are any and if the view mode is correct."""
        measurement = self.module.model.displayed_measurement

        if not measurement.fits:
            logger.debug("No fits to plot.")
            return

        for fit in measurement.fits:
            if fit.domain == self.module.model.view_mode:
                logger.debug(f"Plotting {fit.name} fit in domain {fit.domain}.")
                x = fit.x
                y = fit.y
                # Shift the x values if the view mode is FFT
                if fit.domain == self.module.model.FFT_VIEW:
                    x = x + float(
                        measurement.target_frequency - measurement.IF_frequency
                    ) * 1e-6

                self._ui_form.plotter.canvas.ax.plot(
                    x, y, label=f"{fit.name} Fit", linestyle="--"
                )

                # Add the parameters to the plot
                offset = 0
                for name, value in fit.parameters.items():
                    if name == "covariance":
                        continue

                    # Only two digits after the comma
                    value = round(value, 2)

                    self._ui_form.plotter.canvas.ax.text(
                        max(x) / 90,
                        max(y) / 2 + offset,
                        f"{name}: {value}",
                    )
                    offset += max(y) / 10

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

        file_manager = self.FileManager(
            self.module.model.FILE_EXTENSION, parent=self
        )
        file_name = file_manager.saveFileDialog()
        if file_name:
            self.module.controller.save_measurement(file_name)

    @pyqtSlot()
    def on_measurement_load_button_clicked(self) -> None:
        """Slot for when the measurement load button is clicked."""
        logger.debug("Measurement load button clicked.")

        file_manager = self.FileManager(
            self.module.model.FILE_EXTENSION, parent=self
        )
        file_name = file_manager.loadFileDialog()
        if file_name:
            self.module.controller.load_measurement(file_name)

    @pyqtSlot()
    def on_measurements_changed(self) -> None:
        """Slot for when a measurement is added."""
        logger.debug("Measurement changed.")

        if len(self.module.model.measurements) == 0:
            self.module.view._ui_form.selectionBox.setMaximum(0)
            self.module.view._ui_form.selectionBox.setValue(0)
        else:
            self.module.view._ui_form.selectionBox.setMaximum(
                len(self.module.model.measurements) - 1
            )

        # Clear the measurements list
        self._ui_form.measurementsList.clear()

        for measurement in self.module.model.measurements:
            measurement_widget = QWidget()
            layout = QHBoxLayout()
            measurement_widget.setLayout(layout)

            delete_button = QPushButton()
            delete_button.setIcon(Logos.Garbage12x12())
            delete_button.setFixedWidth(delete_button.iconSize().width())
            delete_button.clicked.connect(
                lambda: self.module.controller.delete_measurement(measurement)
            )

            edit_button = QPushButton()
            edit_button.setIcon(Logos.Pen12x12())
            edit_button.setFixedWidth(edit_button.iconSize().width())
            edit_button.clicked.connect(lambda: self.show_measurement_edit(measurement))

            name_button = QPushButton()
            name_button.clicked.connect(
                partial(
                    self.module.controller.change_displayed_measurement, measurement
                )
            )

            # Not sure if this is pretty
            name_button.setProperty("measurement", measurement)
            name_button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
            )  # Set size policy

            layout.addWidget(edit_button)
            layout.addWidget(name_button)
            layout.addWidget(delete_button)
            layout.addStretch()  # Add stretch after delete button to ensure name button takes up space

            item = QListWidgetItem()
            item.setSizeHint(measurement_widget.sizeHint())

            self._ui_form.measurementsList.addItem(item)
            self._ui_form.measurementsList.setItemWidget(item, measurement_widget)

            # Wait for the layout to be updated
            QApplication.processEvents()

            # Get the contents margins (left, top, right, bottom)
            content_margins = layout.contentsMargins()

            # Include the margins and spacing in the maxWidth calculation
            maxWidth = (
                self._ui_form.measurementsList.width()
                - delete_button.width()
                - content_margins.left()
                - content_margins.right()
                - layout.spacing()
            )

            fontMetrics = QFontMetrics(name_button.font())
            elidedText = fontMetrics.elidedText(
                measurement.name, Qt.TextElideMode.ElideRight, maxWidth
            )
            name_button.setText(elidedText)
            name_button.setToolTip(measurement.name)

    def show_measurement_edit(self, measurement) -> None:
        """Show the measurement dialog.

        Args:
            measurement (Measurement): The measurement to edit.
        """
        dialog = self.MeasurementEdit(measurement, parent=self)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            logger.debug("Measurement edited.")
            self.module.controller.edit_measurement(measurement, dialog.measurement)
        else:
            logger.debug("Measurement edit canceled.")

    class MeasurementDialog(QDialog):
        """This Dialog is shown when the measurement is started and therefore blocks the main window.

        It shows the duck animation and a message.

        Attributes:
            finished (bool): True if the spinner movie is finished.
        """

        def __init__(self, parent=None):
            """Initialize the dialog."""
            super().__init__(parent)
            self.setParent(parent)
            self.finished = False
            self.setModal(True)
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setWindowFlag(
                Qt.WindowType.WindowStaysOnTopHint
            )  # Ensure the window stays on top

            self.message_label = QLabel("Measuring...")
            # Make label bold and text larger
            font = self.message_label.font()
            font.setPointSize(20)
            font.setBold(True)
            self.message_label.setFont(font)

            self.spinner_movie = DuckAnimations.DuckKick128x128()
            self.spinner_label = QLabel(self)
            # Make spinner label
            self.spinner_label.setMovie(self.spinner_movie)

            self.layout = QVBoxLayout(self)
            self.layout.addWidget(self.message_label)
            self.layout.addWidget(self.spinner_label)

            self.spinner_movie.finished.connect(self.on_movie_finished)

        def show(self) -> None:
            """Show the dialog and ensure it is raised and activated."""
            super().show()
            self.raise_()  # Bring the dialog to the front
            self.activateWindow()  # Give the dialog focus
            self.spinner_movie.start()  # Ensure the movie starts playing

        def on_movie_finished(self) -> None:
            """Called when the spinner movie is finished."""
            self.finished = True

        def hide(self) -> None:
            """Hide the dialog and stop the spinner movie."""
            self.spinner_movie.stop()
            super().hide()

    class MeasurementEdit(QDialog):
        """This dialog is displayed when the measurement edit button is clicked.
        
        It allows the user to edit the measurement parameters (e.g. name, ...).
        """

        def __init__(self, measurement, parent=None) -> None:
            """Initialize the dialog."""
            super().__init__(parent)
            self.setParent(parent)

            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            logger.debug("Edit measurement dialog started.")

            self.measurement = measurement
            self.setWindowTitle("Edit Measurement")

            self.layout = QVBoxLayout(self)
            self.setLayout(self.layout)

            self.setup_name_section()
            self.setup_fit_section()
            self.setup_buttons()

            # Resize the dialog
            self.adjustSize()

        def setup_name_section(self):
            """Sets up the name layout section."""
            self.name_layout = QHBoxLayout()
            self.name_label = QLabel("Name:")

            self.name_edit = QLineEdit(self.measurement.name)
            font_metrics = self.name_edit.fontMetrics()
            self.name_edit.setFixedWidth(font_metrics.horizontalAdvance(
                self.name_edit.text()) + 10)
            self.name_edit.adjustSize()

            self.name_layout.addWidget(self.name_label)
            self.name_layout.addWidget(self.name_edit)
            self.layout.addLayout(self.name_layout)

        def setup_fit_section(self):
            """Sets up the fit layout section."""
            self.fit_layout = QVBoxLayout()
            self.update_fit_info()
            self.layout.addLayout(self.fit_layout)

        def setup_buttons(self):
            """Sets up the OK and Cancel buttons."""
            self.ok_button = QPushButton("OK")
            self.ok_button.clicked.connect(self.on_ok_button_clicked)

            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.clicked.connect(self.close)

            button_layout = QHBoxLayout()
            button_layout.addWidget(self.cancel_button)
            button_layout.addWidget(self.ok_button)
            self.layout.addLayout(button_layout)

        def update_fit_info(self) -> None:
            """Adds the associated fits to the dialog."""
            # Clear the layout from previous fits
            while self.fit_layout.count():
                item = self.fit_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clearLayout(item.layout())

            if not self.measurement.fits:
                logger.debug("No fits to display.")
                return

            # Adds the fit information
            fit_label = QLabel("Fits:")
            self.fit_layout.addWidget(fit_label)

            for fit in self.measurement.fits:
                specific_fit_layout = QHBoxLayout()
                specific_fit_layout.addStretch()
                logger.debug(f"Fit: {fit.name}")

                fit_name_edit = QLineEdit(fit.name)
                fit_name_edit.textChanged.connect(
                    lambda text, fit=fit: self.measurement.edit_fit_name(fit, text)
                )

                fit_delete_button = QPushButton()
                fit_delete_button.setIcon(Logos.Garbage12x12())
                fit_delete_button.clicked.connect(partial(self.on_delete_fit, fit))

                specific_fit_layout.addWidget(fit_name_edit)
                specific_fit_layout.addWidget(fit_delete_button)
                self.fit_layout.addLayout(specific_fit_layout)

        def clearLayout(self, layout):
            """Clears all items in the given layout."""
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clearLayout(item.layout())

        def on_delete_fit(self, fit) -> None:
            """Slot for when the delete fit button is clicked."""
            logger.debug(f"Delete fit {fit.name}.")
            self.measurement.delete_fit(fit)
            self.update_fit_info()  # Update the dialog with the changes

        def on_ok_button_clicked(self) -> None:
            """Slot for when the OK button is clicked."""
            logger.debug("OK button clicked.")
            self.measurement.name = self.name_edit.text()
            self.accept()
            self.close()

