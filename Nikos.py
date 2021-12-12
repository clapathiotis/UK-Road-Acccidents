import json
import numpy as np
import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from jupyter_dash import JupyterDash


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# topoJSON of UK Local authority Districts from http://martinjc.github.io/UK-GeoJSON/json/eng/topo_lad.json and https://github.com/martinjc/UK-GeoJSON/blob/master/json/administrative/gb/lad.json
uk_local = json.load(open("lad.json","r"))
counties_map = dict()
for feature in uk_local['features']:
    feature['id'] = feature['properties']['LAD13CD']
    counties_map[feature['properties']['LAD13NM']] = feature['id']

# print(uk_local['features'][1])

# print(uk_local['features'][0]['properties']['LAD13NM'])

csv_file = 'decoded-dft-road-casualty-statistics-accident-2020.csv'
df = pd.read_csv(csv_file, low_memory=False)
# df = pd.read_csv(csv_file, nrows=10000) # use this line if you want to only experiment with a small sample of the dataset
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
# print(count)
# print(len(districts2) - len(districts))

df2 = df.groupby(['id', 'local_authority_district']).size().reset_index(name='Count')

fig = px.choropleth(df2, locations='id', geojson=uk_local, color='Count', hover_data=['local_authority_district'], scope='europe')
fig.update_geos(fitbounds='locations', visible=False)

available_indicators = ['Count', 'Fatal Accidents Percentage']
app.layout = html.Div(children=[
    # All elements from the top of the page
    
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
        ], className='six columns')], className='row')
        ])

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


if __name__ == '__main__':
    app.run_server(debug=True)