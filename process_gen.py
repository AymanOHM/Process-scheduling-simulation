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

    def __repr__(self):
        return f"Process(pid={self.pid}, arrival={self.arrival_time}, burst={self.burst_time}, remaining={self.remaining_time})"


def generate_processes(n=5, max_arrival=10, min_burst=1, max_burst=10, overlap=True, seed=None):
    """
    Generate a list of processes with configurable parameters.
    
    Args:
        n: Number of processes to generate
        max_arrival: Maximum arrival time
        min_burst: Minimum burst time
        max_burst: Maximum burst time
        overlap: If True, create overlapping arrivals for better concurrency
        seed: Random seed for reproducibility
        
    Returns:
        List of Process objects
    """
    if seed is not None:
        random.seed(seed)
    if overlap:
        # Generate arrival times clustered to create overlapping processes
        arrival_times = [random.randint(0, max_arrival // 2) for _ in range(n)]
    else:
        # More spread-out arrival times
        arrival_times = sorted([random.randint(0, max_arrival) for _ in range(n)])

    # Generate a mix of short and long burst times
    burst_times = []
    for _ in range(n):
        # 70% chance of short burst, 30% chance of long burst
        if random.random() < 0.7:
            mid_point = min_burst + (max_burst - min_burst) // 2
            burst_times.append(random.randint(min_burst, mid_point))
        else:
            mid_point = min_burst + (max_burst - min_burst) // 2
            burst_times.append(random.randint(mid_point + 1, max_burst))

    return [
        Process(
            pid=i,
            arrival_time=arrival_times[i],
            burst_time=burst_times[i],
            priority=random.randint(1, 5)
        ) for i in range(n)
    ]


def generate_test_processes():
    """
    Generate a predefined set of processes for testing and comparison.
    
    Returns:
        List of Process objects with known characteristics
    """
    return [
        # Short burst, early arrival
        Process(pid=0, arrival_time=0, burst_time=3, priority=1),
        # Longer burst, early arrival
        Process(pid=1, arrival_time=1, burst_time=8, priority=3),
        # Medium burst, later arrival
        Process(pid=2, arrival_time=2, burst_time=5, priority=2),
        # Short burst, late arrival
        Process(pid=3, arrival_time=5, burst_time=2, priority=4),
        # Long burst, late arrival
        Process(pid=4, arrival_time=6, burst_time=10, priority=5),
    ]