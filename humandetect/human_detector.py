#!/usr/bin/env python3
"""
Real-time Human Detection using YOLOv8 and OpenCV
Detects humans, calculates center coordinates, and draws circles at center positions.
"""

import cv2
import numpy as np
from ultralytics import YOLO
import sys

class HumanDetector:
    def __init__(self):
        """Initialize the human detector with YOLOv8 model"""
        try:
            # Initialize YOLOv8 model (downloads automatically if not present)
            print("🔄 Loading YOLOv8 model...")
            self.model = YOLO('yolov8n.pt')  # Using nano model for speed
            print("✅ YOLOv8 model loaded successfully")
            
            # Person class ID in COCO dataset
            self.person_class_id = 0
            
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
    
    def draw_detection(self, frame, detection):
        """Draw bounding box and center circle on frame"""
        bbox = detection['bbox']
        confidence = detection['confidence']
        x1, y1, x2, y2 = bbox
        
        # Calculate center
        center_x, center_y = self.calculate_center(bbox)
        
        # Print coordinates
        print(f"👤 Person detected at center: ({center_x}, {center_y}) - Confidence: {confidence:.2f}")
        
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
    
    def run(self):
        """Main detection loop"""
        if not self.initialize_camera():
            return
        
        print("\n🚀 Starting human detection...")
        print("📹 Press 'q' to quit, 'r' to reset")
        print("-" * 50)
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Error: Could not read from camera")
                    break
                
                # Detect humans in current frame
                detection = self.detect_humans(frame)
                
                if detection:
                    # Draw detection and get center coordinates
                    center_x, center_y = self.draw_detection(frame, detection)
                else:
                    # Add "No person detected" text
                    cv2.putText(frame, "No person detected", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Add instructions
                cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Display frame
                cv2.imshow('Human Detection', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    print("🔄 Reset detection...")
        
        except KeyboardInterrupt:
            print("\n⏹️  Detection stopped by user")
        
        finally:
            # Cleanup
            self.cap.release()
            cv2.destroyAllWindows()
            print("✅ Resources cleaned up successfully")

def main():
    """Main function"""
    print("🤖 Real-time Human Detection System")
    print("=" * 40)
    
    # Create and run detector
    detector = HumanDetector()
    detector.run()

if __name__ == "__main__":
    main()