"""
Test suite for the jts.helper module.

This suite includes tests for:
- Transformation matrix construction
- Orthonormalization of rotation matrices
- Kabsch algorithm for point set alignment
- Transformation filtering
- Euler angle extraction from rotation matrices
- Relative rotation computation between quaternions
- Interval string conversion
"""

__author__ = "Paul-Otto Müller"
__copyright__ = "Copyright 2025, Paul-Otto Müller"
__credits__ = ["Paul-Otto Müller"]
__license__ = "GNU GPLv3"
__version__ = "1.1.0"
__maintainer__ = "Paul-Otto Müller"
__status__ = "Development"
__date__ = '16.10.2025'
__url__ = "https://github.com/paulotto/jaw_tracking_system"

import numpy as np

from jts import helper as hlp


def test_build_transform():
    """
    Test the build_transform function:
    - Checks that the returned transformation matrix has the correct shape.
    - Verifies that the translation and rotation components are correctly placed.
    - Ensures the homogeneous coordinate is set to 1.
    """
    pos = np.array([1.0, 2.0, 3.0])
    rot = np.eye(3)
    T = hlp.build_transform(pos, rot)
    assert T.shape == (4, 4)
    np.testing.assert_array_equal(T[:3, 3], pos)
    np.testing.assert_array_equal(T[:3, :3], rot)
    assert T[3, 3] == 1.0


def test_ensure_orthonormal():
    """
    Test the ensure_orthonormal function:
    - Checks that the output matrix is orthonormal (R @ R^T = I).
    - Ensures the determinant is close to 1 (proper rotation matrix).
    """
    mat = np.eye(3) + 0.01 * np.random.randn(3, 3)
    ortho = hlp.ensure_orthonormal(mat)
    np.testing.assert_allclose(ortho @ ortho.T, np.eye(3), atol=1e-7)
    assert np.isclose(np.linalg.det(ortho), 1.0, atol=1e-7)


def test_kabsch_algorithm():
    """
    Test the kabsch_algorithm function:
    - Uses two point sets related by a pure translation.
    - Checks that the estimated transform recovers the translation.
    """
    P = np.random.rand(5, 3)
    Q = P + np.array([1.0, 2.0, 3.0])  # pure translation
    T = hlp.kabsch_algorithm(P, Q)
    P_h = np.hstack([P, np.ones((P.shape[0], 1))])
    Q_est = (T @ P_h.T).T[:, :3]
    np.testing.assert_allclose(Q, Q_est, atol=1e-7)


def test_transformation_filter():
    """
    Test the TransformationFilter class:
    - Applies the filter to a sequence of transforms along a straight line.
    - Checks that the smoothed output is close to the original.
    - Verifies output shape.
    """
    N = 21
    T_seq = np.tile(np.eye(4), (N, 1, 1))
    T_seq[:, :3, 3] = np.linspace([0, 0, 0], [10, 0, 0], N)
    filt = hlp.TransformationFilter(window_length=11, poly_order=3)
    T_smooth = filt(T_seq)
    assert T_smooth.shape == (N, 4, 4)

    # Should be close to original for a straight line
    np.testing.assert_allclose(T_seq, T_smooth, atol=1e-2)


def test_rotation_matrix_to_euler_angles():
    """
    Test the rotation_matrix_to_euler_angles function:
    - Checks that the identity matrix yields zero roll, pitch, and yaw.
    """
    R_mat = np.eye(3)
    roll, pitch, yaw = hlp.rotation_matrix_to_euler_angles(R_mat)
    assert np.isclose(roll, 0)
    assert np.isclose(pitch, 0)
    assert np.isclose(yaw, 0)


def test_relative_rotation():
    """
    Test the relative_rotation function:
    - Computes the relative rotation between two quaternions.
    - Checks output shape and expected Euler angles for a 180-degree rotation about x.
    """
    q1 = np.array([1, 0, 0, 0])  # identity quaternion (w, x, y, z)
    q2 = np.array([0, 1, 0, 0])  # 180 deg about x
    q_rel, angles = hlp.relative_rotation(q1, q2, output_format="euler", scalar_first=True)
    assert q_rel.shape == (4,)
    assert angles.shape == (3,)

    # For 180 deg about x, expect roll ~180, pitch/yaw ~0 (modulo sign)
    assert np.isclose(np.abs(angles[0]), 180, atol=1)
    assert np.isclose(angles[1], 0, atol=1)
    assert np.isclose(angles[2], 0, atol=1)


