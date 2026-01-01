
import cv2
import numpy as np
from web_gesture_system import WebGestureSystem
import os

def test_web_gesture_system_initialization():
    system = WebGestureSystem()
    assert system.current_mode == "SELECT_TYPE"
    assert system.selected_category is None
    print("Initialization test passed.")

def test_process_frame_no_hands():
    system = WebGestureSystem()
    # Create a black image
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    processed_frame, action = system.process_frame(frame)

    assert processed_frame is not None
    assert action is None
    # Check if frame shape is preserved (or at least valid)
    assert processed_frame.shape == (480, 640, 3)
    print("Process frame (no hands) test passed.")

def test_assets_existence():
    # Ensure assets directory and subfolders exist
    assert os.path.exists("assets")
    assert os.path.exists("assets/documents")
    assert os.path.exists("assets/images")
    assert os.path.exists("assets/videos")
    assert os.path.exists("assets/audio")
    assert os.path.exists("assets/code")
    print("Assets existence test passed.")

if __name__ == "__main__":
    try:
        test_web_gesture_system_initialization()
        test_process_frame_no_hands()
        test_assets_existence()
        print("All unit tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
