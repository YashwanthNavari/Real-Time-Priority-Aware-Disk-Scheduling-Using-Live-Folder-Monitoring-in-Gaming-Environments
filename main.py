import time
import threading
import queue
import psutil
import os
import random
from monitor import FolderMonitor
from algorithms import DiskScheduler
from metrics import plot_metrics

BASE_DIR = "C:/Gaming_System"
FOLDERS = ["Game_Folder", "Recording_Folder", "Background_Folder"]

def file_generator(num_files=20, delay=0.1):
    """Simulates real-world file activity to trigger watchdog events"""
    for _ in range(num_files):
        folder = random.choice(FOLDERS)
        file_path = os.path.join(BASE_DIR, folder, f"test_{random.randint(1000,9999)}.dat")
        try:
            with open(file_path, "w") as f:
                f.write("Simulated workload")
        except Exception:
            pass
        time.sleep(delay)

def run_simulation(algo_name):
    print(f"\n--- Starting Phase 10 Simulation for {algo_name} ---")
    request_queue = queue.Queue()
    
    # Init Monitor
    monitor = FolderMonitor(BASE_DIR, request_queue)
    
    # Init Scheduler
    scheduler = DiskScheduler(algo_type=algo_name, initial_track=250)
    
    # Phase 9 tracking system metrics
    process = psutil.Process(os.getpid())
    start_cpu = process.cpu_percent()
    try:
        start_io = psutil.disk_io_counters()
    except:
        start_io = None
    
    # Phase 8: Thread 1 - Watchdog Monitor
    monitor.start()
    
    # Thread to generate files creating live folder requests
    gen_thread = threading.Thread(target=file_generator, args=(20, 0.15))
    gen_thread.start()
    
    # Phase 8: Thread 2 - Scheduler Processing Queue
    is_running = True
    def scheduler_worker():
        while is_running or not request_queue.empty():
            batch = []
            while not request_queue.empty():
                batch.append(request_queue.get())
            
            if batch:
                scheduler.schedule_and_process(batch)
            time.sleep(0.5) # Process queue every 500ms
            
    sched_thread = threading.Thread(target=scheduler_worker)
    sched_thread.start()
    
    # Wait for generator to finish
    gen_thread.join()
    time.sleep(1) # Extra time for watchdog to catch trailing events
    
    # Stop the loops
    is_running = False
    sched_thread.join()
    monitor.stop()
    
    # Collect Phase 9 System Metrics
    end_cpu = process.cpu_percent()
    metrics = scheduler.get_metrics()
    
    metrics["CPU Usage (%)"] = end_cpu
    if start_io:
        try:
             end_io = psutil.disk_io_counters()
             metrics["Disk Read Bytes"] = end_io.read_bytes - start_io.read_bytes
             metrics["Disk Write Bytes"] = end_io.write_bytes - start_io.write_bytes
        except:
             pass
             
    print(f"Results for {algo_name}:")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
            
    return metrics

def main():
    algorithms = ["FCFS", "SSTF", "SCAN", "LOOK", "Priority-SCAN"]
    results = []
    
    # Clean previous generated files before test
    for folder in FOLDERS:
        path = os.path.join(BASE_DIR, folder)
        if os.path.exists(path):
            for f in os.listdir(path):
                if f.startswith("test_"):
                     try: os.remove(os.path.join(path, f))
                     except: pass
                     
    # Run simulation for all algorithms
    for algo in algorithms:
        res = run_simulation(algo)
        results.append(res)
        
    print("\n--- Simulation Complete ---")
    plot_metrics(results)

if __name__ == "__main__":
    main()
