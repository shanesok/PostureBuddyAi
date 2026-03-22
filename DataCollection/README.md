## Project Structure

```
Posture-detection/DataCollection/
├── utils/          # Main package
│   ├── app.py              # Main application class
│   ├── config/             # Configuration module
│   │   └── argument_parser.py
│   ├── camera/             # Camera management
│   │   └── camera_manager.py
│   ├── detection/          # Pose detection
│   │   └── pose_detector.py
│   ├── data/               # Data management
│   │   └── dataset_manager.py
│   └── ui/                 # User interface
│       └── keybind_manager.py
├── main.py                 # Entry 
└── requirements.txt        # Dependencies
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Test Camera
Test camera feed only (no pose detection):
```bash
python main.py --test-camera
```

### Test Pose Detection
Test pose detection with landmarks:
```bash
python main.py --test-pose
```

### Save Data
Collect dataset with pose detection:
```bash
python main.py --test-pose --save-data --save-frames --save-landmarks --save-rate 300.0 --username YourName
```

## Keybinds (in test-pose mode, partial WIP)

### General
- **Q** - Quit the program
- **P** - Pause/Resume processing
- **H** - Show/Hide help overlay
- **D** - Toggle debug overlay
- **S** - Save screenshot

### Annotation (for dataset labeling)
- **G** - Mark current frame as GOOD posture
- **B** - Mark current frame as BAD posture
- **N** - Mark current frame as NEUTRAL

### Recording
- **[** - Decrease save rate
- **]** - Increase save rate

## CLI Options

Run `python main.py --help` to see all available options.

### Camera Settings
- `--camera` - Camera device index (default: 0)
- `--width` - Frame width (default: 640)
- `--height` - Frame height (default: 480)
- `--fps` - Target FPS (default: 30)
- `--no-mirror` - Disable mirror mode

### Display Settings
- `--no-display` - Run headless
- `--no-fps` - Hide FPS counter
- `--no-landmarks` - Hide pose landmarks
- `--show-skeleton` - Draw skeleton connections
- `--show-angles` - Display calculated angles

### Model Settings
- `--model-complexity` - Model complexity: 0=Lite, 1=Full, 2=Heavy
- `--min-detection-confidence` - Min detection confidence (0.0-1.0)
- `--min-tracking-confidence` - Min tracking confidence (0.0-1.0)

### Data Saving
- `--save-data` - Enable data saving
- `--save-dir` - Base directory (default: ~/PostureBuddy_Data)
- `--username` - Username for organization
- `--save-frames` - Save raw frames
- `--save-annotated` - Save annotated frames
- `--save-landmarks` - Save landmark CSV
- `--save-rate` - Saves per minute (default: 5.0)
- `--frame-format` - Image format: png or jpg

## Dataset Structure

When saving data, PostureBuddy creates organized folders:

```
~/PostureBuddy_Data/username_YYYYMMDD_HHMMSS/
├── config.json              # Session configuration
├── frames/                  # Raw frames (--save-frames)
├── annotated/              # Annotated frames (--save-annotated)
├── landmarks.csv           # Landmark data (--save-landmarks)
├── good_posture/           # Manual annotations (G key)
│   ├── raw_good_*.png
│   ├── annotated_good_*.png
│   └── landmarks_good.csv
├── bad_posture/            # Manual annotations (B key)
│   ├── raw_bad_*.png
│   ├── annotated_bad_*.png
│   └── landmarks_bad.csv
└── neutral/                # Manual annotations (N key)
    ├── raw_neutral_*.png
    ├── annotated_neutral_*.png
    └── landmarks_neutral.csv
```