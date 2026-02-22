import os
import cv2
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
import time
import base64

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

class SmartTrashBin:
    def __init__(self):
        self.cap = None
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=50, detectShadows=True
        )
        self.last_classification_time = 0
        self.cooldown_period = 1.2  # 5 seconds
        self.motion_threshold = 5000  # Minimum contour area for motion detection
        
    def initialize_camera(self):
        """Initialize webcam"""
        print(" Initializing camera...")
        
        # Try different camera indices
        for camera_index in range(5):  # Try cameras 0-4
            print(f"Trying camera index {camera_index}...")
            self.cap = cv2.VideoCapture(camera_index)
            
            if self.cap.isOpened():
                # Test if camera can actually read frames
                ret, _ = self.cap.read()
                if ret:
                    print(f"Camera {camera_index} opened successfully!")
                    break
                else:
                    self.cap.release()
            
            if camera_index == 4:  # Last attempt
                print(" Error: Could not open any camera (tried indices 0-4)")
                return False
            
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Warm up the camera
        for _ in range(10):
            ret, _ = self.cap.read()
            if not ret:
                print(" Error: Could not read from camera")
                return False
                
        print(" Camera initialized successfully")
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

Categories:
- can (metal, aluminum beverage containers)
- plastic (PET bottles, containers, wrappers)
- paper (cardboard, newspapers, paper materials)
- glass (glass bottles or jars)

Return exactly one lowercase word.
If uncertain, infer based on visible material texture.
Do not explain."""
            
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
            valid_categories = ['can', 'plastic', 'paper', 'glass']
            
            if classification_text in valid_categories:
                result_classification = classification_text
            else:
                # Try to extract valid category
                for category in valid_categories:
                    if category in classification_text:
                        result_classification = category
                        break
                else:
                    result_classification = 'unknown'
            
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
    
    def run_smart_classification(self):
        """Main loop for smart trash bin classification"""
        if not self.initialize_camera():
            return
            
        print("\n SMART TRASH BIN CLASSIFICATION SYSTEM")
        print("=" * 60)
        print(" Live webcam preview active")
        print(" Motion detection enabled")
        print(" 5-second cooldown between classifications")
        print(" Press 'q' to quit")
        print("=" * 60)
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print(" Error reading frame")
                    break
                
                frame_count += 1
                
                # Detect motion
                motion_detected, contours = self.detect_motion(frame)
                
                # Draw motion detection overlay
                display_frame = frame.copy()
                
                if motion_detected:
                    # Draw motion contours
                    cv2.drawContours(display_frame, contours, -1, (0, 255, 0), 2)
                    cv2.putText(display_frame, "MOTION DETECTED", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Classify if not in cooldown
                    if not self.is_in_cooldown():
                        print(f"\n Motion detected! Capturing frame #{frame_count}")
                        
                        # Classify the object
                        result = self.classify_object(frame)
                        self.last_classification_time = time.time()
                        
                        # Print results
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        if result['classification'] != 'error':
                            print(f" [{timestamp}] Classification: {result['classification'].upper()}")
                            print(f"  Processing time: {result['processing_time']:.0f}ms")
                            
                            # Update display with classification
                            cv2.putText(display_frame, f"CLASSIFIED: {result['classification'].upper()}", 
                                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                        else:
                            print(f" [{timestamp}] Classification failed: {result.get('error', 'Unknown error')}")
                            cv2.putText(display_frame, "CLASSIFICATION FAILED", 
                                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    else:
                        remaining_cooldown = self.cooldown_period - (time.time() - self.last_classification_time)
                        cv2.putText(display_frame, f"COOLDOWN: {remaining_cooldown:.1f}s", 
                                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
                
                # Add status text
                status_text = "READY" if not motion_detected else "MOTION"
                cv2.putText(display_frame, f"Status: {status_text}", (10, display_frame.shape[0] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                cv2.putText(display_frame, "Press 'q' to quit", (10, display_frame.shape[0] - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                
                # Show the frame
                cv2.imshow('Smart Trash Bin - Material Classification', display_frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nExiting smart trash bin system...")
                    break
                    
        except KeyboardInterrupt:
            print("\n  Interrupted by user")
        
        finally:
            # Clean up
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            print(" Camera and windows closed")

if __name__ == "__main__":
    # Create and run smart trash bin
    smart_bin = SmartTrashBin()
    smart_bin.run_smart_classification()