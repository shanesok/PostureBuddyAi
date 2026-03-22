"""Main application class for PostureBuddy"""

import cv2
import time
from .camera import CameraManager
from .detection import PoseDetector
from .data import DatasetManager
from .ui import KeybindManager


class PostureBuddyApp:
    """Main application class for PostureBuddy posture detection system"""

    def __init__(self, args):
        """Initialize PostureBuddy application with parsed arguments

        Args:
            args: Parsed command line arguments
        """
        self.args = args
        self.camera = None
        self.pose_detector = None
        self.dataset_manager = None
        self.keybind_manager = None

        if self.args.debug:
            print("PostureBuddy Starting...")
            print(f"Arguments: {vars(args)}")

    def run_camera_test(self):
        """Run camera test mode (camera only, no pose detection)"""
        if self.args.debug:
            print("Running camera test mode (no pose detection)...")

        self.camera = CameraManager(self.args)

        print("Camera test started. Press 'q' to quit.")
        fps_time = time.time()
        frame_count = 0

        try:
            while self.camera.is_opened():
                ret, frame = self.camera.read_frame()
                if not ret:
                    break

                frame = self.camera.process_frame(frame)

                # Calculate FPS
                frame_count += 1
                if self.args.show_fps:
                    current_time = time.time()
                    fps = frame_count / (current_time - fps_time)
                    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                if not self.args.no_display:
                    cv2.imshow('PostureBuddy - Camera Test', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

        finally:
            self._cleanup()
            print(f"Camera test completed! Average FPS: {frame_count / (time.time() - fps_time):.1f}")

    def run_pose_test(self):
        """Run pose detection test mode"""
        if self.args.debug:
            print("Running pose detection test mode...")

        # Initialize components
        self.camera = CameraManager(self.args)
        self.pose_detector = PoseDetector(self.args)

        # Initialize dataset manager if saving is enabled
        if self.args.save_data or self.args.record_video:
            self.dataset_manager = DatasetManager(self.args)

        # Initialize keybind manager
        self.keybind_manager = KeybindManager(self.args)
        self.keybind_manager.print_help()  # Show keybinds at start

        print("\nPose detection test started. Press 'H' for help.")
        start_time = time.time()
        fps_time = start_time
        frame_count = 0

        try:
            while self.camera.is_opened():
                # Skip frame processing if paused
                if self.keybind_manager.paused:
                    key = cv2.waitKey(100) & 0xFF
                    if key != 255:  # If a key was pressed
                        action = self.keybind_manager.process_key(key, self.dataset_manager, None)
                        if action == 'quit':
                            break
                    continue

                ret, frame = self.camera.read_frame()
                if not ret:
                    break

                current_time = time.time()
                elapsed_time = current_time - start_time

                # Process frame (mirror if needed)
                frame_processed = self.camera.process_frame(frame)

                # Keep a copy of the raw frame for saving
                frame_raw = frame_processed.copy()

                # Process pose detection
                results = self.pose_detector.process(frame_processed)

                # Create annotated frame by drawing landmarks if detected
                frame_annotated = frame_processed.copy()
                if results.pose_landmarks:
                    frame_annotated = self.pose_detector.draw_landmarks(frame_annotated, results)

                    if self.args.debug and frame_count % 30 == 0:  # Print every 30 frames
                        print(f"Pose detected! Landmarks: {len(results.pose_landmarks.landmark)}")

                # Use annotated frame for display
                frame_display = frame_annotated.copy()

                # Save data if enabled (pass both raw and annotated)
                if self.dataset_manager and not self.keybind_manager.paused:
                    self.dataset_manager.process_frame(frame_raw, frame_annotated, results,
                                                      current_time, elapsed_time)

                # Handle continuous recording to labeled folders
                if self.dataset_manager and self.keybind_manager.recording_label:
                    self.dataset_manager.save_labeled_landmarks(
                        results,
                        self.keybind_manager.recording_label,
                        current_time
                    )

                # Calculate FPS and add to display
                frame_count += 1
                if self.args.show_fps:
                    fps = frame_count / (current_time - fps_time)
                    cv2.putText(frame_display, f"FPS: {fps:.1f}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Show save count if saving
                if self.dataset_manager and self.args.show_fps:
                    cv2.putText(frame_display, f"Saves: {self.dataset_manager.save_count}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Draw overlays
                frame_display = self.keybind_manager.draw_status_overlay(frame_display, self.dataset_manager)
                frame_display = self.keybind_manager.draw_help_overlay(frame_display)

                if not self.args.no_display:
                    cv2.imshow('PostureBuddy - Pose Test', frame_display)

                    # Handle keyboard input
                    key = cv2.waitKey(1) & 0xFF
                    if key != 255:  # If a key was pressed
                        action = self.keybind_manager.process_key(key, self.dataset_manager, frame_display)

                        if action == 'quit':
                            break
                        # Note: G/B/N keys now toggle recording mode (handled in keybind_manager)

        finally:
            self._cleanup()
            print(f"\nPose test completed! Average FPS: {frame_count / (time.time() - fps_time):.1f}")

    def run_calibration(self):
        """Run calibration mode for posture baseline (placeholder for future implementation)"""
        print("Calibration mode coming soon!")
        print("This will help establish your baseline posture for better detection.")

    def _cleanup(self):
        """Clean up resources"""
        if self.camera:
            self.camera.release()

        if self.pose_detector:
            self.pose_detector.close()

        if self.dataset_manager:
            self.dataset_manager.close()

        cv2.destroyAllWindows()

    def run(self):
        """Run the application based on configured mode"""
        # Test camera mode (camera only, no pose detection)
        if self.args.test_camera:
            self.run_camera_test()
            return

        # Test pose detection mode
        if self.args.test_pose:
            self.run_pose_test()
            return

        # Calibration mode
        if self.args.calibrate:
            self.run_calibration()
            return

        # Default: show help
        print("PostureBuddy - Posture Detection System")
        print("\nAvailable modes:")
        print("  --test-camera    Test camera feed only (no pose detection)")
        print("  --test-pose      Test pose detection with landmarks")
        print("  --calibrate      Run calibration mode (coming soon)")
        print("\nRun with --help to see all available options.")
