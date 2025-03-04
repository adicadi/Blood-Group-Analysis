import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# Load dataset
df = pd.read_csv("Data/processed_blood_type_data_with_continent.csv")

# Blood type columns
blood_groups = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Navbar with Dropdowns Integrated
navbar = dbc.Navbar(
    dbc.Container([
        html.H2("🩸 Blood Type Dashboard", className="text-white mb-0 fw-bold"),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='blood-type-dropdown',
                    options=[{'label': bt, 'value': bt} for bt in blood_groups],
                    value='O+',
                    clearable=False,
                    style={
                        "width": "250px",
                        "border-radius": "8px",
                        "font-size": "14px",
                        "padding": "3px",
                    }
                )
            ], width="auto", className="mx-2"),
            dbc.Col([
                dcc.Dropdown(
                    id='continent-dropdown',
                    options=[{'label': c, 'value': c} for c in df["Continent"].unique()],
                    value=df["Continent"].unique()[0],
                    clearable=False,
                    style={
                        "width": "250px",
                        "border-radius": "8px",
                        "font-size": "14px",
                        "padding": "3px",
                    }
                )
            ], width="auto", className="mx-2"),
        ], align="center")
    ], fluid=True),
    color="dark",
    style={"background": "linear-gradient(to right, #2193b0, #6dd5ed)", "padding": "10px"}
)

# App Layout with Bigger Charts
app.layout = dbc.Container([
    navbar,

    # Bigger Charts (Freed Up Space)
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Choropleth Map", className="bg-primary text-white"),
            dbc.CardBody(dcc.Graph(id='choropleth-map', style={"height": "350px"}))
        ]), width=6),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Pie Chart", className="bg-primary text-white"),
            dbc.CardBody(dcc.Graph(id='pie-chart', style={"height": "350px"}))
        ]), width=6),
    ]),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Bar Chart", className="bg-primary text-white"),
            dbc.CardBody(dcc.Graph(id='bar-chart', style={"height": "350px"}))
        ]), width=6),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Gauge Chart", className="bg-primary text-white"),
            dbc.CardBody(dcc.Graph(id='gauge-chart', style={"height": "350px"}))
        ]), width=6),
    ]),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Blood Group Data", className="bg-primary text-white"),
            dbc.CardBody(dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                fixed_rows={'headers': True},
                style_table={'overflowX': 'auto', 'maxHeight': '250px', 'overflowY': 'scroll'},
                page_size=5
            ))
        ]), width=12)
    ])
], fluid=True,style={
    "background": "linear-gradient(to right, #E3FDFD, #CBF1F5, #A6E3E9)", 
    "padding": "20px",
    "min-height": "100vh"
})

# Callback to update graphs
@app.callback(
    [
        Output('choropleth-map', 'figure'),
        Output('bar-chart', 'figure'),
        Output('gauge-chart', 'figure'),
        Output('pie-chart', 'figure')
    ],
    [
        Input('blood-type-dropdown', 'value'),
        Input('continent-dropdown', 'value')
    ]
)
def update_all_charts(selected_blood_type, selected_continent):
    df_continent = df[df["Continent"] == selected_continent]

    # Choropleth Map
    fig_map = px.choropleth(
        df_continent,
        locations="Country",
        locationmode="country names",
        color=selected_blood_type,
        hover_data=blood_groups,
        title=f"Global Distribution of {selected_blood_type} in {selected_continent}",
        color_continuous_scale="plasma"
    )

    # Bar Chart
    fig_bar = px.bar(
        df_continent,
        x="Country",
        y=selected_blood_type,
        title=f"{selected_blood_type} Distribution in {selected_continent}",
        opacity=0.9
    )
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        height=350
    )

    # Gauge Chart
    rarest_blood = df_continent[blood_groups].mean().idxmin()
    rarest_percentage = df_continent[rarest_blood].mean()
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rarest_percentage,
        title={"text": f"Rarest Blood Type in {selected_continent}: {rarest_blood}"},
        gauge={"axis": {"range": [0, 10]}, "bar": {"color": "red"}}
    ))
    fig_gauge.update_layout(height=350)

    # Pie Chart
    pie_data = df_continent[blood_groups].mean().reset_index().rename(columns={'index': 'BloodType', 0: 'MeanValue'})
    fig_pie = px.pie(
        pie_data,
        values='MeanValue',
        names='BloodType',
        title=f"Blood Type Distribution in {selected_continent}"
    )

    return fig_map, fig_bar, fig_gauge, fig_pie

# Run App
if __name__ == '__main__':
    app.run_server(debug=True)
