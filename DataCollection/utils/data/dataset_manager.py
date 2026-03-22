"""Dataset creation and data saving for posture monitoring"""

import cv2
import csv
import json
from datetime import datetime
from pathlib import Path


class DatasetManager:
    """Manages dataset creation and data saving for posture monitoring"""

    def __init__(self, args):
        """Initialize dataset manager with settings from arguments

        Args:
            args: Parsed command line arguments containing data saving settings
        """
        self.args = args
        self.dataset_dir = None
        self.frames_dir = None
        self.annotated_dir = None
        self.good_posture_dir = None
        self.bad_posture_dir = None
        self.neutral_dir = None
        self.landmarks_file = None
        self.landmarks_writer = None
        self.landmarks_csv = None
        self.config_file = None
        self.video_writer = None
        self.frame_count = 0
        self.save_count = 0
        self.last_save_time = 0
        self.last_labeled_save_time = 0  # Separate timer for continuous labeled recording
        self.annotation_count = {'good': 0, 'bad': 0, 'neutral': 0}

        # Calculate save interval in seconds
        if args.save_rate > 0:
            self.save_interval = 60.0 / args.save_rate  # Convert saves/min to seconds/save
        else:
            self.save_interval = 0

        if args.save_data or args.record_video:
            self._create_dataset_folder()

    def _create_dataset_folder(self):
        """Create organized dataset folder structure"""
        # Expand user directory
        base_dir = Path(self.args.save_dir).expanduser()

        # Create timestamp-based dataset folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dataset_name = f"{self.args.username}_{timestamp}"
        self.dataset_dir = base_dir / dataset_name

        # Create directories
        self.dataset_dir.mkdir(parents=True, exist_ok=True)

        if self.args.save_frames:
            self.frames_dir = self.dataset_dir / "frames"
            self.frames_dir.mkdir(exist_ok=True)

        if self.args.save_annotated:
            self.annotated_dir = self.dataset_dir / "annotated"
            self.annotated_dir.mkdir(exist_ok=True)

        # Create annotation directories for manual labeling
        self.good_posture_dir = self.dataset_dir / "good_posture"
        self.good_posture_dir.mkdir(exist_ok=True)

        self.bad_posture_dir = self.dataset_dir / "bad_posture"
        self.bad_posture_dir.mkdir(exist_ok=True)

        self.neutral_dir = self.dataset_dir / "neutral"
        self.neutral_dir.mkdir(exist_ok=True)

        # Initialize landmarks CSV
        if self.args.save_landmarks:
            self.landmarks_file = self.dataset_dir / "landmarks.csv"
            self.landmarks_csv = open(self.landmarks_file, 'w', newline='')
            self.landmarks_writer = csv.writer(self.landmarks_csv)

            # Write CSV header
            header = ['timestamp', 'frame_id', 'elapsed_time']
            # Add landmark columns (33 landmarks * 4 values: x, y, z, visibility)
            for i in range(11,25):
                header.extend([f'landmark_{i}_x', f'landmark_{i}_y',
                              f'landmark_{i}_z', f'landmark_{i}_visibility'])
            self.landmarks_writer.writerow(header)

        # Save configuration
        self._save_config()

        # Initialize video writer if requested
        if self.args.record_video:
            video_path = self.dataset_dir / self.args.record_video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                str(video_path),
                fourcc,
                self.args.fps,
                (self.args.width, self.args.height)
            )

        if self.args.debug:
            print(f"\nDataset folder created: {self.dataset_dir}")
            print(f"  Raw frames: {'Yes' if self.args.save_frames else 'No'}")
            print(f"  Annotated frames: {'Yes' if self.args.save_annotated else 'No'}")
            print(f"  Landmarks CSV: {'Yes' if self.args.save_landmarks else 'No'}")
            print(f"  Video: {'Yes' if self.args.record_video else 'No'}")
            print(f"  Save rate: {self.args.save_rate} saves/minute")
            print(f"  Save interval: {self.save_interval:.2f} seconds\n")

    def _save_config(self):
        """Save session configuration to JSON (only saves settings, not mode flags)"""
        # Get all arguments
        all_args = vars(self.args)

        # Exclude mode flags and meta parameters that shouldn't be persisted
        excluded_keys = {
            'test_camera',      # Test mode flag
            'test_pose',        # Test mode flag
            'calibrate',        # Test mode flag
            'load_config',      # Meta parameter (path to config file)
            'debug',            # Runtime flag (user decides per run)
            'benchmark',        # Runtime flag (user decides per run)
            'no_display',       # Runtime flag (user decides per run)
            'fullscreen',       # Runtime flag (user decides per run)
        }

        # Filter out excluded keys
        session_args = {k: v for k, v in all_args.items() if k not in excluded_keys}

        config = {
            'username': self.args.username,
            'timestamp': datetime.now().isoformat(),
            'session_args': session_args  # Only save reusable settings
        }

        config_file = self.dataset_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def should_save(self, current_time):
        """Check if it's time to save based on save rate

        Args:
            current_time: Current time in seconds

        Returns:
            bool: True if it's time to save
        """
        if self.save_interval == 0:
            return False

        if current_time - self.last_save_time >= self.save_interval:
            self.last_save_time = current_time
            return True
        return False

    def save_frame(self, frame_raw, frame_annotated, timestamp, elapsed_time):
        """Save frame images to disk (raw and/or annotated)

        Args:
            frame_raw: Raw frame without annotations
            frame_annotated: Frame with annotations
            timestamp: Timestamp string
            elapsed_time: Elapsed time in seconds
        """
        filename = f"frame_{self.save_count:06d}_{timestamp.replace(':', '-').replace('.', '_')}.{self.args.frame_format}"

        # Save raw frame
        if self.args.save_frames and self.frames_dir is not None:
            filepath = self.frames_dir / filename
            if self.args.frame_format == 'jpg':
                cv2.imwrite(str(filepath), frame_raw, [cv2.IMWRITE_JPEG_QUALITY, 95])
            else:
                cv2.imwrite(str(filepath), frame_raw)

        # Save annotated frame
        if self.args.save_annotated and self.annotated_dir is not None:
            filepath = self.annotated_dir / filename
            if self.args.frame_format == 'jpg':
                cv2.imwrite(str(filepath), frame_annotated, [cv2.IMWRITE_JPEG_QUALITY, 95])
            else:
                cv2.imwrite(str(filepath), frame_annotated)

        if self.args.debug and self.save_count % 10 == 0:
            saved_types = []
            if self.args.save_frames:
                saved_types.append("raw")
            if self.args.save_annotated:
                saved_types.append("annotated")
            print(f"Saved frame {self.save_count} ({', '.join(saved_types)}): {filename}")

    def save_landmarks(self, results, timestamp, elapsed_time):
        """Save pose landmarks to CSV

        Args:
            results: MediaPipe pose results object
            timestamp: Timestamp string
            elapsed_time: Elapsed time in seconds
        """
        if not self.args.save_landmarks or self.landmarks_writer is None:
            return

        if results.pose_landmarks:
            row = [timestamp, self.save_count, f"{elapsed_time:.2f}"]

            # Extract all 33 landmarks
            for landmark in results.pose_landmarks.landmark:
                row.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])

            self.landmarks_writer.writerow(row)
            self.landmarks_csv.flush()  # Ensure data is written

    def record_video_frame(self, frame):
        """Write frame to video file

        Args:
            frame: Frame to record
        """
        if self.video_writer is not None:
            self.video_writer.write(frame)

    def process_frame(self, frame_raw, frame_annotated, results, current_time, elapsed_time):
        """Process and save frame/landmarks based on settings

        Args:
            frame_raw: Raw frame without annotations
            frame_annotated: Frame with annotations
            results: MediaPipe pose results object
            current_time: Current time in seconds
            elapsed_time: Elapsed time in seconds
        """
        self.frame_count += 1

        # Record video every frame if enabled (use annotated if available, else raw)
        if self.args.record_video:
            self.record_video_frame(frame_annotated)

        # Check if we should save based on save rate
        if self.should_save(current_time):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            if self.args.save_frames or self.args.save_annotated:
                self.save_frame(frame_raw, frame_annotated, timestamp, elapsed_time)

            if self.args.save_landmarks and results is not None:
                self.save_landmarks(results, timestamp, elapsed_time)

            self.save_count += 1

    def adjust_save_rate(self, multiplier):
        """Adjust save rate by a multiplier

        Args:
            multiplier: Multiplier to apply to current save rate
        """
        self.args.save_rate *= multiplier
        self.save_interval = 60.0 / self.args.save_rate if self.args.save_rate > 0 else 0
        print(f"\nSave rate adjusted to: {self.args.save_rate:.1f} saves/min ({self.save_interval:.2f}s interval)")

    def annotate_frame(self, frame_raw, frame_annotated, results, label):
        """Save a frame to the appropriate annotation directory

        Args:
            frame_raw: Raw frame without annotations
            frame_annotated: Frame with annotations
            results: MediaPipe pose results object
            label: Annotation label ('good', 'bad', or 'neutral')
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{label}_{timestamp}.{self.args.frame_format}"

        # Choose directory based on label
        if label == 'good':
            target_dir = self.good_posture_dir
            self.annotation_count['good'] += 1
        elif label == 'bad':
            target_dir = self.bad_posture_dir
            self.annotation_count['bad'] += 1
        else:  # neutral
            target_dir = self.neutral_dir
            self.annotation_count['neutral'] += 1

        # Save raw frame
        filepath = target_dir / f"raw_{filename}"
        if self.args.frame_format == 'jpg':
            cv2.imwrite(str(filepath), frame_raw, [cv2.IMWRITE_JPEG_QUALITY, 95])
        else:
            cv2.imwrite(str(filepath), frame_raw)

        # Save annotated frame
        filepath = target_dir / f"annotated_{filename}"
        if self.args.frame_format == 'jpg':
            cv2.imwrite(str(filepath), frame_annotated, [cv2.IMWRITE_JPEG_QUALITY, 95])
        else:
            cv2.imwrite(str(filepath), frame_annotated)

        # Save landmarks to a separate CSV for this label
        if results and results.pose_landmarks:
            landmarks_file = target_dir / f"landmarks_{label}.csv"
            file_exists = landmarks_file.exists()

            with open(landmarks_file, 'a', newline='') as f:
                writer = csv.writer(f)

                # Write header if new file
                if not file_exists:
                    header = ['timestamp', 'filename']
                    for i in range(33):
                        header.extend([f'landmark_{i}_x', f'landmark_{i}_y',
                                      f'landmark_{i}_z', f'landmark_{i}_visibility'])
                    writer.writerow(header)

                # Write data
                row = [timestamp, filename]
                for landmark in results.pose_landmarks.landmark:
                    row.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
                writer.writerow(row)

        print(f"\n[{label.upper()}] Frame saved: {filename}")
        print(f"  Annotations: Good={self.annotation_count['good']}, "
              f"Bad={self.annotation_count['bad']}, Neutral={self.annotation_count['neutral']}")

    def should_save_labeled(self, current_time):
        """Check if it's time to save labeled data (uses separate timer)

        Args:
            current_time: Current time in seconds

        Returns:
            bool: True if it's time to save
        """
        if self.save_interval == 0:
            return False

        if current_time - self.last_labeled_save_time >= self.save_interval:
            self.last_labeled_save_time = current_time
            return True
        return False

    def save_labeled_landmarks(self, results, label, current_time):
        """Save only landmarks (no frames) to a labeled directory during continuous recording

        Args:
            results: MediaPipe pose results object
            label: Label ('good', 'bad', or 'neutral')
            current_time: Current time in seconds (for rate limiting)
        """
        if not results or not results.pose_landmarks:
            return

        # Check if it's time to save using separate timer
        if not self.should_save_labeled(current_time):
            return

        # Choose directory based on label
        if label == 'good':
            target_dir = self.good_posture_dir
            self.annotation_count['good'] += 1
        elif label == 'bad':
            target_dir = self.bad_posture_dir
            self.annotation_count['bad'] += 1
        else:  # neutral
            target_dir = self.neutral_dir
            self.annotation_count['neutral'] += 1

        # Save landmarks to CSV
        landmarks_file = target_dir / f"landmarks_{label}.csv"
        file_exists = landmarks_file.exists()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        with open(landmarks_file, 'a', newline='') as f:
            writer = csv.writer(f)

            # Write header if new file
            if not file_exists:
                header = ['timestamp']
                for i in range(33):
                    header.extend([f'landmark_{i}_x', f'landmark_{i}_y',
                                  f'landmark_{i}_z', f'landmark_{i}_visibility'])
                writer.writerow(header)

            # Write data
            row = [timestamp]
            for landmark in results.pose_landmarks.landmark:
                row.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
            writer.writerow(row)

        if self.args.debug and self.annotation_count[label] % 5 == 0:
            print(f"  Saved {label} sample #{self.annotation_count[label]}")

    def close(self):
        """Clean up and close files"""
        if self.landmarks_csv:
            self.landmarks_csv.close()
            if self.args.debug:
                print(f"\nLandmarks saved to: {self.landmarks_file}")

        if self.video_writer:
            self.video_writer.release()
            if self.args.debug:
                print(f"Video saved to: {self.dataset_dir / self.args.record_video}")

        if self.args.debug and self.dataset_dir:
            print(f"Dataset saved to: {self.dataset_dir}")
