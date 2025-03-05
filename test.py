import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from layout import layout
from callbacks import register_callbacks

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Set layout
app.layout = layout

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)