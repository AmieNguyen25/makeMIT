# Human Detection System

Real-time human detection using YOLOv8 and OpenCV that detects humans in camera feed and displays their center coordinates.

## Features
- ✅ Real-time human detection using YOLOv8
- ✅ Calculates and prints center coordinates (x, y) of detected persons
- ✅ Draws circles at center positions 
- ✅ Selects largest bounding box when multiple people detected (closest person)
- ✅ Optimized for performance with lightweight YOLOv8n model

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the human detection script:
```bash
python human_detector.py
```

### Controls
- **q**: Quit the application
- **r**: Reset detection

### Output
When a person is detected, the script will:
- Print center coordinates to console: `👤 Person detected at center: (x, y) - Confidence: 0.XX`
- Draw a green bounding box around the person
- Draw a red circle at the center position
- Display the coordinates as text overlay

## Technical Details
- Uses YOLOv8 nano model for fast inference
- Person class ID: 0 (COCO dataset)
- Minimum confidence threshold: 0.5
- Camera resolution: 640x480 for optimal performance
- Selects largest bounding box area when multiple detections

## Requirements
- Python 3.8+
- Webcam/camera device
- See requirements.txt for package dependencies