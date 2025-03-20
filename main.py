import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from pypfopt import expected_returns, risk_models, EfficientFrontier, DiscreteAllocation
import logging
import traceback
import requests
import plotly
from plotly.subplots import make_subplots 
from components import create_sidebar, create_main_content
from config import app, API_KEY

def create_layout():
    return dbc.Container([
        dbc.Row([
            create_sidebar(),
            create_main_content(),
        ], style={'background-color': '#282c34', 'color': 'white'}),
    ], fluid=True, style={'background-color': '#282c34', 'color': 'white', 'font-family': 'Roboto, sans-serif'})


@app.callback(
    [
        Output('pie-chart', 'figure'),
        Output('performance-chart', 'figure'),
        Output('weight-allocation', 'figure'),
        Output('cumulative-return', 'figure'),
        Output('portfolio-growth', 'figure'),
        Output('performance-table', 'data'),
        Output('monthly-returns', 'figure'),
        Output('annual-returns', 'figure'),
    ],
    [
        Input('submit-button', 'n_clicks')
    ],
    [
        State('stocks', 'value'),
        State('start_date', 'value'),
        State('end_date', 'value'),
        State('investment', 'value'),
        State('min_weight', 'value'),
        State('max_weight', 'value'),
        State('risk_aversion', 'value'),
        State('benchmark', 'value')
    ],
    prevent_initial_call=True
)
def update_output(n_clicks, stocks, start_date, end_date, investment, min_weight, max_weight, risk_aversion, benchmark):
    """Updates all graphs and tables based on user input."""
    if n_clicks > 0:
        try:
            tickers = [stock.strip().upper() for stock in stocks.split(',')]
            data = fetch_polygon_data(tickers, start_date, end_date)
            
            data.index = pd.to_datetime(data.index)

            benchmark_data = fetch_polygon_data([benchmark], start_date, end_date)
            benchmark_data.index = pd.to_datetime(benchmark_data.index)
            benchmark_data = fetch_polygon_data([benchmark], start_date, end_date)
            print("Benchmark Data:", benchmark_data)  # DEBUG


            benchmark_returns = benchmark_data.pct_change().dropna()
            cumulative_benchmark_returns = (1 + benchmark_returns).cumprod() - 1

            mu = expected_returns.mean_historical_return(data)
            S = risk_models.sample_cov(data)
            ef = EfficientFrontier(mu, S)
            ef.add_constraint(lambda x: x >= min_weight)
            ef.add_constraint(lambda x: x <= max_weight)

            if risk_aversion == 'low':
                weights = ef.max_quadratic_utility(risk_aversion=0.1)
            elif risk_aversion == 'high':
                weights = ef.max_quadratic_utility(risk_aversion=10)
            else:
                weights = ef.max_sharpe()

            cleaned_weights = ef.clean_weights()

            pie_chart = create_pie_chart(cleaned_weights)
            performance_chart = create_performance_chart(ef)
            weight_allocation_chart = create_weight_allocation_chart(data, cleaned_weights, investment)
            cumulative_return_chart = create_cumulative_return_chart(data, tickers)
            portfolio_growth_chart = create_portfolio_growth_chart(data, cleaned_weights, cumulative_benchmark_returns, benchmark)
            performance_table_data = create_performance_table_data(ef, data, cleaned_weights)
            monthly_returns_chart = create_monthly_returns_chart(data, cleaned_weights)
            annual_returns_chart = create_annual_returns_chart(data, cleaned_weights)

            return [pie_chart, performance_chart, weight_allocation_chart, cumulative_return_chart, portfolio_growth_chart, performance_table_data, monthly_returns_chart, annual_returns_chart]

        except Exception as e:
            logging.error(f"Exception in processing portfolio optimization: {str(e)}")
            logging.error(traceback.format_exc())
            return [go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), [], go.Figure(), go.Figure()]
    return [go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), [], go.Figure(), go.Figure()]
    

