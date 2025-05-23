# Import required modules and components
from schedulers.fcfs import FCFS  # First-Come, First-Served scheduler
from schedulers.rr import RoundRobin  # Round Robin scheduler
from schedulers.sjf import SJF  # Shortest Job First scheduler
from cpu import MultiCoreCPU  # Multi-core CPU simulation
from stats import compute_stats  # Function to compute statistics
from visualizer import plot_aggregate_stats, plot_gantt_chart, plot_input_processes, plot_process_timeline, plot_performance_comparison_bar  # Visualization functions
from process_gen import generate_processes, Process, generate_test_processes  # Process generation utilities
import dash
from dash import dcc, html
from dash import dash_table
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import copy
from layout import get_app_layout, colors, card_style
from layout import get_result_components

# Create Dash app with external stylesheets for fonts and custom styles
external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap',
        'rel': 'stylesheet',
    },
]
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True, 
    external_stylesheets=external_stylesheets,
    assets_folder='assets'  # Explicitly set assets folder
)

# Set the app layout using a function from layout.py
app.layout = get_app_layout()

# Utility function to generate different sets of processes for simulation
# Includes fixed, small, medium, and large sets for comparison
# Allows for reproducible random sets using a seed

def generate_process_sets(min_burst=1, max_burst=10, random_seed=42):
    # Fixed process set (for consistent comparison)
    fixed_processes = generate_test_processes()
    # Small process set (for quick testing)
    small_processes = [
        Process(pid=0, arrival_time=0, burst_time=3),
        Process(pid=1, arrival_time=1, burst_time=5),
        Process(pid=2, arrival_time=2, burst_time=2),
        Process(pid=3, arrival_time=4, burst_time=4),
        Process(pid=4, arrival_time=6, burst_time=3)
    ]
    # Medium process set (random)
    medium_processes = generate_processes(n=8, max_arrival=5, min_burst=min_burst, max_burst=max_burst, overlap=True, seed=random_seed)
    # Larger process set (random)
    large_processes = generate_processes(n=12, max_arrival=10, min_burst=min_burst, max_burst=max_burst, overlap=True, seed=random_seed)
    return {
        "fixed": fixed_processes,
        "small": small_processes,
        "medium": medium_processes,
        "large": large_processes
    }

# Main callback to run the simulation and display results
# Triggers when the user clicks the Run Simulation button
# Uses the selected parameters from the sidebar
@app.callback(
    [Output("results-container", "children"),
     Output("status-message", "children")],
    [Input("run-simulation", "n_clicks")],
    [State("process-set-size", "value"),
     State("algorithms", "value"),
     State("cores", "value"),
     State("quantum", "value"),
     State("min-burst", "value"),
     State("max-burst", "value"),
     State("random-seed", "value")]
)
def run_and_display_simulation(n_clicks, process_set_size, algorithms, cores, quantum, min_burst, max_burst, random_seed):
    # Only run if the button has been clicked
    if n_clicks == 0:
        return [], "Select parameters and click 'Run Simulation'"
    # Require at least one algorithm
    if not algorithms:
        return [], html.Div([
            html.I(className="fas fa-exclamation-triangle", style={"marginRight": "8px"}),
            "Please select at least one scheduling algorithm"
        ], style={
            "backgroundColor": "rgba(255, 243, 224, 1)",
            "color": "#E65100",
            "border": "1px solid rgba(255, 152, 0, 0.3)",
            "padding": "10px",
            "borderRadius": "4px"
        })
    # Require at least one core
    if not cores:
        return [], html.Div([
            html.I(className="fas fa-exclamation-triangle", style={"marginRight": "8px"}),
            "Please select at least one core configuration"
        ], style={
            "backgroundColor": "rgba(255, 243, 224, 1)",
            "color": "#E65100", 
            "border": "1px solid rgba(255, 152, 0, 0.3)",
            "padding": "10px",
            "borderRadius": "4px"
        })
    # Get the selected process set
    process_sets = generate_process_sets(min_burst=min_burst, max_burst=max_burst, random_seed=random_seed)
    processes = process_sets[process_set_size]
    # Status message for user feedback
    status = f"Running simulation with {len(processes)} processes..."
    # Map algorithm names to their classes
    algo_map = {
        "fcfs": FCFS,
        "rr": RoundRobin,
        "sjf": SJF
    }
    # Build a list of configurations to compare (algorithm x core count)
    configs = []
    for algo in algorithms:
        for num_cores in cores:
            if algo == "rr":
                configs.append({
                    "algorithm_name": algo,
                    "algorithm_class": algo_map[algo], 
                    "num_cores": num_cores,
                    "quantum": quantum,
                    "display_name": f"Round Robin (q={quantum})"
                })
            else:
                configs.append({
                    "algorithm_name": algo,
                    "algorithm_class": algo_map[algo], 
                    "num_cores": num_cores,
                    "display_name": algo_map[algo].__name__
                })
    # Run the simulation for each configuration and collect results
    results = []
    for config in configs:
        # Deep copy the processes so each simulation is independent
        process_copy = copy.deepcopy(processes)
        # Create and run the multi-core CPU simulation
        multicore_cpu = MultiCoreCPU(
            num_cores=config["num_cores"],
            scheduler_class=config["algorithm_class"],
            quantum=config.get("quantum", None),
        )
        timeline = multicore_cpu.run(process_copy)
        # Gather the final state of processes for each core
        processes_by_core = [[] for _ in range(config["num_cores"])]
        for core_idx, core in enumerate(multicore_cpu.cores):
            for process in core.scheduler.queue:
                if process.completion_time is not None:  # Only include completed processes
                    processes_by_core[core_idx].append(process)
        # Compute statistics for this configuration
        stats = compute_stats(processes_by_core)
        # Calculate throughput (processes per unit time)
        max_completion_time = max([p.completion_time for core in processes_by_core 
                                  for p in core if p.completion_time is not None] or [0])
        if max_completion_time > 0:
            throughput = stats["overall"]["total_completed"] / max_completion_time
        else:
            throughput = 0
        # Add throughput to stats
        stats["overall"]["throughput"] = throughput
        # Create a JSON-serializable config for storage
        serializable_config = {
            "algorithm_name": config["algorithm_name"],
            "num_cores": config["num_cores"],
            "display_name": config["display_name"]
        }
        # Add quantum if it exists
        if "quantum" in config:
            serializable_config["quantum"] = config["quantum"]
        # Add to results
        results.append({
            "config": serializable_config, 
            "stats": stats, 
            "timeline": timeline,
            "max_time": max_completion_time
        })
    # Prepare data for the aggregate statistics table
    aggregate_data = [
        {
            "Configuration": f"{res['config']['display_name']} ({res['config']['num_cores']} cores)",
            "Avg Waiting Time": f"{res['stats']['overall']['avg_waiting_time']:.2f}",
            "Avg Turnaround Time": f"{res['stats']['overall']['avg_turnaround_time']:.2f}",
            "Throughput": f"{res['stats']['overall']['throughput']:.3f}",
            "Completion Time": f"{res['max_time']:.0f}"
        }
        for res in results
    ]
    # Create bar chart for statistics comparison
    bar_fig = plot_performance_comparison_bar(aggregate_data)
    # Create a visualization of the input processes
    process_fig = plot_input_processes(processes, title="Input Process Set")
    # Create results UI components (charts, tables, etc.)
    result_components = get_result_components(process_fig, bar_fig, aggregate_data, results, card_style, colors, processes)
    # Return the UI components and a status message
    return result_components, html.Div([
        html.I(className="fas fa-check-circle", style={"marginRight": "8px"}),
        f"Simulation completed for {len(processes)} processes with {len(configs)} configurations"
    ])

