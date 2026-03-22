"""Camera management and frame processing"""

import cv2


class CameraManager:
    """Manages camera initialization and frame processing"""

    def __init__(self, args):
        """Initialize camera with settings from arguments

        Args:
            args: Parsed command line arguments containing camera settings
        """
        self.args = args
        self.cap = None
        self.initialize()

    def initialize(self):
        """Initialize the camera with configured settings"""
        self.cap = cv2.VideoCapture(self.args.camera)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.args.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.args.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.args.fps)

        if self.args.debug:
            print(f"Camera initialized:")
            print(f"  Device: {self.args.camera}")
            print(f"  Resolution: {self.args.width}x{self.args.height}")
            print(f"  Target FPS: {self.args.fps}")
            print(f"  Mirror mode: {self.args.mirror}")

    def read_frame(self):
        """Read a frame from the camera

        Returns:
            tuple: (success, frame) - success is bool, frame is numpy array
        """
        if self.cap is None:
            return False, None
        return self.cap.read()

    def process_frame(self, frame):
        """Process frame with configured settings (e.g., mirror mode)

        Args:
            frame: Input frame as numpy array

        Returns:
            Processed frame as numpy array
        """
        if self.args.mirror:
            frame = cv2.flip(frame, 1)
        return frame

    def is_opened(self):
        """Check if camera is opened and available

        Returns:
            bool: True if camera is available
        """
        return self.cap is not None and self.cap.isOpened()

    def release(self):
        """Release the camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            if self.args.debug:
                print("Camera released")
