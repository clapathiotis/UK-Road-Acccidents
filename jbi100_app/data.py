import plotly.express as px
import pandas as pd

def get_data():
    # Read data
    df = pd.read_csv('decoded-dft-road-casualty-statistics-accident-2020.csv')

    # Any further data preprocessing can go her
    df = df[df["number_of_casualties"]>1]
    df = df[df["weather_conditions"] != "Other"]
    df = df[df["weather_conditions"] != "Unknown"]
    return df
