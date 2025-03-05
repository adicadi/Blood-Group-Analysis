import dash
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_and_preprocess_data
import io
from plotly.io import to_image
import logging
from dash import dcc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load data (cached)
df = load_and_preprocess_data()

blood_groups = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]

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
            Input('blood-type-dropdown', 'value'),
            Input('continent-dropdown', 'value'),
            Input('population-slider', 'value'),
            Input('blood-types-multi', 'value'),
            Input('reset-filters', 'n_clicks')
        ],
        [State('blood-type-dropdown', 'value'),
         State('continent-dropdown', 'value')]
    )
    def update_all_charts(selected_blood_type, selected_continent, pop_value, multi_blood_types, reset_n, blood_state, continent_state):
        if reset_n:
            selected_blood_type = 'O+'
            selected_continent = 'Europe'
            pop_value = df['Population'].max()
            multi_blood_types = ['O+']

        try:
            # Filter by population
            df_filtered = df[df['Population'] <= pop_value]

            # Filter by continent
            df_continent = df_filtered[df_filtered["Continent"] == selected_continent]

            # Choropleth Map
            fig_map = px.choropleth(
                df_continent,
                locations="Country",
                locationmode="country names",
                color=selected_blood_type,
                hover_data=blood_groups + ["Population", "Rarest_Blood_Type", "Diversity_Index"],
                title=f"Global Distribution of {selected_blood_type} in {selected_continent}",
                color_continuous_scale="Reds"
            )
            fig_map.update_geos(
                fitbounds="locations",
                visible=True,
                showcountries=True,
                countrycolor="Black",
                showcoastlines=True,
                coastlinecolor="Black"
            )

            # Pie Chart (single blood type for simplicity, or average for multi)
            if len(multi_blood_types) > 1:
                pie_data = df_continent[multi_blood_types].mean().reset_index().rename(columns={'index': 'BloodType', 0: 'MeanValue'})
            else:
                pie_data = df_continent[blood_groups].mean().reset_index().rename(columns={'index': 'BloodType', 0: 'MeanValue'})
            fig_pie = px.pie(
                pie_data,
                values='MeanValue',
                names='BloodType',
                title=f"Blood Type Distribution in {selected_continent}"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')

            # Bar Chart (multi blood types)
            if len(multi_blood_types) > 1:
                melt_df = df_continent.melt(id_vars=["Country"], value_vars=multi_blood_types, var_name='BloodType', value_name='Percentage')
                fig_bar = px.bar(
                    melt_df,
                    x="Country",
                    y="Percentage",
                    color="BloodType",
                    title=f"{', '.join(multi_blood_types)} Distribution in {selected_continent}",
                    barmode='group',
                    opacity=0.9
                )
            else:
                fig_bar = px.bar(
                    df_continent,
                    x="Country",
                    y=selected_blood_type,
                    title=f"{selected_blood_type} Distribution in {selected_continent}",
                    opacity=0.9
                )
            fig_bar.update_layout(
                xaxis_tickangle=-45,
                height=350,
                xaxis_tickfont_size=10
            )

            # Gauge Chart
            rarest_blood = df_continent[blood_groups].mean().idxmin()
            rarest_percentage = df_continent[rarest_blood].mean()
            global_rarest = df[df['Country'] == 'World'][rarest_blood].values[0]
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=rarest_percentage,
                delta={'reference': global_rarest, 'increasing': {'color': "red"}},
                title={"text": f"Rarest Blood Type in {selected_continent}: {rarest_blood}"},
                gauge={"axis": {"range": [0, 10]}, "bar": {"color": "red"}, "threshold": {"value": rarest_percentage}}
            ))
            fig_gauge.update_layout(height=350)

            # Scatter Plot
            fig_scatter = px.scatter(
                df_continent,
                x="Population",
                y=selected_blood_type,
                color="Country",
                size="Population",
                hover_data=["Rarest_Blood_Type", "Diversity_Index"],
                title=f"{selected_blood_type} vs Population in {selected_continent}",
                log_x=True
            )

            # Heatmap (Correlations)
            correlation_matrix = df_continent[blood_groups].corr()
            fig_heatmap = px.imshow(
                correlation_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu",
                title=f"Blood Type Correlations in {selected_continent}"
            )

            # Data Table
            table_data = df_continent.to_dict('records')

            return (fig_map, fig_pie, fig_bar, fig_gauge, fig_scatter, fig_heatmap, table_data, "Data loaded successfully")
        
        except Exception as e:
            logger.error(f"Error in update_all_charts: {str(e)}")
            return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, [], f"Error: {str(e)}")

    @app.callback(
        Output("info-modal", "is_open"),
        [Input("open-info", "n_clicks"), Input("close-info", "n_clicks")],
        [State("info-modal", "is_open")],
    )
    def toggle_modal(open_n, close_n, is_open):
        if open_n or close_n:
            return not is_open
        return is_open

    @app.callback(
        Output("download-data", "data"),
        Input("btn-download", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_data(n_clicks):
        return dcc.send_data_frame(df.to_csv, "blood_type_data.csv")

    @app.callback(
        Output("download-charts", "data"),
        Input("btn-download-charts", "n_clicks"),
        [State('choropleth-map', 'figure'),
         State('pie-chart', 'figure'),
         State('bar-chart', 'figure'),
         State('gauge-chart', 'figure'),
         State('scatter-plot', 'figure'),
         State('heatmap', 'figure')],
        prevent_initial_call=True,
    )
    def download_charts(n_clicks, choropleth_fig, pie_fig, bar_fig, gauge_fig, scatter_fig, heatmap_fig):
        try:
            # Validate that figures are not None or empty
            figures = [f for f in [choropleth_fig, pie_fig, bar_fig, gauge_fig, scatter_fig, heatmap_fig] if f and 'data' in f]
            if not figures:
                raise ValueError("No valid figures available for download")

            # Use the first figure (choropleth) as the main chart for simplicity
            main_fig = choropleth_fig if choropleth_fig else figures[0]

            # Generate image bytes using plotly.io.to_image
            img_bytes = to_image(main_fig, format="png", engine="kaleido", width=1200, height=800)

            logger.info("Charts downloaded successfully as PNG")
            return dcc.send_bytes(img_bytes, "charts.png")

        except Exception as e:
            logger.error(f"Error downloading charts: {str(e)}")
            # Fallback: Return an error message as a text file
            return dcc.send_string(f"Error generating chart image: {str(e)}", "error.txt")