def test_interval_to_string():
    """
    Test the interval_to_string function:
    - Checks that a tuple (5, 10) is converted to the string '5-10'.
    """
    assert hlp.interval_to_string((5, 10)) == '5-10'


def test_store_transformations_scale_and_unit(tmp_path):
    """
    Test that store_transformations applies scale_factor and unit correctly.
    """
    T = np.tile(np.eye(4), (2, 1, 1))
    T[0, :3, 3] = [1, 2, 3]
    T[1, :3, 3] = [4, 5, 6]
    out_file = tmp_path / "test.h5"
    hlp.store_transformations([T], [100], out_file, scale_factor=0.01, unit="cm")
    import h5py
    with h5py.File(out_file, 'r') as f:
        group = f['T_0']
        translations = group['translations'][:]  # type: ignore
        # Should be scaled by 0.01
        np.testing.assert_allclose(translations[0], [0.01, 0.02, 0.03])  # type: ignore
        np.testing.assert_allclose(translations[1], [0.04, 0.05, 0.06])  # type: ignore
        assert group.attrs['unit'] == 'cm'


def test_inspect_hdf5(tmp_path):
    """
    Test the inspect_hdf5 function:
    - Checks that file inspection returns correct structure information
    - Verifies metadata, sample rate, unit, and dataset information
    - Tests verbose and non-verbose modes
    """
    # Create test HDF5 file
    N = 50
    T_t = np.zeros((N, 4, 4))
    T_t[:, :3, :3] = np.eye(3)
    T_t[:, :3, 3] = np.random.randn(N, 3) * 10
    T_t[:, 3, 3] = 1.0
    
    test_file = tmp_path / "test_inspect.h5"
    hlp.store_transformations(
        [T_t], [200.0], test_file,
        metadata=['Test trajectory for inspection'],
        group_names=['test_group'],
        derivative_order=2
    )
    
    # Test non-verbose mode
    info = hlp.inspect_hdf5(test_file, verbose=False)
    
    assert 'test_group' in info
    assert info['test_group']['sample_rate'] == 200.0
    assert info['test_group']['num_frames'] == N
    assert info['test_group']['rotation_format'] == 'quaternion'
    assert info['test_group']['derivative_order'] == 2
    assert 'translations' in info['test_group']['datasets']
    assert 'rotations' in info['test_group']['datasets']
    
    # Test verbose mode (should not raise errors)
    info_verbose = hlp.inspect_hdf5(test_file, verbose=True)
    assert info_verbose == info


def test_load_hdf5_transformations_as_matrices(tmp_path):
    """
    Test load_hdf5_transformations with as_matrices=True:
    - Verifies that quaternions are converted to rotation matrices
    - Checks that 4x4 transformation matrices are constructed correctly
    - Ensures translations, rotations, and metadata are loaded properly
    """
    # Create test data
    N = 30
    T_t = np.zeros((N, 4, 4))
    for i in range(N):
        # Random rotation
        angle = i * 0.1
        rot = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
        T_t[i, :3, :3] = rot
        T_t[i, :3, 3] = [i, i*2, i*3]
        T_t[i, 3, 3] = 1.0
    
    test_file = tmp_path / "test_load_matrices.h5"
    hlp.store_transformations(
        [T_t], [100.0], test_file,
        metadata=['Test data'],
        group_names=['trajectory'],
        store_as_quaternion=True
    )
    
    # Load with as_matrices=True
    data = hlp.load_hdf5_transformations(test_file, as_matrices=True)
    
    assert 'trajectory' in data
    assert data['trajectory']['transformations'].shape == (N, 4, 4)
    assert data['trajectory']['translations'].shape == (N, 3)
    assert data['trajectory']['rotations'].shape == (N, 3, 3)
    assert data['trajectory']['sample_rate'] == 100.0
    assert data['trajectory']['metadata'] == 'Test data'
    
    # Check that transformations are close to original
    np.testing.assert_allclose(
        data['trajectory']['transformations'],
        T_t,
        rtol=1e-5, atol=1e-6
    )


