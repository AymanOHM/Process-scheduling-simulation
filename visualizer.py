import matplotlib.pyplot as plt


def plot_gantt_chart(timeline):

    colors = {}
    fig, ax = plt.subplots()
    y = 0
    current_pid = None
    start_time = 0

    for t, pid in timeline + [(None, None)]:
        if pid != current_pid:
            if current_pid is not None and current_pid != -1 and t is not None:

                ax.broken_barh(
                    [(start_time, t - start_time)],
                    (y, 4),
                    facecolors=colors.setdefault(current_pid, f"C{current_pid % 10}")
                )

                y += 5

            start_time = t
            current_pid = pid

    ax.set_xlabel("Time")
    ax.set_ylabel("Processes")
    ax.set_yticks([])
    plt.title("CPU Gantt Chart")
    plt.show()