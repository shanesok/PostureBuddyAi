"""Keyboard bindings and visual overlays management"""

import cv2
from datetime import datetime


class KeybindManager:
    """Manages keyboard bindings and actions"""

    def __init__(self, args):
        """Initialize keybind manager with settings from arguments

        Args:
            args: Parsed command line arguments
        """
        self.args = args
        self.actions = {}
        self.key_names = {}

        # Define default keybinds
        self.register_keybind('q', 'quit', "Quit the program")
        self.register_keybind('c', 'clear_canvas', "Clear drawing canvas (if applicable)")
        self.register_keybind('s', 'save_screenshot', "Save current frame screenshot")
        self.register_keybind('p', 'pause', "Pause/Resume processing")
        self.register_keybind('d', 'toggle_debug', "Toggle debug overlay")
        self.register_keybind('l', 'toggle_landmarks', "Toggle landmark display")
        self.register_keybind('h', 'show_help', "Show help/keybinds")

        # Dataset annotation keybinds (toggle recording mode)
        self.register_keybind('g', 'toggle_good_recording', "Start/Stop recording GOOD posture")
        self.register_keybind('b', 'toggle_bad_recording', "Start/Stop recording BAD posture")
        self.register_keybind('n', 'toggle_neutral_recording', "Start/Stop recording NEUTRAL")

        # Recording controls
        self.register_keybind('r', 'toggle_recording', "Toggle frame recording")

        # Display controls
        self.register_keybind('[', 'decrease_save_rate', "Decrease save rate")
        self.register_keybind(']', 'increase_save_rate', "Increase save rate")

        # State variables
        self.paused = False
        self.show_debug = args.debug if hasattr(args, 'debug') else False
        self.show_help_overlay = False
        self.recording_label = None  # 'good', 'bad', 'neutral', or None

    def register_keybind(self, key, action_name, description):
        """Register a keybind with an action name and description

        Args:
            key: Keyboard key character
            action_name: Name of the action
            description: Human-readable description of the action
        """
        self.actions[key] = action_name
        self.key_names[action_name] = {'key': key, 'description': description}

    def get_action(self, key_code):
        """Get action name from key code

        Args:
            key_code: Key code from cv2.waitKey()

        Returns:
            str: Action name or None if not found
        """
        key_char = chr(key_code & 0xFF)
        return self.actions.get(key_char, None)

    def process_key(self, key_code, dataset_manager=None, frame=None):
        """Process a key press and return action to take

        Args:
            key_code: Key code from cv2.waitKey()
            dataset_manager: Optional DatasetManager instance for annotation actions
            frame: Optional frame for screenshot actions

        Returns:
            str: Action to take ('quit', 'continue', 'annotate_good', 'annotate_bad', 'annotate_neutral')
        """
        action = self.get_action(key_code)

        if action == 'quit':
            return 'quit'

        elif action == 'pause':
            self.paused = not self.paused
            status = "PAUSED" if self.paused else "RESUMED"
            print(f"\n{status}")
            return 'continue'

        elif action == 'toggle_debug':
            self.show_debug = not self.show_debug
            print(f"\nDebug overlay: {'ON' if self.show_debug else 'OFF'}")
            return 'continue'

        elif action == 'show_help':
            self.show_help_overlay = not self.show_help_overlay
            if self.show_help_overlay:
                self.print_help()
            return 'continue'

        elif action == 'save_screenshot':
            if frame is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                cv2.imwrite(filename, frame)
                print(f"\nScreenshot saved: {filename}")
            return 'continue'

        elif action == 'toggle_good_recording':
            if dataset_manager:
                if self.recording_label == 'good':
                    self.recording_label = None
                    print("\n⏹  Stopped recording GOOD posture")
                else:
                    self.recording_label = 'good'
                    print("\n⏺  Started recording GOOD posture")
            return 'continue'

        elif action == 'toggle_bad_recording':
            if dataset_manager:
                if self.recording_label == 'bad':
                    self.recording_label = None
                    print("\n⏹  Stopped recording BAD posture")
                else:
                    self.recording_label = 'bad'
                    print("\n⏺  Started recording BAD posture")
            return 'continue'

        elif action == 'toggle_neutral_recording':
            if dataset_manager:
                if self.recording_label == 'neutral':
                    self.recording_label = None
                    print("\n⏹  Stopped recording NEUTRAL")
                else:
                    self.recording_label = 'neutral'
                    print("\n⏺  Started recording NEUTRAL")
            return 'continue'

        elif action == 'increase_save_rate':
            if dataset_manager:
                dataset_manager.adjust_save_rate(1.5)
            return 'continue'

        elif action == 'decrease_save_rate':
            if dataset_manager:
                dataset_manager.adjust_save_rate(0.75)
            return 'continue'

        return 'continue'

    def print_help(self):
        """Print keybind help to console"""
        print("\n" + "="*60)
        print("KEYBIND REFERENCE")
        print("="*60)

        categories = {
            'General': ['quit', 'pause', 'show_help', 'toggle_debug', 'save_screenshot'],
            'Display': ['toggle_landmarks'],
            'Recording': ['toggle_good_recording', 'toggle_bad_recording', 'toggle_neutral_recording'],
            'Controls': ['increase_save_rate', 'decrease_save_rate']
        }

        for category, actions in categories.items():
            print(f"\n{category}:")
            for action in actions:
                if action in self.key_names:
                    info = self.key_names[action]
                    print(f"  [{info['key'].upper()}] - {info['description']}")

        print("\n" + "="*60 + "\n")

    def draw_help_overlay(self, frame):
        """Draw help overlay on frame

        Args:
            frame: Frame to draw on

        Returns:
            Modified frame with help overlay
        """
        if not self.show_help_overlay:
            return frame

        overlay = frame.copy()
        height, width = frame.shape[:2]

        # Semi-transparent background
        cv2.rectangle(overlay, (10, 10), (width - 10, height - 10), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

        # Title
        cv2.putText(frame, "KEYBINDS", (width//2 - 100, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        # Keybind list
        y_pos = 80
        for info in self.key_names.values():
            text = f"[{info['key'].upper()}] {info['description']}"
            cv2.putText(frame, text, (30, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 25

            if y_pos > height - 30:
                break

        cv2.putText(frame, "Press [H] to hide", (width//2 - 80, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        return frame

    def draw_status_overlay(self, frame, dataset_manager=None):
        """Draw status information overlay

        Args:
            frame: Frame to draw on
            dataset_manager: Optional DatasetManager for save stats

        Returns:
            Modified frame with status overlay
        """
        height, width = frame.shape[:2]
        y_pos = 100

        # Always show recording status if active (even without debug mode)
        if self.recording_label:
            # Draw recording indicator in top-right corner
            label_text = f"REC [{self.recording_label.upper()}]"
            text_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            x_pos = width - text_size[0] - 20

            # Blinking effect (blink every ~30 frames at 30fps = 1Hz)
            import time
            if int(time.time() * 2) % 2 == 0:  # Blink at 2Hz
                color = (0, 0, 255) if self.recording_label == 'bad' else (0, 255, 0)
                cv2.putText(frame, label_text, (x_pos, 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        if not self.show_debug:
            return frame

        # Paused status
        if self.paused:
            cv2.putText(frame, "PAUSED", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            y_pos += 40

        # Recording label info
        if self.recording_label and dataset_manager:
            cv2.putText(frame, f"Recording: {self.recording_label.upper()}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y_pos += 30

        # Dataset manager info
        if dataset_manager:
            label_key = self.recording_label if self.recording_label else 'general'
            save_count = dataset_manager.annotation_count.get(self.recording_label, 0) if self.recording_label else dataset_manager.save_count

            info_text = [
                f"Save rate: {dataset_manager.args.save_rate:.1f}/min",
                f"Saved ({label_key}): {save_count}",
                f"Interval: {dataset_manager.save_interval:.1f}s"
            ]

            for text in info_text:
                cv2.putText(frame, text, (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y_pos += 20

        return frame
