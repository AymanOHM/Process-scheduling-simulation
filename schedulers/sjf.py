from .base import SchedulerBase

class SJF(SchedulerBase):
    """
    Shortest Job First (SJF) scheduler implementation.
    
    This scheduler selects the process with the shortest remaining burst time among those ready to run.
    """
    
    def __init__(self):
        # List to hold all processes added to the scheduler
        self.queue = []
        # Set to keep track of process IDs already added
        self.processed_pids = set()

    def add_process(self, process):
        """Add a process to the queue if it hasn't been added before."""
        if process.pid not in self.processed_pids:
            self.queue.append(process)
            self.processed_pids.add(process.pid)

    def get_next_process(self, current_time):
        """
        Get the next process to run according to SJF rules.
        
        Returns the process with the shortest remaining time that is ready and not finished.
        Returns None if no process is ready.
        """
        # Filter for processes that have arrived and still need CPU time
        ready_processes = [p for p in self.queue 
                          if p.arrival_time <= current_time and p.remaining_time > 0]
        
        if not ready_processes:
            return None
            
        # Return the one with the shortest remaining time
        return min(ready_processes, key=lambda p: p.remaining_time)
