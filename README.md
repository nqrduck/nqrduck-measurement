# NQRduck Module: nqrduck-measurement

A module for the [nqrduck](https://github.com/nqrduck/nqrduck) project. This module is used for single frequency magnetic resonance experiments.

## Installation

### Requirements
Dependencies are handled via the pyproject.toml file.

### Setup
To install the module you need the NQRduck core. You can find the installation instructions for the NQRduck core [here](https://github.com/nqrduck/nqrduck).

Ideally you should install the module in a virtual environment. You can create a virtual environment by running the following command in the terminal:
```bash
python -m venv nqrduck
# Activate the virtual environment
. nqrduck/bin/activate
```

You can install this module and the dependencies by running the following command in the terminal while the virtual environment is activated and you are in the root directory of this module:
```bash
pip install .
```

Alternatively, you can install the module and the dependencies by running the following command in the terminal while the virtual environment is activated:
```bash
pip install nqrduck-measurement
```

## Usage
The module is used with the [Spectrometer](https://github.com/nqrduck/nqrduck-spectrometer) module. However you need to use an actual submodule of the spectrometer module like:

- [nqrduck-spectrometer-limenqr](https://github.com/nqrduck/nqrduck-spectrometer-limenqr) A module used for magnetic resonance experiments with the LimeSDR (USB or Mini 2.0).
- [nqrduck-spectrometer-simulator](https://github.com/nqrduck/nqrduck-spectrometer-simulator) A module used for simulating magnetic resonance experiments.

The pulse sequence and spectrometer settings can be adjusted using the 'Spectrometer' tab. 

<img src="https://github.com/nqrduck/nqrduck-measurement/raw/0b28ae6b33230c6ca9eda85bd18de7cbcade27d1/docs/img/measurement_ui_labeled_v2.png" alt="drawing" width="800">

- a.) The experiments settings for frequency and number of averages.
- b.) The signal processing settings for the measurement.
- c.) The 'Measurement Plot'. Here the measured data is displayed. One can switch time and frequency domain plots.
- d.) The import and export buttons for the measurement data.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Contributing
If you're interested in contributing to the project, start by checking out our [nqrduck-module template](https://github.com/nqrduck/nqrduck-module). To contribute to existing modules, please first open an issue in the respective module repository to discuss your ideas or report bugs.
