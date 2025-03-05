import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from utils import BLOOD_GROUPS, CONTINENTS


# Card Style with Static Shadows (No Hover or 3D Effect)
# Card Style with Light/Dark Mode Support
CARD_STYLE_LIGHT = {
    "box-shadow": "0 8px 16px rgba(0, 0, 0, 0.2)",
    "border-radius": "12px",
    "background-color": "#ffffff",
    "overflow": "hidden",
    "padding": "10px",
    "transition": "all 0.3s ease-in-out",
}

CARD_STYLE_DARK = {
    "box-shadow": "0 8px 16px rgba(255, 255, 255, 0.1)",
    "border-radius": "12px",
    "background-color": "#1e1e1e",
    "overflow": "hidden",
    "padding": "10px",
    "transition": "all 0.3s ease-in-out",
    "color": "#ffffff"
}

# Light and Dark Mode Container Styles
LIGHT_MODE_STYLE = {
    "background-color": "#E3FDFD", 
    "padding": "20px", 
    "min-height": "100vh"
}

DARK_MODE_STYLE = {
    "background-color": "#121212", 
    "padding": "20px", 
    "min-height": "100vh",
    "color": "#ffffff"
}

# Light and Dark Mode Styles for DataTable
DATATABLE_STYLE_LIGHT = {
    "backgroundColor": "#ffffff",
    "color": "#000000",
    "border": "1px solid #ddd",
}

DATATABLE_STYLE_DARK = {
    "backgroundColor": "#1e1e1e",
    "color": "#ffffff",
    "border": "1px solid #444",
}

TOGGLE_LABEL_LIGHT = {"color": "#000000"}  # Black text for light mode
TOGGLE_LABEL_DARK = {"color": "#ffffff"}  # White text for dark mode





