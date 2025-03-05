import dash
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from utils import load_and_preprocess_data, BLOOD_GROUPS
import logging
from plotly.io import to_image
from dash import dcc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load data
df = load_and_preprocess_data()

def register_callbacks(app):
    @app.callback(
        [
            Output('choropleth-map', 'figure'),
            Output('pie-chart', 'figure'),
            Output('bar-chart', 'figure'),
            Output('gauge-chart', 'figure'),
            Output('scatter-plot', 'figure'),
            Output('heatmap', 'figure'),
            Output('data-table', 'data'),
            Output('loading-message', 'children')
        ],
        [
            Input('blood-types-multi', 'value'),
            Input('continent-dropdown', 'value'),
            Input('population-slider', 'value'),
            Input('reset-filters', 'n_clicks')
        ]
    )
    def update_all_charts(multi_blood_types, selected_continent, pop_value, reset_n):
        if reset_n:
            multi_blood_types = ['O+']
            selected_continent = 'Europe'
            pop_value = df['Population'].max()

        try:
            df_filtered = df[df['Population'] <= pop_value]
            df_continent = df_filtered[df_filtered["Continent"] == selected_continent]
            selected_blood_type = multi_blood_types[0]  # Use first for single-type charts

            # Choropleth Map
            fig_map = px.choropleth(df_continent, locations="Country", locationmode="country names", color=selected_blood_type,
                                    hover_data=BLOOD_GROUPS + ["Population", "Rarest_Blood_Type", "Diversity_Index"],
                                    color_continuous_scale="Reds")
            fig_map.update_geos(fitbounds="locations", visible=True, showcountries=True, countrycolor="Black", showcoastlines=True, coastlinecolor="Black")
            fig_map.update_layout(
                title=f"Global Distribution of {selected_blood_type} in {selected_continent}",
                title_font=dict(size=18, family="Arial, sans-serif", color="#2c3e50", weight="bold"),  # Dark blue, bold, larger font
                title_x=0.5,  # Center the title
                title_y=0.95,  # Adjust vertical position slightly
                title_pad=dict(t=10),  # Add top padding
                margin=dict(t=50)  # Increase top margin to prevent overlap
            )

            # Pie Chart
            pie_data = df_continent[multi_blood_types].mean().reset_index().rename(columns={'index': 'BloodType', 0: 'MeanValue'})
            fig_pie = px.pie(pie_data, values='MeanValue', names='BloodType', title=f"Blood Type Distribution in {selected_continent}")
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(
                title_font=dict(size=18, family="Arial, sans-serif", color="#2c3e50", weight="bold"),
                title_x=0.5,
                title_y=0.95,
                title_pad=dict(t=10),
                margin=dict(t=50)
            )

            # Bar Chart
            melt_df = df_continent.melt(id_vars=["Country"], value_vars=multi_blood_types, var_name='BloodType', value_name='Percentage')
            fig_bar = px.bar(melt_df, x="Country", y="Percentage", color="BloodType", barmode='group', opacity=0.9, title=f"{', '.join(multi_blood_types)} Distribution in {selected_continent}")
            fig_bar.update_layout(
                xaxis_tickangle=-45,
                xaxis_tickfont_size=10,
                title_font=dict(size=18, family="Arial, sans-serif", color="#2c3e50", weight="bold"),
                title_x=0.5,
                title_y=0.95,
                title_pad=dict(t=10),
                margin=dict(t=50)
            )

            # Gauge Chart
            rarest_blood = df_continent[BLOOD_GROUPS].mean().idxmin()
            rarest_percentage = df_continent[rarest_blood].mean()
            global_rarest = df[df['Country'] == 'World'][rarest_blood].values[0] if 'World' in df['Country'].values else rarest_percentage
            fig_gauge = go.Figure(go.Indicator(mode="gauge+number+delta", value=rarest_percentage, delta={'reference': global_rarest, 'increasing': {'color': "red"}},
                                              ))
            fig_gauge.update_layout(
                title=f"Rarest Blood Type in {selected_continent}: {rarest_blood}",
                title_font=dict(size=18, family="Arial, sans-serif", color="#2c3e50", weight="bold"),
                title_x=0.5,
                title_y=0.95,
                title_pad=dict(t=10),
                margin=dict(t=50)
            )

            # Scatter Plot
            fig_scatter = px.scatter(df_continent, x="Population", y=selected_blood_type, color="Country", size="Population",
                                     hover_data=["Rarest_Blood_Type", "Diversity_Index"], log_x=True, title=f"{selected_blood_type} vs Population in {selected_continent}")
            fig_scatter.update_layout(
                title_font=dict(size=18, family="Arial, sans-serif", color="#2c3e50", weight="bold"),
                title_x=0.5,
                title_y=0.95,
                title_pad=dict(t=10),
                margin=dict(t=50)
            )

            # Heatmap
            correlation_matrix = df_continent[BLOOD_GROUPS].corr()
            fig_heatmap = px.imshow(correlation_matrix, text_auto=True, aspect="auto", color_continuous_scale="RdBu", title=f"Blood Type Correlations in {selected_continent}")
            fig_heatmap.update_layout(
                title_font=dict(size=18, family="Arial, sans-serif", color="#2c3e50", weight="bold"),
                title_x=0.5,
                title_y=0.95,
                title_pad=dict(t=10),
                margin=dict(t=50)
            )

            table_data = df_continent.to_dict('records')
            return (fig_map, fig_pie, fig_bar, fig_gauge, fig_scatter, fig_heatmap, table_data, "Data loaded successfully")

        except Exception as e:
            logger.error(f"Error in update_all_charts: {str(e)}")
            return (dash.no_update,) * 6 + ([], f"Error: {str(e)}")

    @app.callback(
    Output("sidebar", "is_open"),
    Input("toggle-sidebar", "n_clicks"),
    State("sidebar", "is_open"),
    prevent_initial_call=True  # Ensures callback only runs after a click
    )
    def toggle_sidebar(toggle_clicks, is_open):
        return not is_open  # Toggle sidebar state


    @app.callback(Output("info-modal", "is_open"), [Input("open-info", "n_clicks"), Input("close-info", "n_clicks"), State("info-modal", "is_open")])
    def toggle_modal(open_n, close_n, is_open):
        if open_n or close_n:
            return not is_open
        return is_open

    @app.callback(Output("download-data", "data"), Input("btn-download", "n_clicks"), prevent_initial_call=True)
    def download_data(n_clicks):
        return dcc.send_data_frame(df.to_csv, "blood_type_data.csv")

    @app.callback(Output("download-charts", "data"), Input("btn-download-charts", "n_clicks"),
                  [State('choropleth-map', 'figure')], prevent_initial_call=True)
    def download_charts(n_clicks, choropleth_fig):
        try:
            if not choropleth_fig or 'data' not in choropleth_fig:
                raise ValueError("No valid figure available")
            img_bytes = to_image(choropleth_fig, format="png", engine="kaleido", width=1200, height=800)
            return dcc.send_bytes(img_bytes, "charts.png")
        except Exception as e:
            logger.error(f"Error downloading charts: {str(e)}")
            return dcc.send_string(f"Error: {str(e)}", "error.txt")