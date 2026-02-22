# 👁️ Human Detection System

Real-time human detection using YOLOv8 and OpenCV with both standalone and Flask API versions for React integration.

## 🚀 Two Usage Modes

### 1. Standalone Detection (`human_detector.py`)
Real-time detection that displays coordinates in console and OpenCV window.

### 2. Flask API (`human_detector_api.py`) 
Web API that provides video streaming and coordinates for React frontend integration.

## 📁 Files

- `human_detector.py` - Original standalone version with OpenCV display
- `human_detector_api.py` - Flask API server for React integration  
- `requirements.txt` - Python dependencies for both versions
- `README.md` - This file

## 🔧 Installation

Install dependencies:
```bash
pip install -r requirements.txt
```

## 🖥️ Standalone Usage

Run the standalone detection script:
```bash
python human_detector.py
```

### Controls
- **q**: Quit the application  
- **r**: Reset detection

### Output
- Prints coordinates to console: `👤 Person detected at center: (x, y) - Confidence: 0.XX`
- Shows green bounding box around person
- Red circle marks center position
- Coordinates displayed as text overlay

## 🌐 Flask API Usage

Start the API server:
```bash
python human_detector_api.py
```

Server runs on `http://localhost:5001`

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web testing interface |
| GET | `/video_feed` | Live video stream with overlays |
| GET | `/coordinates` | Current human coordinates (JSON) |
| POST | `/start` | Start detection system |
| POST | `/stop` | Stop detection system |
| GET | `/status` | Get system status |

### Coordinate Response Format
```json
{
  "x": 320,
  "y": 240, 
  "detected": true,
  "confidence": 0.85,
  "timestamp": "2025-01-21T10:30:45.123456"
}
```

## ⚛️ React Integration

The API is designed to work with React eye tracking components:

```javascript
// Example: Poll for coordinates every 100ms
const fetchCoordinates = async () => {
  try {
    const response = await fetch('http://localhost:5001/coordinates')
    const data = await response.json()
    
    if (data.detected) {
      // Convert camera coords to eye movement (-40 to 40)
      const eyeX = (data.x / 640 - 0.5) * 40
      const eyeY = (data.y / 480 - 0.5) * 20
      setEyePosition({ x: eyeX, y: eyeY })
    }
  } catch (error) {
    console.error('Coordinate fetch failed:', error)
  }
}
```

See `HumanTrackingEyes.jsx` in the main app for complete implementation.

## 🎯 Features

- ✅ Real-time human detection using YOLOv8 nano
- ✅ Center coordinate calculation and tracking
- ✅ Largest person priority (closest/biggest detection)
- ✅ Video streaming with detection overlays
- ✅ RESTful API with CORS support
- ✅ Confidence filtering (>50% threshold)
- ✅ Multi-camera support (auto-detects cameras 0-4)
- ✅ React frontend integration ready

## ⚙️ Technical Details

- **Model**: YOLOv8 nano (`yolov8n.pt`) for speed
- **Person Class**: ID 0 (COCO dataset)
- **Confidence Threshold**: 0.5 minimum
- **Camera Resolution**: 640x480 (configurable)
- **Frame Rate**: ~30 FPS detection, ~10 FPS API polling recommended
- **Selection**: Largest bounding box when multiple people detected

## 🔧 Troubleshooting

### Camera Issues
- Close other apps using camera
- Check Windows camera permissions
- Try different camera indices (0-4)

### API Connection Issues  
- Verify server running on port 5001
- Check firewall/antivirus blocking Flask
- Ensure Flask-CORS installed for React

### Performance Issues
- Use YOLOv8n (nano) model for speed
- Reduce camera resolution if needed
- Limit API polling to 100ms intervals

## 📊 System Requirements

- **Python**: 3.8+
- **Camera**: Any USB/built-in webcam
- **Memory**: ~500MB for loaded model
- **CPU**: Modern processor recommended
- **OS**: Windows/Linux/macOS

---

*Part of makeMIT 2025 Smart Trash Bin Project* 🗑️👁️