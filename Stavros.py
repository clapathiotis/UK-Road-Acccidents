import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from numpy import true_divide

import pandas as pd

df = pd.read_csv(r'dft-road-casualty-statistics-vehicle-last-5-years.csv', delimiter=',', low_memory=False)
dff = df.copy()
dff = dff.drop(labels=["accident_index", "accident_reference", "vehicle_reference", "vehicle_type", "towing_and_articulation", "vehicle_manoeuvre", "vehicle_direction_from", "vehicle_direction_to", "vehicle_location_restricted_lane", "junction_location", "skidding_and_overturning", "hit_object_in_carriageway", "vehicle_leaving_carriageway", "hit_object_off_carriageway", "first_point_of_impact", "vehicle_left_hand_drive", "journey_purpose_of_driver", "propulsion_code", "generic_make_model", "driver_imd_decile", "driver_home_area_type"], axis=1)
dff = dff[dff.engine_capacity_cc != -1]
dff = dff[dff.age_of_vehicle != -1]
dff = dff[dff.age_of_driver != -1]
dff = dff[dff.age_band_of_driver != -1]
print(dff.head())


app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        id='year-slider',
        min=dff['accident_year'].min(),
        max=dff['accident_year'].max(),
        value=dff['accident_year'].min(),
        marks={str(year): str(year) for year in dff['accident_year'].unique()},
        step=None
    )
])


@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('year-slider', 'value'))
def update_figure(selected_year):
    filtered_df = dff[dff.accident_year == selected_year]

    fig = px.scatter(filtered_df, x="age_of_driver", y="engine_capacity_cc",
                     size="age_of_vehicle", hover_name="age_band_of_driver", size_max=55)

    fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
