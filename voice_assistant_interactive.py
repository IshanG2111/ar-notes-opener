# Voice Assistant for Interactive Gesture System
# Integrates with the new sequential selection workflow

import speech_recognition as sr
import pyttsx3
import os
import time
import subprocess
import platform
from interactive_gesture_system import InteractiveGestureFileSystem

class VoiceAssistant:
    def __init__(self, assets_dir='assets'):
        self.assets_dir = assets_dir
        self.gesture_system = InteractiveGestureFileSystem(assets_dir)
        
        # Initialize TTS
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id)  # Try female voice
        self.engine.setProperty('rate', 180)  # Slightly faster speech
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Calibrate for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"🤖 Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        """Listen for voice input with timeout handling"""
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
            
            print("🔄 Processing...")
            text = self.recognizer.recognize_google(audio)
            print(f"👤 You said: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            return None  # No speech detected
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't understand. Could you repeat that?")
            return None
        except sr.RequestError:
            self.speak("Speech recognition service is unavailable.")
            return None
    
    def list_files_by_type(self, file_type_num):
        """List files of a specific type"""
        files = self.gesture_system.get_files_by_type(file_type_num)
        type_name = self.gesture_system.file_types[file_type_num]["name"]
        
        if not files:
            self.speak(f"No {type_name.lower()} files found in assets folder.")
            return
        
        self.speak(f"Found {len(files)} {type_name.lower()} files:")
        for i, filename in enumerate(files[:9], 1):  # Limit to first 9
            self.speak(f"Number {i}: {filename}")
    
    def open_file_by_name(self, filename):
        """Open a specific file by name"""
        file_path = os.path.join(self.assets_dir, filename)
        
        if not os.path.exists(file_path):
            self.speak(f"File {filename} not found in assets folder.")
            return False
        
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])
            
            self.speak(f"Opening {filename}")
            return True
        except Exception as e:
            self.speak(f"Error opening {filename}")
            return False
    
    def open_file_by_type_and_number(self, file_type_num, file_number):
        """Open file by type and position number"""
        files = self.gesture_system.get_files_by_type(file_type_num)
        
        if not files:
            type_name = self.gesture_system.file_types[file_type_num]["name"]
            self.speak(f"No {type_name.lower()} files found.")
            return False
        
        if 1 <= file_number <= len(files):
            filename = files[file_number - 1]
            return self.open_file_by_name(filename)
        else:
            self.speak(f"Invalid file number. Please choose between 1 and {len(files)}")
            return False
    
    def show_help(self):
        """Show available voice commands"""
        help_text = """
Here are the voice commands you can use:

File Type Commands:
- "List documents" or "Show documents"
- "List images" or "Show images"  
- "List videos" or "Show videos"
- "List audio" or "Show audio"
- "List code" or "Show code files"
- "List all files"

Direct File Opening:
- "Open [filename]" - e.g., "Open meeting notes dot txt"
- "Open document number 1" - Opens first document
- "Open image number 2" - Opens second image

System Commands:
- "Help" - Show this help
- "What can you do" - Show capabilities
- "Exit" or "Quit" - Exit assistant

Gesture System:
- "Start gesture system" - Launch the interactive hand gesture interface

Remember: You can also use the gesture system directly by running it separately!
        """
        self.speak("Here are the available commands:")
        print(help_text)
    
    def parse_file_type_command(self, text):
        """Parse file type from voice command"""
        if "document" in text:
            return 1
        elif "image" in text:
            return 2
        elif "video" in text:
            return 3
        elif "audio" in text or "music" in text:
            return 4
        elif "code" in text:
            return 5
        elif "all" in text:
            return 6
        return None
    
    def process_command(self, text):
        """Process voice command"""
        if not text:
            return True
        
        # Exit commands
        if any(word in text for word in ["exit", "quit", "goodbye", "stop"]):
            self.speak("Goodbye! Thanks for using AR Notes voice assistant.")
            return False
        
        # Help commands
        elif any(word in text for word in ["help", "what can you do", "commands"]):
            self.show_help()
        
        # List files commands
        elif "list" in text or "show" in text:
            file_type = self.parse_file_type_command(text)
            if file_type:
                self.list_files_by_type(file_type)
            else:
                self.speak("Please specify a file type: documents, images, videos, audio, code, or all files")
        
        # Direct file opening
        elif "open" in text:
            if "number" in text:
                # Extract file type and number
                file_type = self.parse_file_type_command(text)
                if file_type:
                    # Extract number
                    words = text.split()
                    try:
                        number_index = words.index("number")
                        if number_index + 1 < len(words):
                            file_number = int(words[number_index + 1])
                            self.open_file_by_type_and_number(file_type, file_number)
                        else:
                            self.speak("Please specify which number file to open")
                    except (ValueError, IndexError):
                        self.speak("Please specify a valid file number")
                else:
                    self.speak("Please specify the file type: document, image, video, audio, or code")
            else:
                # Extract filename (replace "dot" with ".")
                filename = text.replace("open ", "").replace("dot ", ".")
                self.open_file_by_name(filename)
        
        # Start gesture system
        elif "gesture" in text or "start gesture" in text:
            self.speak("Starting the interactive gesture system. Use hand gestures to select and open files.")
            # Note: In practice, you'd launch this in a separate process
            print("🖐️ To start gesture system, run: python interactive_gesture_system.py")
        
        else:
            self.speak("I didn't understand that command. Say 'help' to see available commands.")
        
        return True
    
    def run(self):
        """Main voice assistant loop"""
        self.speak("Hello! I'm your AR Notes voice assistant. I can help you manage and open files using voice commands.")
        self.speak("Say 'help' to see what I can do, or give me a command.")
        
        timeout_count = 0
        max_timeouts = 3
        
        while True:
            text = self.listen()
            
            if text is None:
                timeout_count += 1
                if timeout_count >= max_timeouts:
                    self.speak("I haven't heard anything for a while. Say something or I'll exit.")
                    text = self.listen()
                    if text is None:
                        self.speak("Goodbye!")
                        break
                    timeout_count = 0
                continue
            else:
                timeout_count = 0
            
            if not self.process_command(text):
                break
            
            time.sleep(0.5)  # Brief pause between commands

if __name__ == "__main__":
    print("🎙️ AR Notes Voice Assistant")
    print("Make sure your microphone is connected and working.")
    print("Starting in 3 seconds...")
    
    time.sleep(3)
    
    assistant = VoiceAssistant()
    assistant.run()