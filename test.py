import dash
import dash_bootstrap_components as dbc
from layout import layout
from callbacks import register_callbacks

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, "https://use.fontawesome.com/releases/v5.15.4/css/all.css"])

# Set layout
app.layout = layout

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)