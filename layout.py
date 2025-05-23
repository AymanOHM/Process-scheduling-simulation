from dash import dcc, html
from dash import dash_table
import plotly.graph_objects as go

# Define custom styles
colors = {
    'background': '#f9fcff',
    'panel': '#ffffff',
    'primary': '#1e88e5',
    'secondary': '#7cb342',
    'accent': '#ff6d00',
    'text': '#37474f',
    'light-text': '#78909c',
    'header': '#0d47a1',
    'border': '#e1e5ea'
}

card_style = {
    'backgroundColor': colors['panel'],
    'borderRadius': '8px',
    'boxShadow': '0 2px 10px rgba(0, 0, 0, 0.05)',
    'padding': '20px',
    'marginBottom': '20px',
}

def get_app_layout():
    return html.Div([
        # Header (should be outside the flex row)
        html.Div([
            html.H1("Process Scheduling Simulation", className="app-header"),
        ], style={
            'backgroundColor': colors['header'],
            'color': 'white',
            'padding': '20px 0',
            'textAlign': 'center',
            'borderRadius': '8px',
            'marginBottom': '20px',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'width': '100%',
            'maxWidth': '100%',
        }),
        # Main content row: sidebar + results
        html.Div([
            html.Div([
                html.H3("Simulation Parameters", style={
                    'color': colors['header'],
                    'borderBottom': f'2px solid {colors["border"]}',
                    'paddingBottom': '10px',
                    'marginBottom': '20px'
                }),
                # Process set size
                html.Label("Process Set Size", style={'fontWeight': 'bold', 'marginTop': '10px'}),
                dcc.Dropdown(
                    id="process-set-size",
                    options=[
                        {"label": "Fixed (5, demo)", "value": "fixed"},
                        {"label": "Small (5, random)", "value": "small"},
                        {"label": "Medium (8, random)", "value": "medium"},
                        {"label": "Large (12, random)", "value": "large"},
                    ],
                    value="fixed",
                    clearable=False,
                    style={'marginBottom': '15px'}
                ),
                # Algorithms
                html.Label("Scheduling Algorithms", style={'fontWeight': 'bold', 'marginTop': '10px'}),
                dcc.Checklist(
                    id="algorithms",
                    options=[
                        {"label": "FCFS", "value": "fcfs"},
                        {"label": "Round Robin", "value": "rr"},
                        {"label": "SJF", "value": "sjf"},
                    ],
                    value=["fcfs"],
                    inputStyle={"marginRight": "8px"},
                    style={'marginBottom': '15px'}
                ),
                # Number of cores
                html.Label("Number of Cores", style={'fontWeight': 'bold', 'marginTop': '10px'}),
                dcc.Checklist(
                    id="cores",
                    options=[
                        {"label": "1", "value": 1},
                        {"label": "2", "value": 2},
                        {"label": "4", "value": 4},
                    ],
                    value=[1],
                    inputStyle={"marginRight": "8px"},
                    style={'marginBottom': '15px'}
                ),
                # Quantum (for RR)
                html.Label("Quantum (for Round Robin)", style={'fontWeight': 'bold', 'marginTop': '10px'}),
                html.Div([
                    dcc.Slider(
                        id="quantum",
                        min=1,
                        max=10,
                        step=1,
                        value=4,
                        marks={i: str(i) for i in range(1, 11)},
                        tooltip={"placement": "bottom", "always_visible": False},
                        updatemode="drag",
                        included=False
                    )
                ], style={'marginBottom': '15px'}),
                # Burst time range
                html.Label("Burst Time Range", style={'fontWeight': 'bold', 'marginTop': '10px'}),
                html.Div([
                    dcc.Input(id="min-burst", type="number", min=1, max=20, value=1, style={'width': '45%', 'marginRight': '5%'}),
                    dcc.Input(id="max-burst", type="number", min=1, max=20, value=10, style={'width': '45%'}),
                ], style={'display': 'flex', 'marginBottom': '15px'}),
                # Random seed
                html.Label("Random Seed", style={'fontWeight': 'bold', 'marginTop': '10px'}),
                dcc.Input(id="random-seed", type="number", min=0, max=9999, value=42, style={'width': '100%', 'marginBottom': '15px'}),
                # Run button
                html.Button("Run Simulation", id="run-simulation", n_clicks=0, style={
                    'backgroundColor': colors['primary'],
                    'color': 'white',
                    'fontWeight': 'bold',
                    'width': '100%',
                    'padding': '12px',
                    'border': 'none',
                    'borderRadius': '4px',
                    'fontSize': '1.1rem',
                    'marginTop': '10px',
                    'marginBottom': '10px',
                    'boxShadow': '0 2px 6px rgba(30, 136, 229, 0.08)'
                }),
                # Status message
                html.Div(id="status-message", style={'marginTop': '10px', 'minHeight': '28px'}),
            ], className="sidebar-content", style=card_style),
            html.Div(
                id="results-container",
                children=[],
                style={
                    'flex': '1',
                    'minWidth': '0'
                }
            )
        ], style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'width': '100%'
        })
    ], style={
        'width': '100%',
        'maxWidth': '100vw',
        'margin': '0',
        'padding': '0',
        'backgroundColor': colors['background']
    })

