import streamlit as st
import os
import time
import queue
import threading
import psutil
import pandas as pd
import matplotlib.pyplot as plt

# Local imports
from monitor import FolderMonitor
from algorithms import DiskScheduler

# Layout config MUST be the first Streamlit command
st.set_page_config(page_title="Gaming Disk Scheduler", layout="wide")

BASE_DIR = "C:/Gaming_System"
FOLDERS = ["Game_Folder", "Recording_Folder", "Background_Folder"]

def init_session_state():
    if 'request_queue' not in st.session_state:
        st.session_state.request_queue = queue.Queue()
    if 'processed_requests' not in st.session_state:
        st.session_state.processed_requests = []
    if 'monitor_running' not in st.session_state:
        st.session_state.monitor_running = False
    
    # One dictionary containing schedulers for all algorithms to track them simultaneously
    if 'schedulers' not in st.session_state:
        st.session_state.schedulers = {
            "FCFS": DiskScheduler(algo_type="FCFS", initial_track=250),
            "SSTF": DiskScheduler(algo_type="SSTF", initial_track=250),
            "SCAN": DiskScheduler(algo_type="SCAN", initial_track=250),
            "LOOK": DiskScheduler(algo_type="LOOK", initial_track=250),
            "Priority-SCAN": DiskScheduler(algo_type="Priority-SCAN", initial_track=250),
        }
        
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()

def start_monitor_thread():
    if not st.session_state.monitor_running:
        monitor = FolderMonitor(BASE_DIR, st.session_state.request_queue)
        monitor.start()
        st.session_state.monitor = monitor
        st.session_state.monitor_running = True
        
def process_queue(active_algo_type):
    batch = []
    # Dump queue into batch
    while not st.session_state.request_queue.empty():
        batch.append(st.session_state.request_queue.get())
        
    if batch:
        # Add to all algorithms pending queue
        for algo_name, sched in st.session_state.schedulers.items():
            sched.add_requests(batch)
            
    # Process up to 5 requests per tick for all algorithms to simulate real-world preemptive time windows
    for algo_name, sched in st.session_state.schedulers.items():
        processed = sched.process_next(max_process=3)
        
        # We only track the specific processed timeline visually for the "Active" user-selected one
        if algo_name == active_algo_type:
            st.session_state.processed_requests.extend(processed)
                
    return st.session_state.schedulers[active_algo_type]

def count_files():
    counts = {}
    for folder in FOLDERS:
        path = os.path.join(BASE_DIR, folder)
        if os.path.exists(path):
            counts[folder] = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
        else:
            counts[folder] = 0
    return counts

def plot_comparative_graphs():
    algorithms = list(st.session_state.schedulers.keys())
    
    seek_times = []
    wait_times = []
    throughputs = []
    
    for algo in algorithms:
        metrics = st.session_state.schedulers[algo].get_metrics()
        seek_times.append(metrics["Total Seek Time"])
        wait_times.append(metrics["Average Waiting Time"])
        throughputs.append(metrics["Throughput"])
        
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4))
    
    # Seek Time Chart
    bars1 = ax1.bar(algorithms, seek_times, color=['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0'])
    ax1.set_title('Total Seek Time 📉 (Lower = Better)')
    ax1.set_ylabel('Tracks')
    ax1.tick_params(axis='x', rotation=45)
    
    # Wait Time Chart
    bars2 = ax2.bar(algorithms, wait_times, color=['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0'])
    ax2.set_title('Avg Wait Time ⏱️ (Lower = Better)')
    ax2.set_ylabel('Seconds')
    ax2.tick_params(axis='x', rotation=45)
    
    # Throughput Chart
    bars3 = ax3.bar(algorithms, throughputs, color=['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0'])
    ax3.set_title('Throughput 🚀 (Higher = Better)')
    ax3.set_ylabel('Req/sec')
    ax3.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return fig

