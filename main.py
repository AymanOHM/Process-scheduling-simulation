from schedulers.fcfs import FCFS
from schedulers.rr import RoundRobin
from schedulers.sjf import SJF  # Import our new scheduler
from cpu import MultiCoreCPU
from stats import compute_stats
from visualizer import plot_aggregate_stats, plot_gantt_chart, plot_input_processes, plot_process_timeline, plot_performance_comparison_bar
from process_gen import generate_processes, Process, generate_test_processes
import dash
from dash import dcc, html
from dash import dash_table
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import copy
from layout import get_app_layout, colors, card_style
from layout import get_result_components

# Create Dash app with external stylesheets
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

# Layout
app.layout = get_app_layout()

# Generate different process sets for comparison
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

# Callback to run simulation and display results
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
    if n_clicks == 0:
        return [], "Select parameters and click 'Run Simulation'"
    
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
    
    # Get selected process set
    process_sets = generate_process_sets(min_burst=min_burst, max_burst=max_burst, random_seed=random_seed)
    processes = process_sets[process_set_size]
    
    # Status message
    status = f"Running simulation with {len(processes)} processes..."
    
    # Map algorithm strings to classes
    algo_map = {
        "fcfs": FCFS,
        "rr": RoundRobin,
        "sjf": SJF
    }
    
    # Build configurations to compare
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

    # Run simulations and collect data
    results = []
    for config in configs:
        # Create a fresh copy of processes for each simulation
        process_copy = copy.deepcopy(processes)
        
        # Run the simulation
        multicore_cpu = MultiCoreCPU(
            num_cores=config["num_cores"],
            scheduler_class=config["algorithm_class"],
            quantum=config.get("quantum", None),
        )
        timeline = multicore_cpu.run(process_copy)
        
        # Get the final state of processes after simulation
        processes_by_core = [[] for _ in range(config["num_cores"])]
        for core_idx, core in enumerate(multicore_cpu.cores):
            for process in core.scheduler.queue:
                if process.completion_time is not None:  # Only include completed processes
                    processes_by_core[core_idx].append(process)
        
        # Compute statistics
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
        
        # Create a JSON serializable config for storage
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

    # Prepare data for the table
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
    
    # Create results components
    result_components = get_result_components(process_fig, bar_fig, aggregate_data, results, card_style, colors, processes)

    return result_components, html.Div([
        html.I(className="fas fa-check-circle", style={"marginRight": "8px"}),
        f"Simulation completed for {len(processes)} processes with {len(configs)} configurations"
    ])

# Callback to update Gantt chart based on selected configuration
@app.callback(
    Output("gantt-chart", "figure"),
    [Input("config-dropdown", "value"),
     Input("simulation-results", "data")]
)
def update_gantt_chart(selected_index, results):
    if not results or selected_index is None:
        # Return empty figure if no data
        return go.Figure()
    
    selected_timeline = results[selected_index]["timeline"]
    selected_config = results[selected_index]["config"]
    title = f"Gantt Chart: {selected_config['display_name']} with {selected_config['num_cores']} cores"
    
    # Add quantum info for Round Robin
    if selected_config.get('algorithm_name') == "rr":
        title += f" (quantum={selected_config.get('quantum', 'N/A')})"
    
    return plot_gantt_chart(selected_timeline, title=title)

# Callback to update Process Timeline based on selected configuration
@app.callback(
    Output("process-timeline", "figure"),
    [Input("config-dropdown", "value"),
     Input("simulation-results", "data")]
)
def update_process_timeline(selected_index, results):
    if not results or selected_index is None:
        # Return empty figure if no data
        return go.Figure()
    
    # Get all completed processes from the selected configuration
    selected_config = results[selected_index]["config"]
    
    # Flatten the list of processes from all cores
    all_processes = []
    for core_processes in results[selected_index]["stats"]["per_core"]:
        if "processes_completed" in core_processes and core_processes["processes_completed"] > 0:
            core_id = core_processes["core_id"]
            # Here we would add the processes, but we need to restructure how we store the data
            # Since we don't store the actual Process objects in the JSON data
            pass
    
    # For now, let's create dummy processes based on the timeline
    # This isn't ideal, but works for visualization purposes
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
    
    # Extract process info from the timeline
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
    
    # Convert to dummy process objects
    dummy_processes = []
    for pid, info in processes.items():
        # Use the first execution time as start time
        start_time = info["execution_times"][0][0] if info["execution_times"] else info["first_seen"]
        
        # Use arrival time = start_time - 2 as a placeholder
        # In reality this should come from the original processes array
        arrival_time = max(0, start_time - 2)
        
        # Use the last seen time as completion time
        completion_time = info["last_seen"] + 1
        
        # Calculate total execution time
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
    
    # Add quantum info for Round Robin
    if selected_config.get('algorithm_name') == "rr":
        title += f" (quantum={selected_config.get('quantum', 'N/A')})"
        
    return plot_process_timeline(dummy_processes, title=title)

if __name__ == "__main__":
    app.run(debug=True)