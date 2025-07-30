# Interactive Sequential Hand Gesture File System
# User selects file type -> Views numbered files -> Shows number -> Confirms with thumbs up

import cv2
import mediapipe as mp
import os
import time
from collections import Counter
import subprocess
import platform

class InteractiveGestureFileSystem:
    def __init__(self, assets_dir='assets'):
        self.assets_dir = assets_dir
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # System states
        self.current_state = "FILE_TYPE_SELECTION"  # FILE_TYPE_SELECTION, FILE_BROWSING, NUMBER_INPUT, CONFIRMATION
        self.selected_file_type = None
        self.current_files = []
        self.selected_file_index = None
        self.gesture_history = []
        self.last_gesture_time = 0
        self.confirmation_start_time = None
        
        # File type categories
        self.file_types = {
            1: {"name": "Documents", "extensions": ['.pdf', '.docx', '.txt', '.doc']},
            2: {"name": "Images", "extensions": ['.jpg', '.jpeg', '.png', '.gif', '.bmp']},
            3: {"name": "Videos", "extensions": ['.mp4', '.avi', '.mkv', '.mov', '.wmv']},
            4: {"name": "Audio", "extensions": ['.mp3', '.wav', '.flac', '.m4a']},
            5: {"name": "Code", "extensions": ['.py', '.js', '.html', '.css', '.java']},
            6: {"name": "All Files", "extensions": []}
        }
        
        # Initialize display
        self.display_text = []
        self.update_display()
    
    def count_fingers(self, landmarks):
        """Count raised fingers from hand landmarks"""
        if not landmarks:
            return 0
            
        # Finger tip and pip landmarks
        finger_tips = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky
        finger_pips = [3, 6, 10, 14, 18]
        
        fingers_up = 0
        
        # Thumb (different logic due to thumb orientation)
        if landmarks[finger_tips[0]].x > landmarks[finger_pips[0]].x:
            fingers_up += 1
            
        # Other fingers
        for i in range(1, 5):
            if landmarks[finger_tips[i]].y < landmarks[finger_pips[i]].y:
                fingers_up += 1
                
        return fingers_up
    
    def detect_thumbs_up(self, landmarks):
        """Detect thumbs up gesture"""
        if not landmarks:
            return False
            
        # Thumb up: thumb tip higher than thumb mcp, other fingers down
        thumb_tip = landmarks[4]
        thumb_mcp = landmarks[2]
        index_tip = landmarks[8]
        index_mcp = landmarks[5]
        
        # Thumb is up and index is down
        thumb_up = thumb_tip.y < thumb_mcp.y
        index_down = index_tip.y > index_mcp.y
        
        return thumb_up and index_down
    
    def get_files_by_type(self, file_type_num):
        """Get files from assets directory by type"""
        if not os.path.exists(self.assets_dir):
            return []
            
        files = []
        extensions = self.file_types[file_type_num]["extensions"]
        
        for filename in os.listdir(self.assets_dir):
            file_path = os.path.join(self.assets_dir, filename)
            if os.path.isfile(file_path):
                if not extensions or any(filename.lower().endswith(ext) for ext in extensions):
                    files.append(filename)
        
        return sorted(files)
    
    def update_display(self):
        """Update display text based on current state"""
        self.display_text = []
        
        if self.current_state == "FILE_TYPE_SELECTION":
            self.display_text = [
                "=== SELECT FILE TYPE ===",
                "Show fingers to select:",
                ""
            ]
            for num, file_type in self.file_types.items():
                self.display_text.append(f"{num} finger(s): {file_type['name']}")
                
        elif self.current_state == "FILE_BROWSING":
            type_name = self.file_types[self.selected_file_type]["name"]
            self.display_text = [
                f"=== {type_name.upper()} FILES ===",
                "Show number to select file:",
                ""
            ]
            for i, filename in enumerate(self.current_files[:9], 1):  # Limit to 9 files
                self.display_text.append(f"{i}: {filename}")
            
            if len(self.current_files) > 9:
                self.display_text.append("(Showing first 9 files)")
                
        elif self.current_state == "NUMBER_INPUT":
            self.display_text = [
                "WAITING FOR NUMBER...",
                f"Show 1-{min(len(self.current_files), 9)} fingers",
                "to select file"
            ]
            
        elif self.current_state == "CONFIRMATION":
            if self.selected_file_index is not None:
                filename = self.current_files[self.selected_file_index]
                self.display_text = [
                    "=== CONFIRM SELECTION ===",
                    f"Selected: {filename}",
                    "",
                    "👍 Thumbs UP to OPEN",
                    "✊ Fist to CANCEL"
                ]
    
    def open_file(self, filename):
        """Open file with system default application"""
        file_path = os.path.join(self.assets_dir, filename)
        
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
            print(f"✅ Opened: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error opening {filename}: {e}")
            return False
    
    def process_gesture(self, finger_count, thumbs_up, fist):
        """Process detected gesture based on current state"""
        current_time = time.time()
        
        # Debounce gestures (minimum 1 second between gestures)
        if current_time - self.last_gesture_time < 1.0:
            return
        
        if self.current_state == "FILE_TYPE_SELECTION":
            if 1 <= finger_count <= 6:
                self.selected_file_type = finger_count
                self.current_files = self.get_files_by_type(finger_count)
                
                if not self.current_files:
                    print(f"❌ No {self.file_types[finger_count]['name'].lower()} files found!")
                    return
                
                self.current_state = "FILE_BROWSING"
                self.update_display()
                self.last_gesture_time = current_time
                print(f"✅ Selected: {self.file_types[finger_count]['name']}")
                
        elif self.current_state == "FILE_BROWSING":
            if 1 <= finger_count <= min(len(self.current_files), 9):
                self.selected_file_index = finger_count - 1
                self.current_state = "CONFIRMATION"
                self.update_display()
                self.last_gesture_time = current_time
                filename = self.current_files[self.selected_file_index]
                print(f"📄 Selected: {filename}")
                
        elif self.current_state == "CONFIRMATION":
            if thumbs_up:
                filename = self.current_files[self.selected_file_index]
                if self.open_file(filename):
                    # Reset to file type selection after successful open
                    time.sleep(2)  # Give time to see the file open
                    self.current_state = "FILE_TYPE_SELECTION"
                    self.selected_file_type = None
                    self.current_files = []
                    self.selected_file_index = None
                    self.update_display()
                self.last_gesture_time = current_time
                
            elif fist:
                # Cancel and go back to file browsing
                self.current_state = "FILE_BROWSING"
                self.selected_file_index = None
                self.update_display()
                self.last_gesture_time = current_time
                print("❌ Cancelled selection")
    
    def detect_fist(self, landmarks):
        """Detect closed fist gesture"""
        if not landmarks:
            return False
            
        # Check if all fingertips are below their respective MCPs
        finger_tips = [8, 12, 16, 20]  # index, middle, ring, pinky
        finger_mcps = [5, 9, 13, 17]
        
        fingers_down = 0
        for tip, mcp in zip(finger_tips, finger_mcps):
            if landmarks[tip].y > landmarks[mcp].y:
                fingers_down += 1
                
        return fingers_down >= 3  # At least 3 fingers down = fist
    
    def run(self):
        """Main loop for interactive gesture system"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        print("🚀 Interactive Gesture File System Started!")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hand landmarks
            results = self.hands.process(rgb_frame)
            
            finger_count = 0
            thumbs_up = False
            fist = False
            
            if results.multi_hand_landmarks:
                for landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    self.mp_draw.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Detect gestures
                    finger_count = self.count_fingers(landmarks.landmark)
                    thumbs_up = self.detect_thumbs_up(landmarks.landmark)
                    fist = self.detect_fist(landmarks.landmark)
                    
                    # Process the gesture
                    self.process_gesture(finger_count, thumbs_up, fist)
            
            # Display current state and instructions
            y_offset = 30
            for line in self.display_text:
                cv2.putText(frame, line, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (0, 255, 0), 2)
                y_offset += 30
            
            # Display current gesture
            if finger_count > 0:
                cv2.putText(frame, f"Fingers: {finger_count}", (10, frame.shape[0] - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            
            if thumbs_up:
                cv2.putText(frame, "👍 THUMBS UP", (10, frame.shape[0] - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            if fist:
                cv2.putText(frame, "✊ FIST", (10, frame.shape[0] - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            cv2.imshow('Interactive Gesture File System', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    system = InteractiveGestureFileSystem()
    system.run()