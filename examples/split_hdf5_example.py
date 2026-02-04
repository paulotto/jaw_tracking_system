#!/usr/bin/env python3

"""
Example script demonstrating how to split an HDF5 file by sub-experiments.

This script shows how to:
1. Load sub-experiment definitions from a config file or define them manually
2. Split a large HDF5 file into smaller files based on frame intervals
3. Verify the split files were created correctly

Usage:
    python split_hdf5_example.py <path_to_hdf5_file> [config_file]
"""

__author__ = "Paul-Otto Müller"
__copyright__ = "Copyright 2026, Paul-Otto Müller"
__credits__ = ["Paul-Otto Müller"]
__license__ = "CC BY-NC-SA 4.0"
__version__ = "1.1.1"
__maintainer__ = "Paul-Otto Müller"
__status__ = "Development"
__date__ = "04.02.2026"
__url__ = "https://github.com/paulotto/jaw_tracking_system"

import sys
from pathlib import Path

# Add parent directory to path if jts module is not installed
try:
    import jts.helper as hlp
except ModuleNotFoundError:
    script_dir = Path(__file__).resolve().parent
    parent_dir = script_dir.parent
    sys.path.insert(0, str(parent_dir))
    import jts.helper as hlp


def main():
    """Main function to demonstrate HDF5 splitting."""

    # Check if HDF5 file path was provided
    if len(sys.argv) < 2:
        print("Usage: python split_hdf5_example.py <path_to_hdf5_file> [config_file]")
        print("\nExample:")
        print("  python split_hdf5_example.py output/jaw_motion.h5")
        print("  python split_hdf5_example.py output/jaw_motion.h5 config/config.json")
        sys.exit(1)

    hdf5_file = Path(sys.argv[1])

    if not hdf5_file.exists():
        print(f"Error: File not found: {hdf5_file}")
        sys.exit(1)

    print("=" * 80)
    print("HDF5 File Splitting Example")
    print("=" * 80)
    print()

    # ========================================================================
    # OPTION 1: Load sub-experiments from config file
    # ========================================================================
    config_file_path = None
    if len(sys.argv) >= 3:
        config_file_path = Path(sys.argv[2])

        if not config_file_path.exists():
            print(f"Error: Config file not found: {config_file_path}")
            sys.exit(1)

        print(f"Will load sub-experiments from config: {config_file_path}")

    # ========================================================================
    # OPTION 2: Define sub-experiments manually (if no config provided)
    # ========================================================================
    if config_file_path is None:
        print("No config file provided - defining sub-experiments manually")

        # Define sub-experiments with frame intervals
        # Format: 'name': [start_frame, end_frame] or 'name': [[s1,e1], [s2,e2], ...]
        sub_experiments = {
            "open_close": [15300, 18400],  # Opening/closing motion
            "left_right": [20050, 21850],  # Lateral movements
            "protrusion_retrusion": [21851, 23950],  # Forward/backward motion
            "chewing": [24400, 26051],  # Chewing motion
            "complex_motion": [  # Multiple intervals concatenated
                [27000, 27500],
                [28000, 28500],
                [29000, 29500],
            ],
        }

        print("\nSub-experiments to extract:")
        for name, intervals in sub_experiments.items():
            if isinstance(intervals[0], list):
                print(f"  {name}: {len(intervals)} intervals")
                for i, interval in enumerate(intervals):
                    print(f"    {i + 1}. [{interval[0]}, {interval[1]}]")
            else:
                print(f"  {name}: [{intervals[0]}, {intervals[1]}]")
    else:
        # Will be loaded from config by the split function
        sub_experiments = None
        print("\nSub-experiments will be loaded from config file")

    # ========================================================================
    # SPLIT THE HDF5 FILE
    # ========================================================================
    print("\n" + "=" * 80)
    print("Splitting HDF5 file by sub-experiments...")
    print("=" * 80)
    print()

    # Create output directory
    output_dir = hdf5_file.parent / "sub_experiments"

    # Split the file - using either config_file or manual sub_experiments
    # NOTE: When using config_file, frame_offset is automatically detected
    # from 'analysis.experiment.frame_interval[0]' if present in the config.
    # This handles cases where HDF5 frames are renumbered (e.g., [0-11700])
    # but sub-experiments use original frame numbers (e.g., [15300-27000]).
    if config_file_path is not None:
        output_files = hlp.split_hdf5_by_sub_experiments(
            hdf5_file,
            config_file=config_file_path,
            output_dir=output_dir,
            copy_all_groups=True,
        )
    else:
        # Manual mode - you can also specify frame_offset if needed:
        # frame_offset=15300  # Subtract this from all frame numbers
        output_files = hlp.split_hdf5_by_sub_experiments(
            hdf5_file,
            sub_experiments=sub_experiments,
            output_dir=output_dir,
            copy_all_groups=True,
        )

    # ========================================================================
    # VERIFY THE SPLIT FILES
    # ========================================================================
    print("\n" + "=" * 80)
    print("Verifying split files...")
    print("=" * 80)
    print()

    for sub_name, output_file in output_files.items():
        print(f"\n{sub_name}: {output_file.name}")
        print("-" * 40)

        # Inspect the split file
        info = hlp.inspect_hdf5(output_file, verbose=False)

        for group_name, group_info in info.items():
            print(f"  {group_name}:")
            print(f"    Frames: {group_info['num_frames']}")
            
            # Calculate duration if we have both num_frames and sample_rate
            if group_info['num_frames'] != 'N/A' and group_info['sample_rate'] != 'N/A':
                duration = group_info['num_frames'] / group_info['sample_rate']
                print(f"    Duration: {duration:.2f} s")
            
            print(f"    Sample rate: {group_info['sample_rate']} Hz")
            print(f"    Unit: {group_info['unit']}")
            print(f"    Rotation format: {group_info['rotation_format']}")
            
            if group_info['derivative_order'] > 0:
                print(f"    Derivatives: order {group_info['derivative_order']}")

    print("\n" + "=" * 80)
    print(f"Successfully split into {len(output_files)} files!")
    print(f"Output directory: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
