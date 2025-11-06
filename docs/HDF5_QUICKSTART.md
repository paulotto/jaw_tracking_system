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

# Access derivatives (if available) with convenient aliases
derivatives = data['T_model_origin_mand_landmark_t']['derivatives']

# Translational derivatives
if 'translational_velocity' in derivatives:
    trans_vel = derivatives['translational_velocity']  # (N, 3)
if 'translational_acceleration' in derivatives:
    trans_acc = derivatives['translational_acceleration']  # (N, 3)

# Rotational derivatives  
if 'angular_velocity' in derivatives:
    ang_vel = derivatives['angular_velocity']  # (N, 3) or (N, 4)
if 'angular_acceleration' in derivatives:
    ang_acc = derivatives['angular_acceleration']  # (N, 3) or (N, 4)
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

# Compare derivatives
hlp.compare_hdf5_trajectories(
    'jaw_motion.h5',
    component='translational_velocity',
    save_path='comparison_velocity.png'
)
plt.show()
```

### 5. Split by sub-experiments
```python
# Option 1: Direct definition (no frame offset needed)
sub_exps = {
    'first_half': [0, 100],
    'second_half': [100, 200]
}
output_files = hlp.split_hdf5_by_sub_experiments(
    'jaw_motion.h5',
    sub_experiments=sub_exps,
    output_dir='sub_experiments/'
)

# Option 2: With frame offset (when HDF5 frames don't match interval numbering)
# Example: HDF5 has frames [0-11700] but sub-experiments use original [15300-27000]
sub_exps = {
    'open_close': [15300, 18400],
    'chewing': [24400, 26051]
}
output_files = hlp.split_hdf5_by_sub_experiments(
    'jaw_motion.h5',
    sub_experiments=sub_exps,
    frame_offset=15300,  # Automatically adjusts intervals
    output_dir='sub_experiments/'
)

# Option 3: From config file (auto-detects frame_offset)
# Config has: "frame_interval": [15300, 27000]
# Automatically uses 15300 as offset for sub_experiments
output_files = hlp.split_hdf5_by_sub_experiments(
    'jaw_motion.h5',
    config_file='config/config.json',  # Frame offset auto-detected!
    output_dir='sub_experiments/'
)
```

## Command-Line Tools

```bash
# Analyze HDF5 file
python examples/hdf5_analysis_example.py output/jaw_motion.h5

# Split by sub-experiments
python examples/split_hdf5_example.py jaw_motion.h5 config/config.json
```

## Full Documentation

See `docs/HDF5_ANALYSIS.md` for complete API reference and examples.
