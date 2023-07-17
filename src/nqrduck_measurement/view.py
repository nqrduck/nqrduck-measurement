import logging
import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSlot
from .widget import Ui_Form
from nqrduck.module.module_view import ModuleView

logger = logging.getLogger(__name__)

class MeasurementView(ModuleView):
    def __init__(self, module):
        super().__init__(module)

        widget = QWidget()
        self._ui_form = Ui_Form()
        self._ui_form.setupUi(self)
        self.widget = widget

        # Connect signals
        self.module.model.single_measurement_changed.connect(self.update_single_measurement)
        self._ui_form.buttonStart.clicked.connect(self.on_measurement_start_button_clicked)

    @pyqtSlot()
    def update_single_measurement(self):
        logger.debug("Updating single measurement view.")
        # Set the x data
        tdx = self.module.model.single_measurement.tdx
        tdy = self.module.model.single_measurement.tdy
        #correcting a offset in the time domain by subtracting the mean
        tdy_mean = tdy[:,0]-np.mean(tdy)
        self._ui_form.plotter.canvas.ax.clear()  # Clear the axes for the new plot
        self._ui_form.plotter.canvas.ax.plot(tdx, tdy_mean)
        self._ui_form.plotter.canvas.ax.set_xlabel("Time (µs)")
        self._ui_form.plotter.canvas.ax.set_ylabel("Amplitude (a.u.)")
        self._ui_form.plotter.canvas.ax.set_title("Single measurement")
        self._ui_form.plotter.canvas.ax.grid()
        self._ui_form.plotter.canvas.draw()

    @pyqtSlot()
    def on_measurement_start_button_clicked(self):
        logger.debug("Measurement start button clicked.")
        self.module.controller.start_measurement()