
import cv2
import mediapipe as mp
import os
import time
import numpy as np

class WebGestureSystem:
    def __init__(self):
        # Prefer classic Solutions API if available
        self.use_tasks_api = False
        try:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
        except Exception:
            # Fall back to Tasks API
            self.use_tasks_api = True
            try:
                from mediapipe.tasks.python import vision as mp_vision
                from mediapipe.tasks.python.core import base_options as mp_base_options
                from mediapipe.tasks.python.vision.core import image as mp_image_lib
                self._mp_vision = mp_vision
                self._mp_image_lib = mp_image_lib
                env_path = os.environ.get('MEDIAPIPE_HAND_MODEL')
                default_path = os.path.join('assets', 'models', 'hand_landmarker.task')
                # Prefer a valid env var path, otherwise fall back to bundled model
                model_path = env_path if (env_path and os.path.exists(env_path)) else default_path
                if os.path.exists(model_path):
                    options = mp_vision.HandLandmarkerOptions(
                        base_options=mp_base_options.BaseOptions(model_asset_path=model_path),
                        running_mode=mp_vision.RunningMode.IMAGE,
                        num_hands=1,
                        min_hand_detection_confidence=0.7,
                        min_tracking_confidence=0.5,
                    )
                    self.hand_landmarker = mp_vision.HandLandmarker.create_from_options(options)
                else:
                    self.hand_landmarker = None
                    print(f"MediaPipe Tasks API detected but no model found at '{model_path}'.")
                    print("Set MEDIAPIPE_HAND_MODEL or place the model at assets/models/hand_landmarker.task")
            except Exception as e:
                self.hand_landmarker = None
                print('Failed to initialize MediaPipe Tasks hand landmarker:', e)

        self.assets_dir = "assets"
        self.categories = {
            1: {"name": "Documents", "folder": "documents", "extensions": ['.pdf', '.txt', '.docx', '.doc']},
            2: {"name": "Images", "folder": "images", "extensions": ['.jpg', '.jpeg', '.png', '.gif', '.bmp']},
            3: {"name": "Videos", "folder": "videos", "extensions": ['.mp4', '.avi', '.mkv', '.mov', '.wmv']},
            4: {"name": "Audio", "folder": "audio", "extensions": ['.mp3', '.wav', '.flac', '.aac', '.ogg']},
            5: {"name": "Code", "folder": "code", "extensions": ['.py', '.js', '.html', '.css', '.cpp', '.java']}
        }

        self.colors = {
            'primary': (255, 87, 34),       # Orange
            'secondary': (76, 175, 80),     # Green
            'background': (30, 30, 30),     # Dark gray
            'text': (245, 245, 245),        # Light gray
            'selected': (255, 193, 7),      # Amber
            'accent': (156, 39, 176)        # Purple
        }

        # Initial state
        self.current_mode = "SELECT_TYPE"
        self.selected_category = None
        self.file_list = []
        self.selected_file_index = None

        self.last_detected_fingers = -1
        self.stability_frames = 0
        self.required_stability = 20  # Number of frames with stable gesture needed
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0  # seconds

        # New state for web interaction
        self.last_action_message = ""
        self.last_action_time = 0

    def count_fingers(self, landmarks):
        tips = [4, 8, 12, 16, 20]
        pips = [3, 6, 10, 14, 18]

        count = 0
        # Thumb: Check if it's open; depends on hand orientation
        if landmarks[tips[0]].x > landmarks[pips[0]].x:
            count += 1
        # Other fingers: tip y < pip y means fingers open
        for i in range(1, 5):
            if landmarks[tips[i]].y < landmarks[pips[i]].y:
                count += 1
        return count

    def detect_thumbs_up(self, landmarks):
        # Thumb tip y < IP y means thumb is pointing up
        # Other fingers closed: tip y > pip y
        thumb_up = landmarks[4].y < landmarks[3].y
        others_down = all(landmarks[tip].y > landmarks[pip].y for tip, pip in zip([8, 12, 16, 20], [6, 10, 14, 18]))
        return thumb_up and others_down

    def detect_fist(self, landmarks):
        # All fingers closed
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        return all(landmarks[tip].y > landmarks[pip].y for tip, pip in zip(tips, pips)) and landmarks[4].x < landmarks[3].x

    def get_files_for_category(self, category_num):
        category = self.categories[category_num]
        folder = os.path.join(self.assets_dir, category['folder'])
        if not os.path.exists(folder):
            return []
        files = [f for f in sorted(os.listdir(folder)) if os.path.splitext(f)[1].lower() in category['extensions']]
        return files

    def draw_text(self, frame, text, position, font_scale=1.2, thickness=2, color=(245, 245, 245)):
        cv2.putText(frame, text, position, cv2.FONT_HERSHEY_DUPLEX, font_scale, color, thickness, cv2.LINE_AA)

    def draw_overlay(self, frame):
        overlay = frame.copy()
        h, w = frame.shape[:2]

        # Semi-transparent dark background for text
        alpha = 0.6
        cv2.rectangle(overlay, (20, 20), (w-20, h-20), self.colors['background'], -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        if self.current_mode == "SELECT_TYPE":
            title = "Select File Category (Show 1-5 Fingers)"
            self.draw_text(frame, title, (60, 70), 1.8, 3, self.colors['primary'])
            for idx, cat in self.categories.items():
                y = 140 + (idx - 1) * 60
                is_selected = (self.last_detected_fingers == idx and self.stability_frames >= self.required_stability)
                color_bg = self.colors['selected'] if is_selected else self.colors['background']
                color_text = self.colors['text'] if not is_selected else self.colors['background']
                # Background box
                cv2.rectangle(frame, (50, y - 35), (w - 50, y + 15), color_bg, cv2.FILLED)
                cv2.putText(frame,
                            f"{idx}. {cat['name']}",
                            (70, y),
                            cv2.FONT_HERSHEY_DUPLEX,
                            1.3,
                            color_text,
                            2,
                            cv2.LINE_AA)
            footer = "Show fingers for category"
            self.draw_text(frame, footer, (60, h - 40), 1.0, 1, self.colors['accent'])

        elif self.current_mode == "SELECT_FILE":
            title = f"{self.categories[self.selected_category]['name']} Files (Show finger for file number)"
            self.draw_text(frame, title, (60, 70), 1.6, 3, self.colors['secondary'])
            max_files = min(len(self.file_list), 9)
            for i in range(max_files):
                y = 130 + i * 50
                filename = self.file_list[i]
                is_selected = (self.last_detected_fingers == i + 1 and self.stability_frames >= self.required_stability)
                color_bg = self.colors['selected'] if is_selected else self.colors['background']
                color_text = self.colors['text'] if not is_selected else self.colors['background']
                # Background box
                cv2.rectangle(frame, (40, y - 30), (w - 50, y + 10), color_bg, cv2.FILLED)
                display_name = filename if len(filename) < 40 else filename[:37] + "..."
                cv2.putText(frame,
                            f"{i + 1}. {display_name}",
                            (60, y),
                            cv2.FONT_HERSHEY_DUPLEX,
                            1.0,
                            color_text,
                            2,
                            cv2.LINE_AA)
            footer = "Thumbs Up to Open | Fist to Cancel"
            self.draw_text(frame, footer, (60, h - 40), 1.0, 1, self.colors['accent'])

        elif self.current_mode == "CONFIRM":
            message = f"Open '{self.file_list[self.selected_file_index]}'? Show Thumbs Up to Confirm"
            self.draw_text(frame, message, (60, h // 2), 1.5, 3, self.colors['accent'])

        # Draw debug info — finger count and stability (optional)
        debug_text = f"Fingers: {self.last_detected_fingers} | Stability: {self.stability_frames}/{self.required_stability}"
        self.draw_text(frame, debug_text, (20, 40), 0.7, 1, (0, 255, 0))

        # Draw last action message
        if time.time() - self.last_action_time < 3.0:
            self.draw_text(frame, self.last_action_message, (20, h - 80), 1.0, 2, (0, 255, 255))

        return frame

    def process_gesture(self, finger_count, thumbs_up, fist):
        current_time = time.time()
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return None # cooldown to avoid rapid triggers

        action_result = None

        if self.current_mode == "SELECT_TYPE":
            if finger_count in self.categories and self.stability_frames >= self.required_stability:
                self.selected_category = finger_count
                self.file_list = self.get_files_for_category(finger_count)
                if len(self.file_list) == 0:
                    self.last_action_message = f"No files found for category: {self.categories[finger_count]['name']}"
                    self.last_action_time = current_time
                    self.last_gesture_time = current_time
                    return None
                self.current_mode = "SELECT_FILE"
                self.last_gesture_time = current_time

        elif self.current_mode == "SELECT_FILE":
            if fist and self.stability_frames >= self.required_stability:
                self.current_mode = "SELECT_TYPE"
                self.selected_category = None
                self.file_list = []
                self.selected_file_index = None
                self.last_gesture_time = current_time
            elif 1 <= finger_count <= len(self.file_list) and self.stability_frames >= self.required_stability:
                self.selected_file_index = finger_count - 1
                self.current_mode = "CONFIRM"
                self.last_gesture_time = current_time

        elif self.current_mode == "CONFIRM":
            if thumbs_up:
                filename = self.file_list[self.selected_file_index]
                category = self.categories[self.selected_category]

                # Signal to open file
                action_result = {
                    "type": "open_file",
                    "filename": filename,
                    "folder": category['folder']
                }

                self.last_action_message = f"Opened {filename}"
                self.last_action_time = current_time

                # Reset state after opening
                self.current_mode = "SELECT_TYPE"
                self.selected_category = None
                self.file_list = []
                self.selected_file_index = None
                self.last_gesture_time = current_time
            elif fist: # Cancel
                 self.current_mode = "SELECT_FILE"
                 self.last_gesture_time = current_time

        return action_result

    def process_frame(self, frame):
        """
        Process a single frame and return the annotated frame and any action event.
        """
        frame = cv2.flip(frame, 1)  # mirror for natural interaction
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        finger_count = 0
        thumbs_up = False
        fist = False

        if not self.use_tasks_api:
            results = self.hands.process(rgb_frame)
            if results.multi_hand_landmarks:
                # Considering only first hand detected
                hand_landmarks = results.multi_hand_landmarks[0]
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                finger_count = self.count_fingers(hand_landmarks.landmark)
                thumbs_up = self.detect_thumbs_up(hand_landmarks.landmark)
                fist = self.detect_fist(hand_landmarks.landmark)
        else:
            if self.hand_landmarker is not None:
                mp_img = self._mp_image_lib.Image(self._mp_image_lib.ImageFormat.SRGB, rgb_frame)
                try:
                    res = self.hand_landmarker.detect(mp_img)
                except Exception:
                    res = None
                if res and res.hand_landmarks:
                    landmarks = res.hand_landmarks[0]
                    h, w = frame.shape[:2]
                    for lm in landmarks:
                        x, y = int(lm.x * w), int(lm.y * h)
                        cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)
                    finger_count = self.count_fingers(landmarks)
                    thumbs_up = self.detect_thumbs_up(landmarks)
                    fist = self.detect_fist(landmarks)

        # Stability check
        if finger_count == self.last_detected_fingers:
            self.stability_frames += 1
        else:
            self.stability_frames = 0
        self.last_detected_fingers = finger_count

        # Override finger count if thumbs up or fist is detected to avoid conflict
        if thumbs_up:
            # finger_count = -1 # Special
            pass

        # Process gesture if stable
        action = None
        if self.stability_frames >= self.required_stability:
            action = self.process_gesture(finger_count, thumbs_up, fist)

        frame = self.draw_overlay(frame)

        return frame, action
