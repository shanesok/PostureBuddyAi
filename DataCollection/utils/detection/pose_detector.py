"""MediaPipe pose detection and landmark drawing"""

import cv2
import mediapipe as mp


class PoseDetector:
    """Handles pose detection using MediaPipe"""

    def __init__(self, args):
        """Initialize pose detector with settings from arguments

        Args:
            args: Parsed command line arguments containing model settings
        """
        self.args = args
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.pose = None
        self.initialize()

    def initialize(self):
        """Initialize MediaPipe pose detector with configured settings"""
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=self.args.model_complexity,
            min_detection_confidence=self.args.min_detection_confidence,
            min_tracking_confidence=self.args.min_tracking_confidence,
            smooth_landmarks=self.args.smooth_landmarks
        )

        if self.args.debug:
            print(f"Pose detector initialized:")
            print(f"  Model complexity: {self.args.model_complexity}")
            print(f"  Detection confidence: {self.args.min_detection_confidence}")
            print(f"  Tracking confidence: {self.args.min_tracking_confidence}")
            print(f"  Smooth landmarks: {self.args.smooth_landmarks}")

    def process(self, frame):
        """Process a frame to detect pose landmarks

        Args:
            frame: Input frame in BGR format

        Returns:
            MediaPipe pose results object
        """
        # MediaPipe requires RGB format
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        return results

    def draw_landmarks(self, frame, results):
        """Draw pose landmarks on frame based on configured settings

        Args:
            frame: Frame to draw on (will be modified)
            results: MediaPipe pose results object

        Returns:
            Modified frame with landmarks drawn
        """
        if not results.pose_landmarks:
            return frame

        if self.args.show_landmarks:
            # Draw landmarks
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS if self.args.show_skeleton else None,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )

        if self.args.show_skeleton:
            # Draw full skeleton connections
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )

        return frame

    def close(self):
        """Release pose detector resources"""
        if self.pose is not None:
            self.pose.close()
            self.pose = None
            if self.args.debug:
                print("Pose detector closed")
