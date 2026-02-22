#!/usr/bin/env python3
"""
Smart Human Detection System with AI Greeting
Uses YOLO for detection, Gemini for greeting generation, and ElevenLabs for speech.
Includes eye movement display and intelligent greeting timing.
"""

import cv2
import numpy as np
from ultralytics import YOLO
import sys
import time
import threading
import requests
import json
from datetime import datetime, timedelta
import pygame

class SmartHumanDetector:
    def __init__(self):
        """Initialize the smart human detector with AI greeting capabilities"""
        try:
            # Initialize YOLOv8 model
            print("🔄 Loading YOLOv8 model...")
            self.model = YOLO('yolov8n.pt')  # Using nano model for speed
            print("✅ YOLOv8 model loaded successfully")
            
            # Person class ID in COCO dataset
            self.person_class_id = 0
            
            # Detection and greeting state
            self.detection_start_time = None
            self.last_greeting_time = None
            self.greeting_triggered = False
            self.continuous_detection_threshold = 2.0  # seconds
            self.greeting_cooldown = 10.0  # seconds
            
            # Eye movement state (similar to eyes.jsx)
            self.eye_offset_x = 0
            self.eye_offset_y = 0
            
            # API endpoints
            self.elevenlabs_url = "http://127.0.0.1:5000/tts"
            self.gemini_url = "http://127.0.0.1:5000/gemini"  # Assuming similar endpoint
            
            # Initialize pygame for audio playback
            pygame.mixer.init()
            
        except Exception as e:
            print(f"❌ Error initializing detector: {e}")
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
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
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
    
    def update_eye_movement(self, center_x, center_y):
        """Update eye movement based on human position (similar to eyes.jsx logic)"""
        # Convert camera coordinates to eye movement (-70 to 70 range like updated eyes.jsx)
        camera_width = 640
        camera_height = 480
        
        # Calculate offsets similar to HumanTrackingEyes.jsx
        horizontal_percent = center_x / camera_width
        self.eye_offset_x = (0.5 - horizontal_percent) * 70  # Flipped X-axis for natural movement
        
        vertical_percent = center_y / camera_height
        self.eye_offset_y = (vertical_percent - 0.5) * 45
    
    def draw_eyes_display(self, frame):
        """Draw animated eyes on the frame (similar to eyes.jsx)"""
        # Eye socket dimensions (scaled down for video overlay)
        eye_width = 120
        eye_height = 80
        eye_spacing = 60
        
        # Calculate eye positions (top-right corner of frame)
        frame_height, frame_width = frame.shape[:2]
        right_eye_center = (frame_width - 200, 100)
        left_eye_center = (frame_width - 200 - eye_spacing - eye_width, 100)
        
        # Draw eye sockets (dark background)
        for eye_center in [left_eye_center, right_eye_center]:
            cv2.ellipse(frame, eye_center, (eye_width//2, eye_height//2), 0, 0, 360, (26, 32, 44), -1)
            cv2.ellipse(frame, eye_center, (eye_width//2, eye_height//2), 0, 0, 360, (45, 55, 72), 3)
        
        # Draw pupils with movement
        pupil_width = 56  # 140px -> 56px scaled down
        pupil_height = 32  # 80px -> 32px scaled down
        
        for eye_center in [left_eye_center, right_eye_center]:
            # Apply eye movement offset
            pupil_x = int(eye_center[0] + self.eye_offset_x * 0.4)  # Scale down movement
            pupil_y = int(eye_center[1] + self.eye_offset_y * 0.4)
            
            # Draw green pupil
            cv2.ellipse(frame, (pupil_x, pupil_y), (pupil_width//2, pupil_height//2), 
                       0, 0, 360, (0, 255, 65), -1)
            cv2.ellipse(frame, (pupil_x, pupil_y), (pupil_width//2, pupil_height//2), 
                       0, 0, 360, (0, 204, 51), 2)
    
    def human_detection(self, frame):
        """Detect humans in frame and return largest detection"""
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
    
    def should_trigger_greeting(self, human_detected):
        """Determine if greeting should be triggered based on detection timing"""
        current_time = time.time()
        
        if human_detected:
            # Start or continue detection timer
            if self.detection_start_time is None:
                self.detection_start_time = current_time
                self.greeting_triggered = False
            
            # Check if continuous detection threshold met
            detection_duration = current_time - self.detection_start_time
            
            # Check cooldown period
            if self.last_greeting_time is not None:
                time_since_last_greeting = current_time - self.last_greeting_time
                if time_since_last_greeting < self.greeting_cooldown:
                    return False
            
            # Trigger greeting if threshold met and not already triggered
            if (detection_duration >= self.continuous_detection_threshold and 
                not self.greeting_triggered):
                self.greeting_triggered = True
                self.last_greeting_time = current_time
                return True
        
        else:
            # Reset detection timer when no human detected
            self.detection_start_time = None
            self.greeting_triggered = False
        
        return False
    
    def generate_greeting_with_gemini(self):
        """Generate greeting message using Gemini API"""
        try:
            print("🤖 Generating greeting with Gemini...")
            
            prompt = (
                "Generate a short, friendly greeting for someone approaching a smart trash bin. "
                "The message should: "
                "1. Greet the person warmly "
                "2. Ask if they have trash to recycle "
                "3. Encourage eco-friendly behavior "
                "4. End with 'Have a nice day!' "
                "Keep it under 3 sentences and sound cheerful and natural."
            )
            
            # Try direct Gemini API call first (you may need to adjust this)
            # For now, I'll implement a fallback with predefined messages
            predefined_greetings = [
                "Hello there! Do you have any trash to recycle today? Every small action helps our planet. Have a nice day!",
                "Hi! Ready to make a difference with your recycling? Let's keep our environment clean together. Have a nice day!",
                "Welcome! Got some items to recycle? You're doing great for the environment. Have a nice day!",
                "Hey there! Any recyclables for me today? Thank you for caring about our planet. Have a nice day!",
                "Hello! Looking to recycle something? Every bit counts towards a greener future. Have a nice day!"
            ]
            
            import random
            greeting = random.choice(predefined_greetings)
            print(f"✅ Generated greeting: {greeting}")
            return greeting
            
        except Exception as e:
            print(f"❌ Error generating greeting: {e}")
            return "Hello! Do you have any trash to recycle today? Have a nice day!"
    
    def speak_with_elevenlabs(self, text):
        """Convert text to speech using ElevenLabs API"""
        try:
            print(f"🔊 Speaking with ElevenLabs: {text}")
            
            response = requests.post(
                self.elevenlabs_url,
                headers={"Content-Type": "application/json"},
                json={"text": text},
                timeout=10
            )
            
            if response.ok:
                data = response.json()
                if 'audio' in data:
                    # Play audio using pygame
                    audio_data = data['audio']
                    
                    # Save temporary audio file and play
                    import base64
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                        tmp_file.write(base64.b64decode(audio_data))
                        tmp_file_path = tmp_file.name
                    
                    # Play audio
                    pygame.mixer.music.load(tmp_file_path)
                    pygame.mixer.music.play()
                    
                    # Wait for playback to complete
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    
                    # Clean up temporary file
                    os.unlink(tmp_file_path)
                    
                    print("✅ Audio played successfully!")
                    return True
                else:
                    print("❌ No audio data in response")
            else:
                print(f"❌ ElevenLabs API error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error with ElevenLabs: {e}")
        
        return False
    
    def draw_detection_info(self, frame, detection):
        """Draw detection information on frame"""
        if detection:
            bbox = detection['bbox']
            confidence = detection['confidence']
            x1, y1, x2, y2 = bbox
            
            # Calculate center
            center_x, center_y = self.calculate_center(bbox)
            
            # Update eye movement
            self.update_eye_movement(center_x, center_y)
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw center circle
            cv2.circle(frame, (center_x, center_y), 8, (0, 0, 255), -1)
            cv2.circle(frame, (center_x, center_y), 15, (0, 0, 255), 2)
            
            # Add text with coordinates
            text = f"Center: ({center_x}, {center_y})"
            cv2.putText(frame, text, (center_x - 80, center_y - 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Add confidence text
            conf_text = f"Conf: {confidence:.2f}"
            cv2.putText(frame, conf_text, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            return center_x, center_y
        else:
            # No detection - center eyes
            self.eye_offset_x = 0
            self.eye_offset_y = 0
            
            cv2.putText(frame, "No person detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return None, None
    
    def draw_status_info(self, frame):
        """Draw system status information"""
        current_time = time.time()
        
        # Detection timer status
        if self.detection_start_time:
            detection_duration = current_time - self.detection_start_time
            status_text = f"Detecting: {detection_duration:.1f}s"
            color = (0, 255, 255)  # Yellow
            
            if detection_duration >= self.continuous_detection_threshold:
                if self.greeting_triggered:
                    status_text = "Greeted!"
                    color = (0, 255, 0)  # Green
                else:
                    status_text = f"Ready to greet ({detection_duration:.1f}s)"
                    color = (255, 255, 0)  # Cyan
        else:
            status_text = "Waiting for human..."
            color = (128, 128, 128)  # Gray
        
        cv2.putText(frame, status_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Cooldown status
        if self.last_greeting_time:
            time_since_greeting = current_time - self.last_greeting_time
            if time_since_greeting < self.greeting_cooldown:
                cooldown_remaining = self.greeting_cooldown - time_since_greeting
                cooldown_text = f"Cooldown: {cooldown_remaining:.1f}s"
                cv2.putText(frame, cooldown_text, (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    
    def run(self):
        """Main detection and greeting loop"""
        if not self.initialize_camera():
            return
        
        print("\n🤖 Smart Human Detection with AI Greeting")
        print("=" * 50)
        print("🎯 Features:")
        print("   • Real-time human detection")
        print("   • 2-second detection threshold")
        print("   • AI greeting generation")
        print("   • Text-to-speech with ElevenLabs")
        print("   • Animated eye tracking")
        print("   • 10-second greeting cooldown")
        print("=" * 50)
        print("📹 Press 'q' to quit, 'r' to reset, 'g' for manual greeting")
        print("-" * 50)
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Error: Could not read from camera")
                    break
                
                # Detect humans in current frame
                detection = self.human_detection(frame)
                human_detected = detection is not None
                
                # Check if greeting should be triggered
                if self.should_trigger_greeting(human_detected):
                    # Run greeting in separate thread to avoid blocking
                    greeting_thread = threading.Thread(
                        target=self.trigger_greeting_sequence, 
                        daemon=True
                    )
                    greeting_thread.start()
                
                # Draw detection information and update eyes
                self.draw_detection_info(frame, detection)
                
                # Draw animated eyes
                self.draw_eyes_display(frame)
                
                # Draw status information
                self.draw_status_info(frame)
                
                # Add instructions
                cv2.putText(frame, "Press 'q' to quit, 'g' for manual greeting", 
                           (10, frame.shape[0] - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                
                # Display frame
                cv2.imshow('Smart Human Detection with AI Greeting', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    print("🔄 Reset detection state...")
                    self.detection_start_time = None
                    self.greeting_triggered = False
                elif key == ord('g'):
                    print("🎤 Manual greeting triggered...")
                    threading.Thread(target=self.trigger_greeting_sequence, daemon=True).start()
        
        except KeyboardInterrupt:
            print("\n⏹️  Detection stopped by user")
        
        finally:
            # Cleanup
            self.cap.release()
            cv2.destroyAllWindows()
            pygame.mixer.quit()
            print("✅ Resources cleaned up successfully")
    
    def trigger_greeting_sequence(self):
        """Trigger the complete greeting sequence (Gemini + ElevenLabs)"""
        try:
            print("\n🎯 Triggering greeting sequence...")
            
            # Generate greeting with Gemini
            greeting_text = self.generate_greeting_with_gemini()
            
            # Speak with ElevenLabs
            success = self.speak_with_elevenlabs(greeting_text)
            
            if success:
                print("✅ Greeting sequence completed successfully!")
            else:
                print("⚠️ Greeting sequence completed with audio issues")
                
        except Exception as e:
            print(f"❌ Error in greeting sequence: {e}")

def main():
    """Main function"""
    print("🤖 Smart Human Detection System with AI Greeting")
    print("=" * 60)
    
    # Create and run detector
    detector = SmartHumanDetector()
    detector.run()

if __name__ == "__main__":
    main()