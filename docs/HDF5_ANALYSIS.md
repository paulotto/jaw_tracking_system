# HDF5 File Analysis Functions

This document describes the comprehensive HDF5 inspection, loading, and visualization functions available in `jts.helper`.

## Overview

The jaw tracking system saves trajectory data in HDF5 format for efficient storage and analysis. The following functions allow you to work with these files programmatically:

1. **`inspect_hdf5()`** - Inspect file structure and metadata
2. **`load_hdf5_transformations()`** - Load transformation data into memory
3. **`visualize_hdf5_trajectory()`** - Create 3D trajectory visualizations
4. **`compare_hdf5_trajectories()`** - Compare multiple trajectories (raw vs smoothed)

## Functions

### `inspect_hdf5()`

Inspect an HDF5 file and return comprehensive information about its contents.

**Signature:**
```python
def inspect_hdf5(filename: Union[str, Path], 
                 verbose: bool = True) -> Dict[str, Dict[str, any]]
```

**Parameters:**
- `filename`: Path to HDF5 file
- `verbose`: If True, print detailed information to console

**Returns:**
Dictionary with structure information for each group

**Example:**
```python
import jts.helper as hlp

# Inspect file and print summary
info = hlp.inspect_hdf5('jaw_motion.h5')

# Access specific information
num_frames = info['T_model_origin_mand_landmark_t']['num_frames']
sample_rate = info['T_model_origin_mand_landmark_t']['sample_rate']
print(f"Loaded {num_frames} frames at {sample_rate} Hz")
```

**Output structure:**
```python
{
    'group_name': {
        'metadata': str,           # Configuration and processing info
        'sample_rate': float,      # Sample rate in Hz
        'unit': str,               # Unit of translations (e.g., 'mm')
        'num_frames': int,         # Number of frames
        'rotation_format': str,    # 'quaternion' or 'matrix'
        'derivative_order': int,   # Maximum derivative order stored
        'datasets': {              # Information about each dataset
            'translations': {'shape': tuple, 'dtype': str, 'size_mb': float},
            'rotations': {'shape': tuple, 'dtype': str, 'size_mb': float},
            ...
        }
    }
}
```

---

### `load_hdf5_transformations()`

Load transformation data from HDF5 file into memory.

**Signature:**
```python
def load_hdf5_transformations(filename: Union[str, Path],
                              group_name: Optional[str] = None,
                              as_matrices: bool = True) -> Dict[str, any]
```

**Parameters:**
- `filename`: Path to HDF5 file
- `group_name`: Specific group to load (None = load all groups)
- `as_matrices`: If True, convert quaternions to rotation matrices and construct 4x4 transformation matrices

**Returns:**
Dictionary containing transformation data for each group:
```python
{
    'group_name': {
        'transformations': np.ndarray,  # Shape (N, 4, 4) - Homogeneous transformation matrices
        'translations': np.ndarray,     # Shape (N, 3) - Translation vectors
        'rotations': np.ndarray,        # Shape (N, 3, 3) or (N, 4) - Rotation matrices or quaternions
        'sample_rate': float,           # Sample rate in Hz
        'unit': str,                    # Unit of translations
        'metadata': str,                # Metadata string
        'derivatives': dict             # Optional derivatives if stored
    }
}
```

**Example:**
```python
import jts.helper as hlp
import numpy as np

# Load all transformation groups
data = hlp.load_hdf5_transformations('jaw_motion.h5')

# Access specific group
raw_data = data['T_model_origin_mand_landmark_t']
transforms = raw_data['transformations']  # (N, 4, 4) matrices
translations = raw_data['translations']   # (N, 3) vectors
rotations = raw_data['rotations']         # (N, 3, 3) matrices

# Extract position at frame 100
position_100 = transforms[100, :3, 3]
print(f"Position at frame 100: {position_100} {raw_data['unit']}")

# Access translational derivatives
if 'translational_velocity' in raw_data['derivatives']:
    trans_vel = raw_data['derivatives']['translational_velocity']
    vel_magnitude = np.linalg.norm(trans_vel, axis=1)
    print(f"Max translational velocity: {vel_magnitude.max():.3f} {raw_data['unit']}/s")

if 'translational_acceleration' in raw_data['derivatives']:
    trans_acc = raw_data['derivatives']['translational_acceleration']
    acc_magnitude = np.linalg.norm(trans_acc, axis=1)
    print(f"Max translational acceleration: {acc_magnitude.max():.3f} {raw_data['unit']}/s²")

# Access rotational derivatives
if 'angular_velocity' in raw_data['derivatives']:
    ang_vel = raw_data['derivatives']['angular_velocity']
    ang_vel_mag = np.linalg.norm(ang_vel, axis=1)
    print(f"Max angular velocity: {ang_vel_mag.max():.3f} rad/s")

if 'angular_acceleration' in raw_data['derivatives']:
    ang_acc = raw_data['derivatives']['angular_acceleration']
    ang_acc_mag = np.linalg.norm(ang_acc, axis=1)
    print(f"Max angular acceleration: {ang_acc_mag.max():.3f} rad/s²")

# Load only quaternions (don't convert to matrices)
data_quat = hlp.load_hdf5_transformations('jaw_motion.h5', as_matrices=False)
quaternions = data_quat['T_model_origin_mand_landmark_t']['rotations']  # (N, 4)
```

