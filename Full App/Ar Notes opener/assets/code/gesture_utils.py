# Gesture Utility Functions

def count_extended_fingers(landmarks):
    """Count extended fingers from hand landmarks"""
    finger_tips = [4, 8, 12, 16, 20]
    finger_pips = [3, 6, 10, 14, 18]
    
    count = 0
    
    # Thumb (special case)
    if landmarks[4].x > landmarks[3].x:
        count += 1
    
    # Other fingers
    for i in range(1, 5):
        if landmarks[finger_tips[i]].y < landmarks[finger_pips[i]].y:
            count += 1
    
    return count
