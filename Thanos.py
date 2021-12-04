import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from numpy import true_divide

import pandas as pd

df = pd.read_csv(r'BloodAlcoholContent_CoronersData2009.csv', delimiter=',', low_memory=False)
dff = df.copy()
print(df.head())

app = dash.Dash(__name__)

app.layout = html.Div([
     dcc.Dropdown(
         id="dropdown",
         options=[{"label": x, "value": x} for x in "UngaBunga"],
         value="Ungabunga"[0],
         clearable=False,
     ),
     dcc.Graph(id="bar-chart"),
 ])

@app.callback(
     Output("bar-chart", "figure"), 
     [Input("dropdown", "value")])
def update_bar_chart(day):
     #mask = dff[""] == day
     fig = px.bar(dff, x="AgeBand", y="BloodAlcoholLevel(mg/100ml)", 
                  color="SexOfCasualty", barmode="group")
     return fig





app.run_server(debug=True)