import cv2
import mediapipe as mp
import os
import platform
import time

def test_camera():
    print("Testing Camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera.")
        return False
    # Test resolution capture
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        print("❌ Cannot capture frame.")
        return False
    print("✅ Camera accessible and frames captured.")
    return True

def test_mediapipe():
    print("Testing MediaPipe Hand module...")
    try:
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        hands.close()
        print("✅ MediaPipe initialized successfully.")
        return True
    except Exception as e:
        print(f"❌ MediaPipe error: {e}")
        return False

def test_assets():
    print("Testing Assets folder structure...")
    assets_dir = 'assets'
    categories = ['documents', 'images', 'videos', 'audio', 'code']
    missing = []
    for c in categories:
        path = os.path.join(assets_dir, c)
        if not os.path.isdir(path):
            print(f"❌ Missing folder: {c}")
            missing.append(c)
    if missing:
        print("❗️ Please run setup_enhanced_assets.py to create missing folders.")
        return False
    print("✅ All asset folders present.")
    return True

def test_file_opening():
    print("Testing file opening functionality...")
    test_file = os.path.join('assets', 'documents', 'meeting_notes.txt')
    if not os.path.isfile(test_file):
        print("❌ Test file missing: meeting_notes.txt")
        return False
    try:
        if platform.system() == "Windows":
            os.startfile(test_file)
        elif platform.system() == "Darwin":
            import subprocess
            subprocess.Popen(["open", test_file])
        else:
            import subprocess
            subprocess.Popen(["xdg-open", test_file])
        print("✅ File opening executed. (Close opened file manually)")
        return True
    except Exception as e:
        print(f"❌ Error opening file: {e}")
        return False

def run_tests():
    print("\n--- Running AR Notes System Tests ---\n")
    c = test_camera()
    m = test_mediapipe()
    a = test_assets()
    f = test_file_opening()
    all_ok = all([c, m, a, f])
    if all_ok:
        print("\n🎉 All systems operational. Ready to run enhanced_gesture_system.py\n")
    else:
        print("\n⚠️ Issues found. Please fix before continuing.\n")
    return all_ok

if __name__ == "__main__":
    run_tests()
