# Changelog

All notable changes to the Jaw Tracking System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2025-10-16

### Fixed

#### Core Package (`jts/`)
- **core.py**: Fixed 15 critical type checking issues
  - Added proper `Callable` import from typing
  - Fixed type annotations for callable parameters
  - Added runtime checks for streaming-specific attributes (`load_data`, `plot_utils`, `rigid_bodies`, `frame_rate`)
  - Fixed `FrameInterval` vs `window_size` parameter compatibility between streaming and offline modes
  - Added None checks for optional motion data attributes

- **qualisys_streaming.py**: Fixed 8 critical issues
  - Added None checks before tuple unpacking from `packet.get_3d_markers()` and `packet.get_6d()`
  - Fixed event loop None checks with proper error handling
  - Fixed connection None checks before streaming operations
  - Updated `Queue.get()` API usage with proper await syntax

- **streaming.py**: Fixed 1 critical issue
  - Added None check for `stability_buffer.maxlen` before comparison to prevent potential errors

- **calibration_controllers.py**: Fixed 5 issues
  - Removed unused imports (`timedelta`, `deque`)
  - Added None checks for timestamps before operations
  - Fixed return type annotation to `Dict[str, Any]`

- **helper.py**: Fixed 13 issues
  - Fixed matplotlib type annotations (`plt.Figure` → `Figure`, `plt.Axes` → `Axes`)
  - Added `# type: ignore` for 3D axes methods not recognized by type checker
  - Fixed colormap access with proper type handling

- **precision_analysis.py**: Fixed 18 issues
  - Fixed f-string formatting issues
  - Added `# type: ignore` for h5py and scipy type checker limitations
  - Added proper type coercion for numpy types

- **plotly_visualization.py**: Fixed 23 issues
  - Removed 5 unused imports (`Tuple`, `Any`, `json`, `logging`, `pio`)
  - Fixed 2 unused variables in CLI functions (`figures`, `fig_anim`)
  - Added `# type: ignore` for 13 h5py type checker limitations
  - Fixed `kaleido` import warning with proper annotation
  - Fixed `base_name` potentially unbound issue
  - Added assertion for `trajectory_name` type safety
  - Fixed Plotly frames attribute access

- **qualisys.py**: Fixed 22 issues
  - Removed 1 unused variable (`num_bodies`)
  - Added `# type: ignore` for 13 scipy.io/h5py type checker limitations
  - Added `# type: ignore` for 8 positions/rotations subscript operations

#### Test Suite (`tests/`)
- **test_core.py**: Fixed 2 type assignment issues
  - Added `# type: ignore` for test mock assignments where `DummyMotionData` is used

- **test_helper.py**: Fixed 8 issues
  - Added `# type: ignore` for h5py type checker limitations in test assertions

- **test_qualisys.py**: Fixed 2 issues
  - Added `# type: ignore` for `.shape` attribute access on test data

### Improved
- Enhanced code quality with consistent type annotations across the entire package
- Improved error handling with proper None checks and runtime validations
- Better separation of streaming vs offline API requirements
- All type checker errors resolved (80+ issues fixed)
- All 28 unit tests passing successfully

### Technical Details
- Total issues resolved: ~80+ across 12 files
- Type checker: Pylance/Pyright
- Test coverage: 28/28 tests passing (100%)
- Python compatibility: 3.13+

## [1.0.3] - 2025-06-03

### Added
- Initial public release
- Core jaw motion analysis framework
- Qualisys motion capture integration (offline and streaming)
- Calibration and registration tools
- Precision analysis utilities
- Interactive 3D visualization with Plotly
- Comprehensive test suite

### Features
- Modular architecture for motion capture data processing
- Support for offline (.mat files) and real-time streaming (QTM RT protocol, not yet tested)
- Automatic calibration point detection and validation (not yet tested)
- Rigid body transformation analysis
- Low-pass filtering and frequency analysis
- HDF5 export with metadata preservation
- Interactive and static visualization options
- LaTeX-ready figure export

---

## Version History

- **1.0.4** (2025-10-16): Major code quality improvements, type safety enhancements, all type errors resolved
- **1.0.3** (2025-06-03): Initial public release

[1.0.4]: https://github.com/paulotto/jaw_tracking_system/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/paulotto/jaw_tracking_system/releases/tag/v1.0.3