# Callback to update the Gantt chart when a configuration is selected
@app.callback(
    Output("gantt-chart", "figure"),
    [Input("config-dropdown", "value"),
     Input("simulation-results", "data")]
)
def update_gantt_chart(selected_index, results):
    # If no results or nothing selected, return an empty figure
    if not results or selected_index is None:
        return go.Figure()
    selected_timeline = results[selected_index]["timeline"]
    selected_config = results[selected_index]["config"]
    title = f"Gantt Chart: {selected_config['display_name']} with {selected_config['num_cores']} cores"
    # Add quantum info for Round Robin
    if selected_config.get('algorithm_name') == "rr":
        title += f" (quantum={selected_config.get('quantum', 'N/A')})"
    return plot_gantt_chart(selected_timeline, title=title)

# Callback to update the process timeline chart when a configuration is selected
@app.callback(
    Output("process-timeline", "figure"),
    [Input("config-dropdown", "value"),
     Input("simulation-results", "data")]
)
def update_process_timeline(selected_index, results):
    # If no results or nothing selected, return an empty figure
    if not results or selected_index is None:
        return go.Figure()
    # Get all completed processes from the selected configuration (not available in JSON, so reconstruct)
    selected_config = results[selected_index]["config"]
    # Flatten the list of processes from all cores (not available, so reconstruct dummy processes)
    class DummyProcess:
        def __init__(self, pid, arrival_time, start_time, completion_time, burst_time):
            self.pid = pid
            self.arrival_time = arrival_time
            self.start_time = start_time
            self.completion_time = completion_time
            self.burst_time = burst_time
    # Extract process timing info from the timeline
    timeline = results[selected_index]["timeline"]
    processes = {}
    for core_id, core_timeline in enumerate(timeline):
        for time, pid in core_timeline:
            if pid != -1:  # Not idle
                if pid not in processes:
                    processes[pid] = {
                        "pid": pid,
                        "first_seen": time,
                        "last_seen": time,
                        "execution_times": []
                    }
                else:
                    processes[pid]["last_seen"] = time
                # Check if this is a continuation of the previous time slot
                if len(processes[pid]["execution_times"]) > 0:
                    last_slot = processes[pid]["execution_times"][-1]
                    if last_slot[1] == time - 1:  # Continued execution
                        processes[pid]["execution_times"][-1] = (last_slot[0], time)
                    else:  # New execution slot
                        processes[pid]["execution_times"].append((time, time))
                else:
                    # First execution slot for this process
                    processes[pid]["execution_times"].append((time, time))
    # Convert to dummy process objects for visualization
    dummy_processes = []
    for pid, info in processes.items():
        start_time = info["execution_times"][0][0] if info["execution_times"] else info["first_seen"]
        arrival_time = max(0, start_time - 2)  # Placeholder
        completion_time = info["last_seen"] + 1
        total_execution = sum(end - start + 1 for start, end in info["execution_times"])
        dummy_processes.append(
            DummyProcess(
                pid=pid,
                arrival_time=arrival_time,
                start_time=start_time,
                completion_time=completion_time,
                burst_time=total_execution
            )
        )
    title = f"Process Timeline: {selected_config['display_name']} with {selected_config['num_cores']} cores"
    if selected_config.get('algorithm_name') == "rr":
        title += f" (quantum={selected_config.get('quantum', 'N/A')})"
    return plot_process_timeline(dummy_processes, title=title)

# Run the Dash app
if __name__ == "__main__":
    app.run(debug=True)