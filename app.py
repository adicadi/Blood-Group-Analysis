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

# Compact styling for DataTable
table_style = {
    'fontSize': '12px',
    'padding': '5px',
    'whiteSpace': 'nowrap',
    'backgroundColor': 'white',
    'color': 'black'
}

# Header styling for DataTable
header_style = {'backgroundColor': '#007bff', 'color': 'white', 'fontWeight': 'bold'}

# Conditional formatting for blood group columns
def style_cell_conditional(df):
    styles = []
    for col in blood_groups:
        styles.append({'if': {'column_id': col, 'filter_query': f'{{{col}}} >= 30'}, 'backgroundColor': '#28a745', 'color': 'white'})
        styles.append({'if': {'column_id': col, 'filter_query': f'{{{col}}} >= 15 && {{{col}}} < 30'}, 'backgroundColor': '#ffc107', 'color': 'black'})
        styles.append({'if': {'column_id': col, 'filter_query': f'{{{col}}} < 15'}, 'backgroundColor': '#dc3545', 'color': 'white'})
    return styles

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Create KPI Cards
def create_kpi_cards():
    return dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Total Countries", className="card-title"),
                html.H2(f"{df['Country'].nunique()} 🌍", className="text-primary")
            ])
        ], className="shadow-lg p-3 mb-3 rounded border-0"), width=3),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Most Common Blood Type", className="card-title"),
                html.H2(f"{df[blood_groups].mean().idxmax()} 💉", className="text-success")
            ])
        ], className="shadow-lg p-3 mb-3 rounded border-0"), width=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Rarest Blood Type", className="card-title"),
                html.H2(f"{df[blood_groups].mean().idxmin()} ⚠️", className="text-danger")
            ])
        ], className="shadow-lg p-3 mb-3 rounded border-0"), width=3)
    ])


# Navigation Bar
navbar = dbc.Navbar(
    dbc.Container([
        html.H2("🩸 Blood Type Dashboard", className="text-white"),
    ]),
    color="dark",
    style={"background": "linear-gradient(to right, #007bff, #6610f2)", "padding": "10px"}
)


# App Layout
app.layout = dbc.Container([
    navbar,
    create_kpi_cards(),

    # Filters
    dbc.Row([
    dbc.Col([
        html.Label("Select Blood Type", style={"font-weight": "bold"}),
        dcc.Dropdown(
            id='blood-type-dropdown',
            options=[{'label': bt, 'value': bt} for bt in blood_groups],
            value='O+',
            clearable=False,
            style={"width": "100%", "padding": "5px", "border-radius": "8px"}
        )
    ], width=6, className="p-3 border rounded bg-light shadow-sm"),

    dbc.Col([
        html.Label("Select Continent", style={"font-weight": "bold"}),
        dcc.Dropdown(
            id='continent-dropdown',
            options=[{'label': c, 'value': c} for c in df["Continent"].unique()],
            value=df["Continent"].unique()[0],
            clearable=False,
            style={"width": "100%", "padding": "5px", "border-radius": "8px"}
        )
    ], width=6, className="p-3 border rounded bg-light shadow-sm")
], className="mb-3"),
    # Charts
    dbc.Row([
        dbc.Col(dbc.Card([
    dbc.CardHeader("🌍 Global Blood Type Distribution", className="bg-primary text-white"),
    dbc.CardBody(dcc.Graph(id='choropleth-map'))
]), width=6, className="shadow-sm mb-3 border-0"),
        dbc.Col(dbc.Card([dbc.CardHeader("Blood Type Pie Chart", className= "bg-primary text-white"), dbc.CardBody(dcc.Graph(id='pie-chart'))]), width=6)
    ], className="shadow-lg p-3 mb-3 rounded border-0"),

    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("Blood Group Distribution", className= "bg-primary text-white"), dbc.CardBody(dcc.Graph(id='bar-chart'))]), width=6),
        dbc.Col(dbc.Card([dbc.CardHeader("Rarest Blood Type Indicator", className= "bg-primary text-white"), dbc.CardBody(dcc.Graph(id='gauge-chart'))]), width=6)
    ], className="shadow-lg p-3 mb-3 rounded border-0"),

    # Data Table
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Blood Group Data Table", className= "bg-primary text-white"),
            dbc.CardBody(dash_table.DataTable(
    id='data-table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
    style_table={'overflowX': 'auto', 'maxHeight': '400px', 'overflowY': 'scroll'},
    style_header={'backgroundColor': '#007bff', 'color': 'white', 'fontWeight': 'bold'},
    style_data={'textAlign': 'center', 'padding': '8px'},

    # 🔥 Alternative Fix: Apply Hover Effect for Every Row
    style_data_conditional=[
        {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'},  
        {'if': {'row_index': 'even'}, 'backgroundColor': 'white'},  
        {'if': {'state': 'selected'}, 'backgroundColor': '#ffcc00', 'color': 'black'},  # Selected row fix
        {'if': {'state': 'active'}, 'backgroundColor': '#d3e0ea', 'color': 'black'},  # Hover effect fix
    ],

    filter_action="native",
    sort_action="native",
    page_size=10
)
)
        ]), width=12)
    ])
], fluid=True)

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

    # 🌍 Choropleth Map
    fig_map = px.choropleth(
        df_continent,
        locations="Country",
        locationmode="country names",
        color=selected_blood_type,
        hover_data=blood_groups,
        title=f"Global Distribution of {selected_blood_type} in {selected_continent}",
        color_continuous_scale="plasma"
    )

    # 📊 Bar Chart
    fig_bar = px.bar(
        df_continent,
        x="Country",
        y=blood_groups,
        barmode="group",
        title=f"Blood Group Distribution in {selected_continent}",
        opacity=0.9
    )

    # ⏳ Gauge Chart
    rarest_blood = df_continent[blood_groups].mean().idxmin()
    rarest_percentage = df_continent[rarest_blood].mean()
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rarest_percentage,
        title={"text": f"Rarest Blood Type in {selected_continent}: {rarest_blood}"},
        gauge={"axis": {"range": [0, 10]}, "bar": {"color": "red"}}
    ))

    # 🥧 Pie Chart
    pie_data = df_continent[blood_groups].mean().reset_index().rename(columns={'index': 'BloodType', 0: 'MeanValue'})
    fig_pie = px.pie(
        pie_data,
        values='MeanValue',
        names='BloodType',
        title=f"Blood Type Distribution in {selected_continent}"
    )

    return fig_map, fig_bar, fig_gauge, fig_pie

import os
print("Assets Folder Exists:", os.path.exists("assets"))
print("CSS File Exists:", os.path.exists("assets/styles.css"))

# Run App
if __name__ == '__main__':
    app.run_server(debug=True)
