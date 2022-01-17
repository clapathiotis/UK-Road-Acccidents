from jbi100_app.main import app
from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.scatterplot import Scatterplot
import pandas as pd

from dash import html
import plotly.express as px
from dash.dependencies import Input, Output


if __name__ == '__main__':
    # Create data
    
    df = pd.read_csv(r'decoded-dft-road-casualty-statistics-accident-2020.csv', delimiter=',')

    df = df[df["number_of_casualties"] > 1]
    df = df[df["weather_conditions"] != 9]
    df = df[df["weather_conditions"] != "Uknown"]
    df = df[df["weather_conditions"] != 8]
    
    # Instantiate custom views
    scatterplot1 = Scatterplot("Scatterplot 1", 'weather_conditions', 'number_of_casualties', df)
    scatterplot2 = Scatterplot("Scatterplot 2", 'light_conditions', 'number_of_casualties', df)

    app.layout = html.Div(
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
    )

    # Define interactions
    @app.callback(
        Output(scatterplot1.html_id, "figure"), [
        Input("select-area-scatter-1", "value"),
        Input(scatterplot2.html_id, 'selectedData')
    ])
    def update_scatter_1(selected_area, selected_data):
        return scatterplot1.update(selected_area, selected_data)

    @app.callback(
        Output(scatterplot2.html_id, "figure"), [
        Input("select-area-scatter-2", "value"),
        Input(scatterplot1.html_id, 'selectedData')
    ])
    def update_scatter_2(selected_area, selected_data):
        return scatterplot2.update(selected_area, selected_data)


    app.run_server(debug=False, dev_tools_ui=False)