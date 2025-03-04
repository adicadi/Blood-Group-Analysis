import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_csv("Data/processed_blood_type_data_with_continent.csv")


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Global Blood Group Distribution Dashboard"),
    
    dcc.Dropdown(
        id = "blood-type-dropdown",
        options = [{'label': bt, 'value': bt} for bt in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]],
        value = "O+",
        clearable = False
    ),
    
    dcc.Graph(id = "choropleth-map"),
    
    dcc.Dropdown(
        id = 'continent-dropdown',
        options = [{'label': c, 'value': c} for c in df['Continent'].unique()],
        value = df['Continent'].unique(),
        clearable = False,
    ),
    
    dcc.Graph(id = "bar-chart")
])

@app.callback(
    Output("choropleth-map", "figure"),
    Input("blood-type-dropdown", "value")
)
def update_choropleth(blood_type):
    fig = px.choropleth(
        df,
        locations = "Country",
        locationmode = "country names",
        color = blood_type,
        hover_name = "Country",
        title = f"Global Distribution of {blood_type} Blood Type"
    )
    return fig

@app.callback(
    Output("bar-chart", "figure"),
    Input("continent-dropdown", "value")
)
def update_bar_chart(selected_continent):
    filtered_df = df[df['Continent'] == selected_continent]
    fig = px.bar(
        filtered_df,
        x = "Country",
        y = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
        barmode = "group",
        title = f"Blood Group Distribution in {selected_continent}"
    )
    return fig

if __name__ == "__main__":
    app.run_server(debug = True)