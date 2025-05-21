from .base import SchedulerBase

class SJF(SchedulerBase):
    """
    Shortest Job First (SJF) scheduler
    
    This scheduler selects processes based on their burst time,
    choosing the one with the shortest remaining time first.
    """
    
    def __init__(self):
        self.queue = []
        # Keep track of processes we've seen
        self.processed_pids = set()

    def add_process(self, process):
        if process.pid not in self.processed_pids:
            self.queue.append(process)
            self.processed_pids.add(process.pid)

    def get_next_process(self, current_time):
        # If there is no process in the queue, return None
        if not self.queue:
            return None
        
        # Find all processes that have arrived by the current time 
        # and still have remaining execution time
        ready_processes = [p for p in self.queue 
                          if p.arrival_time <= current_time and p.remaining_time > 0]
        
        if not ready_processes:
            return None
            
        # Get the process with the shortest remaining time
        next_process = min(ready_processes, key=lambda p: p.remaining_time)
        return next_process
