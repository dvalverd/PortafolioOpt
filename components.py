
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html, dcc,dash_table


def create_main_content():
    """Creates the main content area with graphs and tables."""
    return dbc.Col([
        dbc.Row([create_pie_chart_col(), create_performance_chart_col()], style={'margin-bottom': '10px'}),
        dbc.Row([create_cumulative_return_col(), create_weight_allocation_col()]),
        dbc.Row([create_portfolio_growth_col(), create_performance_table_col()]),
        dbc.Row([create_monthly_returns_col(), create_annual_returns_col()])
    ], width=9, style={'padding': '10px'})


def create_sidebar():
    """Creates the sidebar of the app with input controls."""
    return dbc.Col([
        html.Div([
            html.H3("Portfolio Optimization", style={'color': 'white', 'font-family': 'Roboto, sans-serif', 'text-align': 'center'}),
            html.Hr(style={'background-color': 'white'}),
            html.Div([html.I(className="fas fa-list-ul", style={'margin-right': '10px'}), html.Label("Stocks (comma-separated):", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
            dcc.Input(id='stocks', type='text', placeholder='Enter stock tickers (e.g., AAPL, MSFT)', style={'width': '100%', 'margin-bottom': '10px'}),
            html.Div([html.I(className="fas fa-calendar-alt", style={'margin-right': '10px'}), html.Label("Start Date (YYYY-MM-DD):", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
            dcc.Input(id='start_date', type='text', placeholder='Start Date (YYYY-MM-DD)', style={'width': '100%', 'margin-bottom': '10px'}),
            html.Div([html.I(className="fas fa-calendar-alt", style={'margin-right': '10px'}), html.Label("End Date (YYYY-MM-DD):", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
            dcc.Input(id='end_date', type='text', placeholder='End Date (YYYY-MM-DD)', style={'width': '100%', 'margin-bottom': '10px'}),
            html.Div([html.I(className="fas fa-dollar-sign", style={'margin-right': '10px'}), html.Label("Investment Amount ($):", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
            dcc.Input(id='investment', type='number', placeholder='Investment Amount ($)', style={'width': '100%', 'margin-bottom': '10px'}),
            html.Div([html.I(className="fas fa-balance-scale", style={'margin-right': '10px'}), html.Label("Min Weight:", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
            dcc.Input(id='min_weight', type='number', placeholder='Min Weight (e.g., 0.1)', style={'width': '100%', 'margin-bottom': '10px'}),
            html.Div([html.I(className="fas fa-balance-scale", style={'margin-right': '10px'}), html.Label("Max Weight:", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
            dcc.Input(id='max_weight', type='number', placeholder='Max Weight (e.g., 0.5)', style={'width': '100%', 'margin-bottom': '10px'}),
            html.Div([html.I(className="fas fa-exclamation-triangle", style={'margin-right': '10px'}), html.Label("Risk Aversion:", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
            dcc.Dropdown(id='risk_aversion', options=[{'label': 'Low', 'value': 'low'}, {'label': 'Medium', 'value': 'medium'}, {'label': 'High', 'value': 'high'}], value='medium', style={'width': '100%', 'margin-bottom': '10px'}),
            html.Div([html.I(className="fas fa-chart-line", style={'margin-right': '10px'}), html.Label("Benchmark Index (e.g., SPY):", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
            dcc.Input(id='benchmark', type='text', placeholder='Benchmark Index (e.g., SPY)', style={'width': '100%', 'margin-bottom': '10px'}),
            html.Button('Optimize', id='submit-button', n_clicks=0, style={'width': '100%', 'background-color': '#007bff', 'color': 'white', 'border': 'none', 'padding': '10px'}),
            html.Hr(style={'background-color': 'white'}),
            html.P('"An investment in knowledge pays the best interest." - Benjamin Franklin', style={'color': 'white', 'font-family': 'Roboto, sans-serif', 'font-size': '14px', 'text-align': 'center', 'margin-top': '20px'}),
        ], style={'background-color': '#343a40', 'padding': '20px', 'border-radius': '10px', 'color': 'white'}),
    ], width=3, style={'padding': '20px'})

def create_pie_chart_col():
    return dbc.Col([
        html.Div([html.I(className="fas fa-chart-pie", style={'margin-right': '10px'}), html.H5("Portfolio Weights", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
        dcc.Graph(id='pie-chart', style={'background-color': '#282c34', 'color': 'white', 'border-radius': '10px'})
    ], width=6)

def create_performance_chart_col():
    return dbc.Col([
        html.Div([html.I(className="fas fa-chart-bar", style={'margin-right': '10px'}), html.H5("Portfolio Performance", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
        dcc.Graph(id='performance-chart', style={'background-color': '#282c34', 'color': 'white', 'border-radius': '10px'})
    ], width=6)

def create_cumulative_return_col():
    return dbc.Col([
        html.Div([html.I(className="fas fa-chart-line", style={'margin-right': '10px'}), html.H5("Cumulative Returns", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
        dcc.Graph(id='cumulative-return', style={'background-color': '#282c34', 'color': 'white', 'border-radius': '10px'})
    ], width=6)

def create_weight_allocation_col():
    return dbc.Col([
        html.Div([html.I(className="fas fa-table", style={'margin-right': '10px'}), html.H5("Discrete Allocation", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
        dcc.Graph(id='weight-allocation', style={'background-color': '#282c34', 'color': 'white', 'border-radius': '10px'})
    ], width=6)

def create_portfolio_growth_col():
    return dbc.Col([
        html.Div([html.I(className="fas fa-chart-line", style={'margin-right': '10px'}), html.H5("Portfolio Growth", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
        dcc.Graph(id='portfolio-growth', style={'background-color': '#282c34', 'color': 'white', 'border-radius': '10px'})
    ], width=6)

def create_performance_table_col():
    return dbc.Col([
        html.Div([html.I(className="fas fa-table", style={'margin-right': '10px'}), html.H5("Performance Summary", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
        dash_table.DataTable(
            id='performance-table',
            columns=[{"name": i, "id": i} for i in ['Metric', 'Value']],
            style_cell={'backgroundColor': '#282c34', 'color': 'white', 'textAlign': 'left'},
            style_header={'backgroundColor': '#343a40', 'color': 'white', 'fontWeight': 'bold'},
            style_table={'overflowX': 'auto'}
        )
    ], width=6)

def create_monthly_returns_col():
    return dbc.Col([
        html.Div([html.I(className="fas fa-calendar", style={'margin-right': '10px'}), html.H5("Monthly Returns", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
        dcc.Graph(id='monthly-returns', style={'background-color': '#282c34', 'color': 'white', 'border-radius': '10px'})
    ], width=6)

def create_annual_returns_col():
    return dbc.Col([
        html.Div([html.I(className="fas fa-calendar", style={'margin-right': '10px'}), html.H5("Annual Returns", style={'color': 'white', 'font-family': 'Roboto, sans-serif'})], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),
        dcc.Graph(id='annual-returns', style={'background-color': '#282c34', 'color': 'white', 'border-radius': '10px'})
    ], width=6)