# Quick Start: HDF5 Analysis Functions

## Installation
The functions are available in `jts.helper` module.

If you haven't installed the package yet, you can either:

**Option 1: Install the package**
```bash
pip install jaw-tracking-system
# or from source
pip install -e .
```

**Option 2: Add to Python path (for development)**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('/path/to/jaw_tracking_system')))
import jts.helper as hlp
```

**Note:** The example script `examples/hdf5_analysis_example.py` automatically handles both cases.

## Quick Usage

### 1. Inspect an HDF5 file
```python
import jts.helper as hlp

info = hlp.inspect_hdf5('jaw_motion.h5', verbose=True)
```

### 2. Load transformation data
```python
data = hlp.load_hdf5_transformations('jaw_motion.h5')

# Access data
transforms = data['T_model_origin_mand_landmark_t']['transformations']  # (N, 4, 4)
translations = data['T_model_origin_mand_landmark_t']['translations']   # (N, 3)
sample_rate = data['T_model_origin_mand_landmark_t']['sample_rate']
```

### 3. Visualize in 3D
```python
import matplotlib.pyplot as plt

fig, ax = hlp.visualize_hdf5_trajectory(
    'jaw_motion.h5',
    frame_step=100,
    save_path='trajectory.png'
)
plt.show()
```

### 4. Compare trajectories
```python
# Compare raw vs smoothed - translations
hlp.compare_hdf5_trajectories(
    'jaw_motion.h5',
    component='translations',
    save_path='comparison_trans.png'
)

# Compare rotations
hlp.compare_hdf5_trajectories(
    'jaw_motion.h5',
    component='rotations_euler',
    save_path='comparison_rot.png'
)
plt.show()
```

## Command-Line Tool

```bash
python examples/hdf5_analysis_example.py output/jaw_motion.h5
```

## Full Documentation

See `docs/HDF5_ANALYSIS.md` for complete API reference and examples.
