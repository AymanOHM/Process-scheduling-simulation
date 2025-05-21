class CPUcore:
    """
    Simulates a single CPU core running processes according to a scheduling algorithm.
    """
    def __init__(self, scheduler, quantum=None):
        self.scheduler = scheduler
        self.quantum = quantum or float('inf')
        
        # If this is a RoundRobin scheduler, ensure its quantum is set correctly
        if hasattr(scheduler, '__class__') and scheduler.__class__.__name__ == 'RoundRobin' and quantum is not None:
            self.scheduler.quantum = quantum

    def run(self, processes):
        # Create deep copies of processes to avoid modifying the original
        import copy
        processes = copy.deepcopy(processes)
        
        timeline = []
        time = 0
        completed = 0
        total_processes = len(processes)
        
        # Keep track of which processes have been added to the scheduler
        added_processes = set()
        
        # Maximum simulation time to prevent infinite loops
        total_burst = sum(p.burst_time for p in processes)
        max_time = min(100, total_burst * 2)  # Limit to reasonable simulation time
        
        # For small total_burst times, ensure we have enough time to complete
        if total_burst < 20:
            max_time = max(max_time, 30) 

        while completed < total_processes and time < max_time:
            # Add all arrived processes to the scheduler
            for p in processes:
                if (p.arrival_time <= time and 
                    p.pid not in added_processes and 
                    p.completion_time is None):
                    self.scheduler.add_process(p)
                    added_processes.add(p.pid)

            current = self.scheduler.get_next_process(time)

            if current:
                if current.start_time is None:
                    current.start_time = time

                # Only run for 1 time unit at a time for consistency with the MultiCoreCPU implementation
                run_time = 1
                
                # Add the current time slot to the timeline
                timeline.append((time, current.pid))

                current.remaining_time -= run_time
                time += run_time

                if current.remaining_time == 0:
                    current.completion_time = time
                    completed += 1
            else:
                timeline.append((time, -1))  # Idle
                time += 1

        if time >= max_time:
            print(f"Simulation terminated: Time limit exceeded after {time} units.")
            
        return timeline


class MultiCoreCPU:
    """
    Simulates a multi-core CPU with multiple cores running in parallel.
    Each core uses the specified scheduling algorithm with load balancing.
    """
    def __init__(self, num_cores, scheduler_class, quantum=None):
        # Create the specified number of CPUcore instances, each with its own scheduler
        self.cores = []
        for _ in range(num_cores):
            if scheduler_class.__name__ == 'RoundRobin' and quantum is not None:
                scheduler = scheduler_class(quantum=quantum)
            else:
                scheduler = scheduler_class()
            self.cores.append(CPUcore(scheduler, quantum))

    def run(self, processes):
        # Deep copy the processes to avoid modifying the original list
        import copy
        processes = copy.deepcopy(processes)

        # Sort processes by arrival time for fair distribution
        processes.sort(key=lambda p: p.arrival_time)

        # --- Static round-robin distribution (current implementation) ---
        core_process_lists = [[] for _ in self.cores]
        for idx, process in enumerate(processes):
            core_id = idx % len(self.cores)
            core_process_lists[core_id].append(process)

        timelines = []
        for core, core_processes in zip(self.cores, core_process_lists):
            timeline = core.run(core_processes)
            timelines.append(timeline)

        return timelines

        # --- Dynamic idle management (alternative, commented for study) ---
        # This approach assigns processes to idle cores as they arrive, simulating dynamic load balancing.
        # Uncomment and adapt as needed.
        #
        # timelines = [[] for _ in self.cores]
        # time = 0
        # completed = 0
        # total_processes = len(processes)
        # available_processes = []
        # scheduled_pids = set()
        # completed_pids = set()
        # total_burst = sum(p.burst_time for p in processes)
        # max_time = min(100, total_burst * 2)
        # if total_burst < 20:
        #     max_time = max(max_time, 30)
        # while completed < total_processes and time < max_time:
        #     # Add newly arrived processes to available_processes
        #     for process in processes:
        #         if (process.arrival_time <= time and 
        #             process.pid not in scheduled_pids and 
        #             process.pid not in completed_pids and
        #             process not in available_processes):
        #             available_processes.append(process)
        #     # Find idle cores
        #     idle_cores = []
        #     for core_id, core in enumerate(self.cores):
        #         if not core.scheduler.get_next_process(time):
        #             idle_cores.append((core_id, core))
        #     # Assign available processes to idle cores
        #     for process in available_processes[:]:
        #         if not idle_cores:
        #             break
        #         core_id, core = idle_cores.pop(0)
        #         core.scheduler.add_process(process)
        #         scheduled_pids.add(process.pid)
        #         available_processes.remove(process)
        #     # Run each core for one time unit
        #     for core_id, core in enumerate(self.cores):
        #         core_timeline = timelines[core_id]
        #         current = core.scheduler.get_next_process(time)
        #         if current:
        #             if current.start_time is None:
        #                 current.start_time = time
        #             run_time = 1
        #             core_timeline.append((time, current.pid))
        #             current.remaining_time -= run_time
        #             if current.remaining_time == 0:
        #                 current.completion_time = time + run_time
        #                 completed += 1
        #                 completed_pids.add(current.pid)
        #         else:
        #             core_timeline.append((time, -1))
        #     time += 1
        # if time >= max_time:
        #     print(f"Simulation terminated: Time limit exceeded after {time} units.")
        # return timelines