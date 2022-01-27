import click
from jbi100_app.data import get_data
from jbi100_app.main import app
from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.scatterplot import Scatterplot

from dash import html
import plotly.express as px
from dash.dependencies import Input, Output

import json
import pandas as pd
from dash import dcc
from dash import html

# Create data
df = get_data()
# print(df.head())

# topoJSON of UK Local authority Districts from http://martinjc.github.io/UK-GeoJSON/json/eng/topo_lad.json and https://github.com/martinjc/UK-GeoJSON/blob/master/json/administrative/gb/lad.json
uk_local = json.load(open("lad.json","r"))
counties_map = dict()
for feature in uk_local['features']:
    feature['id'] = feature['properties']['LAD13CD']
    counties_map[feature['properties']['LAD13NM']] = feature['id']

df['id'] = df['local_authority_district'].apply(lambda x: counties_map[x] if x in counties_map.keys() else pd.NA)
df = df.dropna(subset=['id'])
df.set_index('id', drop=False, inplace=True)
df.index.rename('district_id', inplace=True)
# df['id'].isna().sum()

districts = [uk_local['features'][i]['properties']['LAD13NM'] for i in range(len(uk_local['features']))]

districts2 = df['local_authority_district'].unique()
# count = 0

# for i in range(len(districts2)):
#     if districts2[i] not in districts:
#         print(districts2[i])
#         count += 1

df2 = df.groupby(['id', 'local_authority_district']).size().reset_index(name='Count')

fig = px.choropleth(df2, locations='id', geojson=uk_local, color='Count', hover_data=['local_authority_district'], scope='europe')
fig.update_geos(fitbounds='locations', visible=False)
available_indicators = ['Count', 'Fatal Accidents Percentage']
# Instantiate custom views
scatterplot1 = Scatterplot("Scatterplot 1", 'weather_conditions', 'number_of_casualties', df)
scatterplot2 = Scatterplot("Scatterplot 2", 'light_conditions', 'number_of_casualties', df)
app.layout = html.Div(children=[
    # All elements from the top of the page
    dcc.Loading(id = "loading-icon",
        fullscreen=True,
        children=[
            html.Div([
                dcc.Dropdown(
                    id='view',
                    options=[{'label': i, 'value': i} for i in available_indicators],
                    value='Count',
                    
                ),
            ],
            style={'display': 'inline-block', 'width': '49%'}
            ),
            html.Div([
                
                html.Div([
                    dcc.Graph(
                        id='graph1',
                        clickData={'points': [{'customdata': 'City of London'}]},
                        style = {
                            'width': '115vh',
                            'height': '95vh',
                        }    
                    ),
                ], 
                style={'margin': '10px', 'display': 'inline-block'}),
                html.Div([
                    dcc.Graph(
                        id='heatmap',
                    ),
                ], 
            style={'display': 'inline-block', 'vertical-align': 'top'}),
                
            ]),
             

            html.Div(
                id="app-container",
                children=[
                    # Left column
                    html.Div(
                        id="left-column",
                        className="three columns",
                        children=make_menu_layout()
                    ),

                    # Right column
                    html.Div(
                        id="right-column",
                        className="nine columns",
                        children=[
                            scatterplot1,
                            scatterplot2
                        ],
                    ),
                ],
            ),
            
            ], 
            type="graph"
        ),
    
    ]
)
@app.callback(
    Output('graph1', 'figure'),  
    Input('view', 'value'))
def update_graph(view_value):
    if view_value == 'Count':
        fig = px.choropleth(df2, locations='id', geojson=uk_local, color='Count', hover_data=['local_authority_district'], scope='europe')
        fig.update_geos(fitbounds='locations', visible=False)

    elif view_value == 'Fatal Accidents Percentage':
        print(df)
        df3 = (df.groupby(['id','local_authority_district'])['accident_severity'].value_counts(normalize=True) * 100).reset_index(name="Percentage")
        print(df3)
        df3 = df3.loc[df3['accident_severity'] == 'Fatal']
        df3.set_index('id', drop=False, inplace=True)
        df3 = df3.reindex(df.index, fill_value=0)
        df3['id'] = df3.index
        df3.index.rename('district_id', inplace=True)
        print(df3)
        df3.reindex(df.index, fill_value=0)
        # df3 = df3.loc[df3['accident_severity'] == 'Fatal']
       

        fig = px.choropleth(df3, locations='id', geojson=uk_local, color='Percentage', hover_data=['local_authority_district'], scope='europe')
        fig.update_geos(fitbounds='locations', visible=False)

    return fig


# Define interactions
@app.callback(
    Output(scatterplot1.html_id, "figure"), [
    Input("select-color-scatter-1", "value"),
    Input(scatterplot2.html_id, 'selectedData')
])
def update_scatter_1(selected_color, selected_data):
    return scatterplot1.update(selected_color, selected_data)

@app.callback(
    Output(scatterplot2.html_id, "figure"), [
    Input("select-color-scatter-2", "value"),
    Input(scatterplot1.html_id, 'selectedData')
])
def update_scatter_2(selected_color, selected_data):
    return scatterplot2.update(selected_color, selected_data)

