import os

def create_asset_folder(folder_name, description, extensions):
    folder_path = os.path.join('assets', folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # README for folder
    readme_fp = os.path.join(folder_path, "README.md")
    with open(readme_fp, 'w', encoding='utf-8') as f:
        f.write(f"# {folder_name.capitalize()} Folder\n\n")
        f.write(f"This folder contains {description} files.\n\n")
        f.write("Supported extensions:\n")
        for ext in extensions:
            f.write(f"- {ext}\n")
        f.write("\nAdd your files here. The AR Notes system automatically detects and categorizes files.\n")

def create_sample_file(folder_name, filename, content):
    full_path = os.path.join('assets', folder_name, filename)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("Setting up asset folders and sample files...")

    folders = {
        "documents": {
            "description": "document (PDF, TXT, DOCX, DOC)",
            "extensions": [".pdf", ".txt", ".docx", ".doc"],
            "samples": {
                "meeting_notes.txt": "# Meeting Notes\n- Discuss gesture-controlled AR Notes\n- Setup assets\n- Test system",
                "project_proposal.txt": "# Project Proposal\nBuild a natural hand gesture controlled AR notes app"
            }
        },
        "images": {
            "description": "image (PNG, JPG, GIF, BMP)",
            "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "samples": {
                "screenshot_app.png": "# This is a placeholder file. Add actual images."
            }
        },
        "videos": {
            "description": "video (MP4, AVI, MKV, MOV)",
            "extensions": [".mp4", ".avi", ".mkv", ".mov"],
            "samples": {
                "tutorial.mp4": "# Placeholder file. Add your video tutorials."
            }
        },
        "audio": {
            "description": "audio (MP3, WAV, FLAC, AAC)",
            "extensions": [".mp3", ".wav", ".flac", ".aac"],
            "samples": {
                "confirmation.wav": "# Placeholder for confirmation beep sound. Replace with WAV file."
            }
        },
        "code": {
            "description": "code files (PY, JS, HTML, CSS, CPP)",
            "extensions": [".py", ".js", ".html", ".css", ".cpp"],
            "samples": {
                "example.py": "# Example Python script\nprint('Hello AR Notes')"
            }
        }
    }

    os.makedirs('assets', exist_ok=True)

    for folder, info in folders.items():
        create_asset_folder(folder, info['description'], info['extensions'])
        for filename, content in info.get('samples', {}).items():
            create_sample_file(folder, filename, content)

    print("Asset folders and sample files created successfully.\n")

if __name__ == "__main__":
    main()
