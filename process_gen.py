import random


class Process:

    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.start_time = None
        self.completion_time = None
        self.waiting_time = None
        self.turnaround_time = None


def generate_processes(n=5, max_arrival=10, max_burst=10):
    return [
        Process(
            pid=i,
            arrival_time=random.randint(0, max_arrival),
            burst_time=random.randint(1, max_burst),
            priority=random.randint(1, 5)
        ) for i in range(n)
    ]