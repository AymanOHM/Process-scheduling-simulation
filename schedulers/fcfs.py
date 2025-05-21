from .base import SchedulerBase

class FCFS(SchedulerBase):
    """
    First-Come-First-Served Scheduler
    
    Processes are executed in the order they arrive. Once a process starts executing,
    it continues until completion.
    """
    def __init__(self):
        self.queue = []
        self.current_process = None
        # Keep track of processes we've seen
        self.processed_pids = set()

    def add_process(self, process):
        # Add the process to the queue if it's not already there
        if process.pid not in self.processed_pids:
            self.queue.append(process)
            self.processed_pids.add(process.pid)
            # Sort the queue by arrival time - FCFS principle
            self.queue.sort(key=lambda p: p.arrival_time)

    def get_next_process(self, current_time):
        # If there is no process in the queue, return None
        if not self.queue:
            return None
            
        # Get the first process that has arrived and has remaining time
        for p in self.queue:
            if p.arrival_time <= current_time and p.remaining_time > 0:
                # FCFS doesn't remove processes from the queue until they're done
                # So we just return the reference
                return p
                
        # If no valid process is found, return None
        return None