from ssl import ALERT_DESCRIPTION_UNRECOGNIZED_NAME
import click
from matplotlib.pyplot import title
from numpy import size
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
print("Loading Data...")
df = get_data()

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

districts = [uk_local['features'][i]['properties']['LAD13NM'] for i in range(len(uk_local['features']))]

districts2 = df['local_authority_district'].unique()

df2 = df.groupby(['id', 'local_authority_district']).size().reset_index(name='Count')

fig = px.choropleth(df2, locations='id', geojson=uk_local, color='Count', hover_data=['local_authority_district'], scope='europe')
fig.update_geos(fitbounds='locations', visible=False)
available_indicators = ['Count', 'Fatal Accidents Percentage']
# Instantiate custom views
app.layout = html.Div(children=[
    # All elements from the top of the page
    dcc.Loading(id = "loading-icon",
        fullscreen=True,
        children=[
            html.Div([
                html.H2('UK Road Accident Analytics Tool Per Municipality', style={'textAlign': 'center'})
            ]),
            html.Div([
                html.Center('Choose Between Total Amout of Accidents of Fatality Rate'),
                dcc.Dropdown(
                    id='view',
                    options=[{'label': i, 'value': i} for i in available_indicators],
                    value='Count',
                ),
                dcc.Graph(
                        id='graph1',
                        clickData={'points': [{'customdata': 'North Somerset'}]} 
                    ),
            ],
            style={'display': 'inline-block', 'width': '48%', 'align' : 'left'}),

            html.Div([
                html.Center('Choose a Municipality in order to update the other graphs and find correlations!'),
                dcc.Graph(
                    id='heatmap'
                ),
            ], 
            style={'display': 'inline-block', 'width' : '40%', 'align' : 'right', 'margin' : '10px'}),

            html.Div([
                dcc.Graph(id="histo"),
                html.P("Select Distribution:"),
                dcc.RadioItems(
                    id='dist-marginal',
                    options=[{'label': x, 'value': x} 
                        for x in ['box', 'violin']],
                    value='box'
                )
            ],
            style={'display': 'inline-block', 'width' : '45%', 'align' : 'left', 'margin' : '10px'}
            ),

            html.Div([
                dcc.Graph(id="histo2"),
                html.P("Select Distribution:"),
                dcc.RadioItems(
                    id='dist-marginal2',
                    options=[{'label': x, 'value': x} 
                        for x in ['box', 'violin']],
                    value='box'
                )
            ],
            style={'display': 'inline-block', 'width' : '45%', 'align' : 'right', 'margin' : '10px'}), 
            html.H2("Choosing between Distributions can give a better view of the trends hourly or according to speed limit of the road.", style={'fontSize': 15})          
            ], 
        type="graph"
        ),
    ],
    style = {'display' : 'inline-block', 'width' : '100%', 'height' : '100%'}
)

@app.callback(
    Output("histo2", "figure"), 
    [Input("dist-marginal2", "value"),
    Input("graph1", "clickData")])
def update_hist2(marginal2, clickData):
    district = get_district(clickData)
    df = get_data()
    df = df[['accident_severity', 'time', 'number_of_casualties', 'local_authority_district']]
    df['time'] = pd.to_datetime(df["time"], format = "%H:%M").dt.hour
    df = df.sort_values('time')
    df = df[df["local_authority_district"] == district]
    fig = px.histogram(df, x='time', y='number_of_casualties', color='accident_severity', hover_data=df.columns,
                     title="Number of Casualties and Accident Severity hourly at "+ district, marginal = marginal2, barmode = 'overlay', opacity=0.75, nbins=24, 
                     labels={
                     "number_of_casualties": "Number of Casualties",
                     "time": "Time of Day (Hours)",
                     "accident_severity": "Accident Severity"
                 }, height=400, width = 750)
    return fig

@app.callback(
    Output("histo", "figure"), 
    [Input("dist-marginal", "value"), 
    Input("graph1", "clickData")])
def update_hist(marginal, clickData):
    district = get_district(clickData)
    df = get_data()
    df = df[["local_authority_district", "speed_limit", 'accident_severity', "number_of_casualties"]]
    df = df[df["local_authority_district"] == district]
    df = df[df["speed_limit"] != -1]
    df = df.sort_values('speed_limit')
    fig = px.histogram(
        df, x="speed_limit", y="number_of_casualties", color ='accident_severity',
        marginal=marginal, range_x=[-1, 6], hover_data=df.columns, width = 700, height=400, title = "Number of Casualties and Speed Correlation at "+ district,
        labels={
                     "speed_limit": "Road Speed Limit(mph)",
                     "number_of_casualties": "Amount of Casualties",
                     "accident_severity": "Accident Severity"
                 },)

    return fig

@app.callback(
    Output('graph1', 'figure'),  
    Input('view', 'value'))
def update_graph(view_value):
    if view_value == 'Count':
        fig = px.choropleth(df2, locations='id', geojson=uk_local, color='Count', hover_data=['local_authority_district'], scope='europe')
        fig.update_geos(fitbounds='locations', visible=False)

    elif view_value == 'Fatal Accidents Percentage':
        df3 = (df.groupby(['id','local_authority_district'])['accident_severity'].value_counts(normalize=True) * 100).reset_index(name="Percentage")
        df3 = df3.loc[df3['accident_severity'] == 'Fatal']
        df3.set_index('id', drop=False, inplace=True)
        df3 = df3.reindex(df.index, fill_value=0)
        df3['id'] = df3.index
        df3.index.rename('district_id', inplace=True)
        df3.reindex(df.index, fill_value=0)
       

        fig = px.choropleth(df3, locations='id', geojson=uk_local, color='Percentage', hover_data=['local_authority_district'], scope='europe')
        fig.update_geos(fitbounds='locations', visible=False)

    return fig


def get_z_values(clickData, df):
    district = get_district(clickData)
    df = df[df['local_authority_district']==district]
    
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
    print("Updaing Data...")
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
    if (clickData is None):
        return {'data': []}
    else :
        dff = df[["local_authority_district", "road_surface_conditions", "light_conditions"]]
        z_values = get_z_values(clickData, dff)
        district = get_district(clickData)
        return {
            'data': [{
                'z': z_values,
                'y': ['Dry', 'Wet / damp', 'Snow', 'Frost / ice', 'Flood',  'Oil / diesel', 'Mud'],
                'x': ['Daylight', 'Darkness - lights lit', 'Darkness - lights unlit', 'Darkness - no lighting'],
                'ygap': 2,
                'reversescale': 'true',
                'colorscale': 'z_values',
                'type': 'heatmap',
            }],
            'layout': {
                'height': 485,
                'width': 715,
                'title' : "Road Surface vs Lighting Conditions at " + district,
                'xaxis': {'side':'bottom'},
                'margin': {
                	'l': 140,
                	'r': 100,
                	'b': 120,
                	't': 100
                },
            }
        }


if __name__ == '__main__':
    # app.run_server(debug=False, dev_tools_ui=False)
    app.run_server(debug=True) # to check errors. Need to change later