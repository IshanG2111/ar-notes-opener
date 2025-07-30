# Setup Demo Files for Interactive Gesture System

import os

def create_sample_files():
    """Create sample files in different categories for testing"""
    
    assets_dir = 'assets'
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"✅ Created {assets_dir} directory")
    
    # Sample file contents and names
    sample_files = {
        # Documents
        'meeting_notes.txt': """Meeting Notes - July 31, 2025
=====================================

Attendees: John, Sarah, Mike
Topic: AR Notes App Development

Key Points:
- Implemented hand gesture recognition
- Added interactive file selection
- Next: Voice integration testing

Action Items:
- Test gesture accuracy (John)
- Create demo files (Sarah)
- Document features (Mike)
""",
        
        'project_proposal.txt': """AR Notes Project Proposal
=========================

Objective: Create an intuitive AR notes system using hand gestures

Features:
1. Hand gesture recognition
2. File type categorization  
3. Interactive selection process
4. Voice command integration
5. Cross-platform compatibility

Timeline: 4 weeks
Budget: $5000
Expected ROI: 200%
""",
        
        'user_manual.txt': """AR Notes User Manual
====================

Getting Started:
1. Run interactive_gesture_system.py
2. Show 1-6 fingers to select file type
3. Show 1-9 fingers to select specific file
4. Thumbs up to confirm and open
5. Fist gesture to cancel

File Types:
- 1 finger: Documents (.pdf, .txt, .docx)
- 2 fingers: Images (.jpg, .png, .gif)
- 3 fingers: Videos (.mp4, .avi, .mkv)
- 4 fingers: Audio (.mp3, .wav, .flac)
- 5 fingers: Code (.py, .js, .html)
- 6 fingers: All files

Tips:
- Hold gestures steady for 1-2 seconds
- Ensure good lighting for accuracy
- Keep hand centered in camera view
""",
        
        # Code files
        'hello_world.py': '''# Hello World Python Example
print("Hello, World!")
print("Welcome to AR Notes!")

def greet(name):
    return f"Hello, {name}! Ready to explore AR?"

if __name__ == "__main__":
    user_name = "AR Explorer"
    message = greet(user_name)
    print(message)
''',
        
        'web_page.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AR Notes Demo</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: #4CAF50; color: white; padding: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖐️ AR Notes Web Demo</h1>
            <p>Gesture-controlled file management system</p>
        </div>
        <div class="content">
            <h2>Features</h2>
            <ul>
                <li>Hand gesture recognition</li>
                <li>Interactive file selection</li>
                <li>Multi-category support</li>
                <li>Voice command integration</li>
            </ul>
        </div>
    </div>
</body>
</html>
''',
        
        'styles.css': '''/* AR Notes CSS Demo */
.ar-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.gesture-display {
    font-size: 3rem;
    text-align: center;
    color: #fff;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

.file-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 2rem;
}

.file-item {
    background: rgba(255,255,255,0.1);
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    color: white;
    transition: transform 0.3s ease;
}

.file-item:hover {
    transform: translateY(-5px);
}
''',
        
        # README files
        'README.md': '''# AR Notes Interactive Gesture System

This folder contains sample files for testing the AR Notes gesture recognition system.

## File Categories

### 📄 Documents
- meeting_notes.txt
- project_proposal.txt  
- user_manual.txt

### 🖼️ Images
- (Add your own .jpg, .png files here)

### 🎥 Videos
- (Add your own .mp4, .avi files here)

### 🎵 Audio
- (Add your own .mp3, .wav files here)

### 💻 Code
- hello_world.py
- web_page.html
- styles.css

## Usage

1. Run the gesture system: `python interactive_gesture_system.py`
2. Show fingers to select category
3. Show number to select specific file
4. Thumbs up to confirm and open

## Adding Your Own Files

Simply drop your files into this assets folder. The system will automatically categorize them based on file extensions.

Supported extensions:
- Documents: .pdf, .docx, .txt, .doc
- Images: .jpg, .jpeg, .png, .gif, .bmp
- Videos: .mp4, .avi, .mkv, .mov, .wmv
- Audio: .mp3, .wav, .flac, .m4a
- Code: .py, .js, .html, .css, .java

Happy gesturing! 🖐️
'''
    }
    
    created_count = 0
    for filename, content in sample_files.items():
        filepath = os.path.join(assets_dir, filename)
        
        # Only create if doesn't exist
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created: {filename}")
            created_count += 1
        else:
            print(f"⏭️  Skipped: {filename} (already exists)")
    
    print(f"\n🎉 Setup complete! Created {created_count} sample files.")
    print(f"📁 Files are in: {os.path.abspath(assets_dir)}")
    print("\n🚀 Now you can run: python interactive_gesture_system.py")

if __name__ == "__main__":
    create_sample_files()