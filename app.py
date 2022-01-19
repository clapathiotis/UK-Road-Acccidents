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
print(df.head())

# topoJSON of UK Local authority Districts from http://martinjc.github.io/UK-GeoJSON/json/eng/topo_lad.json and https://github.com/martinjc/UK-GeoJSON/blob/master/json/administrative/gb/lad.json
uk_local = json.load(open("lad.json","r"))
counties_map = dict()
for feature in uk_local['features']:
    feature['id'] = feature['properties']['LAD13CD']
    counties_map[feature['properties']['LAD13NM']] = feature['id']

df['id'] = df['local_authority_district'].apply(lambda x: counties_map[x] if x in counties_map.keys() else pd.NA)
df = df.dropna(subset=['id'])
# df['id'].isna().sum()

districts = [uk_local['features'][i]['properties']['LAD13NM'] for i in range(len(uk_local['features']))]

districts2 = df['local_authority_district'].unique()
count = 0

for i in range(len(districts2)):
    if districts2[i] not in districts:
        print(districts2[i])
        count += 1

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
                children=[
                html.Div([
        
        html.Div([
            
            dcc.Dropdown(
                id='view',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Count'
            ),

            dcc.Graph(
                id='graph1',
                figure=fig,
                style = {
                    'width': '130vh',
                    'height': '110vh'
                }
            ),  
        ], className='six columns')], className='row'),
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
        
        df3 = (df.groupby(['id','local_authority_district'])['accident_severity'].value_counts(normalize=True) * 100).reset_index(name="Percentage")
        df3 = df3.loc[df3['accident_severity'] == 'Fatal']


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

if __name__ == '__main__':
    # app.run_server(debug=False, dev_tools_ui=False)
    app.run_server(debug=True) # to check errors. Need to change later