def test_load_hdf5_transformations_as_quaternions(tmp_path):
    """
    Test load_hdf5_transformations with as_matrices=False:
    - Verifies that quaternions are loaded without conversion
    - Checks shape and format of quaternion data
    """
    N = 20
    T_t = np.tile(np.eye(4), (N, 1, 1))
    T_t[:, :3, 3] = np.random.randn(N, 3) * 5
    
    test_file = tmp_path / "test_load_quat.h5"
    hlp.store_transformations(
        [T_t], [150.0], test_file,
        group_names=['quat_trajectory'],
        store_as_quaternion=True
    )
    
    # Load with as_matrices=False
    data = hlp.load_hdf5_transformations(test_file, as_matrices=False)
    
    assert 'quat_trajectory' in data
    assert data['quat_trajectory']['rotations'].shape == (N, 4)  # Quaternions
    assert 'transformations' not in data['quat_trajectory']  # Not constructed


def test_load_hdf5_transformations_specific_group(tmp_path):
    """
    Test loading a specific group from HDF5 file:
    - Creates file with multiple groups
    - Loads only one specific group
    - Verifies only requested group is loaded
    """
    N = 25
    T1 = np.tile(np.eye(4), (N, 1, 1))
    T1[:, :3, 3] = np.random.randn(N, 3)
    
    T2 = np.tile(np.eye(4), (N, 1, 1))
    T2[:, :3, 3] = np.random.randn(N, 3) * 2
    
    test_file = tmp_path / "test_multi_group.h5"
    hlp.store_transformations(
        [T1, T2], [100.0, 100.0], test_file,
        group_names=['group1', 'group2']
    )
    
    # Load only group1
    data = hlp.load_hdf5_transformations(test_file, group_name='group1')
    
    assert 'group1' in data
    assert 'group2' not in data
    assert data['group1']['transformations'].shape == (N, 4, 4)


def test_load_hdf5_transformations_with_derivatives(tmp_path):
    """
    Test loading transformations with derivatives:
    - Stores transformations with derivative_order=2
    - Verifies derivatives are loaded in the derivatives dictionary
    """
    N = 40
    T_t = np.tile(np.eye(4), (N, 1, 1))
    T_t[:, :3, 3] = np.random.randn(N, 3) * 10
    
    test_file = tmp_path / "test_derivatives.h5"
    hlp.store_transformations(
        [T_t], [200.0], test_file,
        group_names=['with_derivatives'],
        derivative_order=2
    )
    
    data = hlp.load_hdf5_transformations(test_file)
    
    assert 'with_derivatives' in data
    assert 'derivatives' in data['with_derivatives']
    derivs = data['with_derivatives']['derivatives']
    
    # Check that derivatives exist
    assert 'translational_derivative_order_1' in derivs
    assert 'translational_derivative_order_2' in derivs
    assert 'rotational_derivative_order_1' in derivs
    assert 'rotational_derivative_order_2' in derivs


def test_visualize_hdf5_trajectory(tmp_path):
    """
    Test visualize_hdf5_trajectory function:
    - Creates a simple trajectory
    - Visualizes it and checks that Figure and Axes are returned
    - Tests with and without coordinate frames
    - Tests saving to file
    """
    # Create test trajectory
    N = 100
    t = np.linspace(0, 2*np.pi, N)
    T_t = np.zeros((N, 4, 4))
    
    for i, theta in enumerate(t):
        T_t[i, :3, 3] = [np.cos(theta)*10, np.sin(theta)*10, theta]
        T_t[i, :3, :3] = np.eye(3)
        T_t[i, 3, 3] = 1.0
    
    test_file = tmp_path / "test_viz.h5"
    hlp.store_transformations(
        [T_t], [100.0], test_file,
        group_names=['helix_trajectory']
    )
    
    # Test visualization without saving
    fig, ax = hlp.visualize_hdf5_trajectory(
        test_file,
        group_name='helix_trajectory',
        frame_step=20,
        show_frames=True,
        frame_scale=2.0
    )
    
    import matplotlib.pyplot as plt
    assert fig is not None
    assert ax is not None
    plt.close(fig)
    
    # Test visualization with saving
    save_path = tmp_path / "trajectory_plot.png"
    fig2, ax2 = hlp.visualize_hdf5_trajectory(
        test_file,
        frame_step=0,  # No frames
        show_frames=False,
        save_path=save_path,
        title="Test Trajectory"
    )
    
    assert save_path.exists()
    plt.close(fig2)


