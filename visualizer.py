import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def plot_input_processes(processes, title="Input Processes"):
    """
    Create a visualization of the input processes showing arrival and burst times
    
    Args:
        processes: List of Process objects
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    # Sort processes by arrival time for better visualization
    sorted_processes = sorted(processes, key=lambda p: p.arrival_time)
    
    # Create a figure with subplots
    fig = go.Figure()
    
    # Color palette for processes - using a more vibrant palette
    color_palette = [
        '#1E88E5',  # Blue
        '#FF8F00',  # Amber
        '#8E24AA',  # Purple
        '#43A047',  # Green
        '#E53935',  # Red
        '#5E35B1',  # Deep Purple
        '#00897B',  # Teal
        '#F4511E',  # Deep Orange
        '#039BE5',  # Light Blue
        '#7CB342',  # Light Green
        '#C0CA33',  # Lime
        '#6D4C41',  # Brown
    ]
    
    # Add arrival time markers with improved styling
    for i, process in enumerate(sorted_processes):
        color = color_palette[i % len(color_palette)]
        
        # Add arrival point with enhanced marker
        fig.add_trace(go.Scatter(
            x=[process.arrival_time],
            y=[i+1],  # Keep markers aligned with bars
            mode='markers',
            marker=dict(
                size=14, 
                color=color, 
                symbol='triangle-up',
                line=dict(width=1, color='white'),
                opacity=0.9
            ),
            name=f'Process {process.pid}',
            legendgroup=f'Process {process.pid}',
            hovertemplate=f"<b>Process {process.pid}</b><br>" +
                         f"Arrival time: {process.arrival_time}<br>" +
                         f"Priority: {process.priority}" +
                         f"<extra></extra>",
            showlegend=True
        ))
        
        # Add horizontal bar to represent burst time with enhanced styling
        fig.add_trace(go.Bar(
            x=[process.burst_time],
            y=[i+1],  # Position bars at different heights
            orientation='h',
            marker=dict(
                color=color,
                opacity=0.8,
                line=dict(width=1, color='white')
            ),
            name=f'Process {process.pid}',
            legendgroup=f'Process {process.pid}',
            text=f'Burst: {process.burst_time}',
            textposition='inside',
            insidetextanchor='middle',
            hovertemplate=f"<b>Process {process.pid}</b><br>" +
                         f"Burst time: {process.burst_time} units<br>" +
                         f"Priority: {process.priority}" +
                         f"<extra></extra>",
            showlegend=False
        ))
        
        # Add text label for the process with improved visibility
        fig.add_annotation(
            x=0,
            y=i+1,
            text=f'P{process.pid}',
            showarrow=False,
            xanchor='right',
            xshift=-10,
            font=dict(
                color='#37474F',
                size=12,
                family='Roboto, Arial, sans-serif',
                weight='bold'
            )
        )
    
    # Update layout with modern styling
    fig.update_layout(
        title={
            'text': title,
            'font': {'size': 22, 'color': '#0D47A1', 'family': 'Roboto, Arial, sans-serif'}
        },
        xaxis_title={
            'text': 'Time',
            'font': {'size': 14, 'color': '#37474F'}
        },
        yaxis_title={
            'text': 'Process',
            'font': {'size': 14, 'color': '#37474F'}
        },
        legend_title={
            'text': 'Processes',
            'font': {'size': 12, 'color': '#37474F'}
        },
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            borderwidth=1
        ),
        height=max(350, 60 * (len(sorted_processes) + 2)),  # More space for each process
        barmode='overlay',
        xaxis=dict(
            tickmode='linear',
            dtick=1,
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor='rgba(0, 0, 0, 0.2)',
            gridcolor='rgba(0, 0, 0, 0.05)',
            showgrid=True,
        ),
        yaxis=dict(
            showticklabels=False,
            range=[0, len(sorted_processes) + 1.5],
            showgrid=False
        ),
        plot_bgcolor='rgba(255, 255, 255, 1)',  # Clean white background
        paper_bgcolor='rgba(255, 255, 255, 1)',
        margin=dict(l=40, r=20, t=60, b=40),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor='rgba(0, 0, 0, 0.2)',
            align='left',
            font=dict(
                family="Roboto, Arial, sans-serif",
                size=14
            )
        ),
    )
    
    return fig


def plot_aggregate_stats(results):
    # Prepare data for aggregate statistics
    configurations = []
    for res in results:
        if 'display_name' in res['config']:
            config_name = f"{res['config']['display_name']} ({res['config']['num_cores']} cores)"
        else:
            config_name = f"{res['config']['algorithm_name']} ({res['config']['num_cores']} cores)"
        configurations.append(config_name)
        
    avg_waiting_times = [res['stats']['overall']['avg_waiting_time'] for res in results]
    avg_turnaround_times = [res['stats']['overall']['avg_turnaround_time'] for res in results]

    # Create bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=configurations,
        y=avg_waiting_times,
        name="Avg Waiting Time"
    ))
    fig.add_trace(go.Bar(
        x=configurations,
        y=avg_turnaround_times,
        name="Avg Turnaround Time"
    ))

    # Update layout
    fig.update_layout(
        title="Aggregate Statistics",
        barmode="group",
        xaxis_title="Configuration",
        yaxis_title="Time",
    )

    return fig


def plot_process_timeline(processes, title="Process Timeline"):
    """
    Create a timeline visualization showing what happens to each process:
    waiting time, execution time, etc.
    
    Args:
        processes: List of Process objects that have been executed
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    # Filter out processes that haven't completed
    completed_processes = [p for p in processes if p.completion_time is not None]
    
    # Sort processes by arrival time
    sorted_processes = sorted(completed_processes, key=lambda p: p.arrival_time)
    
    if not sorted_processes:
        # Create empty figure if no completed processes
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': "No completed processes to display",
                'font': {'size': 22, 'color': '#0D47A1', 'family': 'Roboto, Arial, sans-serif'}
            },
            plot_bgcolor='rgba(255, 255, 255, 1)',
            paper_bgcolor='rgba(255, 255, 255, 1)'
        )
        return fig
    
    # Enhanced color palette for processes
    color_palette = [
        'rgb(30, 136, 229)',   # blue
        'rgb(255, 143, 0)',    # amber
        'rgb(142, 36, 170)',   # purple
        'rgb(67, 160, 71)',    # green
        'rgb(229, 57, 53)',    # red
        'rgb(94, 53, 177)',    # deep purple
        'rgb(0, 137, 123)',    # teal
        'rgb(244, 81, 30)',    # deep orange
        'rgb(3, 155, 229)',    # light blue
        'rgb(124, 179, 66)',   # light green
    ]
    
    fig = go.Figure()
    
    for i, process in enumerate(sorted_processes):
        # Calculate time intervals
        arrival = process.arrival_time
        start = process.start_time
        completion = process.completion_time
        burst = process.burst_time
        
        # Enhanced colors with better opacity
        waiting_color = 'rgba(239, 154, 154, 0.7)'  # Light red for waiting
        execution_color = color_palette[i % len(color_palette)]
        # Make the execution color slightly transparent
        execution_color_rgba = execution_color.replace('rgb', 'rgba').replace(')', ', 0.9)')
        
        # Process label for y-axis
        process_label = f"P{process.pid}"
        
        # Add waiting time (from arrival to start) with improved styling
        if start > arrival:
            wait_time = start - arrival
            fig.add_trace(go.Bar(
                x=[wait_time],
                y=[i],
                orientation='h',
                base=arrival,
                marker=dict(
                    color=waiting_color,
                    line=dict(width=1, color='rgba(239, 83, 80, 0.9)')
                ),
                name="Waiting Time",
                legendgroup="Waiting Time",
                hovertemplate=f"<b>Process {process.pid} - Waiting Time</b><br>" +
                             f"From t={arrival} to t={start}<br>" +
                             f"Duration: {wait_time} time units" +
                             f"<extra></extra>",
                showlegend=(i == 0),  # Show legend only for the first process
                opacity=0.85
            ))
            
            # Add a label for longer wait times
            if wait_time >= 2:
                fig.add_annotation(
                    x=(arrival + start) / 2,
                    y=i,
                    text=f"{wait_time}",
                    showarrow=False,
                    font=dict(color='black', size=9),
                    bgcolor='rgba(255,255,255,0.7)',
                    bordercolor='rgba(239, 83, 80, 0.7)',
                    borderwidth=1,
                    borderpad=2,
                    opacity=0.9
                )
        
        # Add execution time (from start to completion) with improved styling
        exec_time = completion - start
        fig.add_trace(go.Bar(
            x=[exec_time],
            y=[i],
            orientation='h',
            base=start,
            marker=dict(
                color=execution_color_rgba,
                line=dict(width=1, color=execution_color)
            ),
            name=f"Process {process.pid}",
            legendgroup=f"Process {process.pid}",
            hovertemplate=f"<b>Process {process.pid} - Execution</b><br>" +
                         f"From t={start} to t={completion}<br>" +
                         f"Duration: {exec_time} time units<br>" +
                         f"Total burst: {burst} time units" +
                         f"<extra></extra>",
            showlegend=True,
            opacity=0.9
        ))
        
        # Add a label for longer execution times
        if exec_time >= 2:
            fig.add_annotation(
                x=(start + completion) / 2,
                y=i,
                text=f"{exec_time}",
                showarrow=False,
                font=dict(color='white', size=9, family="Roboto, Arial, sans-serif"),
                bgcolor='rgba(0,0,0,0.0)',
                opacity=0.9
            )
            
        # Add annotations for key timing points with enhanced styling
        annotation_style = dict(
            font=dict(size=10, color='white', family="Roboto, Arial, sans-serif"),
            bordercolor='rgba(0, 0, 0, 0.4)',
            borderwidth=1,
            borderpad=3,
            bgcolor='rgba(55, 71, 79, 0.8)',
            opacity=0.9
        )
        
        # Arrival marker
        fig.add_annotation(
            x=arrival,
            y=i,
            text="A",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor='rgba(55, 71, 79, 0.8)',
            yshift=22,
            **annotation_style
        )
        
        # Start marker
        fig.add_annotation(
            x=start,
            y=i,
            text="S",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor='rgba(55, 71, 79, 0.8)',
            yshift=22,
            **annotation_style
        )
        
        # Completion marker
        fig.add_annotation(
            x=completion,
            y=i,
            text="C",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor='rgba(55, 71, 79, 0.8)',
            yshift=22,
            **annotation_style
        )
    
    # Add y-axis labels for processes
    y_labels = [f"P{p.pid}" for p in sorted_processes]
    
    # Find the max completion time to set proper x-axis range
    max_time = max([p.completion_time for p in sorted_processes]) if sorted_processes else 10
    
    # Update layout with modern styling
    fig.update_layout(
        title={
            'text': title,
            'font': {'size': 22, 'color': '#0D47A1', 'family': 'Roboto, Arial, sans-serif'}
        },
        xaxis_title={
            'text': 'Time',
            'font': {'size': 14, 'color': '#37474F'}
        },
        yaxis_title={
            'text': 'Process',
            'font': {'size': 14, 'color': '#37474F'}
        },
        legend_title={
            'text': 'Processes',
            'font': {'size': 12, 'color': '#37474F'}
        },
        yaxis=dict(
            tickvals=list(range(len(sorted_processes))),
            ticktext=y_labels,
            automargin=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
        ),
        xaxis=dict(
            tickmode='linear',
            dtick=1,
            range=[-0.2, max_time + 0.5],  # Add padding
            gridcolor='rgba(200, 200, 200, 0.2)',
            zerolinecolor='rgba(0, 0, 0, 0.2)',
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            borderwidth=1,
        ),
        height=max(350, 80 * len(sorted_processes)),
        margin=dict(l=50, r=50, t=80, b=50),
        bargap=0.15,
        plot_bgcolor='rgba(255, 255, 255, 1)',  # Clean white background
        paper_bgcolor='rgba(255, 255, 255, 1)',
        hoverlabel=dict(
            bgcolor="white",
            bordercolor='rgba(0, 0, 0, 0.2)',
            align='left',
            font=dict(
                family="Roboto, Arial, sans-serif",
                size=14
            )
        ),
    )
    
    # Add legend for the markers at the bottom of the chart
    fig.add_annotation(
        x=0.5,
        y=-0.15,
        xref="paper",
        yref="paper",
        text="A = Arrival Time | S = Start Time | C = Completion Time",
        showarrow=False,
        font=dict(size=12, color='#37474F', family="Roboto, Arial, sans-serif"),
        align="center",
        bgcolor='rgba(255, 248, 225, 0.8)',
        bordercolor='rgba(255, 183, 77, 0.8)',
        borderwidth=1,
        borderpad=4,
    )
    
    return fig


