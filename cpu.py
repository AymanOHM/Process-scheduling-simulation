class CPU:

    def __init__(self, scheduler, quantum=None):
        self.scheduler = scheduler
        self.quantum = quantum or float('inf')

    def run(self, processes):
        timeline = []
        time = 0
        completed = 0
        total_processes = len(processes)

        while completed < total_processes:

            for p in processes:
                if p.arrival_time <= time and p not in self.scheduler.queue:
                    self.scheduler.add_process(p)

            current = self.scheduler.get_next_process(time)

            if current:
                if current.start_time is None:
                    current.start_time = time

                run_time = min(self.quantum, current.remaining_time)

                for t in range(run_time):
                    timeline.append((time + t, current.pid))

                current.remaining_time -= run_time
                time += run_time

                if current.remaining_time == 0:
                    current.completion_time = time
                    completed += 1

            else:
                timeline.append((time, -1))
                time += 1

        return timeline