"""Argument parsing and configuration management for PostureBuddy"""

import argparse
import json
import sys
from pathlib import Path


class ArgumentParser:
    """Handles command line argument parsing with config file support"""

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self):
        """Create and configure the argument parser"""
        parser = argparse.ArgumentParser(
            description='PostureBuddy - Posture Detection and Monitoring System',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        # Camera settings
        camera_group = parser.add_argument_group('Camera Settings')
        camera_group.add_argument('--camera', type=int, default=0,
                                 help='Camera device index')
        camera_group.add_argument('--width', type=int, default=640,
                                 help='Camera frame width')
        camera_group.add_argument('--height', type=int, default=480,
                                 help='Camera frame height')
        camera_group.add_argument('--fps', type=int, default=30,
                                 help='Target frames per second')
        camera_group.add_argument('--no-mirror', dest='mirror', action='store_false', default=True,
                                 help='Disable mirror mode (mirror is on by default)')

        # Display settings
        display_group = parser.add_argument_group('Display Settings')
        display_group.add_argument('--no-display', action='store_true',
                                  help='Run headless without display window')
        display_group.add_argument('--fullscreen', action='store_true',
                                  help='Run in fullscreen mode')
        display_group.add_argument('--no-fps', dest='show_fps', action='store_false', default=True,
                                  help='Hide FPS counter (shown by default)')
        display_group.add_argument('--no-landmarks', dest='show_landmarks', action='store_false', default=True,
                                  help='Hide pose landmarks (shown by default)')
        display_group.add_argument('--show-angles', action='store_true',
                                  help='Display calculated angles on screen')
        display_group.add_argument('--show-skeleton', action='store_true',
                                  help='Draw skeleton connections between landmarks')

        # MediaPipe model settings
        model_group = parser.add_argument_group('MediaPipe Model Settings')
        model_group.add_argument('--model-complexity', type=int, default=1, choices=[0, 1, 2],
                                help='Model complexity: 0=Lite, 1=Full, 2=Heavy')
        model_group.add_argument('--min-detection-confidence', type=float, default=0.5,
                                help='Minimum confidence for pose detection (0.0-1.0)')
        model_group.add_argument('--min-tracking-confidence', type=float, default=0.5,
                                help='Minimum confidence for pose tracking (0.0-1.0)')
        model_group.add_argument('--smooth-landmarks', action='store_true',
                                help='Enable landmark smoothing')

        # Posture detection settings
        posture_group = parser.add_argument_group('Posture Detection Settings')
        posture_group.add_argument('--neck-angle-threshold', type=float, default=30.0,
                                  help='Maximum neck forward angle in degrees')
        posture_group.add_argument('--hip-angle-threshold', type=float, default=15.0,
                                  help='Maximum hip slouch angle in degrees')
        posture_group.add_argument('--alert-threshold', type=int, default=5,
                                  help='Number of bad posture detections before alert')
        posture_group.add_argument('--reset-time', type=int, default=3,
                                  help='Seconds of good posture to reset counter')

        # Data saving and logging
        data_group = parser.add_argument_group('Data Saving and Logging')
        data_group.add_argument('--save-data', action='store_true',
                                help='Enable data saving (frames and/or landmarks)')
        data_group.add_argument('--save-dir', type=str, default='PostureDetector/datasets',
                                help='Base directory for saving datasets')
        data_group.add_argument('--username', type=str, default='user',
                                help='Username for dataset organization')
        data_group.add_argument('--save-frames', action='store_true',
                                help='Save frame images (raw, no annotations by default)')
        data_group.add_argument('--save-annotated', action='store_true',
                                help='Save frames with landmarks/skeleton annotations drawn')
        data_group.add_argument('--save-landmarks', action='store_true',
                                help='Save pose landmarks to CSV (includes x,y,z,visibility for each)')
        data_group.add_argument('--frame-format', type=str, default='png', choices=['png', 'jpg'],
                                help='Image format for saved frames')
        data_group.add_argument('--save-rate', type=float, default=5.0,
                                help='Saves per minute (e.g., 5.0 = 5 saves/minute)')
        data_group.add_argument('--record-video', type=str, metavar='FILENAME.mp4',
                                help='Record video to file in dataset folder')

        # Debug and logging
        debug_group = parser.add_argument_group('Debug and Logging')
        debug_group.add_argument('--debug', action='store_true',
                                help='Enable debug mode with verbose output')
        debug_group.add_argument('--benchmark', action='store_true',
                                help='Show performance benchmarks')

        # Testing modes
        test_group = parser.add_argument_group('Testing Modes')
        test_group.add_argument('--test-camera', action='store_true',
                               help='Test camera only (no pose detection)')
        test_group.add_argument('--test-pose', action='store_true',
                               help='Test pose detection only')
        test_group.add_argument('--calibrate', action='store_true',
                               help='Run calibration mode for posture baseline')

        # Config loading
        config_group = parser.add_argument_group('Configuration')
        config_group.add_argument('--load-config', type=str, metavar='CONFIG.json',
                                 help='Load settings from a previous session config file')

        return parser

    def parse(self):
        """Parse arguments with config file support"""
        # First parse to check if --load-config is present
        args, _ = self.parser.parse_known_args()

        # If config file is specified, load it and merge with command line args
        if args.load_config:
            config_args = load_config_from_file(args.load_config)
            if config_args is not None:
                # Command line args override config file
                # Re-parse with config args as defaults + any remaining args
                full_args = config_args + sys.argv[1:]
                return self.parser.parse_args(full_args)

        return self.parser.parse_args()


def load_config_from_file(config_path):
    """Load configuration from a JSON file and return as command line args"""
    config_path = Path(config_path).expanduser()

    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        return None

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Extract session args from the config
        if 'session_args' not in config:
            print(f"Error: Invalid config file format (missing 'session_args')")
            return None

        session_args = config['session_args']

        print(f"Loading config from: {config_path}")
        print(f"  Original session: {config.get('timestamp', 'unknown')}")
        print(f"  Username: {config.get('username', 'unknown')}")

        # Build command line args from config
        # Filter out test mode flags to avoid conflicts
        cmd_args = []
        for key, value in session_args.items():
            # Skip these as they should be set by command line
            if key in ['test_camera', 'test_pose', 'calibrate', 'load_config']:
                continue

            arg_name = f"--{key.replace('_', '-')}"

            # Handle boolean flags
            if isinstance(value, bool):
                if value:
                    cmd_args.append(arg_name)
            # Handle None values
            elif value is None:
                continue
            # Handle other values
            else:
                cmd_args.extend([arg_name, str(value)])

        print(f"  Loaded {len(session_args)} settings\n")
        return cmd_args

    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse config file: {e}")
        return None
    except Exception as e:
        print(f"Error: Failed to load config: {e}")
        return None
