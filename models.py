import hashlib

class DiskRequest:
    def __init__(self, file_path, folder_type, arrival_time):
        self.file_path = file_path
        self.folder_type = folder_type
        self.arrival_time = arrival_time
        
        # Phase 4: Calculate track based on hash of file name (0 - 499)
        # Using md5 for consistent hashing across runs
        file_name = file_path.split("\\")[-1].split("/")[-1]
        hash_val = int(hashlib.md5(file_name.encode()).hexdigest(), 16)
        self.track = hash_val % 500
        
        # Phase 7: Assign Priority based on folder type
        if folder_type == "Game_Folder":
            self.priority = 1
        elif folder_type == "Recording_Folder":
            self.priority = 2
        elif folder_type == "Background_Folder":
            self.priority = 3
        else:
            self.priority = 4 # Lowest priority

    def __repr__(self):
        return f"DiskRequest(track={self.track}, prio={self.priority}, folder={self.folder_type}, file={self.file_path})"
