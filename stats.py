def compute_stats(processes):

    total_waiting = 0
    total_turnaround = 0

    for process in processes:

        process.turnaround_time = process.completion_time - process.arrival_time

        process.waiting_time = process.turnaround_time - process.burst_time

        total_waiting += process.waiting_time
        total_turnaround += process.turnaround_time

    return {
        "avg_waiting_time": total_waiting / len(processes),
        "avg_turnaround_time": total_turnaround / len(processes),
    }