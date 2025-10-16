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
import numpy as np
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
        
        # Check for derivatives
        if 'derivatives' in group_data and group_data['derivatives']:
            print("  Derivatives available:")
            
            # Translational derivatives
            if 'translational_velocity' in group_data['derivatives']:
                trans_vel = group_data['derivatives']['translational_velocity']
                vel_magnitude = np.linalg.norm(trans_vel, axis=1)
                print("    - Translational velocity (1st derivative):")
                print(f"      Shape: {trans_vel.shape}")
                print(f"      Magnitude range: [{vel_magnitude.min():.4f}, {vel_magnitude.max():.4f}] {group_data['unit']}/s")
                print(f"      Mean magnitude: {vel_magnitude.mean():.4f} {group_data['unit']}/s")
            
            if 'translational_acceleration' in group_data['derivatives']:
                trans_acc = group_data['derivatives']['translational_acceleration']
                acc_magnitude = np.linalg.norm(trans_acc, axis=1)
                print("    - Translational acceleration (2nd derivative):")
                print(f"      Shape: {trans_acc.shape}")
                print(f"      Magnitude range: [{acc_magnitude.min():.4f}, {acc_magnitude.max():.4f}] {group_data['unit']}/s²")
                print(f"      Mean magnitude: {acc_magnitude.mean():.4f} {group_data['unit']}/s²")
            
            # Rotational derivatives
            if 'angular_velocity' in group_data['derivatives']:
                ang_vel = group_data['derivatives']['angular_velocity']
                ang_vel_magnitude = np.linalg.norm(ang_vel, axis=1) if ang_vel.ndim > 1 else np.abs(ang_vel)
                print("    - Angular velocity (1st rotational derivative):")
                print(f"      Shape: {ang_vel.shape}")
                print(f"      Magnitude range: [{ang_vel_magnitude.min():.4f}, {ang_vel_magnitude.max():.4f}] rad/s")
                print(f"      Mean magnitude: {ang_vel_magnitude.mean():.4f} rad/s")
            
            if 'angular_acceleration' in group_data['derivatives']:
                ang_acc = group_data['derivatives']['angular_acceleration']
                ang_acc_magnitude = np.linalg.norm(ang_acc, axis=1) if ang_acc.ndim > 1 else np.abs(ang_acc)
                print("    - Angular acceleration (2nd rotational derivative):")
                print(f"      Shape: {ang_acc.shape}")
                print(f"      Magnitude range: [{ang_acc_magnitude.min():.4f}, {ang_acc_magnitude.max():.4f}] rad/s²")
                print(f"      Mean magnitude: {ang_acc_magnitude.mean():.4f} rad/s²")
            
            # Show any other derivatives
            other_derivs = [k for k in group_data['derivatives'].keys() 
                          if k not in ['translational_velocity', 'translational_acceleration',
                                      'angular_velocity', 'angular_acceleration',
                                      'velocity', 'acceleration',  # backward compat aliases
                                      'rotational_velocity', 'rotational_acceleration']]  # other aliases
            if other_derivs:
                print(f"    - Other derivatives: {', '.join(other_derivs)}")
        else:
            print("  Derivatives: None")
    
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
        
        # Compare translational velocities (if derivatives available)
        first_group_data = data[group_names[0]]
        if 'derivatives' in first_group_data and 'translational_velocity' in first_group_data['derivatives']:
            fig_vel, axes_vel = hlp.compare_hdf5_trajectories(
                hdf5_file,
                group_names=group_names,
                component='translational_velocity'
            )
            print("Created comparison plots for translations, rotations, and translational velocity")
            
            # Compare angular velocities
            if 'angular_velocity' in first_group_data['derivatives']:
                fig_ang_vel, axes_ang_vel = hlp.compare_hdf5_trajectories(
                    hdf5_file,
                    group_names=group_names,
                    component='angular_velocity'
                )
                print("Added comparison plot for angular velocity")
        else:
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