---

#### `visualize_hdf5_trajectory`

Visualize a 3D trajectory from an HDF5 file with optional coordinate frames.

**Signature:**
```python
def visualize_hdf5_trajectory(
    filename: Union[str, Path],
    group_name: Optional[str] = None,
    frame_step: int = 100,
    show_frames: bool = True,
    frame_scale: Optional[float] = None,
    save_path: Optional[Union[str, Path]] = None,
    title: Optional[str] = None
) -> Tuple[Figure, Axes]
```

**Parameters:**
- `filename`: Path to HDF5 file
- `group_name`: Specific group to visualize (if `None`, uses first group)
- `frame_step`: Show coordinate frame every N frames (default: 100)
- `show_frames`: Whether to show coordinate frames along trajectory (default: `True`)
- `frame_scale`: Scale factor for coordinate frame arrows. If `None` (default), automatically calculated as 3% of trajectory range for optimal visualization
- `save_path`: Optional path to save the figure
- `title`: Plot title (auto-generated if `None`)

**Returns:**
- `(fig, ax)`: Matplotlib Figure and Axes objects

**Example:**
```python
import jts.helper as hlp
import matplotlib.pyplot as plt

# Create 3D visualization with auto-scaled coordinate frames
fig, ax = hlp.visualize_hdf5_trajectory(
    'jaw_motion.h5',
    group_name='T_model_origin_mand_landmark_t',
    frame_step=200,       # Show coordinate frame every 200 frames
    show_frames=True,
    frame_scale=None,     # Auto-calculate optimal scale (recommended)
    save_path='trajectory_3d.png'
)

plt.show()
```

**Features:**
- Trajectory path plotted as a 3D line
- Start point (green circle) and end point (red square) markers
- Optional coordinate frames showing orientation at regular intervals
- RGB arrows representing X, Y, Z axes of the coordinate frame
- Equal aspect ratio for accurate spatial representation
- Automatic scaling based on trajectory extent (when `frame_scale=None`)

---

### `compare_hdf5_trajectories()`

Compare multiple trajectories from the same HDF5 file (e.g., raw vs smoothed).

**Signature:**
```python
def compare_hdf5_trajectories(filename: Union[str, Path],
                              group_names: Optional[List[str]] = None,
                              component: str = 'translations',
                              save_path: Optional[Union[str, Path]] = None) -> Tuple[Figure, Axes]
```

**Parameters:**
- `filename`: Path to HDF5 file
- `group_names`: List of groups to compare (None = all groups)
- `component`: What to plot:
  - `'translations'` - X, Y, Z translations over time
  - `'rotations_euler'` - Roll, Pitch, Yaw (Euler angles) over time
  - `'rotations_rotvec'` - Rotation vector components over time
  - `'translational_velocity'` - Linear velocity (1st derivative)
  - `'translational_acceleration'` - Linear acceleration (2nd derivative)
  - `'angular_velocity'` - Angular velocity (1st rotational derivative)
  - `'angular_acceleration'` - Angular acceleration (2nd rotational derivative)
- `save_path`: Optional path to save the figure

**Returns:**
Matplotlib Figure and Axes objects (3 subplots)

