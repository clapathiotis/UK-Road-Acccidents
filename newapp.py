import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from jupyter_dash import JupyterDash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


df = pd.read_csv(r'dft-road-casualty-statistics-accident-2020.csv', delimiter=',')

df = df[df["number_of_casualties"] > 2]
df = df[df["weather_conditions"] != 9]
df = df[df["weather_conditions"] != -1]
df = df[df["weather_conditions"] != 8]

dff = pd.read_csv(r'BloodAlcoholContent_CoronersData2009.csv', delimiter=',', low_memory=False)


fig = px.bar(df, x="day_of_week", y="number_of_casualties", color = 'number_of_casualties',
                labels={'number_of_casualties':'Number of Casualties', 'day_of_week' : 'Day of the Week: Monday to Sunday'}, title="dis")

fig2 = px.scatter(df, x="weather_conditions", y="number_of_casualties", color = 'number_of_casualties',
                labels={'number_of_casualties':'Number of Casualties', 'day_of_week' : 'Day of the Week: Monday to Sunday'}, title="dis")

fig3 = px.bar(dff, x="AgeBand", y="BloodAlcoholLevel(mg/100ml)", 
                  color="SexOfCasualty", barmode="group")

app.layout = html.Div(children=[
    # All elements from the top of the page
    html.Div([
        html.Div([
            html.H1(children='Hello Dash'),

            html.Div(children='''
                Dash: A web application framework for Python.
            '''),

            dcc.Graph(
                id='graph1',
                figure=fig
            ),  
        ], className='six columns'),
        html.Div([
            html.H1(children='Hello Dash'),

            html.Div(children='''
                Dash: A web application framework for Python.
            '''),

            dcc.Graph(
                id='graph2',
                figure=fig2
            ),  
        ], className='six columns'),
    ], className='row'),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H1(children='Hello Dash'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        dcc.Graph(
            id='graph3',
            figure=fig3
        ),  
    ], className='row'),
])

if __name__ == '__main__':
    app.run_server(debug=True)