def test_compare_hdf5_trajectories_translations(tmp_path):
    """
    Test compare_hdf5_trajectories with translations:
    - Creates raw and smoothed trajectories
    - Compares them using 'translations' component
    - Verifies Figure with 3 subplots is returned
    """
    N = 80
    
    # Raw trajectory (with noise)
    T_raw = np.zeros((N, 4, 4))
    T_raw[:, :3, 3] = np.column_stack([
        np.linspace(0, 10, N) + np.random.randn(N) * 0.5,
        np.linspace(0, 5, N) + np.random.randn(N) * 0.3,
        np.linspace(0, 3, N) + np.random.randn(N) * 0.2
    ])
    T_raw[:, :3, :3] = np.eye(3)
    T_raw[:, 3, 3] = 1.0
    
    # Smoothed trajectory (less noise)
    T_smooth = np.zeros((N, 4, 4))
    T_smooth[:, :3, 3] = np.column_stack([
        np.linspace(0, 10, N),
        np.linspace(0, 5, N),
        np.linspace(0, 3, N)
    ])
    T_smooth[:, :3, :3] = np.eye(3)
    T_smooth[:, 3, 3] = 1.0
    
    test_file = tmp_path / "test_compare_trans.h5"
    hlp.store_transformations(
        [T_raw, T_smooth], [100.0, 100.0], test_file,
        group_names=['raw', 'smooth']
    )
    
    # Compare translations
    fig, axes = hlp.compare_hdf5_trajectories(
        test_file,
        group_names=['raw', 'smooth'],
        component='translations'
    )
    
    import matplotlib.pyplot as plt
    assert fig is not None
    assert len(axes) == 3  # type: ignore # X, Y, Z subplots
    plt.close(fig)


def test_compare_hdf5_trajectories_rotations_euler(tmp_path):
    """
    Test compare_hdf5_trajectories with rotations_euler:
    - Creates trajectories with different rotations
    - Compares them using 'rotations_euler' component
    """
    from scipy.spatial.transform import Rotation as R
    
    N = 60
    
    # Trajectory 1: rotating around Z axis
    T1 = np.zeros((N, 4, 4))
    for i in range(N):
        angle = i * 0.1
        T1[i, :3, :3] = R.from_euler('z', angle).as_matrix()
        T1[i, 3, 3] = 1.0
    
    # Trajectory 2: rotating around X axis
    T2 = np.zeros((N, 4, 4))
    for i in range(N):
        angle = i * 0.05
        T2[i, :3, :3] = R.from_euler('x', angle).as_matrix()
        T2[i, 3, 3] = 1.0
    
    test_file = tmp_path / "test_compare_rot.h5"
    hlp.store_transformations(
        [T1, T2], [100.0, 100.0], test_file,
        group_names=['rotation_z', 'rotation_x']
    )
    
    # Compare rotations
    fig, axes = hlp.compare_hdf5_trajectories(
        test_file,
        component='rotations_euler',
        save_path=tmp_path / "rotation_comparison.png"
    )
    
    import matplotlib.pyplot as plt
    assert fig is not None
    assert len(axes) == 3  # type: ignore # Roll, Pitch, Yaw subplots
    assert (tmp_path / "rotation_comparison.png").exists()
    plt.close(fig)


