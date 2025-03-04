import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load dataset
df = pd.read_csv("Data/processed_blood_type_data_with_continent.csv")

# Define Dash App with Bootstrap Theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Blood type columns
blood_groups = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]

# Average Blood Group Distribution Pie Chart
fig_pie = px.pie(df[blood_groups].mean().reset_index(), 
                  values=0, names="index", 
                  title="Global Blood Type Distribution")

# Layout
app.layout = dbc.Container([
    
    # Header
    dbc.Row([
        dbc.Col(html.H1("🌍 Global Blood Group Distribution Dashboard", 
                        className="text-center mb-4"), width=12)
    ]),

    # Filters (Dropdowns)
    dbc.Row([
        dbc.Col([
            html.Label("Select Blood Type"),
            dcc.Dropdown(
                id='blood-type-dropdown',
                options=[{'label': bt, 'value': bt} for bt in blood_groups],
                value='O+',
                clearable=False,
                className="mb-3"
            )
        ], width=4),

        dbc.Col([
            html.Label("Select Continent"),
            dcc.Dropdown(
                id='continent-dropdown',
                options=[{'label': c, 'value': c} for c in df["Continent"].unique()],
                value=df["Continent"].unique()[0],
                clearable=False,
                className="mb-3"
            )
        ], width=4)
    ]),

    # Main Dashboard Layout
    dbc.Row([

        # Left: World Map
        dbc.Col([
            dcc.Graph(id='choropleth-map')
        ], width=6),

        # Right: Pie Chart
        dbc.Col([
            dcc.Graph(figure=fig_pie)
        ], width=6)
    ]),

    # Middle Section: Bar Chart & Satisfaction Metrics
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-chart')
        ], width=6),

        dbc.Col([
            dcc.Graph(id='gauge-chart')  # Gauge chart for rarest blood type
        ], width=6),
    ]),

    # Table View of Data
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={'padding': '10px', 'textAlign': 'center'}
            )
        ], width=12)
    ])

], fluid=True)

# Callbacks for Interactivity
from dash.dependencies import Input, Output

@app.callback(
    [Output('choropleth-map', 'figure'),
     Output('bar-chart', 'figure'),
     Output('gauge-chart', 'figure')],
    [Input('blood-type-dropdown', 'value'),
     Input('continent-dropdown', 'value')]
)
def update_all_charts(selected_blood_type, selected_continent):
    # Filter data based on selected continent
    filtered_df = df[df["Continent"] == selected_continent]

    # 🌍 Update World Map (Choropleth)
    fig_map = px.choropleth(
        filtered_df,
        locations="Country",
        locationmode="country names",
        color=selected_blood_type,
        hover_data=blood_groups,
        title=f"Global Distribution of {selected_blood_type} in {selected_continent}",
        color_continuous_scale="plasma"
    )
    fig_map.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

    # 📊 Update Bar Chart
    fig_bar = px.bar(
        filtered_df,
        x="Country",
        y=blood_groups,
        barmode="group",
        title=f"Blood Group Distribution in {selected_continent}",
        opacity=0.9
    )
    fig_bar.update_layout(xaxis_tickangle=-45, height=500)

    # ⏳ Update Gauge Chart for Rarest Blood Type in Selected Continent
    rarest_blood = filtered_df[blood_groups].mean().idxmin()  # Find rarest blood type
    rarest_percentage = filtered_df[rarest_blood].mean()  # Get its average percentage

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rarest_percentage,
        title={"text": f"Rarest Blood Type in {selected_continent}: {rarest_blood}"},
        gauge={"axis": {"range": [0, 10]}, "bar": {"color": "red"}}
    ))

    return fig_map, fig_bar, fig_gauge


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
