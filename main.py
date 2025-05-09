from process_gen import generate_processes
from schedulers.fcfs import FCFS
from schedulers.rr import RoundRobin
from cpu import CPU
from stats import compute_stats
from visualizer import plot_gantt_chart

if __name__ == "__main__":

    processes = generate_processes(n=5)
    scheduler = FCFS()  # or RoundRobin()
    cpu = CPU(scheduler, quantum=3)

    timeline = cpu.run(processes)

    stats = compute_stats(processes)

    for process in processes:
        print(f"PID {process.pid}: Waiting Time={process.waiting_time}, Turnaround Time={process.turnaround_time}")

    print("Overall Stats:", stats)

    plot_gantt_chart(timeline)