def test_compare_hdf5_trajectories_rotations_rotvec(tmp_path):
    """
    Test compare_hdf5_trajectories with rotations_rotvec:
    - Verifies rotation vector component comparison works
    """
    N = 50
    T_t = np.tile(np.eye(4), (N, 1, 1))
    
    test_file = tmp_path / "test_compare_rotvec.h5"
    hlp.store_transformations(
        [T_t], [100.0], test_file,
        group_names=['identity']
    )
    
    # Compare rotation vectors
    fig, axes = hlp.compare_hdf5_trajectories(
        test_file,
        component='rotations_rotvec'
    )
    
    import matplotlib.pyplot as plt
    assert fig is not None
    assert len(axes) == 3  # type: ignore
    plt.close(fig)


def test_split_hdf5_single_interval(tmp_path):
    """
    Test split_hdf5_by_sub_experiments with single intervals:
    - Verifies basic splitting functionality
    - Checks that output files are created
    - Validates frame counts match interval ranges
    """
    # Create test data with 200 frames
    N = 200
    T_t = np.tile(np.eye(4), (N, 1, 1))
    T_t[:, :3, 3] = np.random.randn(N, 3)  # Random translations
    
    test_file = tmp_path / "test_full.h5"
    hlp.store_transformations(
        [T_t], [100.0], test_file,
        group_names=['trajectory'],
        derivative_order=2
    )
    
    # Define sub-experiments with single intervals
    sub_exps = {
        'first_half': [0, 99],      # 100 frames
        'second_half': [100, 199]   # 100 frames
    }
    
    # Split the file
    output_files = hlp.split_hdf5_by_sub_experiments(
        test_file,
        sub_experiments=sub_exps,  # type: ignore
        output_dir=tmp_path / 'split'
    )
    
    # Verify outputs
    assert len(output_files) == 2
    assert 'first_half' in output_files
    assert 'second_half' in output_files
    assert output_files['first_half'].exists()
    assert output_files['second_half'].exists()
    
    # Load and verify frame counts
    data_first = hlp.load_hdf5_transformations(output_files['first_half'])
    data_second = hlp.load_hdf5_transformations(output_files['second_half'])
    
    assert len(data_first['trajectory']['transformations']) == 100
    assert len(data_second['trajectory']['transformations']) == 100
    
    # Verify metadata
    assert data_first['trajectory']['sample_rate'] == 100.0
    
    # Verify derivatives were recalculated
    assert 'derivatives' in data_first['trajectory']
    assert 'translational_velocity' in data_first['trajectory']['derivatives']
    assert 'angular_velocity' in data_first['trajectory']['derivatives']


def test_split_hdf5_multiple_intervals(tmp_path):
    """
    Test split_hdf5_by_sub_experiments with multiple concatenated intervals:
    - Verifies interval concatenation works
    - Checks that derivatives are recalculated
    """
    # Create test data
    N = 300
    T_t = np.tile(np.eye(4), (N, 1, 1))
    T_t[:, :3, 3] = np.random.randn(N, 3)
    
    test_file = tmp_path / "test_multi.h5"
    hlp.store_transformations(
        [T_t], [200.0], test_file,
        group_names=['trajectory'],
        derivative_order=2
    )
    
    # Define sub-experiment with multiple intervals
    sub_exps = {
        'combined': [[0, 49], [100, 149], [200, 249]]  # 3 x 50 frames = 150 total
    }
    
    # Split the file
    output_files = hlp.split_hdf5_by_sub_experiments(
        test_file,
        sub_experiments=sub_exps,  # type: ignore
        output_dir=tmp_path / 'split'
    )
    
    # Load and verify
    data = hlp.load_hdf5_transformations(output_files['combined'])
    assert len(data['trajectory']['transformations']) == 150
    
    # Verify derivatives exist (recalculated for concatenated intervals)
    assert 'derivatives' in data['trajectory']
    assert 'translational_velocity' in data['trajectory']['derivatives']
    assert len(data['trajectory']['derivatives']['translational_velocity']) == 150


