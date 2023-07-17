import logging
from nqrduck.module.module_controller import ModuleController
from nqrduck_spectrometer.measurement import Measurement

logger = logging.getLogger(__name__)

class MeasurementController(ModuleController):
    def __init__(self, module):
        super().__init__(module)

    def start_measurement(self):
        logger.debug("Start measurement clicked")
        self.module.nqrduck_signal.emit("start_measurement", None)

    def process_signals(self, key: str, value: Measurement):
        if key == "single_measurement":
            logger.debug("Received single measurement.")
            self.module.model.single_measurement = value
