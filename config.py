
import dash
import dash_bootstrap_components as dbc
import os
from dotenv import load_dotenv

load_dotenv()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.config.suppress_callback_exceptions = True

API_KEY = os.environ.get('POLYGON_API_KEY')
if not API_KEY:
    raise ValueError("POLYGON_API_KEY environment variable not set.")