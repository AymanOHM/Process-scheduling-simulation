def compute_stats(processes_by_core):
    total_waiting = 0
    total_turnaround = 0
    total_completed_processes = 0
    core_stats = []

    for core_id, processes in enumerate(processes_by_core):
        # Filter to only include completed processes
        completed_processes = [p for p in processes if p.completion_time is not None]
        
        if not completed_processes:  # Skip empty cores
            core_stats.append({
                "core_id": core_id,
                "avg_waiting_time": 0,
                "avg_turnaround_time": 0,
                "processes_completed": 0
            })
            continue

        core_waiting = 0
        core_turnaround = 0

        for process in completed_processes:
            # Calculate turnaround time
            process.turnaround_time = process.completion_time - process.arrival_time
            
            # Calculate waiting time (time spent not executing)
            # It's the turnaround time minus the actual execution time
            # This ensures waiting time is never negative
            process.waiting_time = max(0, process.turnaround_time - process.burst_time)

            core_waiting += process.waiting_time
            core_turnaround += process.turnaround_time

        core_stats.append({
            "core_id": core_id,
            "avg_waiting_time": core_waiting / len(completed_processes),
            "avg_turnaround_time": core_turnaround / len(completed_processes),
            "processes_completed": len(completed_processes)
        })

        total_waiting += core_waiting
        total_turnaround += core_turnaround
        total_completed_processes += len(completed_processes)

    # Prevent division by zero if no processes were completed
    if total_completed_processes == 0:
        overall_stats = {
            "avg_waiting_time": 0,
            "avg_turnaround_time": 0,
            "total_completed": 0
        }
    else:
        overall_stats = {
            "avg_waiting_time": total_waiting / total_completed_processes,
            "avg_turnaround_time": total_turnaround / total_completed_processes,
            "total_completed": total_completed_processes
        }

    return {"overall": overall_stats, "per_core": core_stats}