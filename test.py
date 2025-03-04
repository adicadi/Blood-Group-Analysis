import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load dataset
df = pd.read_csv("Data/processed_blood_type_data_with_continent.csv")

# Blood type columns
blood_groups = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]

# Bootstrap theme for dark mode
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

# Sidebar navigation
sidebar = dbc.Nav(
    [
        html.H3("Quantum Dashboard", className="text-center text-light mt-2"),
        html.Hr(),
        dbc.NavLink("E-Commerce", href="#", active=True, className="text-light"),
        dbc.NavLink("CRM", href="#", className="text-light"),
        dbc.NavLink("Analytics", href="#", className="text-light"),
        dbc.NavLink("Project Management", href="#", className="text-light"),
        dbc.NavLink("Cryptocurrency", href="#", className="text-light"),
    ],
    vertical=True,
    pills=True,
    className="bg-dark p-3",
)

# 📊 **Charts and Data**
def create_line_chart():
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=df[blood_groups[0]], mode='lines', name=blood_groups[0], line=dict(color='#00ccff')))
    fig.add_trace(go.Scatter(y=df[blood_groups[1]], mode='lines', name=blood_groups[1], line=dict(color='#ffcc00')))
    fig.update_layout(
        plot_bgcolor="#1e1e2f",
        paper_bgcolor="#1e1e2f",
        font_color="white",
        title="Sales History"
    )
    return fig

def create_pie_chart():
    avg_blood_groups = df[blood_groups].mean()
    fig = px.pie(values=avg_blood_groups, names=avg_blood_groups.index, title="Blood Type Distribution",
                 color_discrete_sequence=px.colors.sequential.Plasma)
    fig.update_layout(
        plot_bgcolor="#1e1e2f",
        paper_bgcolor="#1e1e2f",
        font_color="white"
    )
    return fig

def create_bar_chart():
    fig = px.bar(df, x="Country", y=blood_groups, title="Blood Group Distribution",
                 color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_layout(
        plot_bgcolor="#1e1e2f",
        paper_bgcolor="#1e1e2f",
        font_color="white"
    )
    return fig

def create_gauge_chart():
    rarest_blood = df[blood_groups].mean().idxmin()
    rarest_percentage = df[rarest_blood].mean()

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rarest_percentage,
        title={"text": f"Rarest Blood Type: {rarest_blood}"},
        gauge={"axis": {"range": [0, 10]}, "bar": {"color": "red"}}
    ))
    fig.update_layout(
        plot_bgcolor="#1e1e2f",
        paper_bgcolor="#1e1e2f",
        font_color="white"
    )
    return fig

# 🏦 **Dashboard Layout**
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(sidebar, width=2, className="vh-100"),  # Sidebar taking full height
        dbc.Col([
            html.H2("E-Commerce Dashboard", className="text-center text-light mb-4"),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=create_line_chart()), width=6),
                dbc.Col(dcc.Graph(figure=create_pie_chart()), width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=create_bar_chart()), width=6),
                dbc.Col(dcc.Graph(figure=create_gauge_chart()), width=6),
            ], className="mb-3"),
            # 📋 **Data Table**
            dbc.Row([
                dbc.Col([
                    html.H5("Blood Group Data", className="text-light"),
                    dash_table.DataTable(
                        id='data-table',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict('records'),
                        style_table={'overflowX': 'auto', 'maxHeight': '400px', 'overflowY': 'scroll'},
                        style_cell={'textAlign': 'center', 'backgroundColor': '#1e1e2f', 'color': 'white'},
                        style_header={'backgroundColor': '#343a40', 'color': 'white', 'fontWeight': 'bold'},
                    )
                ], width=12)
            ])
        ], width=10, className="bg-dark p-4")
    ])
], fluid=True)

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
