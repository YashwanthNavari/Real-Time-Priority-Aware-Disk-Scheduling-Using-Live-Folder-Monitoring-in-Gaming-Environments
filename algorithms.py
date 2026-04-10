import time

class DiskScheduler:
    def __init__(self, algo_type="FCFS", initial_track=0, max_track=499):
        self.algo_type = algo_type
        self.current_track = initial_track
        self.max_track = max_track
        self.direction = 1 # 1 for counting up, -1 for counting down
        
        # Metrics
        self.total_seek_time = 0
        self.total_waiting_time = 0
        self.total_requests = 0
        self.start_time = time.time()
        self.pending_requests = []
        self.log_history = []
        
    def add_requests(self, requests):
        self.pending_requests.extend(requests)
        for req in requests:
            self.log_history.append(f"[{time.strftime('%H:%M:%S', time.localtime(req.arrival_time))}] {req.folder_type} File Detected → Track {req.track}")
        
    def schedule_and_process(self, batch):
        # Backward compatibility for old calls, but now adds to pending and processes all
        self.add_requests(batch)
        return self.process_next(len(self.pending_requests))
        
    def process_next(self, max_process=5):
        if not self.pending_requests:
            return []
            
        # Select scheduling logic based on pending
        order = []
        requests = self.pending_requests
        if self.algo_type == "FCFS":
            order = self._fcfs(requests)
        elif self.algo_type == "SSTF":
            order = self._sstf(requests)
        elif self.algo_type == "SCAN":
            order = self._scan(requests)
        elif self.algo_type == "LOOK":
            order = self._look(requests)
        elif self.algo_type == "Priority-SCAN":
            order = self._priority_scan(requests)
            
        # Process the chosen order to simulate track movement and preemption
        to_process = order[:max_process]
        process_log = []
        
        for req in to_process:
            self.pending_requests.remove(req)
            old_track = self.current_track
            seek = abs(self.current_track - req.track)
            wait = time.time() - req.arrival_time
            
            self.total_seek_time += seek
            self.total_waiting_time += wait
            self.total_requests += 1
            
            self.current_track = req.track
            
            # Rich OS logging
            msg = f"[{time.strftime('%H:%M:%S')}] Applying {self.algo_type}... Head moved from {old_track} → {req.track}"
            if self.algo_type == "Priority-SCAN" and req.priority == 1:
                msg += " ⚡ (Preempted for Game!)"
            self.log_history.append(msg)
            
            req.log_message = msg
            process_log.append(req)
            
        return process_log

    def _fcfs(self, requests):
        # First Come First Serve maintains arrival order (already strictly chronological in queue by default)
        return list(requests)
        
    def _sstf(self, requests):
        # Shortest Seek Time First
        pending = list(requests)
        order = []
        curr_track = self.current_track
        
        while pending:
            # Find closest request track to current track
            closest_req = min(pending, key=lambda req: abs(req.track - curr_track))
            order.append(closest_req)
            curr_track = closest_req.track
            pending.remove(closest_req)
            
        return order

    def _scan(self, requests):
        # SCAN moves to one end, then reverses
        order = []
        left = sorted([r for r in requests if r.track < self.current_track], key=lambda x: x.track)
        right = sorted([r for r in requests if r.track >= self.current_track], key=lambda x: x.track)
        
        if self.direction == 1:
            order.extend(right)
            order.extend(reversed(left))
            if left:
                self.direction = -1
        else:
            order.extend(reversed(left))
            order.extend(right)
            if right:
                self.direction = 1
                
        # Update current Track (which happens inside process anyway, but SCAN conceptually touches the end track)
        # However, for request ordering, the sequence of requests visited is what matters.
        return order
        
    def _look(self, requests):
        # LOOK moves only as far as the furthest request in the active direction
        # This implementation matches the ordering of SCAN but logic stops at last request instead of max_track edge.
        return self._scan(requests)
        
    def _priority_scan(self, requests):
        # Strict Preemptive Logic
        # If there are Priority 1 requests, ONLY return the processed priority 1 requests.
        # This forces the disk head to immediately abandon lower priority processing.
        has_prio_1 = any(r.priority == 1 for r in requests)
        
        priorities = {}
        for r in requests:
            if has_prio_1 and r.priority > 1:
                continue # Ignore background tasks completely if Game tasks exist
                
            if r.priority not in priorities:
                priorities[r.priority] = []
            priorities[r.priority].append(r)
            
        order = []
        # Process priority 1 (Game), then 2 (Recording), then 3 (Background)
        for prio in sorted(priorities.keys()):
            prio_group = priorities[prio]
            prio_order = self._scan(prio_group)
            
            # Notice the self.current_track and self.direction are updated dynamically when we stitch orders?
            # For strict algorithm logic, let's process the tracks internally to set the `current_track` 
            # for the next priority group realistically.
            
            # Since _scan uses self.current_track, we need isolated processing:
            # But earlier _scan uses self.current_track that hasn't been updated. A simpler approach:
            
            sub_left = sorted([r for r in prio_group if r.track < self.current_track], key=lambda x: x.track)
            sub_right = sorted([r for r in prio_group if r.track >= self.current_track], key=lambda x: x.track)
            
            if self.direction == 1:
                prio_order_local = sub_right + list(reversed(sub_left))
                if sub_left: self.direction = -1
            else:
                prio_order_local = list(reversed(sub_left)) + sub_right
                if sub_right: self.direction = 1
                
            if prio_order_local:
                self.current_track = prio_order_local[-1].track
                
            order.extend(prio_order_local)
            
        return order
        
    def get_metrics(self):
        avg_wait = self.total_waiting_time / self.total_requests if self.total_requests > 0 else 0
        elapsed_time = time.time() - self.start_time
        throughput = self.total_requests / elapsed_time if elapsed_time > 0 else 0
        
        return {
            "Algorithm": self.algo_type,
            "Total Seek Time": self.total_seek_time,
            "Average Waiting Time": avg_wait,
            "Throughput": throughput
        }