def test_split_hdf5_from_config_file(tmp_path):
    """
    Test split_hdf5_by_sub_experiments loading from config file:
    - Verifies config file loading works
    - Tests error handling for missing config
    """
    import json
    
    # Create test data
    N = 150
    T_t = np.tile(np.eye(4), (N, 1, 1))
    T_t[:, :3, 3] = np.random.randn(N, 3)
    
    test_file = tmp_path / "test_config.h5"
    hlp.store_transformations(
        [T_t], [100.0], test_file,
        group_names=['trajectory']
    )
    
    # Create config file
    config = {
        'analysis': {
            'experiment': {
                'sub_experiments': {
                    'segment1': [0, 49],
                    'segment2': [50, 99],
                    'segment3': [100, 149]
                }
            }
        }
    }
    
    config_file = tmp_path / 'test_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f)
    
    # Split using config file
    output_files = hlp.split_hdf5_by_sub_experiments(
        test_file,
        config_file=config_file,
        output_dir=tmp_path / 'split'
    )
    
    # Verify outputs
    assert len(output_files) == 3
    assert all(f.exists() for f in output_files.values())
    
    # Verify frame counts
    data = hlp.load_hdf5_transformations(output_files['segment1'])
    assert len(data['trajectory']['transformations']) == 50


def test_split_hdf5_multiple_groups(tmp_path):
    """
    Test split_hdf5_by_sub_experiments with multiple trajectory groups:
    - Verifies all groups are split correctly
    - Tests copy_all_groups parameter
    """
    # Create test data with two groups
    N = 100
    T1 = np.tile(np.eye(4), (N, 1, 1))
    T2 = np.tile(np.eye(4), (N, 1, 1))
    T1[:, :3, 3] = np.random.randn(N, 3)
    T2[:, :3, 3] = np.random.randn(N, 3)
    
    test_file = tmp_path / "test_groups.h5"
    hlp.store_transformations(
        [T1, T2], [100.0, 100.0], test_file,
        group_names=['group1', 'group2']
    )
    
    # Split both groups
    sub_exps = {
        'first': [0, 49],
        'second': [50, 99]
    }
    
    output_files = hlp.split_hdf5_by_sub_experiments(
        test_file,
        sub_experiments=sub_exps,  # type: ignore
        output_dir=tmp_path / 'split',
        copy_all_groups=True
    )
    
    # Verify both groups are in each output file
    data = hlp.load_hdf5_transformations(output_files['first'])
    assert 'group1' in data
    assert 'group2' in data
    assert len(data['group1']['transformations']) == 50
    assert len(data['group2']['transformations']) == 50


def test_split_hdf5_error_handling(tmp_path):
    """
    Test split_hdf5_by_sub_experiments error handling:
    - Missing file
    - Missing sub_experiments and config_file
    - Empty sub_experiments
    - Invalid config file structure
    """
    import pytest
    
    # Test missing file
    with pytest.raises(FileNotFoundError):
        hlp.split_hdf5_by_sub_experiments(
            tmp_path / "nonexistent.h5",
            sub_experiments={'test': [0, 10]}
        )
    
    # Create valid test file
    N = 50
    T_t = np.tile(np.eye(4), (N, 1, 1))
    test_file = tmp_path / "test.h5"
    hlp.store_transformations([T_t], [100.0], test_file, group_names=['traj'])
    
    # Test missing both sub_experiments and config_file
    with pytest.raises(ValueError, match="Must provide either"):
        hlp.split_hdf5_by_sub_experiments(test_file)
    
    # Test empty sub_experiments
    with pytest.raises(ValueError, match="empty dictionary"):
        hlp.split_hdf5_by_sub_experiments(
            test_file,
            sub_experiments={}
        )
    
    # Test missing config file
    with pytest.raises(FileNotFoundError):
        hlp.split_hdf5_by_sub_experiments(
            test_file,
            config_file=tmp_path / "missing_config.json"
        )
    
    # Test invalid config structure
    import json
    bad_config = tmp_path / 'bad_config.json'
    with open(bad_config, 'w') as f:
        json.dump({'wrong': 'structure'}, f)
    
    with pytest.raises(ValueError, match="missing required key"):
        hlp.split_hdf5_by_sub_experiments(
            test_file,
            config_file=bad_config
        )