**Example:**
```python
import jts.helper as hlp
import matplotlib.pyplot as plt

# Compare raw and smoothed trajectories - translations
fig1, axes1 = hlp.compare_hdf5_trajectories(
    'jaw_motion.h5',
    group_names=[
        'T_model_origin_mand_landmark_t',        # Raw trajectory
        'T_model_origin_mand_landmark_t_smooth'  # Smoothed trajectory
    ],
    component='translations',
    save_path='comparison_translations.png'
)

# Compare rotations (Euler angles)
fig2, axes2 = hlp.compare_hdf5_trajectories(
    'jaw_motion.h5',
    component='rotations_euler',
    save_path='comparison_rotations.png'
)

# Compare translational velocities
fig3, axes3 = hlp.compare_hdf5_trajectories(
    'jaw_motion.h5',
    component='translational_velocity',
    save_path='comparison_velocity.png'
)

# Compare angular velocities
fig4, axes4 = hlp.compare_hdf5_trajectories(
    'jaw_motion.h5',
    component='angular_velocity',
    save_path='comparison_angular_velocity.png'
)

plt.show()
```

**Features:**
- Side-by-side comparison of multiple trajectory groups
- Time-aligned plots for easy comparison
- Separate subplots for X/Y/Z components
- Automatic color coding for different trajectories
- Grid for easy reading
- Time axis in seconds (computed from sample rate)

---

## Complete Workflow Example

Here's a complete example showing a typical analysis workflow:

```python
import jts.helper as hlp
import matplotlib.pyplot as plt
from pathlib import Path

# Define file path
hdf5_file = Path('output/jaw_motion.h5')

# Step 1: Inspect the file
print("=" * 80)
print("STEP 1: Inspecting HDF5 file")
print("=" * 80)
info = hlp.inspect_hdf5(hdf5_file, verbose=True)

# Step 2: Load the data
print("\n" + "=" * 80)
print("STEP 2: Loading transformation data")
print("=" * 80)
data = hlp.load_hdf5_transformations(hdf5_file)

for group_name, group_data in data.items():
    print(f"\nGroup: {group_name}")
    print(f"  Frames: {len(group_data['transformations'])}")
    print(f"  Duration: {len(group_data['transformations']) / group_data['sample_rate']:.2f} s")

# Step 3: Visualize in 3D
print("\n" + "=" * 80)
print("STEP 3: Creating 3D visualization")
print("=" * 80)
fig1, ax1 = hlp.visualize_hdf5_trajectory(
    hdf5_file,
    frame_step=100,
    save_path='trajectory_3d.png'
)

# Step 4: Compare trajectories (if multiple groups exist)
if len(data) > 1:
    print("\n" + "=" * 80)
    print("STEP 4: Comparing trajectories")
    print("=" * 80)
    
    fig2, axes2 = hlp.compare_hdf5_trajectories(
        hdf5_file,
        component='translations',
        save_path='comparison_translations.png'
    )
    
    fig3, axes3 = hlp.compare_hdf5_trajectories(
        hdf5_file,
        component='rotations_euler',
        save_path='comparison_rotations.png'
    )

# Display all plots
plt.show()
```

---

## HDF5 File Structure

The jaw tracking system stores data in the following HDF5 structure:

```
jaw_motion.h5
├── T_model_origin_mand_landmark_t/          # Raw trajectory
│   ├── translations (N, 3)                  # Translation vectors [mm]
│   ├── rotations (N, 4) or (N, 3, 3)       # Quaternions or rotation matrices
│   ├── translational_derivative_order_1     # Velocity (if requested)
│   ├── translational_derivative_order_2     # Acceleration (if requested)
│   ├── rotational_derivative_order_1        # Angular velocity (if requested)
│   └── rotational_derivative_order_2        # Angular acceleration (if requested)
│
└── T_model_origin_mand_landmark_t_smooth/   # Smoothed trajectory (if enabled)
    ├── translations (N, 3)
    ├── rotations (N, 4) or (N, 3, 3)
    ├── ... (derivatives if requested)
```

**Group Attributes:**
- `metadata`: JSON string with configuration and processing parameters
- `sample_rate`: Sample rate in Hz (e.g., 200.0)
- `unit`: Unit of translations (e.g., 'mm', 'm')

**Dataset Information:**
- `translations`: (N, 3) array of translation vectors
- `rotations`: (N, 4) quaternions [w, x, y, z] or (N, 3, 3) rotation matrices
- `translational_derivative_order_k`: (N, 3) kth derivative of translation
- `rotational_derivative_order_k`: (N, 4) or (N, 3, 3) kth derivative of rotation

---

## Command-Line Usage

