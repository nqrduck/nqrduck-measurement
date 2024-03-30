"""Module initialization file for the nqrduck-measurement module."""

from nqrduck.module.module import Module
from .model import MeasurementModel
from .view import MeasurementView
from .controller import MeasurementController

Measurement = Module(MeasurementModel, MeasurementView, MeasurementController)