def create_layout():
    sidebar = dbc.Offcanvas(
        [
            html.H4("Filters", className="text-white mb-3"),
            html.Div([
                html.Label("Blood Types", className="text-white"),
                dcc.Dropdown(
                    id='blood-types-multi',
                    options=[{'label': bt, 'value': bt} for bt in BLOOD_GROUPS],
                    value=['O+'],
                    multi=True,
                    clearable=False,
                    style={"width": "100%", "border-radius": "8px", "font-size": "12px", "padding": "3px"}
                ),
            ], style={"margin-bottom": "10px"}),
            html.Div([
                html.Label("Continent", className="text-white"),
                dcc.Dropdown(
                    id='continent-dropdown',
                    options=[{'label': c, 'value': c} for c in CONTINENTS],
                    value='Europe',
                    clearable=False,
                    style={"width": "100%", "border-radius": "8px", "font-size": "12px", "padding": "3px"}
                ),
            ], style={"margin-bottom": "10px"}),
            html.Label("Population Range", className="text-white mt-3"),
            dcc.Slider(
                id='population-slider',
                min=350734,
                max=1397897720,
                value=1397897720,
                marks={int(x): f'{int(x/1e6)}M' for x in [350734, 1e7, 5e7, 1e8, 1e9]},
                step=1000000
            ),
            dbc.Button([html.I(className="fas fa-sync-alt mr-2"), "Reset"], id="reset-filters", color="primary", className="mt-3 w-100"),
            dbc.Button([html.I(className="fas fa-download mr-2"), "Data"], id="btn-download", color="primary", className="mt-2 w-100"),
            dcc.Download(id="download-data"),
            dbc.Button([html.I(className="fas fa-camera mr-2"), "Charts"], id="btn-download-charts", color="primary", className="mt-2 w-100"),
            dcc.Download(id="download-charts"),
            dbc.Button([html.I(className="fas fa-info-circle mr-2"), "Info"], id="open-info", color="secondary", className="mt-2 w-100"),
            html.Div(id="loading-message", style={"margin-top": "10px", "color": "#fff", "font-size": "12px"})
        ],
        id="sidebar",
        title="Filters",
        is_open=False,
        style={"background-color": "#2193b0", "padding": "15px", "width": "250px"},
        close_button=True
    )

    info_modal = dbc.Modal(
        [
            dbc.ModalHeader("Blood Type Information"),
            dbc.ModalBody([
                html.P("O+ is the most common blood type and can donate to O+, A+, B+, and AB+."),
                html.P("AB- is rare and can only receive from AB-."),
                html.P("Data source: Kaggle (placeholder)"),
            ]),
            dbc.ModalFooter(dbc.Button("Close", id="close-info", className="ml-auto"))
        ],
        id="info-modal",
        size="lg"
    )

    main_content = dbc.Container([
        dbc.Row([
            # Dynamically show/hide toggle button based on sidebar state (handled in callbacks)
            dbc.Col([ dbc.Row([
    dbc.Col(
        dbc.Button("☰", id="toggle-sidebar", color="primary", 
                  className="mb-3 d-none d-md-block d-flex align-items-center justify-content-center sidebar-toggle", 
                  style={"width": "50px", "height": "50px"}),
        width="auto"
    ),
    dbc.Col(
        html.H2("🩸 Blood Group Dashboard", className="text-primary mb-4", 
               style={"font-weight": "bold", "margin-left": "10px"}),
        width=True
    ),
    dbc.Col(
        dbc.Switch(
            id="dark-mode-toggle",
            label="Dark Mode",
            value=False,
            className="mt-2",
            style={"color": "#000000","font-weight": "bold"}  # Default color for light mode
        ),
        width="auto"
    )
], align="center", justify="start"),

                dbc.Row([
                    dbc.Col(dcc.Loading(dbc.Card(dcc.Graph(id='choropleth-map', style={"height": "300px"}), id='card-1',style=CARD_STYLE_LIGHT, className="card")), md=4, sm=12, className="mb-3"),
                    dbc.Col(dcc.Loading(dbc.Card(dcc.Graph(id='pie-chart', style={"height": "300px"}), id='card-2',style=CARD_STYLE_LIGHT, className="card")), md=4, sm=12, className="mb-3"),
                    dbc.Col(dcc.Loading(dbc.Card(dcc.Graph(id='bar-chart', style={"height": "300px"}), id='card-3',style=CARD_STYLE_LIGHT, className="card")), md=4, sm=12, className="mb-3"),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Loading(dbc.Card(dcc.Graph(id='gauge-chart', style={"height": "300px"}), id='card-4',style=CARD_STYLE_LIGHT, className="card")), md=4, sm=12, className="mb-3"),
                    dbc.Col(dcc.Loading(dbc.Card(dcc.Graph(id='scatter-plot', style={"height": "300px"}), id='card-5', style=CARD_STYLE_LIGHT, className="card")), md=4, sm=12, className="mb-3"),
                    dbc.Col(dcc.Loading(dbc.Card(dcc.Graph(id='heatmap', style={"height": "300px"}), id='card-6',style=CARD_STYLE_LIGHT, className="card")), md=4, sm=12, className="mb-3"),
                ]),
                dbc.Row([
                    dbc.Col(
    dcc.Loading(
        dbc.Card(
            dash_table.DataTable(
                id="data-table",
                columns=[
                    {"name": i, "id": i}
                    for i in ["Country", "Population"] + BLOOD_GROUPS + ["Continent", "Rarest_Blood_Type", "Diversity_Index", "Can_Donate_To"]
                ],
                data=[],
                fixed_rows={"headers": True},
                style_header={"backgroundColor": "#f8f9fa", 
                        "color": "#000000",         
                        "fontWeight": "bold",
                        "textAlign": "center",},
                style_table={"overflowX": "auto", "maxHeight": "300px", "overflowY": "scroll"},
                page_size=5,
                style_cell={"minWidth": "100px", "textAlign": "left"},  # Default cell style
            ),
            id="data-table-card",
            style={**CARD_STYLE_LIGHT, "max-width": "100%", "margin": "0 auto"},
            className="card mt-3",
        )
    ),
    width=12,
),


                ]),
                html.Footer(
                    [
                        html.Span("© 2025 Blood Type Dashboard | Data from Kaggle"),
                        html.Br(),
                        html.A("Privacy Policy", href="#", style={"color": "#666"}),
                    ],
                    className="text-center mt-auto py-3",
                    style={
                        "color": "#666",
                        "background-color": "#f8f9fa",
                        "position": "relative",
        
                    }
                )
            ], width=12, className="p-3")  # Added padding for content
        ]),
        sidebar,
        info_modal
    ], fluid=True, style={**LIGHT_MODE_STYLE, "background-color": "#E3FDFD", "padding": "20px", "min-height": "100vh"}, id="main-container")  # Full-width layout

    return main_content

layout = create_layout()