import os
import cv2
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
import time
import base64
from flask import Flask, Response, jsonify, render_template_string
from flask_cors import CORS
import threading
import queue
import json
import requests

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Load environment variables
local_env_loaded = load_dotenv('.env')
if not local_env_loaded:
    backend_env_path = os.path.join('..', 'backend', '.env')
    load_dotenv(backend_env_path)

# Initialize Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")

if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    print("✅ Gemini configured successfully")
else:
    print("❌ GEMINI_API_KEY not found in environment variables") 
    exit(1)

class SmartTrashBinAPI:
    def __init__(self):
        self.cap = None
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=50, detectShadows=True
        )
        self.last_classification_time = 0
        self.cooldown_period = 5.0  # 5 seconds
        self.motion_threshold = 5000  # Minimum contour area for motion detection
        self.classification_in_progress = False
        self.latest_classification_result = None
        self.latest_frame = None
        self.frame_queue = queue.Queue(maxsize=10)
        self.running = False
        self.camera_thread = None
        
        # Robot movement API configuration
        self.robot_base_url = "http://10.250.167.161/move"
        self.robot_api_timeout = 5.0  # seconds
        
        # Robot movement parameters for each classification
        self.robot_movements = {
            'plastic': {'spin': 65, 'pivot': -40},
            'can': {'spin': 65, 'pivot': 40},
            'paper': {'spin': -65, 'pivot': -40},
            'other': {'spin': -65, 'pivot': 40}
        }
        
    def initialize_camera(self):
        """Initialize webcam"""
        global has_camera
        print("📷 Initializing camera...")
        
        # Try different camera indices
        for camera_index in range(5):  # Try cameras 0-4
            print(f"🔍 Trying camera index {camera_index}...")
            self.cap = cv2.VideoCapture(camera_index)
            
            if self.cap.isOpened():
                # Test if camera can actually read frames with timeout
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to avoid lag
                ret, _ = self.cap.read()
                if ret:
                    print(f"✅ Camera {camera_index} opened successfully!")
                    break
                else:
                    print(f"❌ Camera index {camera_index} opened but cannot read frames")
                    self.cap.release()
            else:
                print(f"❌ Camera index {camera_index} failed to open")
            
            if camera_index == 4:  # Last attempt
                print("⚠️ No camera detected - enabling web-only mode")
                self.cap = None
                has_camera = False
                return False
            
        # Set camera resolution if we have a working camera
        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Quick warm up test
            ret, _ = self.cap.read()
            if not ret:
                print("❌ Error: Could not read from camera during warmup")
                self.cap.release()
                self.cap = None
                has_camera = False
                return False
                
        print("✅ Camera initialized successfully")
        has_camera = True
        return True
    
    def detect_motion(self, frame):
        """Detect motion in the current frame"""
        # Apply background subtraction
        fg_mask = self.background_subtractor.apply(frame)
        
        # Remove noise using morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check if any contour is large enough to be considered motion
        for contour in contours:
            if cv2.contourArea(contour) > self.motion_threshold:
                return True, contours
                
        return False, contours
    
    def capture_and_resize(self, frame):
        """Capture and resize frame to 640x480"""
        # Ensure frame is 640x480
        resized_frame = cv2.resize(frame, (640, 480))
        return resized_frame
    
    def frame_to_base64(self, frame):
        """Convert frame to base64 encoded JPEG"""
        # Encode frame as JPEG with lower quality for faster processing
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        
        # Convert to base64
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return image_base64
    
    def classify_object(self, frame):
        """Classify object in frame using Gemini AI"""
        try:
            start_time = time.time()
            
            # Resize and encode frame
            resized_frame = self.capture_and_resize(frame)
            image_base64 = self.frame_to_base64(resized_frame)
            
            # Classification prompt
            prompt = """Classify the primary object based on material composition, not brand or label.
IMPORTANT: If you only see an empty black plate with no object on it, respond with "no_object".
If there IS an object ON the plate, classify only the PRIMARY OBJECT (not the plate) as:

- no_object (if the black plate is empty with no object on it)
- can (metal, aluminum beverage cans)
- plastic (bottles)
- paper (paper, cardboard, newspapers, paper materials)
- other (any object that does not fit the above categories)


Rules:
- Empty plate = "no_object"
- Plate with object = classify the object only
- Ignore the plate itself in classification

Return exactly one lowercase word.
If uncertain, infer based on visible material texture.
Do not explain. Do not detect the plate. Focus on the primary object."""
            
            # Create model and generate content
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Convert base64 to bytes
            image_bytes = base64.b64decode(image_base64)
            
            # Create image part
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
            
            # Generate content
            response = model.generate_content([prompt, image_part])
            
            processing_time = (time.time() - start_time) * 1000
            classification_text = response.text.strip().lower()
            
            # Validate response
            valid_categories = ['can', 'plastic', 'paper', 'other', 'no_object']
            
            if classification_text in valid_categories:
                result_classification = classification_text
            else:
                # Try to extract valid category
                for category in valid_categories:
                    if category in classification_text:
                        result_classification = category
                        break
                else:
                    result_classification = 'no_object'
            
            return {
                'classification': result_classification,
                'raw_response': classification_text,
                'processing_time': processing_time
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
            return {
                'classification': 'error',
                'error': str(e),
                'processing_time': processing_time
            }
    
    def is_in_cooldown(self):
        """Check if we're still in cooldown period"""
        return (time.time() - self.last_classification_time) < self.cooldown_period
    
    def start_camera_streaming(self):
        """Start camera in a separate thread for streaming"""
        if not self.initialize_camera():
            return False
            
        self.running = True
        self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.camera_thread.start()
        print("📹 Camera streaming started")
        return True
    
    def stop_camera_streaming(self):
        """Stop camera streaming"""
        self.running = False
        if self.camera_thread:
            self.camera_thread.join()
        if self.cap:
            self.cap.release()
        print("📹 Camera streaming stopped")
    
    def _camera_loop(self):
        """Main camera loop running in separate thread"""
        frame_count = 0
        
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("⚠️ Error reading frame")
                time.sleep(0.1)
                continue
                
            frame_count += 1
            
            # Detect motion
            motion_detected, contours = self.detect_motion(frame)
            
            # Create display frame with overlays
            display_frame = self._create_display_frame(frame.copy(), motion_detected, contours, frame_count)
            
            # Store latest frame for streaming
            self.latest_frame = display_frame
            
            # Handle motion detection and classification
            if motion_detected and not self.is_in_cooldown() and not self.classification_in_progress:
                print(f"🎯 Motion detected! Capturing frame #{frame_count}")
                self._start_classification_thread(frame.copy())
            
            time.sleep(0.033)  # ~30 FPS
    
    def _create_display_frame(self, frame, motion_detected, contours, frame_count):
        """Create frame with all visual overlays"""
        display_frame = frame.copy()
        
        if motion_detected:
            # Draw motion contours
            cv2.drawContours(display_frame, contours, -1, (0, 255, 0), 2)
            cv2.putText(display_frame, "MOTION DETECTED", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if self.classification_in_progress:
                cv2.putText(display_frame, "CLASSIFYING...", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            elif self.is_in_cooldown():
                remaining_cooldown = self.cooldown_period - (time.time() - self.last_classification_time)
                cv2.putText(display_frame, f"COOLDOWN: {remaining_cooldown:.1f}s", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
        
        # Display latest classification result
        if self.latest_classification_result:
            result = self.latest_classification_result
            if result['classification'] != 'error':
                cv2.putText(display_frame, f"CLASSIFIED: {result['classification'].upper()}", 
                           (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
                cv2.putText(display_frame, f"Time: {result['processing_time']:.0f}ms", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            else:
                cv2.putText(display_frame, "CLASSIFICATION FAILED", 
                           (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
        
        # Add status text
        status_text = "READY" if not motion_detected else "MOTION"
        api_status = " | API: BUSY" if self.classification_in_progress else " | API: READY"
        cv2.putText(display_frame, f"Status: {status_text}{api_status}", (10, display_frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return display_frame
    
    def _start_classification_thread(self, frame):
        """Start classification in a separate thread"""
        if not self.classification_in_progress:
            self.classification_in_progress = True
            self.last_classification_time = time.time()
            
            classification_thread = threading.Thread(
                target=self._classify_in_thread, 
                args=(frame,), 
                daemon=True
            )
            classification_thread.start()
    
    def _classify_in_thread(self, frame):
        """Run classification in separate thread"""
        try:
            result = self.classify_object(frame)
            self.latest_classification_result = result
            
            # Print results
            timestamp = datetime.now().strftime("%H:%M:%S")
            if result['classification'] != 'error':
                classification = result['classification'].lower()
                
                if classification == 'no_object':
                    print(f"📭 [{timestamp}] No object detected on plate - no action needed")
                else:
                    print(f"✅ [{timestamp}] Classification: {classification.upper()}")
                    print(f"   Processing time: {result['processing_time']:.0f}ms")
                    
                    # Call robot movement API for detected classifications
                    if classification in self.robot_movements:
                        print(f"🔍 {classification.capitalize()} detected! Triggering robot movement...")
                        robot_success = self.call_robot_movement_api(classification)
                        if robot_success:
                            print(f"🎯 Robot movement for {classification} completed successfully")
                        else:
                            print(f"⚠️ Robot movement for {classification} failed, but classification completed")
                        
            else:
                print(f"❌ [{timestamp}] Classification failed: {result.get('error', 'Unknown error')}")
                
        finally:
            self.classification_in_progress = False
    
    def call_robot_movement_api(self, classification):
        """Call robot movement API for detected classification"""
        try:
            if classification not in self.robot_movements:
                print(f"⚠️ No robot movement configured for: {classification}")
                return False
                
            movement = self.robot_movements[classification]
            api_url = f"{self.robot_base_url}?spin={movement['spin']}&pivot={movement['pivot']}"
            
            print(f"🤖 Calling robot movement API for {classification}: {api_url}")
            response = requests.get(
                api_url,
                timeout=self.robot_api_timeout
            )
            
            if response.status_code == 200:
                print(f"✅ Robot movement API call for {classification} successful")
                
                # Wait 2 seconds before resetting to neutral position
                print("⏱️ Waiting 2 seconds before reset...")
                time.sleep(2)
                
                # Reset robot to neutral position after movement
                reset_url = f"{self.robot_base_url}?spin=0&pivot=0"
                print(f"🔄 Resetting robot to neutral position: {reset_url}")
                
                try:
                    reset_response = requests.get(reset_url, timeout=self.robot_api_timeout)
                    if reset_response.status_code == 200:
                        print("✅ Robot reset to neutral position successful")
                    else:
                        print(f"⚠️ Robot reset failed with status code: {reset_response.status_code}")
                except Exception as reset_error:
                    print(f"⚠️ Robot reset failed: {str(reset_error)}")
                
                return True
            else:
                print(f"⚠️ Robot API returned status code: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"❌ Robot API call for {classification} timed out")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Could not connect to robot API for {classification}")
            return False
        except Exception as e:
            print(f"❌ Robot API call for {classification} failed: {str(e)}")
            return False

# Global instance of the trash bin system
trash_bin = SmartTrashBinAPI()

@app.route('/')
def index():
    """Simple HTML page for testing the video stream"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Trash Bin API</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background-color: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; }
            .video-container { margin: 20px 0; }
            .status-panel { background: #fff; border-radius: 8px; padding: 15px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #0056b3; }
            .classification-result { font-size: 24px; font-weight: bold; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗑️ Smart Trash Bin Classification System</h1>
            
            <div class="video-container">
                <img src="/video_feed" style="width: 100%; max-width: 640px; border: 2px solid #ddd; border-radius: 8px;">
            </div>
            
            <div class="status-panel">
                <h3>System Controls</h3>
                <button class="btn" onclick="startSystem()">Start System</button>
                <button class="btn" onclick="stopSystem()">Stop System</button>
                <button class="btn" onclick="getStatus()">Get Status</button>
            </div>
            
            <div class="status-panel" id="statusPanel">
                <h3>Current Status</h3>
                <div id="systemStatus">System Ready</div>
                <div class="classification-result" id="lastClassification">No classification yet</div>
            </div>
        </div>
        
        <script>
            function startSystem() {
                fetch('/start')
                    .then(response => response.json())
                    .then(data => alert(data.message));
            }
            
            function stopSystem() {
                fetch('/stop')
                    .then(response => response.json())
                    .then(data => alert(data.message));
            }
            
            function getStatus() {
                fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('systemStatus').innerHTML = 
                            `Running: ${data.running}<br>` +
                            `Classifying: ${data.classification_in_progress}<br>` +
                            `Cooldown: ${data.in_cooldown}`;
                        
                        if (data.latest_classification) {
                            const result = data.latest_classification;
                            document.getElementById('lastClassification').innerHTML = 
                                `Latest: ${result.classification.toUpperCase()} (${result.processing_time}ms)`;
                        }
                    });
            }
            
            // Auto-refresh status every 2 seconds
            setInterval(getStatus, 2000);
        </script>
    </body>
    </html>
    ''')

@app.route('/video_feed')
def video_feed():
    """Video streaming endpoint"""
    def generate_frames():
        while trash_bin.running:
            if trash_bin.latest_frame is not None:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', trash_bin.latest_frame, 
                                         [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.033)  # ~30 FPS
    
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start', methods=['GET', 'POST'])
def start_system():
    """Start the camera system"""
    try:
        if trash_bin.running:
            return jsonify({
                'status': 'warning',
                'message': 'System already running',
                'running': True
            })
        
        success = trash_bin.start_camera_streaming()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Smart Trash Bin system started successfully',
                'running': True
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to start camera system',
                'running': False
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error starting system: {str(e)}',
            'running': False
        })

@app.route('/stop', methods=['GET', 'POST'])
def stop_system():
    """Stop the camera system"""
    try:
        trash_bin.stop_camera_streaming()
        return jsonify({
            'status': 'success',
            'message': 'Smart Trash Bin system stopped',
            'running': False
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error stopping system: {str(e)}',
            'running': trash_bin.running
        })

@app.route('/status')
def get_status():
    """Get current system status"""
    return jsonify({
        'running': trash_bin.running,
        'classification_in_progress': trash_bin.classification_in_progress,
        'in_cooldown': trash_bin.is_in_cooldown(),
        'latest_classification': trash_bin.latest_classification_result,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/classify', methods=['POST'])
def trigger_classification():
    """Manually trigger classification (for testing)"""
    try:
        if not trash_bin.running:
            return jsonify({
                'status': 'error',
                'message': 'System not running'
            })
        
        if trash_bin.classification_in_progress:
            return jsonify({
                'status': 'warning',
                'message': 'Classification already in progress'
            })
        
        if trash_bin.is_in_cooldown():
            remaining = trash_bin.cooldown_period - (time.time() - trash_bin.last_classification_time)
            return jsonify({
                'status': 'warning',
                'message': f'In cooldown period. {remaining:.1f}s remaining'
            })
        
        if trash_bin.latest_frame is not None:
            trash_bin._start_classification_thread(trash_bin.latest_frame.copy())
            return jsonify({
                'status': 'success',
                'message': 'Classification triggered'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No frame available for classification'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error triggering classification: {str(e)}'
        })

if __name__ == "__main__":
    print("🚀 Starting Smart Trash Bin Flask API...")
    print("=" * 60)
    print("🌐 API Endpoints:")
    print("   GET  /              - Web interface")
    print("   GET  /video_feed    - Live video stream")
    print("   POST /start         - Start camera system")
    print("   POST /stop          - Stop camera system")
    print("   GET  /status        - Get system status")
    print("   POST /classify      - Manual classification trigger")
    print("=" * 60)
    print("📱 Frontend Integration:")
    print("   Video stream URL: http://localhost:5000/video_feed")
    print("   Status API URL: http://localhost:5000/status")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        trash_bin.stop_camera_streaming()
        print("👋 Goodbye!")
