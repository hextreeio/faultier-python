import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3
import dash_bootstrap_components as dbc
import numpy as np
import sys
import os

# Global variable to store the database name
DATABASE_NAME = None

def get_database_name():
    """Get database name from command line arguments or use default"""
    if len(sys.argv) > 1:
        db_name = sys.argv[1]
        if not db_name.endswith('.db'):
            db_name += '.db'
        return db_name
    else:
        print("Usage: python3 app.py <database_name>")
        print("Example: python3 app.py measurements.db")
        sys.exit(1)

def set_database_name(db_name):
    """Set the database name programmatically"""
    global DATABASE_NAME
    if not db_name.endswith('.db'):
        db_name += '.db'
    DATABASE_NAME = db_name

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def load_data():
    """Load data from the SQLite database"""
    global DATABASE_NAME
    if DATABASE_NAME is None:
        print("Error: No database name set. Use set_database_name() or run as script with argument.")
        return pd.DataFrame(columns=['id', 'identifier', 'pulse', 'delay', 'freetext_result'])
    
    try:
        if not os.path.exists(DATABASE_NAME):
            print(f"Warning: Database file '{DATABASE_NAME}' does not exist.")
            return pd.DataFrame(columns=['id', 'identifier', 'pulse', 'delay', 'freetext_result'])
        
        conn = sqlite3.connect(DATABASE_NAME)
        df = pd.read_sql_query("SELECT * FROM measurements", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading data from '{DATABASE_NAME}': {e}")
        # Return empty dataframe with expected columns for development
        return pd.DataFrame(columns=['id', 'identifier', 'pulse', 'delay', 'freetext_result'])

def get_unique_values(df):
    """Get unique identifiers and results for filter options"""
    identifiers = sorted(df['identifier'].unique()) if not df.empty else []
    results = sorted(df['freetext_result'].unique()) if not df.empty else []
    return identifiers, results

def create_layout():
    """Create the app layout dynamically"""
    global DATABASE_NAME
    db_display = DATABASE_NAME if DATABASE_NAME else "No database set"
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                # html.H1("Voltage Fault-Injection Testing Results", className="text-center mb-4"),
                html.P(f"Database: {db_display}", className="text-center text-muted mb-3"),
                html.Hr()
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Filters"),
                    dbc.CardBody([
                        html.Label("Select Identifiers/Runs:", className="fw-bold"),
                        dcc.Checklist(
                            id='identifier-checklist',
                            options=[],
                            value=[],
                            className="mb-3"
                        ),
                        
                        html.Label("Select Result Categories:", className="fw-bold"),
                        dcc.Checklist(
                            id='result-checklist',
                            options=[],
                            value=[],
                            className="mb-3"
                        ),
                        
                        dbc.Button("Refresh Data", id="refresh-button", color="primary", className="w-100")
                    ])
                ])
            ], width=3),
            
            dbc.Col([
                dcc.Graph(id='scatter-plot')
            ], width=9)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='pulse-histogram')
            ], width=6),
            dbc.Col([
                dcc.Graph(id='delay-histogram')
            ], width=6)
        ])
    ], fluid=True)

# Load initial data and set layout
# df = load_data()
# identifiers, results = get_unique_values(df)
app.layout = create_layout()

@app.callback(
    [Output('identifier-checklist', 'options'),
     Output('identifier-checklist', 'value'),
     Output('result-checklist', 'options'),
     Output('result-checklist', 'value')],
    [Input('refresh-button', 'n_clicks')],
    [State('identifier-checklist', 'value'),
     State('result-checklist', 'value')]
)
def refresh_data(n_clicks, current_identifiers, current_results):
    """Refresh data from database and update filter options while preserving current selections"""
    df = load_data()
    identifiers, results = get_unique_values(df)
    
    identifier_options = [{'label': identifier, 'value': identifier} for identifier in identifiers]
    result_options = [{'label': result, 'value': result} for result in results]
    
    # Preserve current selections if they still exist in the new data
    # If no current selection or first load, select all
    if current_identifiers is None:
        preserved_identifiers = identifiers
    else:
        preserved_identifiers = [id for id in current_identifiers if id in identifiers]
    
    if current_results is None:
        preserved_results = results
    else:
        preserved_results = [result for result in current_results if result in results]
    
    return identifier_options, preserved_identifiers, result_options, preserved_results

@app.callback(
    [Output('scatter-plot', 'figure'),
     Output('pulse-histogram', 'figure'),
     Output('delay-histogram', 'figure')],
    [Input('identifier-checklist', 'value'),
     Input('result-checklist', 'value')]
)
def update_plots(selected_identifiers, selected_results):
    """Update all plots based on selected filters"""
    df = load_data()
    
    if df.empty:
        # Create empty plots if no data
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No data available. Please ensure measurements.db exists and contains data.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        return empty_fig, empty_fig, empty_fig
    
    # Filter data based on selections
    if selected_identifiers:
        df = df[df['identifier'].isin(selected_identifiers)]
    if selected_results:
        df = df[df['freetext_result'].isin(selected_results)]
    
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No data matches the current filters.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        return empty_fig, empty_fig, empty_fig
    
    # Create scatter plot
    scatter_fig = px.scatter(
        df, 
        x='delay', 
        y='pulse',
        color='freetext_result',
        symbol='identifier',
        title='Pulse vs Delay',
        labels={'delay': 'Delay', 'pulse': 'Pulse', 'freetext_result': 'Result'},
        hover_data=['identifier', 'id']
    )
    
    scatter_fig.update_layout(
        xaxis_title="Delay",
        yaxis_title="Pulse",
        legend_title="Result Categories",
        height=500
    )
    
    # Create pulse histogram
    pulse_fig = go.Figure()
    
    for result in df['freetext_result'].unique():
        result_data = df[df['freetext_result'] == result]
        pulse_fig.add_trace(go.Histogram(
            x=result_data['pulse'],
            name=result,
            opacity=0.7,
            nbinsx=20
        ))
    
    pulse_fig.update_layout(
        title='Pulse Distribution by Result Category',
        xaxis_title='Pulse',
        yaxis_title='Count',
        barmode='overlay',
        height=400
    )
    
    # Create delay histogram
    delay_fig = go.Figure()
    
    for result in df['freetext_result'].unique():
        result_data = df[df['freetext_result'] == result]
        delay_fig.add_trace(go.Histogram(
            x=result_data['delay'],
            name=result,
            opacity=0.7,
            nbinsx=20
        ))
    
    delay_fig.update_layout(
        title='Delay Distribution by Result Category',
        xaxis_title='Delay',
        yaxis_title='Count',
        barmode='overlay',
        height=400
    )
    
    return scatter_fig, pulse_fig, delay_fig

def visualize(database_name, host='127.0.0.1', port=8888, debug=False):
    """
    Start the visualization server for the specified database.
    
    Args:
        database_name (str): Name of the database file
        host (str): Host to bind to (default: '127.0.0.1' for localhost only)
        port (int): Port to bind to (default: 8888)
        debug (bool): Enable debug mode (default: True)
    """
    # Set the database name
    set_database_name(database_name)
    
    # Update the layout with the new database
    app.layout = create_layout()
    
    # print(f"Starting Dash application...")
    # print(f"Database: {DATABASE_NAME}")
    # print(f"Server: http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    # Run the app
    app.run(debug=debug, host=host, port=port)

if __name__ == '__main__':
    # When run as script, get database name from command line
    DATABASE_NAME = get_database_name()
    
    print(f"Starting Dash application...")
    print(f"Database: {DATABASE_NAME}")
    print(f"Server: http://localhost:8888")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='127.0.0.1', port=8888) 