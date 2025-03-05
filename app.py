import dash
import dash_bootstrap_components as dbc
from layout import layout
from callbacks import register_callbacks

# Initialize Dash app with both Flatly (light) and Darkly (dark) themes
app = dash.Dash(    
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,  # Light theme
        dbc.themes.DARKLY,  # Dark theme
        "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
    ]
)

app.layout = layout
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
