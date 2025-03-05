import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table

blood_groups = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]

def create_layout():
    sidebar = dbc.Nav(
        [
            html.H4("Filters", className="text-white"),
            dcc.Dropdown(
                id='blood-type-dropdown',
                options=[{'label': bt, 'value': bt} for bt in blood_groups],
                value='O+',
                clearable=False,
                style={"width": "100%", "border-radius": "8px", "font-size": "14px", "padding": "3px"}
            ),
            dcc.Dropdown(
                id='continent-dropdown',
                options=[{'label': c, 'value': c} for c in ["Europe", "Africa", "Asia", "South America", "North America", "Oceania", "Unknown"]],
                value='Europe',
                clearable=False,
                style={"width": "100%", "border-radius": "8px", "font-size": "14px", "padding": "3px"}
            ),
            dcc.Slider(
                id='population-slider',
                min=350734,  # Minimum population (Iceland)
                max=1397897720,  # Maximum population (China)
                value=1397897720,
                marks={int(x): f'{int(x/1e6)}M' for x in [350734, 1e7, 5e7, 1e8, 1e9]},
                step=1000000
            ),
            dcc.Dropdown(
                id='blood-types-multi',
                options=[{'label': bt, 'value': bt} for bt in blood_groups],
                value=['O+'],
                multi=True,
                clearable=False,
                style={"width": "100%", "border-radius": "8px", "font-size": "14px", "padding": "3px"}
            ),
            dbc.Button("Reset Filters", id="reset-filters", color="primary", className="mt-2"),
            dbc.Button("Download Data", id="btn-download", color="primary", className="mt-2"),
            dcc.Download(id="download-data"),
            dbc.Button("Download Charts", id="btn-download-charts", color="primary", className="mt-2"),
            dcc.Download(id="download-charts"),
            dbc.Button("Info", id="open-info", color="secondary", className="mt-2"),
            html.Div(id="loading-message", style={"margin-top": "10px", "color": "white"})
        ],
        vertical=True,
        pills=True,
        style={"background-color": "#2193b0", "padding": "10px", "width": "200px", "height": "100vh"}
    )

    info_modal = dbc.Modal(
        [
            dbc.ModalHeader("Blood Type Information"),
            dbc.ModalBody([
                html.P("O+ is the most common blood type and can donate to O+, A+, B+, and AB+."),
                html.P("AB- is rare and can only receive from AB-."),
                html.P("Data source: [Insert Source Here]"),
            ]),
            dbc.ModalFooter(dbc.Button("Close", id="close-info", className="ml-auto"))
        ],
        id="info-modal",
        size="lg"
    )

    main_content = dbc.Container([
        info_modal,
        dbc.Row([
            dbc.Col(sidebar, width=2),
            dbc.Col([
                html.H1("🩸 Blood Type Dashboard", className="text-center text-danger mb-4"),
                dbc.Row([
                    dbc.Col(dcc.Loading(dbc.Card([
                        dbc.CardHeader("Choropleth Map", className="bg-danger text-white"),
                        dbc.CardBody(dcc.Graph(id='choropleth-map', style={"height": "350px"}))
                    ], style={"box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})), md=6, sm=12),
                    dbc.Col(dcc.Loading(dbc.Card([
                        dbc.CardHeader("Pie Chart", className="bg-danger text-white"),
                        dbc.CardBody(dcc.Graph(id='pie-chart', style={"height": "350px"}))
                    ], style={"box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})), md=6, sm=12),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Loading(dbc.Card([
                        dbc.CardHeader("Bar Chart", className="bg-danger text-white"),
                        dbc.CardBody(dcc.Graph(id='bar-chart', style={"height": "350px"}))
                    ], style={"box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})), md=6, sm=12),
                    dbc.Col(dcc.Loading(dbc.Card([
                        dbc.CardHeader("Gauge Chart", className="bg-danger text-white"),
                        dbc.CardBody(dcc.Graph(id='gauge-chart', style={"height": "350px"}))
                    ], style={"box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})), md=6, sm=12),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Loading(dbc.Card([
                        dbc.CardHeader("Scatter Plot", className="bg-danger text-white"),
                        dbc.CardBody(dcc.Graph(id='scatter-plot', style={"height": "350px"}))
                    ], style={"box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})), md=6, sm=12),
                    dbc.Col(dcc.Loading(dbc.Card([
                        dbc.CardHeader("Heatmap (Correlations)", className="bg-danger text-white"),
                        dbc.CardBody(dcc.Graph(id='heatmap', style={"height": "350px"}))
                    ], style={"box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})), md=6, sm=12),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Loading(dbc.Card([
                        dbc.CardHeader("Blood Group Data", className="bg-danger text-white"),
                        dbc.CardBody(dash_table.DataTable(
                            id='data-table',
                            columns=[{"name": i, "id": i} for i in ["Country", "Population", "O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-", "Continent", "Rarest_Blood_Type", "Diversity_Index", "Can_Donate_To"]],
                            data=[],
                            fixed_rows={'headers': True},
                            style_table={'overflowX': 'auto', 'maxHeight': '250px', 'overflowY': 'scroll'},
                            page_size=5
                        ))
                    ], style={"box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})), width=12)
                ]),
                html.Footer("© 2025 Blood Type Dashboard | Data from [Your Source]", className="text-center mt-4", style={"color": "#666"})
            ], width=10)
        ])
    ], fluid=True, style={
        "background": "linear-gradient(to right, #E3FDFD, #CBF1F5, #A6E3E9)",
        "padding": "20px",
        "min-height": "100vh"
    })

    return main_content

layout = create_layout()