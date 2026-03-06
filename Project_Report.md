# Real-Time Priority-Aware Disk Scheduling System
### Formal Project Report

**Domain:** Operating Systems & Concurrent Programming
**Keywords:** Disk Scheduling, Threads, Watchdog File Monitoring, Inter-Process Communication (IPC), Preemptive Prioritization.

---

## 1. Abstract
In modern gaming operating systems, massive high-resolution textures and audio files must be streamed continuously to avoid stuttering or FPS drops. However, Operating Systems typically use standard disk scheduling algorithms (like SCAN or C-SCAN) which treat all file requests equally based entirely on their physical sector locations or arrival times. This project implements a **Priority-Aware Disk Scheduling Engine**, a simulated hardware driver that continuously monitors OS directories, intercepts file generation events in real-time using `watchdog`, and dynamically preempts background disk head movement to service high-priority Game folders over Background updating processes.

---

## 2. System Architecture
The application involves a multi-threaded Python backend bridged seamlessly with a real-time Streamlit data visualization frontend.

### 2.1 Concurrency Model
1. **Thread 1 (File Event Producer):** Utilizing the `watchdog` library, an observer loop continuously polls the Windows File System recursively traversing target directories. When a file is created, a `DiskRequest` object is formulated containing:
   - Arrival Time
   - Hashed Track Destination `(hash(filename) % 500)`
   - Priority Matrix Assignment
2. **Thread-Safe IPC (Inter-Process Communication):** The `DiskRequest` is securely passed across the thread boundary into a Python `queue.Queue()`. The thread safety is ensured via internally managed memory Mutexes allowing the OS to avoid race conditions.
3. **Thread 2 (Scheduler Consumer):** A 2-second polling loop fetches pending batches from the Queue, passes them to the algorithm logic engine (FCFS, SSTF, SCAN, LOOK, or Priority-SCAN), simulates realistic HDD timeslices (`max_process = 3` operations), and then drives the UI data structure rendering.

### 2.2 Preemptive Prioritization Mapping
The core functionality categorizes intercept requests as follows:
- **Priority 1 (Game_Folder):** Immediate Preemptive Interrupt Status `(Highest QoS)`.
- **Priority 2 (Recording_Folder):** Guaranteed execution over background processes.
- **Priority 3 (Background_Folder):** Standard sweep execution context `(Lowest QoS)`.

---

## 3. Algorithm Implementations

### First Come First Serve (FCFS)
The simplest algorithm. Processes requests strictly in chronologically arriving order.
- **Complexity:** `O(1)` Search.
- **Strengths:** 100% fair. No starvation.
- **Weaknesses:** Results in absolute maximum wasted disk head movement, destroying hardware lifespan and resulting in immense latency on high loads.

### Shortest Seek Time First (SSTF)
Evaluates the entire pending queue array and dynamically selects the single track closest to the active head.
- **Complexity:** `O(N^2)` Worst-case Search.
- **Strengths:** Heavily minimizes average seek time.
- **Weaknesses:** Incurs massive starvation overhead for tracks on the edges of the platter if localized center requests keep arriving continuously.

### SCAN / LOOK
Directionally sweeps from Track `0` to Track `499`, then reverses direction. LOOK optimizes this by only sweeping as far as the furthest outstanding request.
- **Complexity:** `O(N log N)` Base Sort Algorithm.
- **Strengths:** Solves starvation entirely whilst maintaining extremely efficient physical drive mechanics. Reaches an optimal balance between throughput and latency limit guarantees.

### Priority-SCAN (Proposed Innovation)
Applies a strictly preemptive hardware interrupt schema to the classic SCAN model. 
1. If the scanner is sweeping through `Background_Folder` sector requests, and a `Game_Folder` event arrives in the Queue buffer:
2. The current sweep is immediately suspended mid-tick (`Preemption`).
3. The Disk Head routes aggressively to the Game sector requests, isolates them, sorts them by SCAN, and executes the sweep dynamically.
4. Only upon Game Queue exhaust will the Head return the context frame back to the suspended background sweep.

---

## 4. Hardware Emulation
The tracking models simulate a traditional moving-platter Hard Disk Drive (HDD). The project proves mathematically that mechanical track traversal distance inherently correlates with response latency limit times. 

*(Solid State Drives possess roughly equal `O(1)` memory block locational latency without sweeping sector delays, rendering spatial algos like SCAN mostly void for M.2 layout configurations. However, NVMe queue-depth Command Prioritization—the core functionality of the Priority-SCAN innovation—remains absolutely functionally vital to modern SSD driver logic).*

---

## 5. Demonstration & Logging
The project features a **Live Disk Head Path Traversal Visualization** rendering the track processing sequence against a continuous Step-Order Y-Axis mapped down an oscilloscope style tracker. Real-time logging is available displaying instantaneous textual metric events:
> `[14:32:11] Game_Folder File Detected → Track 134`
> `Applying Priority-SCAN... Head moved from 145 → 312 ⚡ (Preempted for Game!)`