def fetch_polygon_data(tickers, start_date, end_date):
    base_url = "https://api.polygon.io/v2/aggs/ticker"
    headers = {'Authorization': f'Bearer {API_KEY}'}
    all_data = {}
    
    for ticker in tickers:
        full_url = f"{base_url}/{ticker}/range/1/day/{start_date}/{end_date}"
        response = requests.get(full_url, headers=headers)
        if response.status_code == 200:
            try:
                results = response.json()['results']
                dates = [result['t'] for result in results] 
                prices = [result['c'] for result in results]  
                df = pd.DataFrame(data=prices, index=pd.to_datetime(dates, unit='ms'), columns=[ticker])
                all_data[ticker] = df
            except KeyError:
                logging.error(f"No data found for {ticker}")
        else:
            logging.error(f"Failed to fetch data for {ticker}: {response.text}")
    
    combined_data = pd.concat(all_data.values(), axis=1)
    combined_data.index = pd.to_datetime(combined_data.index)
    return combined_data


def create_pie_chart(cleaned_weights):
    """Creates the portfolio weights pie chart."""
    return go.Figure(data=[go.Pie(labels=list(cleaned_weights.keys()), values=list(cleaned_weights.values()), title="Portfolio Weights", marker=dict(colors=plotly.colors.qualitative.Plotly))]).update_layout(plot_bgcolor='#282c34', paper_bgcolor='#282c34', font_color='white', font_family='Roboto, sans-serif')

def create_performance_chart(ef):
    """Creates the portfolio performance bar chart."""
    performance_data = ef.portfolio_performance(verbose=False)
    return go.Figure(data=[go.Bar(x=['Expected Annual Return', 'Annual Volatility', 'Sharpe Ratio'], y=list(performance_data), marker=dict(color=['#007bff', '#28a745', '#dc3545']))]).update_layout(plot_bgcolor='#282c34', paper_bgcolor='#282c34', font_color='white', font_family='Roboto, sans-serif')

def create_weight_allocation_chart(data, cleaned_weights, investment):
    """Creates the discrete allocation bar chart."""
    latest_prices = data.iloc[-1]
    da = DiscreteAllocation(cleaned_weights, latest_prices, total_portfolio_value=investment)
    allocation, leftover = da.greedy_portfolio()
    return go.Figure(data=[go.Bar(x=list(allocation.keys()), y=list(allocation.values()), name='Shares', marker=dict(color='#ffc107'))]).update_layout(plot_bgcolor='#282c34', paper_bgcolor='#282c34', font_color='white', font_family='Roboto, sans-serif')

def create_cumulative_return_chart(data):
    """Creates the cumulative returns chart."""
    data.index = pd.to_datetime(data.index)
    cumulative_returns = (1 + data.pct_change()).cumprod() - 1
    
    fig = go.Figure()
    for ticker in data.columns:
        fig.add_trace(go.Scatter(x=cumulative_returns.index, y=cumulative_returns[ticker], mode='lines', name=ticker))
    
    fig.update_layout(
        plot_bgcolor='#282c34',
        paper_bgcolor='#282c34',
        font_color='white',
        font_family='Roboto, sans-serif',
        title="Cumulative Returns"
    )
    return fig

def create_cumulative_return_chart(data, tickers):
    """Creates the cumulative returns line chart."""
    cumulative_returns = (1 + data.pct_change()).cumprod() - 1
    fig = go.Figure()
    for ticker in tickers:
        fig.add_trace(go.Scatter(x=cumulative_returns.index, y=cumulative_returns[ticker], mode='lines', name=ticker))
    return fig.update_layout(plot_bgcolor='#282c34', paper_bgcolor='#282c34', font_color='white', font_family='Roboto, sans-serif')