def get_z_values(clickData, df):
    district = get_district(clickData)
    df = df[df['local_authority_district']==district]
    # print(df.head())
    # print(district)
    Dry_count = (df.road_surface_conditions == "Dry").sum()
    Wet_or_damp = (df.road_surface_conditions == "Wet or damp").sum()
    Snow_count = (df.road_surface_conditions == "Snow").sum()
    Frost_or_ice = (df.road_surface_conditions == "Frost or ice").sum()
    Flood = (df.road_surface_conditions == "Flood over 3cm. deep").sum()
    Oil_or_diesel = (df.road_surface_conditions == "Oil or diesel").sum()
    Mud_count = (df.road_surface_conditions == "Mud").sum()

    #light
    Daylight_count = (df.light_conditions == "Daylight").sum()
    Darkness_lit = (df.light_conditions == "Darkness - lights lit").sum()
    Darkness_unlit = (df.light_conditions == "Darkness - lights unlit").sum()
    Darkness_no_light = (df.light_conditions == "Darkness - no lighting").sum()
    z = [[Daylight_count +Dry_count, Daylight_count +Frost_or_ice, Daylight_count +Wet_or_damp,Daylight_count +Flood, Daylight_count +Snow_count, Daylight_count +Oil_or_diesel, Daylight_count +Mud_count],
        [Darkness_lit +Dry_count, Darkness_lit +Frost_or_ice, Darkness_lit +Wet_or_damp,Darkness_lit +Flood, Darkness_lit +Snow_count, Darkness_lit +Oil_or_diesel, Darkness_lit +Mud_count], 
        [Darkness_unlit +Dry_count, Darkness_unlit +Frost_or_ice, Darkness_unlit +Wet_or_damp,Darkness_unlit +Flood, Darkness_unlit +Snow_count, Darkness_unlit +Oil_or_diesel, Darkness_unlit +Mud_count], 
        [Darkness_no_light +Dry_count, Darkness_no_light +Frost_or_ice, Darkness_no_light +Wet_or_damp,Darkness_no_light +Flood, Darkness_no_light +Snow_count, Darkness_no_light +Oil_or_diesel, Darkness_no_light +Mud_count]]
    return z

def get_district(clickData):
    if type(clickData['points'][0]['customdata']) == str:
        district = clickData['points'][0]['customdata']
    else:
        district = clickData['points'][0]['customdata'][0]
    return district

@app.callback(
    Output('heatmap', 'figure'),  
    [Input('graph1', 'clickData')
])   
def update_heatmap(clickData):
    # if view_value == 'Count':
    #     fig = px.choropleth(dff2, locations='id', geojson=uk_local, color='Count', hover_data=['local_authority_district'], scope='europe')
    #     fig.update_geos(fitbounds='locations', visible=False)

    # elif view_value == 'Fatal Accidents Percentage':
        
    #     df3 = (df.groupby(['id','local_authority_district'])['accident_severity'].value_counts(normalize=True) * 100).fillna(0).reset_index(name="Percentage")
    #     df3 = df3.loc[df3['accident_severity'] == 'Fatal']
    #     dff3 = df3[df3['local_authority_district'] == district]

    #     fig = px.choropleth(dff3, locations='id', geojson=uk_local, color='Percentage', hover_data=['local_authority_district'], scope='europe')
    #     fig.update_geos(fitbounds='locations', visible=False)
    
    # left_margin = 200
    # right_margin = 100
    # print(clickData)
    if (clickData is None):
        return {'data': []}
    else :
        dff = df[["local_authority_district", "road_surface_conditions", "light_conditions"]]
        z_values = get_z_values(clickData, dff)
        district = get_district(clickData)
        # print(z_values[1][1])
        return {
            'data': [{
                'z': z_values,
                'y': ['Dry', 'Wet / damp', 'Snow', 'Frost / ice', 'Flood',  'Oil / diesel', 'Mud'],
                'x': ['Daylight', 'Darkness - lights lit', 'Darkness - lights unlit', 'Darkness - no lighting'],
                'ygap': 2,
                'reversescale': 'true',
                'colorscale': [[0, 'white'], [1, 'orange'], [2, 'red']],
                'type': 'heatmap',
            }],
            'layout': {
                'height': 500,
                'width': 600,
                'title' : "Road Surface vs Lighting Conditions at " + district,
                'xaxis': {'side':'bottom'},
                'margin': {
                	# 'l': left_margin,
                	# 'r': right_margin,
                	'b': 150,
                	't': 100
                }
            }
        }


# @app.callback(
#     dash.dependencies.Output('x-time-series', 'figure'),
#     [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
#      dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
#      dash.dependencies.Input('crossfilter-xaxis-type', 'value')])
# def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
#     country_name = hoverData['points'][0]['customdata']
#     dff = df[df['Country Name'] == country_name]
#     dff = dff[dff['Indicator Name'] == xaxis_column_name]
#     title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
#     return create_time_series(dff, axis_type, title)


# @app.callback(
#     dash.dependencies.Output('y-time-series', 'figure'),
#     [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
#      dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
#      dash.dependencies.Input('crossfilter-yaxis-type', 'value')])
# def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
#     dff = df[df['Country Name'] == hoverData['points'][0]['customdata']]
#     dff = dff[dff['Indicator Name'] == yaxis_column_name]
#     return create_time_series(dff, axis_type, yaxis_column_name)




if __name__ == '__main__':
    # app.run_server(debug=False, dev_tools_ui=False)
    app.run_server(debug=True) # to check errors. Need to change later