import os
import time
import random

BASE_DIR = "C:/Gaming_System"
FOLDERS = ["Game_Folder", "Recording_Folder", "Background_Folder"]

def setup_folders():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        print(f"Created base directory: {BASE_DIR}")
    
    for folder in FOLDERS:
        path = os.path.join(BASE_DIR, folder)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created folder: {path}")

def generate_dummy_file(folder_path, size_mb):
    file_name = f"dummy_{int(time.time())}_{random.randint(1000, 9999)}.dat"
    file_path = os.path.join(folder_path, file_name)
    
    try:
        # Create a file of specified size using null bytes
        with open(file_path, "wb") as f:
            f.write(b"\0" * (size_mb * 1024 * 1024))
        print(f"Generated {size_mb}MB file: {file_path}")
    except Exception as e:
        print(f"Failed to create file {file_path}: {e}")

def main():
    print("Initializing Gaming System Folders...")
    setup_folders()
    
    print("\nGenerating initial dummy files...")
    # Generate one file in each folder to start
    for folder in FOLDERS:
        path = os.path.join(BASE_DIR, folder)
        size = random.randint(100, 500) # 100MB to 500MB
        generate_dummy_file(path, size)
    
    print("\nSetup complete.")

if __name__ == "__main__":
    main()
