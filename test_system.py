# Test and Demo Script for Interactive Gesture System
# Run this to verify your setup is working correctly

import cv2
import mediapipe as mp
import os
import time

def test_camera():
    """Test if camera is working"""
    print("🎥 Testing camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Camera test failed - cannot open camera")
        return False
    
    ret, frame = cap.read()
    if not ret:
        print("❌ Camera test failed - cannot read frame")
        cap.release()
        return False
    
    cap.release()
    print("✅ Camera test passed")
    return True

def test_mediapipe():
    """Test MediaPipe hand detection"""
    print("🖐️ Testing MediaPipe hand detection...")
    
    try:
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("✅ MediaPipe initialization successful")
        return True
    except Exception as e:
        print(f"❌ MediaPipe test failed: {e}")
        return False

def test_assets_folder():
    """Test if assets folder and files exist"""
    print("📁 Testing assets folder...")
    
    if not os.path.exists('assets'):
        print("⚠️  Assets folder not found - run setup_demo_files.py first")
        return False
    
    files = os.listdir('assets')
    if not files:
        print("⚠️  Assets folder is empty - run setup_demo_files.py first")
        return False
    
    print(f"✅ Found {len(files)} files in assets folder")
    return True

def test_gesture_detection():
    """Interactive test of gesture detection"""
    print("\n🖐️ Starting interactive gesture detection test...")
    print("This will open your camera and detect hand gestures.")
    print("Try holding up different numbers of fingers (1-5).")
    print("Press 'q' to quit this test.")
    
    input("Press Enter to start the test...")
    
    # Initialize MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils
    
    cap = cv2.VideoCapture(0)
    
    def count_fingers(landmarks):
        if not landmarks:
            return 0
        
        finger_tips = [4, 8, 12, 16, 20]
        finger_pips = [3, 6, 10, 14, 18]
        fingers_up = 0
        
        # Thumb
        if landmarks[finger_tips[0]].x > landmarks[finger_pips[0]].x:
            fingers_up += 1
        
        # Other fingers
        for i in range(1, 5):
            if landmarks[finger_tips[i]].y < landmarks[finger_pips[i]].y:
                fingers_up += 1
        
        return fingers_up
    
    print("🚀 Camera opened - show your hand!")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        finger_count = 0
        
        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
                finger_count = count_fingers(landmarks.landmark)
        
        # Display information
        cv2.putText(frame, "Interactive Gesture Test", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Fingers detected: {finger_count}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow('Gesture Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Gesture detection test completed")

def run_full_system_test():
    """Run comprehensive system test"""
    print("🧪 AR Notes Interactive System - Full Test Suite")
    print("=" * 50)
    
    # Test results
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_camera():
        tests_passed += 1
    
    if test_mediapipe():
        tests_passed += 1
    
    if test_assets_folder():
        tests_passed += 1
    
    print("\n📊 Test Results:")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your system is ready to use.")
        
        # Ask if user wants to test gesture detection
        response = input("\nWould you like to test gesture detection? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            test_gesture_detection()
        
        print("\n🚀 Next steps:")
        print("1. Run: python setup_demo_files.py (if you haven't already)")
        print("2. Run: python interactive_gesture_system.py")
        print("3. Try the voice assistant: python voice_assistant_interactive.py")
        
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        
        if tests_passed == 0:
            print("\n💡 Troubleshooting tips:")
            print("- Install dependencies: pip install -r requirements_interactive.txt")
            print("- Check camera permissions")
            print("- Create demo files: python setup_demo_files.py")

def main():
    """Main test function"""
    print("Welcome to the AR Notes Interactive System Test!")
    print("\nThis will test your setup and verify everything is working.")
    
    # Check if this is first run
    if not os.path.exists('assets'):
        print("\n⚠️  Assets folder not found!")
        response = input("Would you like to create demo files now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            try:
                import setup_demo_files
                setup_demo_files.create_sample_files()
            except ImportError:
                print("❌ setup_demo_files.py not found. Please ensure all files are in the same directory.")
                return
    
    run_full_system_test()

if __name__ == "__main__":
    main()