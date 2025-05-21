from collections import deque
from .base import SchedulerBase

class RoundRobin(SchedulerBase):
    def __init__(self, quantum=4):
        self.queue = deque()
        self.quantum = quantum
        # Keep track of all processes we've seen to avoid duplicates
        self.processed_pids = set()
        # Track the current process and its runtime for time slicing
        self.current_process = None
        self.current_runtime = 0

    def add_process(self, process):
        """Add a process to the queue if it hasn't been added before"""
        if process.pid not in self.processed_pids:
            self.queue.append(process)
            self.processed_pids.add(process.pid)

    def get_next_process(self, current_time):
        """
        Get the next process from the queue according to Round Robin rules.
        
        In Round Robin, each process gets a fixed time slice (quantum).
        After a process has run for that time, it is preempted and moved
        to the back of the queue.
        
        Returns:
            The next process to execute, or None if no processes are ready.
        """
        # If there are no processes in the queue
        if not self.queue:
            # Reset current process tracking
            self.current_process = None
            self.current_runtime = 0
            return None
        
        # Check if we need to switch processes
        if self.current_process:
            self.current_runtime += 1
            
            # If the process has run for its full quantum OR it's finished
            if self.current_runtime >= self.quantum or self.current_process.remaining_time <= 1:
                # Reset runtime counter
                self.current_runtime = 0
                
                # Move current process to the back of the queue if it has remaining time
                if self.current_process.remaining_time > 1:
                    # We don't need to do anything for queue management here since
                    # the process is already in the queue (it was moved there when selected)
                    pass
                
                # Clear current process so we'll select a new one
                self.current_process = None
            else:
                # Process still has quantum time left, continue with it
                return self.current_process
            
        # If we need a new process (either we don't have one, or the current one is finished with its quantum)
        if self.current_process is None:
            # Cycle through the queue to find a ready process
            for _ in range(len(self.queue)):
                # Check the first process in the queue
                process = self.queue[0]
                self.queue.popleft()  # Remove from front
                
                # If this process is ready and has work to do
                if process.arrival_time <= current_time and process.remaining_time > 0:
                    # Select it as the current process
                    self.current_process = process
                    self.current_runtime = 1  # Start the runtime counter
                    
                    # Add it back to the end of the queue for future scheduling
                    self.queue.append(process)
                    return process
                else:
                    # Process is not ready or finished, requeue it
                    self.queue.append(process)
            
            # If we've looked through all processes and found none ready
            return None
            
        # If we already have a current process running its quantum
        return self.current_process