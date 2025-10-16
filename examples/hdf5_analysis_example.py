#!/usr/bin/env python3

"""
Example script demonstrating HDF5 file inspection, loading, and visualization.

This script shows how to:
1. Inspect existing HDF5 files created by the jaw tracking system
2. Load transformation data programmatically
3. Visualize trajectories in 3D
4. Compare raw vs smoothed trajectories

Usage:
    python hdf5_analysis_example.py <path_to_hdf5_file>
"""

__author__ = "Paul-Otto Müller"
__copyright__ = "Copyright 2025, Paul-Otto Müller"
__credits__ = ["Paul-Otto Müller"]
__license__ = "CC BY-NC-SA 4.0"
__version__ = "1.1.0"
__maintainer__ = "Paul-Otto Müller"
__status__ = "Development"
__date__ = '16.10.2025'
__url__ = "https://github.com/paulotto/jaw_tracking_system"

import sys
from pathlib import Path
import matplotlib.pyplot as plt

# Add parent directory to path if jts module is not installed
try:
    import jts.helper as hlp
except ModuleNotFoundError:
    # Add the parent directory to the Python path
    script_dir = Path(__file__).resolve().parent
    parent_dir = script_dir.parent
    sys.path.insert(0, str(parent_dir))
    import jts.helper as hlp


def main():
    """Main function to demonstrate HDF5 analysis capabilities."""
    
    # Check if HDF5 file path was provided
    if len(sys.argv) < 2:
        print("Usage: python hdf5_analysis_example.py <path_to_hdf5_file>")
        print("\nExample:")
        print("  python hdf5_analysis_example.py output/jaw_motion.h5")
        sys.exit(1)
    
    hdf5_file = Path(sys.argv[1])
    
    if not hdf5_file.exists():
        print(f"Error: File not found: {hdf5_file}")
        sys.exit(1)
    
    print("="*80)
    print("HDF5 Trajectory Analysis Example")
    print("="*80)
    print()
    
    # ========================================================================
    # 1. INSPECT THE HDF5 FILE
    # ========================================================================
    print("STEP 1: Inspecting HDF5 file structure")
    print("-" * 80)
    
    _info = hlp.inspect_hdf5(hdf5_file, verbose=True)
    
    # ========================================================================
    # 2. LOAD TRANSFORMATION DATA
    # ========================================================================
    print("\nSTEP 2: Loading transformation data")
    print("-" * 80)
    
    data = hlp.load_hdf5_transformations(hdf5_file, as_matrices=True)
    
    for group_name, group_data in data.items():
        print(f"\nGroup: {group_name}")
        print(f"  Transformations shape: {group_data['transformations'].shape}")
        print(f"  Sample rate: {group_data['sample_rate']} Hz")
        print(f"  Unit: {group_data['unit']}")
        print(f"  Duration: {len(group_data['transformations']) / group_data['sample_rate']:.2f} seconds")
        
        # Calculate trajectory statistics
        translations = group_data['translations']
        print("  Translation range:")
        print(f"    X: [{translations[:, 0].min():.2f}, {translations[:, 0].max():.2f}] {group_data['unit']}")
        print(f"    Y: [{translations[:, 1].min():.2f}, {translations[:, 1].max():.2f}] {group_data['unit']}")
        print(f"    Z: [{translations[:, 2].min():.2f}, {translations[:, 2].max():.2f}] {group_data['unit']}")
    
    # ========================================================================
    # 3. VISUALIZE 3D TRAJECTORY
    # ========================================================================
    print("\n\nSTEP 3: Visualizing 3D trajectory")
    print("-" * 80)
    
    # Get the first (or only) group for visualization
    first_group = list(data.keys())[0]
    
    fig, ax = hlp.visualize_hdf5_trajectory(
        hdf5_file,
        group_name=first_group,
        frame_step=500,  # Show coordinate frame every 500 frames (~24 frames for better visibility)
        show_frames=True,
        frame_scale=None  # Auto-calculate scale based on trajectory size (3% of trajectory range)
    )
    
    print(f"Created 3D trajectory plot for: {first_group}")
    
    # ========================================================================
    # 4. COMPARE MULTIPLE TRAJECTORIES (if available)
    # ========================================================================
    if len(data) > 1:
        print("\n\nSTEP 4: Comparing trajectories")
        print("-" * 80)
        
        group_names = list(data.keys())
        print(f"Comparing groups: {group_names}")
        
        # Compare translations
        fig_trans, axes_trans = hlp.compare_hdf5_trajectories(
            hdf5_file,
            group_names=group_names,
            component='translations'
        )
        
        # Compare rotations (Euler angles)
        fig_rot, axes_rot = hlp.compare_hdf5_trajectories(
            hdf5_file,
            group_names=group_names,
            component='rotations_euler'
        )
        
        print("Created comparison plots for translations and rotations")
    else:
        print("\n\nSTEP 4: Skipped (only one trajectory group found)")
    
    # ========================================================================
    # 5. SHOW ALL PLOTS
    # ========================================================================
    print("\n" + "="*80)
    print("Displaying plots... Close windows to exit.")
    print("="*80)
    plt.show()


if __name__ == "__main__":
    main()
