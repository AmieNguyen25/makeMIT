#!/usr/bin/env python3
"""
Real-time Human Detection API using YOLOv8 and Flask
Provides video streaming and real-time human coordinates for React frontend
"""

import cv2
import numpy as np
from ultralytics import YOLO
import sys
import threading
import time
from flask import Flask, Response, jsonify, render_template_string
from flask_cors import CORS
import queue
import json
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

class HumanDetectorAPI:
    def __init__(self):
        """Initialize the human detector API with YOLOv8 model"""
        try:
            # Initialize YOLOv8 model
            print("🔄 Loading YOLOv8 model...")
            self.model = YOLO('yolov8n.pt')  # Using nano model for speed
            print("✅ YOLOv8 model loaded successfully")
            
            # Person class ID in COCO dataset
            self.person_class_id = 0
            
            # API state variables
            self.cap = None
            self.running = False
            self.detection_thread = None
            self.latest_frame = None
            self.latest_coordinates = {'x': None, 'y': None, 'detected': False}
            self.frame_lock = threading.Lock()
            self.coord_lock = threading.Lock()
            
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            sys.exit(1)
    
    def initialize_camera(self):
        """Initialize webcam"""
        print("📷 Initializing camera...")
        
        # Try different camera indices
        for camera_index in range(5):
            print(f"🔍 Trying camera index {camera_index}...")
            self.cap = cv2.VideoCapture(camera_index)
            
            if self.cap.isOpened():
                ret, _ = self.cap.read()
                if ret:
                    print(f"✅ Camera {camera_index} opened successfully!")
                    break
                else:
                    self.cap.release()
        else:
            print("❌ Error: No camera available")
            return False
            
        # Set camera resolution for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for real-time
        
        print("✅ Camera initialized successfully")
        return True
    
    def calculate_center(self, bbox):
        """Calculate center coordinates of bounding box"""
        x1, y1, x2, y2 = bbox
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        return center_x, center_y
    
    def calculate_bbox_area(self, bbox):
        """Calculate area of bounding box"""
        x1, y1, x2, y2 = bbox
        return (x2 - x1) * (y2 - y1)
    
    def detect_humans(self, frame):
        """Detect humans in frame and return largest bounding box"""
        try:
            # Run YOLOv8 inference
            results = self.model(frame, verbose=False)
            
            person_detections = []
            
            # Process detections
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get class ID and confidence
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        
                        # Filter for person class with minimum confidence
                        if class_id == self.person_class_id and confidence > 0.5:
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                            person_detections.append({
                                'bbox': [x1, y1, x2, y2],
                                'confidence': confidence,
                                'area': self.calculate_bbox_area([x1, y1, x2, y2])
                            })
            
            # Return largest detection (closest person) if any found
            if person_detections:
                largest_detection = max(person_detections, key=lambda x: x['area'])
                return largest_detection
            
            return None
            
        except Exception as e:
            print(f"❌ Detection error: {e}")
            return None
    
    def draw_detection(self, frame, detection):
        """Draw bounding box and center circle on frame"""
        bbox = detection['bbox']
        confidence = detection['confidence']
        x1, y1, x2, y2 = bbox
        
        # Calculate center
        center_x, center_y = self.calculate_center(bbox)
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Draw center circle
        cv2.circle(frame, (center_x, center_y), 8, (0, 0, 255), -1)  # Red filled circle
        cv2.circle(frame, (center_x, center_y), 15, (0, 0, 255), 2)  # Red outer circle
        
        # Add text with coordinates
        text = f"Center: ({center_x}, {center_y})"
        cv2.putText(frame, text, (center_x - 80, center_y - 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Add confidence text
        conf_text = f"Conf: {confidence:.2f}"
        cv2.putText(frame, conf_text, (x1, y1 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return center_x, center_y
    
    def detection_loop(self):
        """Main detection loop running in separate thread"""
        print("🚀 Starting detection loop...")
        
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Error: Could not read from camera")
                time.sleep(0.1)
                continue
            
            # Detect humans in current frame
            detection = self.detect_humans(frame)
            
            # Update coordinates
            with self.coord_lock:
                if detection:
                    center_x, center_y = self.draw_detection(frame, detection)
                    self.latest_coordinates = {
                        'x': center_x,
                        'y': center_y,
                        'detected': True,
                        'confidence': detection['confidence'],
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    # No person detected
                    cv2.putText(frame, "No person detected", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    self.latest_coordinates = {
                        'x': None,
                        'y': None,
                        'detected': False,
                        'confidence': 0,
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Add status info
            cv2.putText(frame, "Human Detector API - Running", (10, frame.shape[0] - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"Frame: {frame.shape[1]}x{frame.shape[0]}", (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            # Store latest frame
            with self.frame_lock:
                self.latest_frame = frame.copy()
            
            # Small delay for performance
            time.sleep(0.033)  # ~30 FPS
    
    def start_detection(self):
        """Start the detection system"""
        if self.running:
            return False, "Detection already running"
        
        if not self.initialize_camera():
            return False, "Failed to initialize camera"
        
        self.running = True
        self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
        self.detection_thread.start()
        
        print("✅ Human detection started")
        return True, "Detection started successfully"
    
    def stop_detection(self):
        """Stop the detection system"""
        if not self.running:
            return False, "Detection not running"
        
        self.running = False
        
        if self.detection_thread:
            self.detection_thread.join(timeout=2)
        
        if self.cap:
            self.cap.release()
        
        print("🛑 Human detection stopped")
        return True, "Detection stopped successfully"

# Global instance
detector = HumanDetectorAPI()

@app.route('/')
def index():
    """Simple HTML page for testing the system"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Human Detector API</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background-color: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; }
            .video-container { margin: 20px 0; }
            .controls { background: #fff; border-radius: 8px; padding: 15px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #0056b3; }
            .coordinates { font-size: 24px; font-weight: bold; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👁️ Human Detector API</h1>
            
            <div class="video-container">
                <img src="/video_feed" style="width: 100%; max-width: 640px; border: 2px solid #ddd; border-radius: 8px;">
            </div>
            
            <div class="controls">
                <h3>System Controls</h3>
                <button class="btn" onclick="startDetection()">Start Detection</button>
                <button class="btn" onclick="stopDetection()">Stop Detection</button>
                <button class="btn" onclick="getCoordinates()">Get Coordinates</button>
            </div>
            
            <div class="controls" id="statusPanel">
                <h3>Current Coordinates</h3>
                <div class="coordinates" id="coordinates">No human detected</div>
                <div id="status">System Ready</div>
            </div>
        </div>
        
        <script>
            function startDetection() {
                fetch('/start', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => alert(data.message));
            }
            
            function stopDetection() {
                fetch('/stop', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => alert(data.message));
            }
            
            function getCoordinates() {
                fetch('/coordinates')
                    .then(response => response.json())
                    .then(data => {
                        if (data.detected) {
                            document.getElementById('coordinates').innerHTML = 
                                `Human at (${data.x}, ${data.y}) - Conf: ${(data.confidence * 100).toFixed(1)}%`;
                        } else {
                            document.getElementById('coordinates').innerHTML = 'No human detected';
                        }
                    });
            }
            
            // Auto-refresh coordinates every second
            setInterval(getCoordinates, 1000);
        </script>
    </body>
    </html>
    ''')

@app.route('/video_feed')
def video_feed():
    """Video streaming endpoint"""
    def generate_frames():
        while detector.running:
            with detector.frame_lock:
                if detector.latest_frame is not None:
                    # Encode frame as JPEG
                    ret, buffer = cv2.imencode('.jpg', detector.latest_frame, 
                                             [cv2.IMWRITE_JPEG_QUALITY, 85])
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.033)  # ~30 FPS
    
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/coordinates', methods=['GET'])
def get_coordinates():
    """Get current human coordinates"""
    with detector.coord_lock:
        return jsonify(detector.latest_coordinates)

@app.route('/start', methods=['POST'])
def start_detection():
    """Start human detection"""
    try:
        success, message = detector.start_detection()
        return jsonify({
            'status': 'success' if success else 'error',
            'message': message,
            'running': detector.running
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error starting detection: {str(e)}',
            'running': False
        })

@app.route('/stop', methods=['POST'])
def stop_detection():
    """Stop human detection"""
    try:
        success, message = detector.stop_detection()
        return jsonify({
            'status': 'success' if success else 'error',
            'message': message,
            'running': detector.running
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error stopping detection: {str(e)}',
            'running': detector.running
        })

@app.route('/status')
def get_status():
    """Get system status"""
    with detector.coord_lock:
        return jsonify({
            'running': detector.running,
            'latest_coordinates': detector.latest_coordinates,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

if __name__ == "__main__":
    print("🤖 Human Detection API Server")
    print("=" * 50)
    print("🌐 API Endpoints:")
    print("   GET  /              - Web interface")
    print("   GET  /video_feed    - Live video stream")
    print("   GET  /coordinates   - Current human coordinates")
    print("   POST /start         - Start detection system")
    print("   POST /stop          - Stop detection system")
    print("   GET  /status        - Get system status")
    print("=" * 50)
    print("📱 Frontend Integration:")
    print("   Video stream URL: http://localhost:5001/video_feed")
    print("   Coordinates API: http://localhost:5001/coordinates")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        detector.stop_detection()
        print("👋 Goodbye!")