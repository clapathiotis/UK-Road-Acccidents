import plotly.express as pf
import csv
import pandas as pd


def get_data():
    # Read data
    df = pd.read_csv(r'dataset.csv', delimiter=',')
  

    # Any further data preprocessing can go here
    
    return df

