# 🚀 Quick Setup Guide - Human Detection API

## Step 1: Install Dependencies

```bash
# Navigate to human detection folder
cd humandetect

# Install Python dependencies
pip install -r requirements.txt
```

## Step 2: Start the Human Detection API 

```bash
# Start the API server (runs on port 5001)
python human_detector_api.py
```

You should see:
```
🤖 Human Detection API Server
==================================================
🌐 API Endpoints:
   GET  /              - Web interface
   GET  /video_feed    - Live video stream
   GET  /coordinates   - Current human coordinates
   POST /start         - Start detection system
   POST /stop          - Stop detection system
   GET  /status        - Get system status
==================================================
📱 Frontend Integration:
   Video stream URL: http://localhost:5001/video_feed
   Coordinates API: http://localhost:5001/coordinates
==================================================
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5001
 * Running on http://[your-ip]:5001
```

## Step 3: Test the API (Optional)

Open your browser and go to: `http://localhost:5001`

- Click "Start Detection" to begin human tracking
- You should see yourself in the video feed with detection boxes
- The coordinates will update in real-time

## Step 4: Start Your React App

```bash
# In your main project folder
npm run dev
```

## Step 5: Test Human Eye Tracking

1. Go to your React app (usually `http://localhost:5173`)
2. You'll see the eyes page with human tracking enabled by default
3. Click "🤖 Start Human Tracking" to begin
4. The eyes should now track your movement!

## 🎯 How It Works

1. **Human Detection API** (port 5001):
   - Captures video from your camera
   - Detects humans using YOLOv8
   - Calculates center coordinates
   - Provides real-time coordinates via REST API

2. **React Frontend** (port 5173):
   - Polls `/coordinates` endpoint every 100ms
   - Converts human coordinates to eye movement
   - Eyes track the detected human in real-time
   - Shows detection status and video preview

## 🔧 Troubleshooting

### Camera Access Issues
If you get camera errors:
```bash
# Try the standalone version first to test camera
python human_detector.py
```

### API Connection Issues
- Make sure Flask API is running on port 5001
- Check that no firewall is blocking the port
- Verify React app can access `http://localhost:5001`

### No Human Detection
- Make sure you're in front of the camera
- Try better lighting
- Check that confidence threshold isn't too high (default: 0.5)

## 🎮 Controls

### In React App:
- **🤖 Start Human Tracking**: Begins API detection
- **👁️ Stop Human Tracking**: Stops detection, returns to mouse mode
- **🖱️ Switch to Mouse Tracking**: Uses mouse movement instead
- **🗑️ Go to Trash Tracker**: Navigate to trash detection

### Eye Color Indicators:
- 🟢 **Green**: Human detected and tracking
- 🔴 **Red**: Human tracking mode but no human found
- 🟡 **Normal**: Mouse tracking mode

---

**Ready to track humans with your robot eyes!** 👁️🤖