def plot_gantt_chart(timelines, title="Gantt Chart"):
    """
    Create a Gantt chart visualization of process scheduling on multiple cores
    
    Args:
        timelines: List of timelines, one per core
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    # Define an enhanced color palette with distinct colors and better contrast
    color_palette = [
        'rgb(30, 136, 229)',   # blue
        'rgb(255, 143, 0)',    # amber
        'rgb(142, 36, 170)',   # purple
        'rgb(67, 160, 71)',    # green
        'rgb(229, 57, 53)',    # red
        'rgb(94, 53, 177)',    # deep purple
        'rgb(0, 137, 123)',    # teal
        'rgb(244, 81, 30)',    # deep orange
        'rgb(3, 155, 229)',    # light blue
        'rgb(124, 179, 66)',   # light green
    ]
    
    # Create a color mapping for processes
    unique_pids = set()
    for core_timeline in timelines:
        for _, pid in core_timeline:
            if pid != -1:  # Ignore idle times
                unique_pids.add(pid)
                
    # Create deterministic colors based on PID to ensure consistency
    color_map = {pid: color_palette[pid % len(color_palette)] for pid in unique_pids}
    
    # Add a specific color for idle time - slightly improved from plain gray
    idle_color = 'rgba(220, 220, 220, 0.6)'  # Transparent light grey
    
    # Prepare data by consolidating sequential time periods with the same process
    data = []
    for core_id, timeline in enumerate(timelines):
        if not timeline:
            continue
            
        # Group consecutive time slots with the same process ID
        i = 0
        while i < len(timeline):
            start_time, pid = timeline[i]
            end_time = start_time + 1
            
            # Find the end of this continuous segment
            j = i + 1
            while j < len(timeline) and timeline[j][1] == pid and timeline[j][0] == end_time:
                end_time += 1
                j += 1
                
            # Record this segment
            color = color_map.get(pid, idle_color) if pid != -1 else idle_color
            process_name = f'Process {pid}' if pid != -1 else 'Idle'
            
            data.append({
                'Task': f'Core {core_id}',
                'Start': start_time,
                'Finish': end_time,
                'Process': process_name,
                'Color': color,
                'Duration': end_time - start_time,
                'PID': pid
            })
            
            i = j
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    if df.empty:
        # Create an empty figure if there's no data
        fig = go.Figure()
        fig.update_layout(title=title)
        return fig
    
    # Create a Gantt chart using go.Bar for more control
    fig = go.Figure()
    
    # Process names in order (with Idle at the end)
    process_names = sorted([p for p in df['Process'].unique() if p != 'Idle'])
    if 'Idle' in df['Process'].unique():
        process_names.append('Idle')
    
    # Create bars for each process execution segment
    for process_name in process_names:
        process_df = df[df['Process'] == process_name]
        
        # Determine color and style based on process
        if process_name == 'Idle':
            color = idle_color
            border_color = 'rgba(180, 180, 180, 0.8)'
            border_width = 1
            opacity = 0.7
        else:
            pid = int(process_name.split(' ')[1])  # Extract PID from "Process X"
            color = color_map.get(pid, 'gray')
            # Make the color slightly transparent
            color_parts = color.replace('rgb', 'rgba').replace(')', ', 0.9)')
            border_color = color
            border_width = 1
            opacity = 0.9            # Add horizontal bars with improved styling
        for _, row in process_df.iterrows():
            hover_text = (f"<b>{process_name}</b><br>" +
                        f"Time: {row['Start']} to {row['Finish']}<br>" +
                        f"Duration: {row['Duration']} units" +
                        (f"<br>Process ID: {row['PID']}" if 'PID' in row and row['PID'] != -1 else ""))
            
            fig.add_trace(go.Bar(
                x=[row['Duration']],
                y=[row['Task']],
                orientation='h',
                marker=dict(
                    color=color_parts if process_name != 'Idle' else color,
                    line=dict(
                        color=border_color,
                        width=border_width
                    ),
                    opacity=opacity
                ),
                name=process_name,            hovertemplate=hover_text + '<extra></extra>',
            showlegend=True,
            legendgroup=process_name,
            base=row['Start'],  # Position the bar at the start time
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(
                color='white' if process_name != 'Idle' else 'black',
                size=10
            ),
            hoverinfo='text'
            ))
    
    # Group legend entries
    seen_groups = set()
    for trace in fig.data:
        group = trace.legendgroup
        should_show = group not in seen_groups
        seen_groups.add(group)
        trace.update(showlegend=should_show)
    
    # Find the max time to set proper x-axis range
    max_time = df['Finish'].max() if not df.empty else 10
    
    # Customize the figure with modern styling
    fig.update_layout(
        title={
            'text': title,
            'font': {'size': 22, 'color': '#0D47A1', 'family': 'Roboto, Arial, sans-serif'}
        },
        xaxis_title={
            'text': 'Time',
            'font': {'size': 14, 'color': '#37474F'}
        },
        yaxis_title={
            'text': 'Cores',
            'font': {'size': 14, 'color': '#37474F'}
        },
        legend_title={
            'text': 'Process ID',
            'font': {'size': 12, 'color': '#37474F'}
        },
        barmode='stack',
        xaxis=dict(
            title='Time',
            tickmode='linear',
            dtick=1,  # Show tick every 1 time unit
            tickformat=',d',  # Format as integer
            range=[-0.2, max_time + 0.5],  # Add a bit of padding
            gridcolor='rgba(200, 200, 200, 0.2)',
            zerolinecolor='rgba(0, 0, 0, 0.2)',
        ),
        yaxis=dict(
            title='Cores',
            categoryorder='category ascending',  # Show Core 0 at the top
            gridcolor='rgba(200, 200, 200, 0.2)',
        ),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor='rgba(0,0,0,0.1)',
            font=dict(
                family="Roboto, Arial, sans-serif",
                size=12
            )
        ),
        height=max(300, 80 * (len(df['Task'].unique()) + 1)),  # Adjust height based on number of cores
        legend=dict(
            traceorder='grouped',
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            borderwidth=1,
        ),
        plot_bgcolor='rgba(255, 255, 255, 1)',  # Clean white background
        paper_bgcolor='rgba(255, 255, 255, 1)',
        margin=dict(l=40, r=20, t=60, b=40),
    )
    
    return fig