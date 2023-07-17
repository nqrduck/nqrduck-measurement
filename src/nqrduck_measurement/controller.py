import logging
from nqrduck.module.module_controller import ModuleController

logger = logging.getLogger(__name__)

class MeasurementController(ModuleController):
    def __init__(self, module):
        super().__init__(module)