from collections import deque
from .base import SchedulerBase

class RoundRobin(SchedulerBase):
    def __init__(self, quantum=4):
        # Queue to hold processes in the order they should be scheduled
        self.queue = deque()
        # The time slice (quantum) for each process
        self.quantum = quantum
        # Set to keep track of process IDs already added to the queue
        self.processed_pids = set()
        # The process currently being executed
        self.current_process = None
        # How long the current process has been running in this time slice
        self.current_runtime = 0

    def add_process(self, process):
        """Add a process to the queue if it hasn't been added before"""
        # Only add the process if it hasn't been seen before
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
        # If there are no processes in the queue, reset state and return None
        if not self.queue:
            self.current_process = None
            self.current_runtime = 0
            return None
        
        # If there is a current process running
        if self.current_process:
            # Increment the runtime for this time slice
            self.current_runtime += 1 # quantum 4
            # If the process has run for its full quantum or is about to finish
            if self.current_runtime >= self.quantum or self.current_process.remaining_time <= 1:
                # Reset runtime counter for the next process
                self.current_runtime = 0
                # If the process still has work left, it will be re-queued below
                # Clear current process so a new one can be selected
                self.current_process = None
            else:
                # Process still has quantum time left, continue running it
                return self.current_process
        
        # If we need a new process (either none running, or last one finished its quantum)
        if self.current_process is None:
            # Try each process in the queue in order
            for _ in range(len(self.queue)):
                # Get the process at the front of the queue
                process = self.queue[0]
                self.queue.popleft()  # Remove from front
                # If this process has arrived and still needs CPU time
                if process.arrival_time <= current_time and process.remaining_time > 0:
                    # Set as the current process
                    self.current_process = process
                    self.current_runtime = 1  # Start runtime counter
                    # Add it back to the end of the queue for future scheduling
                    self.queue.append(process)
                    return process
                else:
                    # Not ready or already finished, requeue it
                    self.queue.append(process)
            # If no ready process was found, return None
            return None
        # If we already have a current process running its quantum
        return self.current_process