def test_split_hdf5_with_frame_offset(tmp_path):
    """
    Test frame_offset parameter for adjusting frame numbers.
    
    Simulates the case where HDF5 file frames start at 0, but
    sub_experiments are defined in original frame numbers.
    """
    # Create test data (200 frames starting at 0)
    N = 200
    T_t = np.tile(np.eye(4), (N, 1, 1))
    T_t[:, :3, 3] = np.random.randn(N, 3) * 10
    
    test_file = tmp_path / 'test.h5'
    hlp.store_transformations(
        [T_t], [200.0], test_file,
        group_names=['test_group'],
        derivative_order=2
    )
    
    # Sub-experiments defined in "original" frame numbers (e.g., 1000-1199)
    # But HDF5 file has frames [0-199]
    # So we need frame_offset=1000
    sub_exps = {
        'first': [1000, 1099],    # Should map to [0, 99]
        'second': [1100, 1199]    # Should map to [100, 199]
    }
    
    # Test with explicit frame_offset
    output_files = hlp.split_hdf5_by_sub_experiments(
        test_file,
        sub_experiments=sub_exps,  # type: ignore
        frame_offset=1000,
        output_dir=tmp_path / 'split'
    )
    
    assert len(output_files) == 2
    
    # Verify first file has 100 frames
    data_first = hlp.load_hdf5_transformations(output_files['first'])
    assert len(data_first['test_group']['translations']) == 100
    
    # Verify second file has 100 frames
    data_second = hlp.load_hdf5_transformations(output_files['second'])
    assert len(data_second['test_group']['translations']) == 100


def test_split_hdf5_auto_frame_offset_from_config(tmp_path):
    """
    Test automatic frame_offset detection from config file.
    
    When config_file is provided with frame_interval, the function should
    automatically use frame_interval[0] as the frame_offset.
    """
    import json
    
    # Create test data
    N = 200
    T_t = np.tile(np.eye(4), (N, 1, 1))
    T_t[:, :3, 3] = np.random.randn(N, 3) * 10
    
    test_file = tmp_path / 'test.h5'
    hlp.store_transformations(
        [T_t], [200.0], test_file,
        group_names=['test_group'],
        derivative_order=2
    )
    
    # Create config with frame_interval and sub_experiments
    config = {
        'analysis': {
            'experiment': {
                'frame_interval': [15300, 15499],  # Original recording frames
                'sub_experiments': {
                    'first_half': [15300, 15399],   # Original frame numbers
                    'second_half': [15400, 15499]   # Should auto-adjust by -15300
                }
            }
        }
    }
    
    config_file = tmp_path / 'config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f)
    
    # Should automatically detect frame_offset=15300
    output_files = hlp.split_hdf5_by_sub_experiments(
        test_file,
        config_file=config_file,
        output_dir=tmp_path / 'split'
    )
    
    assert len(output_files) == 2
    
    # Verify frame counts
    data_first = hlp.load_hdf5_transformations(output_files['first_half'])
    assert len(data_first['test_group']['translations']) == 100
    
    data_second = hlp.load_hdf5_transformations(output_files['second_half'])
    assert len(data_second['test_group']['translations']) == 100


def test_store_config_metadata(tmp_path):
    """
    Test that config is properly stored in HDF5 files.
    
    Verifies that:
    - File-level metadata includes creation_date, jts_version, and config
    - Group-level metadata includes config as JSON
    - Config can be parsed back from JSON
    """
    import json
    import h5py
    
    # Create test data
    N = 100
    T_t = np.tile(np.eye(4), (N, 1, 1))
    T_t[:, :3, 3] = np.random.randn(N, 3) * 10
    
    # Create test config
    test_config = {
        'analysis': {
            'smoothing': {'window_length': 21, 'poly_order': 3},
            'experiment': {'frame_interval': [0, 99]}
        },
        'output': {'unit': 'm', 'derivative_order': 2}
    }
    
    test_file = tmp_path / 'test_config.h5'
    hlp.store_transformations(
        [T_t], [200.0], test_file,
        metadata=['Test transformation'],
        group_names=['test_group'],
        derivative_order=2,
        config=test_config
    )
    
    # Verify file-level metadata using h5py
    with h5py.File(test_file, 'r') as f:
        assert 'creation_date' in f.attrs
        assert 'jts_version' in f.attrs
        assert 'config' in f.attrs
        
        # Parse and verify config
        stored_config = json.loads(f.attrs['config'])  # type: ignore
        assert stored_config == test_config
        assert stored_config['analysis']['smoothing']['window_length'] == 21
        
        # Verify group-level metadata
        assert 'test_group' in f
        grp = f['test_group']
        assert 'config' in grp.attrs
        
        # Parse and verify group config
        group_config = json.loads(grp.attrs['config'])  # type: ignore
        assert group_config == test_config