def get_result_components(process_fig, bar_fig, aggregate_data, results, card_style, colors, processes):
    return [
        # Input process visualization
        html.Div([
            html.H2("Input Process Visualization", className="card-title", style={
                'color': colors['header'],
                'marginTop': '0',
                'marginBottom': '15px',
                'fontSize': '1.5rem',
            }),
            html.P("This chart shows the input processes with their arrival times (triangles) and burst times (horizontal bars):", 
                   style={'color': colors['light-text'], 'marginBottom': '15px'}),
            dcc.Graph(figure=process_fig)
        ], style={**card_style, 'marginBottom': '25px'}),
    
        # Bar chart comparing metrics
        html.Div([
            html.H2("Performance Metrics Comparison", className="card-title", style={
                'color': colors['header'],
                'marginTop': '0',
                'marginBottom': '15px',
                'fontSize': '1.5rem',
            }),
            dcc.Graph(figure=bar_fig)
        ], style={**card_style, 'marginBottom': '25px'}),
        
        # Table of aggregate statistics
        html.Div([
            html.H2("Detailed Statistics", className="card-title", style={
                'color': colors['header'],
                'marginTop': '0',
                'marginBottom': '15px',
                'fontSize': '1.5rem',
            }),
            dash_table.DataTable(
                id="aggregate-table",
                columns=[
                    {"name": "Configuration", "id": "Configuration"},
                    {"name": "Avg Waiting Time", "id": "Avg Waiting Time"},
                    {"name": "Avg Turnaround Time", "id": "Avg Turnaround Time"},
                    {"name": "Throughput", "id": "Throughput"},
                    {"name": "Completion Time", "id": "Completion Time"}
                ],
                data=aggregate_data,
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "center", 
                    "padding": "12px",
                    "fontFamily": '"Roboto", sans-serif',
                    "backgroundColor": "white",
                    "fontSize": "14px",
                    "minWidth": "100px",
                },
                style_header={
                    "backgroundColor": colors['primary'],
                    "color": "white",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "padding": "14px",
                    "fontSize": "15px",
                    "letterSpacing": "0.5px",
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#f9fcff"
                    },
                    {
                        "if": {"state": "selected"},
                        "backgroundColor": "#e1f5fe",
                        "border": f"1px solid {colors['primary']}"
                    }
                ],
                tooltip_delay=0,
                tooltip_duration=None,
                css=[{
                    'selector': '.dash-table-tooltip',
                    'rule': 'background-color: white; font-family: Roboto, sans-serif; color: #37474f; font-size: 14px; padding: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'
                }]
            )
        ], style={**card_style, 'marginBottom': '25px'}),

        # Gantt chart section with dropdown
        html.Div([
            html.H2("Gantt Chart Visualization", className="card-title", style={
                'color': colors['header'],
                'marginTop': '0',
                'marginBottom': '15px',
                'fontSize': '1.5rem',
            }),
            html.P("Select a configuration to visualize:", style={'marginBottom': '10px', 'color': colors['light-text']}),
            dcc.Dropdown(
                id="config-dropdown",
                options=[
                    {"label": f"{res['config']['display_name']} ({res['config']['num_cores']} cores)", 
                     "value": i}
                    for i, res in enumerate(results)
                ],
                value=0,
                clearable=False,
                style={
                    "width": "100%",
                    "marginBottom": "20px",
                    "backgroundColor": "#fff",
                    "borderRadius": "4px",
                    "border": f"1px solid {colors['border']}",
                }
            ),
            # Gantt chart
            dcc.Graph(id="gantt-chart")
        ], style={**card_style, 'marginBottom': '25px'}),
        
        # Process timeline visualization
        html.Div([
            html.H2("Process Timeline with Waiting Times", className="card-title", style={
                'color': colors['header'],
                'marginTop': '0',
                'marginBottom': '15px',
                'fontSize': '1.5rem',
            }),
            dcc.Graph(id="process-timeline")
        ], style=card_style),
        
        # Store results for use by callbacks
        dcc.Store(id="simulation-results", data=results),
        dcc.Store(id="processes-store", data={
            "processes": [
                {
                    "pid": p.pid,
                    "arrival_time": p.arrival_time,
                    "burst_time": p.burst_time,
                    "priority": p.priority
                }
                for p in processes
            ]
        })
    ]

# Export colors and card_style for reuse
__all__ = ["get_app_layout", "colors", "card_style"]
