import logging
import numpy as np
from pathlib import Path
import matplotlib as mpl
from PyQt6.QtWidgets import QWidget, QDialog, QLabel, QVBoxLayout
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import pyqtSlot, Qt
from nqrduck.module.module_view import ModuleView
from .widget import Ui_Form

logger = logging.getLogger(__name__)

class MeasurementView(ModuleView):
    def __init__(self, module):
        super().__init__(module)

        # Set custom matplotlib parameters
        mpl.rcParams.update({
            "figure.facecolor":  (0.0, 0.0, 0.0, 0.00),  # transparent   
            "axes.facecolor":    (0.0, 1.0, 0.0, 0.03),  # green 
            "savefig.facecolor": (0.0, 0.0, 0.0, 0.0),  # transparent
        })

        # Set custom matplotlib parameters
        mpl.rcParams['figure.subplot.bottom'] = 0.2
        mpl.rcParams['axes.linewidth'] = 1.5
        mpl.rcParams['xtick.major.width'] = 1.5
        mpl.rcParams['ytick.major.width'] = 1.5
        mpl.rcParams['xtick.minor.width'] = 1.5
        mpl.rcParams['ytick.minor.width'] = 1.5
        mpl.rcParams['xtick.major.size'] = 6
        mpl.rcParams['ytick.major.size'] = 6
        mpl.rcParams['xtick.minor.size'] = 4
        mpl.rcParams['ytick.minor.size'] = 4

        widget = QWidget()
        self._ui_form = Ui_Form()
        self._ui_form.setupUi(self)
        self.widget = widget

        # Initialize plotter
        self.init_plotter()
        logger.debug("Facecolor %s" % str(self._ui_form.plotter.canvas.ax.get_facecolor()))

        # Measurement dialog
        self.measurement_dialog = self.MeasurementDialog() 

        # Connect signals
        self.module.model.displayed_measurement_changed.connect(self.update_displayed_measurement)
        self.module.model.view_mode_changed.connect(self.update_displayed_measurement)

        self._ui_form.buttonStart.clicked.connect(self.on_measurement_start_button_clicked)
        self._ui_form.fftButton.clicked.connect(self.module.controller.change_view_mode)

    def init_plotter(self):
        plotter = self._ui_form.plotter
        plotter.canvas.ax.clear()
        plotter.canvas.ax.set_xlim(0, 100)
        plotter.canvas.ax.set_ylim(0, 1)
        plotter.canvas.ax.set_xlabel("Time (µs)")
        plotter.canvas.ax.set_ylabel("Amplitude (a.u.)")
        plotter.canvas.ax.set_title("Measurement data - Time domain")
        plotter.canvas.ax.grid()
            
    def change_to_time_view(self):
        plotter = self._ui_form.plotter
        plotter.canvas.ax.clear()
        plotter.canvas.ax.set_xlabel("Time (µs)")
        plotter.canvas.ax.set_ylabel("Amplitude (a.u.)")
        plotter.canvas.ax.set_title("Measurement data - Time domain")
        plotter.canvas.ax.grid()

    def change_to_fft_view(self):
        plotter = self._ui_form.plotter
        plotter.canvas.ax.clear()
        plotter.canvas.ax.set_xlabel("Frequency (MHz)")
        plotter.canvas.ax.set_ylabel("Amplitude (a.u.)")
        plotter.canvas.ax.set_title("Measurement data - Frequency domain")
        plotter.canvas.ax.grid()

    @pyqtSlot()
    def update_displayed_measurement(self):
        logger.debug("Updating displayed measurement view.")
        plotter = self._ui_form.plotter
        plotter.canvas.ax.clear()
        try:
            if self.module.model.view_mode == self.module.model.FFT_VIEW:
                self.change_to_fft_view()
                x = self.module.model.displayed_measurement.fdx
                y = self.module.model.displayed_measurement.fdy
            else:
                self.change_to_time_view()
                x = self.module.model.displayed_measurement.tdx
                y = self.module.model.displayed_measurement.tdy

            self._ui_form.plotter.canvas.ax.plot(x, y)
        except AttributeError:
            logger.debug("No measurement data to display.")
        self._ui_form.plotter.canvas.draw()

    @pyqtSlot()
    def on_measurement_start_button_clicked(self):
        logger.debug("Measurement start button clicked.")
        self.module.controller.start_measurement()

    class MeasurementDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.finished = True
            self.setModal(True)
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            path = Path(__file__).parent
            self.spinner_movie = QMovie(str(path / "resources/duck_kick.gif"))  # Replace with your own spinner gif
            self.spinner_label = QLabel(self)
            self.spinner_label.setMovie(self.spinner_movie)

            self.layout = QVBoxLayout(self)
            self.layout.addWidget(self.spinner_label)

            self.spinner_movie.finished.connect(self.on_movie_finished)

            self.spinner_movie.start()

        def on_movie_finished(self):
            self.finished = True

        def hide(self):
            while not self.finished:
                continue
            self.spinner_movie.stop()
            super().hide()