def create_portfolio_growth_chart(data, cleaned_weights, benchmark_data, benchmark_name):
    """Creates the portfolio growth chart with two subplots, resampling data within each subplot."""
    portfolio_returns = data.pct_change().dot(pd.Series(cleaned_weights))
    benchmark_returns = benchmark_data[benchmark_name].pct_change()

    
    combined_returns = pd.concat([portfolio_returns, benchmark_returns], axis=1)
    combined_returns.columns = ['Portfolio', 'Benchmark']
    combined_returns = combined_returns.dropna()  

    
    start_date = max(combined_returns.index.min(), combined_returns.index.min()) 
    end_date = min(combined_returns.index.max(), combined_returns.index.max())  


    combined_returns = combined_returns[(combined_returns.index >= start_date) & (combined_returns.index <= end_date)]

    monthly_returns = combined_returns.resample('M').last()

    
    portfolio_cumulative = (1 + monthly_returns['Portfolio']).cumprod() - 1
    benchmark_cumulative = (1 + monthly_returns['Benchmark']).cumprod() - 1

   
    tick_dates = pd.date_range(start=portfolio_cumulative.index.min(), end=portfolio_cumulative.index.max(), freq='MS')

   
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)

    fig.add_trace(go.Scatter(x=portfolio_cumulative.index, y=portfolio_cumulative, mode='lines', name='Portfolio'), row=1, col=1)
    fig.update_yaxes(title_text='Portfolio Cumulative Returns', row=1, col=1)

    fig.add_trace(go.Scatter(x=benchmark_cumulative.index, y=benchmark_cumulative, mode='lines', name=benchmark_name), row=2, col=1)
    fig.update_yaxes(title_text='Benchmark Cumulative Returns', row=2, col=1)

    fig.update_layout(
        plot_bgcolor='#282c34',
        paper_bgcolor='#282c34',
        font_color='white',
        font_family='Roboto, sans-serif',
        title="Portfolio vs. Benchmark Growth",
        xaxis_tickvals=tick_dates,
        xaxis_ticktext=[date.strftime('%Y-%m-%d') for date in tick_dates],
        xaxis_tickangle=-45
    )
    return fig

def create_performance_table_data(ef, data, cleaned_weights):
    """Creates the performance summary table data."""
    performance_data = ef.portfolio_performance(verbose=False)
    portfolio_returns = data.pct_change().dropna()
    weighted_returns = (portfolio_returns * pd.Series(cleaned_weights)).sum(axis=1)
    portfolio_cumulative_returns = (1 + weighted_returns).cumprod() - 1

    return [
        {'Metric': 'Expected Annual Return', 'Value': f'{performance_data[0]:.2%}'},
        {'Metric': 'Annual Volatility', 'Value': f'{performance_data[1]:.2%}'},
        {'Metric': 'Sharpe Ratio', 'Value': f'{performance_data[2]:2f}'},
        {'Metric': 'Total Return', 'Value': f'{portfolio_cumulative_returns.iloc[-1]:.2%}'}
    ]

def create_monthly_returns_chart(data, cleaned_weights):
    """Creates the monthly returns bar chart."""
    portfolio_returns = (data.pct_change().dot(pd.Series(cleaned_weights))).resample('M').apply(lambda x: (1 + x).prod() - 1)
    return go.Figure(data=[go.Bar(x=portfolio_returns.index, y=portfolio_returns, name='Monthly Returns', marker=dict(color='#17BECF'))]).update_layout(plot_bgcolor='#282c34', paper_bgcolor='#282c34', font_color='white', font_family='Roboto, sans-serif')

def create_annual_returns_chart(data, cleaned_weights):
    """Creates the annual returns bar chart."""
    portfolio_returns = (data.pct_change().dot(pd.Series(cleaned_weights))).resample('A').apply(lambda x: (1 + x).prod() - 1)
    return go.Figure(data=[go.Bar(x=portfolio_returns.index, y=portfolio_returns, name='Annual Returns', marker=dict(color='#1F77B4'))]).update_layout(plot_bgcolor='#282c34', paper_bgcolor='#282c34', font_color='white', font_family='Roboto, sans-serif')