def test_load_config_from_hdf5(tmp_path):
    """
    Test that config is properly loaded from HDF5 files.
    
    Verifies that load_hdf5_transformations() returns config in the
    data dictionary for each group.
    """
    import json
    
    # Create test data
    N = 100
    T_t = np.tile(np.eye(4), (N, 1, 1))
    T_t[:, :3, 3] = np.random.randn(N, 3) * 10
    
    # Create test config
    test_config = {
        'analysis': {
            'smoothing': {'window_length': 21, 'poly_order': 3},
            'experiment': {'name': 'test_experiment'}
        },
        'output': {'unit': 'm'}
    }
    
    test_file = tmp_path / 'test_load_config.h5'
    hlp.store_transformations(
        [T_t], [200.0], test_file,
        metadata=['Test transformation'],
        group_names=['test_group'],
        config=test_config
    )
    
    # Load data and verify config is included
    data = hlp.load_hdf5_transformations(test_file)
    
    assert 'test_group' in data
    assert 'config' in data['test_group']
    
    loaded_config = data['test_group']['config']
    assert loaded_config is not None
    assert loaded_config == test_config
    assert loaded_config['analysis']['experiment']['name'] == 'test_experiment'


def test_split_hdf5_preserves_config(tmp_path):
    """
    Test that config is preserved when splitting HDF5 files.
    
    Verifies that:
    - Split files contain the original config at file level
    - Split files contain the config at group level
    - Config is correctly parsed from split files
    """
    import json
    import h5py
    from typing import Dict, List
    
    # Create test data
    N = 200
    T_t = np.tile(np.eye(4), (N, 1, 1))
    T_t[:, :3, 3] = np.random.randn(N, 3) * 10
    
    # Create test config
    test_config = {
        'analysis': {
            'smoothing': {'window_length': 21, 'poly_order': 3},
            'experiment': {
                'name': 'split_test',
                'frame_interval': [0, 199]
            }
        },
        'output': {'unit': 'm', 'derivative_order': 2}
    }
    
    test_file = tmp_path / 'test_split_config.h5'
    hlp.store_transformations(
        [T_t], [200.0], test_file,
        metadata=['Test transformation'],
        group_names=['test_group'],
        derivative_order=2,
        config=test_config
    )
    
    # Define sub-experiments
    sub_experiments: Dict[str, List[int]] = {
        'first_half': [0, 99],
        'second_half': [100, 199]
    }
    
    # Split the file
    output_files = hlp.split_hdf5_by_sub_experiments(
        test_file,
        sub_experiments=sub_experiments,  # type: ignore
        output_dir=tmp_path / 'split'
    )
    
    # Verify config is preserved in split files
    for sub_name, split_file in output_files.items():
        # Check file-level metadata
        with h5py.File(split_file, 'r') as f:
            assert 'config' in f.attrs, f"File-level config missing in {sub_name}"
            file_config = json.loads(f.attrs['config'])  # type: ignore
            assert file_config == test_config
            
            # Check group-level metadata
            assert 'test_group' in f
            grp = f['test_group']
            assert 'config' in grp.attrs, f"Group-level config missing in {sub_name}"
            group_config = json.loads(grp.attrs['config'])  # type: ignore
            assert group_config == test_config
        
        # Also verify using load function
        data = hlp.load_hdf5_transformations(split_file)
        assert 'config' in data['test_group']
        assert data['test_group']['config'] == test_config

