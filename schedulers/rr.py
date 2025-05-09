from collections import deque

class RoundRobin:
    def __init__(self, quantum=4):
        self.queue = deque()
        self.quantum = quantum

    def add_process(self, process):
        if process not in self.queue:
            self.queue.append(process)

    def get_next_process(self, current_time):
        for _ in range(len(self.queue)):
            process = self.queue.popleft()
            if process.remaining_time > 0 and process.arrival_time <= current_time:
                self.queue.append(process)
                return process
            else:
                self.queue.append(process)
        return None