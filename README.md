<a href="#"><img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&style=for-the-badge" /></a>
<a href="https://paulotto.github.io/projects/jaw-tracking-system/"><img src="https://img.shields.io/badge/Website-JTS-color?style=for-the-badge&color=rgb(187%2C38%2C73)" /></a>

# JawTrackingSystem (JTS): A customizable, low-cost, optical jaw tracking system

A modular and extensible Python package for analyzing jaw motion using motion capture data. 
Designed for research and clinical applications, it provides a flexible pipeline for calibration, 
coordinate transformations, registration, smoothing, visualization, and export of jaw kinematics.

---

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Extending the Framework](#extending-the-framework)
- [Directory Structure](#directory-structure)
- [Testing](#testing)
- [License](#license)
- [Citation](#citation)

---

## Features
- Offline or real-time jaw motion analysis
- Abstract base classes for motion capture data (supports Qualisys, extensible to others)
- Calibration routines for anatomical landmark registration
- Modular pipeline: calibration, relative motion, coordinate transformation, smoothing, visualization, export
- Support for multiple file formats (CSV, HDF5)
- Configurable via JSON files
- Visualization utilities for 2D/3D trajectories
- Comprehensive logging and error handling
- Test suite for core functionality

## Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

1. Prepare a configuration JSON file (see [README](config/README.md) for examples).
2. Run the analysis pipeline:

```bash
python -m mocap.core path/to/config.json
```

3. Results (trajectories, plots, exports) will be saved to the output directory specified in your config.

## Configuration

All analysis parameters are specified in a JSON config file. Key sections include:
- `data_source`: Type (e.g., "qualisys"), filename, and system-specific parameters
- `analysis`: Calibration, experiment intervals, smoothing, coordinate transforms
- `output`: Output directory, file formats, export options
- `visualization`: Plotting options

See [config.json](config/config.json) for a template.

## Usage

### As a Script

```bash
python -m mocap.core path/to/config.json
```

Optional flags:
- `--verbose` for detailed logging
- `--plot` to show plots interactively

### As a Library

```python
from jaw_tracking_system.core import JawMotionAnalysis, ConfigManager

config = ConfigManager.load_config('path/to/config.json')
analysis = JawMotionAnalysis(config)
results = analysis.run_analysis()
```

## Extending the Framework

- Add new motion capture system support by subclassing `MotionCaptureData`.
- Implement new calibration or analysis routines by extending `JawMotionAnalysis`.
- Add new visualization or export utilities in `helper.py`.

## Directory Structure

```
jaw_tracking_system/
├── __init__.py
├── calibration_controllers.py
├── core.py
├── helper.py
├── LICENSE
├── plotly_visualization.py
├── precision_analysis.py
├── qualisys_streaming.py
├── qualisys.py
├── README.md
├── requirements.txt
├── setup.py
├── streaming.py
├── config/
│   ├── README.md
│   └── config.json
└── tests/
    ├── __init__.py
    ├── test_core.py
    ├── test_helper.py
    ├── test_precision_analysis.py
    └── test_qualisys.py
```

## Testing

Run the test suite with:

```bash
pytest jaw_tracking_system/tests
```

## License

This project is licensed under the Attribution-NonCommercial-ShareAlike 4.0 International
(CC BY-NC-SA 4.0).

Copyright (C) 2025 Paul-Otto Müller

See the [LICENSE](./LICENSE) file for details.

## Citation

If you use this package in your research, please cite:

```
@software{mueller2025jts,
  author = {Paul-Otto Müller and Sven Suppelt and Mario Kupnik and Oskar von Stryk},
  title = {JawTrackingSystem (JTS): A customizable, low-cost, optical jaw tracking system},
  year = {2025},
  url = {https://github.com/paulotto/jaw-tracking-system},
  version = {1.0.0},
  license = {CC BY-NC-SA 4.0}
}
```

---

For more information, see the [project website](https://paulotto.github.io/projects/jaw-tracking-system/).