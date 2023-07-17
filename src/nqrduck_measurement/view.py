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
        self.module.model.single_measurement_changed.connect(self.update_single_measurement)
        self._ui_form.buttonStart.clicked.connect(self.on_measurement_start_button_clicked)

    def init_plotter(self):
        plotter = self._ui_form.plotter
        plotter.canvas.ax.set_xlim(0, 100)
        plotter.canvas.ax.set_ylim(0, 1)
        plotter.canvas.ax.set_xlabel("Time (µs)")
        plotter.canvas.ax.set_ylabel("Amplitude (a.u.)")
        plotter.canvas.ax.set_title("Measurement data")
        plotter.canvas.ax.grid()
        plotter.canvas.draw()

    @pyqtSlot()
    def update_single_measurement(self):
        logger.debug("Updating single measurement view.")
        # Set the x data
        tdx = self.module.model.single_measurement.tdx
        tdy = self.module.model.single_measurement.tdy
        #correcting a offset in the time domain by subtracting the mean
        tdy_mean = tdy[:,0]-np.mean(tdy)
        self._ui_form.plotter.canvas.ax.set_xlabel("Time (µs)")
        self._ui_form.plotter.canvas.ax.set_ylabel("Amplitude (a.u.)")
        self._ui_form.plotter.canvas.ax.set_title("Measurement data")
        self._ui_form.plotter.canvas.ax.clear()  # Clear the axes for the new plot
        self._ui_form.plotter.canvas.ax.plot(tdx, tdy_mean)
        self._ui_form.plotter.canvas.ax.grid()
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
