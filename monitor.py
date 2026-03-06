import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from models import DiskRequest

class FolderMonitorHandler(FileSystemEventHandler):
    def __init__(self, request_queue):
        self.request_queue = request_queue
        
    def process_event(self, event):
        if event.is_directory:
            return
            
        file_path = event.src_path
        folder_type = None
        
        # Identify folder type
        if "Game_Folder" in file_path:
            folder_type = "Game_Folder"
        elif "Recording_Folder" in file_path:
            folder_type = "Recording_Folder"
        elif "Background_Folder" in file_path:
             folder_type = "Background_Folder"
             
        if folder_type:
             request = DiskRequest(
                 file_path=file_path,
                 folder_type=folder_type,
                 arrival_time=time.time()
             )
             self.request_queue.put(request)
             print(f"[{time.strftime('%H:%M:%S')}] {event.event_type.upper()} event captured -> Track: {request.track} Priority: {request.priority} File: {file_path}")

    def on_created(self, event):
        self.process_event(event)
        
    def on_modified(self, event):
        self.process_event(event)

    def on_deleted(self, event):
        self.process_event(event)

class FolderMonitor:
    def __init__(self, base_dir, request_queue):
        self.base_dir = base_dir
        self.request_queue = request_queue
        self.observer = Observer()
        
    def start(self):
        event_handler = FolderMonitorHandler(self.request_queue)
        
        folders = ["Game_Folder", "Recording_Folder", "Background_Folder"]
        for folder in folders:
            path = os.path.join(self.base_dir, folder)
            if os.path.exists(path):
                self.observer.schedule(event_handler, path, recursive=False)
                print(f"Monitoring started for: {path}")
            else:
                print(f"WARNING: Directory does not exist {path}")
                 
        self.observer.start()
        
    def stop(self):
        self.observer.stop()
        self.observer.join()