def main():
    init_session_state()
    start_monitor_thread()
    
    # Title
    st.title("🎮 Advanced Real-Time Priority-Aware Disk Scheduler")
    tab1, tab2, tab3 = st.tabs(["🔴 Live Disk Tracking", "📊 Comparative Algorithm Analysis", "📘 Theoretical OS Report"])
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Section 1: Folder Status Panel")
            counts = count_files()
            status_df = pd.DataFrame([{
                "Folder": folder, 
                "Status": "✅ Active", 
                "Files Detected": count
            } for folder, count in counts.items()])
            st.dataframe(status_df, hide_index=True, use_container_width=True)
            
            st.subheader("Section 2: Active Visualization Algorithm")
            algorithm = st.selectbox(
                "Select Algorithm to Visualize Head Movement",
                ["FCFS", "SSTF", "SCAN", "LOOK", "Priority-SCAN"]
            )
            
        # Process queue secretly for ALL algorithms, and return the active one for UI
        scheduler = process_queue(algorithm)
        
        # Advanced: Real-time head position
        current_head = scheduler.current_track
        st.markdown(f"**📍 Current Disk Head Position ({algorithm}):** `{current_head}` / 499")
        
        with col2:
            st.subheader("Section 4: Live Disk Head Visualization (Path Traversal)")
            if st.session_state.processed_requests:
                # Transposed line graph mapping X: Track Number, Y: Step Order
                tracks = [req.track for req in st.session_state.processed_requests[-50:]] 
                steps = list(range(len(tracks)))
                
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(tracks, steps, marker='o', linestyle='-', color='crimson', markersize=6)
                ax.set_xticks(range(0, 501, 50))
                ax.set_xlim(0, 499)
                
                # Invert Y axis so Step 0 is at top, stepping downwards
                ax.invert_yaxis()
                ax.set_ylabel("Processing Step Order")
                ax.set_xlabel("Disk Track Number (0 - 499)")
                ax.set_title(f"Live Disk Head Movement Path ({algorithm})")
                ax.grid(True, linestyle='--', alpha=0.6)
                st.pyplot(fig)
            else:
                st.info("No requests processed yet. Generate files in the target folders to begin.")
                
        st.divider()
        
        col3, col4 = st.columns([2, 1])
        
        with col3:
            st.subheader("Section 3: Real-Time Request Table")
            if st.session_state.processed_requests:
                req_data = [{
                    "File": req.file_path.split("\\")[-1].split("/")[-1],
                    "Folder": req.folder_type,
                    "Track": req.track,
                    "Priority": req.priority,
                    "Arrival Time": time.strftime('%H:%M:%S', time.localtime(req.arrival_time))
                } for req in reversed(st.session_state.processed_requests[-20:])] # Last 20, newest top
                st.dataframe(pd.DataFrame(req_data), hide_index=True, use_container_width=True)
            else:
                st.write("Queue is empty.")
                
        with col4:
            st.subheader("Section 5: Performance Metrics")
            metrics = scheduler.get_metrics()
            process = psutil.Process(os.getpid())
            cpu_usage = process.cpu_percent()
            
            st.metric(label=f"Total Seek Time ({algorithm})", value=f"{metrics['Total Seek Time']} Tracks")
            st.metric(label=f"Avg Wait Time ({algorithm})", value=f"{metrics['Average Waiting Time']:.4f} s")
            st.metric(label=f"Throughput ({algorithm})", value=f"{metrics['Throughput']:.2f} req/s")
        st.divider()
        col5, col6 = st.columns([1, 1])
        
        with col5:
            st.subheader("Section 6: Live OS Scheduler Logging")
            log_container = st.container(height=250)
            with log_container:
                for log in reversed(scheduler.log_history[-30:]):
                    st.text(log)
                    
    with tab2:
        st.subheader("🏆 Multi-Algorithm Performance Comparison")
        st.markdown("This tab displays how **all** algorithms are performing simultaneously against the identical incoming file queue. Watch as they diverge!")
        
        # Only draw if we have processed something
        requests_count = max([s.total_requests for s in st.session_state.schedulers.values()])
        if requests_count > 0:
            fig2 = plot_comparative_graphs()
            st.pyplot(fig2)
        else:
            st.info("Waiting for file events to build comparison data...")
            
    with tab3:
        st.subheader("📘 Theoretical OS Scheduling Justification")
        
        st.markdown("""
        ### 1. Time Complexity Comparison
        | Algorithm | Search/Insertion Complexity (Best) | Search Complexity (Worst) | Overheads |
        | :--- | :--- | :--- | :--- |
        | **FCFS** | `O(1)` | `O(1)` | Minimal. Simply pops the first arriving request. |
        | **SSTF** | `O(N)` | `O(N^2)` | High. Must repeatedly scan the entire queue to find the absolute closest track. |
        | **SCAN/LOOK** | `O(N log N)` | `O(N log N)` | Requires sorting the queue initially, but linear `O(N)` sweeping afterwards. |
        | **Priority-SCAN** | `O(N log N)` | `O(N log N)` | Categorizes by Priority `O(N)`, then sorts sub-arrays `O(M log M)`. Highly efficient preemption. |
        
        ### 2. Starvation Analysis & Fairness
        - **FCFS**: 100% Fair. No starvation is possible, but seek times are atrocious.
        - **SSTF**: Highly unfair. Prone to severe starvation if a localized cluster of requests continuously arrives.
        - **SCAN / LOOK**: Fairer than SSTF, bounds waiting time nicely by sweeping directionally, but middle tracks are serviced twice as often as edge tracks.
        - **Priority-SCAN (Our Model)**: Intentionally unfair to lower priorities (Background) to guarantee **Game Folder** QoS (Quality of Service). Starvation is theoretically possible for Background tasks if Game requests are infinite, but OS-level aging can be added to prevent this.
        
        ### 3. HDD versus SSD Mechanical Context
        This simulation models a traditional **Hard Disk Drive (HDD)** with physical rotating platters and a mechanical read/write head. 
        - **Seek Time vs Track** visualizations heavily apply to HDDs, where physical traversal distance equals latency.
        - **Solid State Drives (SSDs)** have no moving parts. While Priority routing (Game > Background) is still highly valuable for SSDs (NVMe Queue depth prioritization), spatial algorithms like SCAN/LOOK are obsolete on SSDs because random memory access latency is nearly perfectly uniform (`O(1)`).
        """)
        
    # Phase 4: Auto trigger rerun for real-time visualization
    time.sleep(2)
    st.rerun()

if __name__ == "__main__":
    main()
