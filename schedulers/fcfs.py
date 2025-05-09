
class FCFS:
    def __init__(self):
        self.queue = []

    def add_process(self, process):
        self.queue.append(process)
        self.queue.sort(key=lambda p: p.arrival_time)

    def get_next_process(self, current_time):
        for p in self.queue:
            if p.arrival_time <= current_time and p.remaining_time > 0:
                return p
        return None