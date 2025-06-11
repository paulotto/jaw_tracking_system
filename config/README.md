# JawTrackingSystem (JTS) Configuration 
Various configurations for the JawTrackingSystem (JTS) can be easily managed through `JSON` files.
These files allow you to customize the system's behavior, such as the motion capture data source, 
analysis parameters, output settings, and visualization options.

---

## Configuration Example with Comments
TODO:
```json
{
  "data_source": {
    "type": "qualisys",
    "mode": "offline",  // or "streaming"
    "filename": "path/data.mat",

    "streaming": {
      "host": "127.0.0.1",
      "port": 22223,
      "version": "1.25",
      "buffer_size": 1000,
      "timeout": 5,
      "components": ["3d", "6d", "6deuler"],
      "stream_rate": "allframes"
    }
  },

  "analysis": {
    "description": "Jaw motion analysis experiment",

    "calibration": {
      "mode": "offline",  // or "online"

      "online_config": {
        "method": "button_triggered",   // or "automatic", "guided"
        "stability_threshold": 0.5,     // mm
        "stability_duration": 0.5,      // seconds
        "capture_window": 1.0,          // seconds
        "auto_capture": false,
        "require_confirmation": true,
        "calibration_tool_name": "CT",  // Rigid body name for calibration tool

        "feedback": {
          "visual": true,
          "audio": true,
          "voice_prompts": false
        },

        "landmarks": {
          "mandibular": ["mand_point_1", "mand_point_2", "mand_point_3"],
          "maxillary": ["max_point_1", "max_point_2", "max_point_3"]
        }
      },

      "mandibular": {
        "rigid_bodies": ["MP", "CT"],
        "points": [
          {
            "name": "mand_point_1",
            "frame_interval": [2100, 2600]
          },
          {
            "name": "mand_point_2",
            "frame_interval": [5100, 5600]
          },
          {
            "name": "mand_point_3",
            "frame_interval": [7500, 8000]
          }
        ]
      },

      "maxillary": {
        "rigid_bodies": ["HP", "CT"],
        "points": [
          {
            "name": "max_point_1",
            "frame_interval": [9500, 10000]
          },
          {
            "name": "max_point_2",
            "frame_interval": [12100, 12600]
          },
          {
            "name": "max_point_3",
            "frame_interval": [14200, 14700]
          }
        ]
      }
    },

    "experiment": {
      "frame_interval": [15300, 27000],  // Still supported for backward compatibility
      "use_sub_experiments": false,  // Enable sub-experiment processing
      "combine_sub_experiments": ["open_close", "chewing"],  // or "all"

      "sub_experiments": {
        "open_close": [15300, 18400],
        "left_right": [20050, 21850],
        "protrusion_retrusion": [21851, 23950],
        "chewing": [24400, 26051],
        // Example of multiple intervals for one sub-experiment:
        "complex_motion": [
          [27000, 27500],
          [28000, 28500],
          [29000, 29500]
        ]
      },

      "interpolation": {
        "method": "cubic",  // "linear", "cubic", "slerp", "hermite", "none"
        "transition_frames": 10,  // Frames for smooth transition
        "connect_intervals": true  // Whether to interpolate between intervals
      }
    },

    "relative_motion": {
      "reference_body": "HP",
      "moving_body": "MP"
    },

    "coordinate_transform": {
      "enabled": true,
      "calibration_type": "maxillary",
      "model_points": [
        [-0.244678, -109.416, 101.356],
        [23.6189, -106.201, 73.9031],
        [-24.0445, -106.078, 74.1795]
      ]
    },

    "smoothing": {
      "enabled": true,
      "window_length": 11,
      "poly_order": 3
    },

    "coordinate_origin_index": 0
  },

  "visualization": {
    "raw_data": true,
    "raw_data_3d": false,
    "calibration_transforms": true, // Static marker-landmark transformations
    "relative_marker_motion": true, // The relative motion of the moouth to head markers
    "landmark_motion": true, // The landmark motion relative to the head markers
    "final_trajectory": true,
    "plot_2d_components": true,
    "plot_export_only": true, // Plots only the final trajectory in a separate figure
    "plot_rot_3d": false,
    "show_plots": true,
    "use_tex_font": false,

    "plot_style": {
      "sample_rate": 10,
      "linewidth": 1.5,
      "axes_label_fontsize": 12,
      "axes_tick_fontsize": 10,
      "title_fontsize": 14,
      "legend_fontsize": 10,
      "figure_size": [12, 8],
      "labelpad_scale": 0.7,

      "view_3d": {
        "elev": 30,
        "azim": 0,
        "roll": 0,
        "vertical_axis": "y"
      },

      "colors": ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown"],
      "line_styles": ["-", "--", "-.", ":"],

      "grid": {
        "enabled": true,
        "alpha": 0.3
      }
    }
  },

  "output": {
    "directory": "./analysis_results",
    "save_csv": true,
    "save_hdf5": true,
    "save_plots": false,
    "save_tikz": false,
    "csv_filename": "jaw_motion",
    "hdf5_filename": "jaw_motion.h5",
    "store_quaternions": true,
    "derivative_order": 2,
    "scale_factor": 0.001,
    "unit": "m"
  }
}

```