A complete example script is provided in `examples/hdf5_analysis_example.py`:

```bash
# Basic usage
python examples/hdf5_analysis_example.py output/jaw_motion.h5

# The script will:
# 1. Inspect the file structure
# 2. Load all transformation data
# 3. Create 3D trajectory visualization
# 4. Compare raw vs smoothed trajectories (if available)
# 5. Display all plots
```

---

## Tips and Best Practices

1. **Memory Management**: Large HDF5 files can consume significant memory. Use the `group_name` parameter to load only specific groups if needed.

2. **Quaternion vs Matrix**: Set `as_matrices=False` if you need quaternions for specific calculations. Matrices are more convenient for most visualization tasks.

3. **Frame Step for Coordinate Frames**: When visualizing trajectories with coordinate frames:
   - **Small datasets (<100 frames)**: Use `frame_step=5-10`
   - **Medium datasets (100-1000 frames)**: Use `frame_step=50-100`
   - **Large datasets (>1000 frames)**: Use `frame_step=200-500` or more
   - **Rule of thumb**: Aim for 10-30 coordinate frames total for clarity
   - **Example**: For 11,701 frames, use `frame_step=500` → ~23 frames (good)
   - **Too cluttered?**: Set `show_frames=False` to hide coordinate frames entirely

4. **Frame Scale**: The coordinate frame size is automatically calculated by default (`frame_scale=None`):
   - **Auto-scaling (recommended)**: Set `frame_scale=None` to automatically calculate as 3% of trajectory range
   - **Manual override**: Adjust `frame_scale` based on your trajectory extent:
     - Trajectory extent 0-10mm: `frame_scale=1.0-2.0`
     - Trajectory extent 10-100mm: `frame_scale=5.0-10.0`
     - Trajectory extent >100mm: `frame_scale=10.0-20.0`
   - **Tip**: Use auto-scaling unless you have specific visualization requirements

5. **Derivatives**: If derivatives are stored in the HDF5 file, they will be loaded automatically in the `derivatives` dictionary with convenient aliases:
   - **Translational derivatives:**
     - `'translational_velocity'` - First derivative of translation (linear velocity)
     - `'translational_acceleration'` - Second derivative of translation (linear acceleration)
   - **Rotational derivatives:**
     - `'angular_velocity'` (or `'rotational_velocity'`) - First derivative of rotation
     - `'angular_acceleration'` (or `'rotational_acceleration'`) - Second derivative of rotation
   - **Backward compatibility:** Generic aliases `'velocity'` and `'acceleration'` point to translational derivatives
   - **Original keys:** All original dataset names are preserved (e.g., `'translational_derivative_order_1'`)
   
   Example:
   ```python
   data = hlp.load_hdf5_transformations('jaw_motion.h5')
   group_data = data['T_model_origin_mand_landmark_t']
   
   # Translational derivatives
   if 'translational_velocity' in group_data['derivatives']:
       trans_vel = group_data['derivatives']['translational_velocity']
       vel_mag = np.linalg.norm(trans_vel, axis=1)
       print(f"Max translational velocity: {vel_mag.max():.3f} m/s")
   
   # Rotational derivatives
   if 'angular_velocity' in group_data['derivatives']:
       ang_vel = group_data['derivatives']['angular_velocity']
       ang_vel_mag = np.linalg.norm(ang_vel, axis=1)
       print(f"Max angular velocity: {ang_vel_mag.max():.3f} rad/s")
   ```

6. **Time Synchronization**: The sample rate is stored in the HDF5 file, allowing you to convert frame indices to timestamps:
   ```python
   data = hlp.load_hdf5_transformations('jaw_motion.h5')
   sample_rate = data['T_model_origin_mand_landmark_t']['sample_rate']
   time = np.arange(len(data['T_model_origin_mand_landmark_t']['translations'])) / sample_rate
   ```

7. **Export Formats**: Use `save_path` parameter to save plots in various formats:
   - PNG: `save_path='plot.png'` (raster, good for presentations)
   - PDF: `save_path='plot.pdf'` (vector, good for publications)
   - SVG: `save_path='plot.svg'` (vector, editable in Inkscape/Illustrator)

---

## See Also

- `jts.plotly_visualization.JawMotionVisualizer`: For interactive Plotly-based visualizations
- `jts.helper.store_transformations()`: For creating HDF5 files programmatically
- Example script: `examples/hdf5_analysis_example.py`
