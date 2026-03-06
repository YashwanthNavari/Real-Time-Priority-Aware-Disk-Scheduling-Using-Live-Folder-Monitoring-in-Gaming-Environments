# Real-Time Priority-Aware Disk Scheduling Using Live Folder Monitoring in Gaming Environments

## What this project is
This project is an advanced, real-time disk scheduling simulator specifically designed to model the I/O priorities of a modern gaming environment. It monitors specific folders on the system (`Game_Folder`, `Recording_Folder`, `Background_Folder`) via the `watchdog` library. When files are created, modified, or deleted in these folders concurrently, it simulates disk I/O requests. These requests then traverse through multiple disk scheduling algorithms simultaneously (FCFS, SSTF, SCAN, LOOK, and a custom Priority-SCAN) to visually and statistically compare their performance in terms of seek time, waiting time, and throughput.

## Key features used in my project
- **Live Folder Monitoring**: Actively monitors directories and translates real file system events into simulated disk I/O requests in real-time.
- **Priority-Aware Scheduling**: Introduces a custom "Priority-SCAN" algorithm which preemptively prioritizes gaming tasks over background and recording tasks to simulate High Quality of Service (QoS).
- **Multi-Algorithm Simulation**: Runs multiple disk scheduling algorithms (FCFS, SSTF, SCAN, LOOK, Priority-SCAN) concurrently against the identical incoming file queue to see how they perform compared to each other.
- **Real-Time Visualizations**: An interactive Streamlit dashboard mapping out the live path traversal of the disk head, a real-time request table, and live OS-like scheduler console logging.
- **Comparative Analysis**: Dynamic bar charts comparing the total seek time, average waiting time, and throughput of all implemented algorithms.

## Modules and features
- **`app.py`**: The main Streamlit dashboard. It sets up the UI logic (Live Disk Tracking, Comparative Algorithm Analysis, Theoretical OS Report) and handles the rendering, threading, and real-time processing loop.
- **`monitor.py`**: Contains the `FolderMonitor` utilizing the `watchdog` module to observe the file system directory events and push `DiskRequest` models to a thread-safe Queue concurrently.
- **`algorithms.py`**: Implements the core logic via `DiskScheduler` handling standard and custom disk scheduling logics (`_fcfs`, `_sstf`, `_scan`, `_look`, `_priority_scan`), tracking operational metrics.
- **`models.py`**: Defines the `DiskRequest` model mapping file events to simulated tracks via MD5 hashing and assigns priorities depending on the origin queue folder.
- **`setup.py`**: A utility script to initialize the simulated `C:/Gaming_System` directory tree and pre-populate dummy files triggering the initial filesystem events seamlessly.

## Tech Stack
- **Python 3.x**: Core application logic.
- **Streamlit**: Web framework powering the real-time interactive user dashboard.
- **Watchdog**: Real-time cross-platform filesystem event monitoring logic.
- **Matplotlib**: Engine for generating comparative analytical charts and plotting live disk head path graphs.
- **Pandas**: Used for managing high-performance data transformation in tabular representations on the UI.
- **Psutil**: To fetch system telemetry like active CPU usage.

## Setup and Installation
1. Ensure you have Python installed.
2. Clone or download the source code files.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the setup and initializing script to create the required base directories (`C:/Gaming_System/Game_Folder`, `C:/Gaming_System/Recording_Folder`, `C:/Gaming_System/Background_Folder`) and generate preliminary data files:
   ```bash
   python setup.py
   ```
   *(Note: The setup script will create these directories directly under your `C:/` drive as part of the simulation context).*

## User Guide
1. **Start the Application**: After installing requirements and executing the setup script, launch the interactive dashboard by running:
   ```bash
   streamlit run app.py
   ```
2. **Navigate the Dashboard**:
   - **🔴 Live Disk Tracking Tab**: Select an active algorithm from the dropdown selection box to observe its real-time head traversal plotted over tracks *0 to 499* mapped alongside live scheduler logs. The left panel shows active target folders.
   - **📊 Comparative Algorithm Analysis Tab**: Watch the live-updating graphical charts comparing Total Seek Time, Average Waiting Time, and Throughput of all 5 algorithms simultaneously.
   - **📘 Theoretical OS Report Tab**: Expand on the mathematical backing concerning time complexity, starvation scenarios, and mechanical context justifying the Priority-SCAN algorithm against SSD integrations.
3. **Trigger File Events Manually**: To see the dashboard react to random I/O occurrences in real-time, manually create, edit, or remove files housed within the `C:/Gaming_System/` subfolders while the app runs in the background. The disk scheduler immediately processes them, hashing new tracks and dispatching algorithms accordingly.
