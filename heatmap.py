import plotly.express as px
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import datetime
import numpy as np

df = pd.read_csv('decoded-dft-road-casualty-statistics-accident-2020.csv', low_memory=False)
df = df.drop(labels=["accident_index", "accident_year", "accident_reference","location_easting_osgr","location_northing_osgr","longitude","latitude","police_force","accident_severity","number_of_vehicles","number_of_casualties","date","day_of_week","local_authority_district","local_authority_ons_district","local_authority_highway","first_road_class","first_road_number","road_type","speed_limit","junction_detail","junction_control","second_road_class","second_road_number","pedestrian_crossing_human_control","pedestrian_crossing_physical_facilities","special_conditions_at_site","carriageway_hazards","urban_or_rural_area","did_police_officer_attend_scene_of_accident","trunk_road_flag","lsoa_of_accident_location"], axis=1)
    
# Any further data preprocessing can go her
# df = df[df["number_of_casualties"]>1]
df = df[df["weather_conditions"] != "Other"]
df = df[df["weather_conditions"] != "Unknown"]
# For counts of accidents per weather condition
 #this does nothing here just an example
Fine_count = (df.weather_conditions == "Fine no high winds").sum()
Rain_count = (df.weather_conditions == "Raining no high winds").sum()
Snow_count = (df.weather_conditions == "Snowing no high winds").sum()
Fine_wind_count = (df.weather_conditions == "Fine + high winds").sum()
Rain_wind_count = (df.weather_conditions == "Snowing + high winds").sum()
Snow_wind_count = (df.weather_conditions == "Snowing + high winds").sum()
Fog_count = (df.weather_conditions == "Fog or mist").sum()

#light
Daylight_count = (df.light_conditions == "Daylight").sum()
Darkness_lit = (df.light_conditions == "Darkness - lights lit").sum()
Darkness_unlit = (df.light_conditions == "Darkness - lights unlit").sum()
Darkness_no_light = (df.light_conditions == "Darkness - no lighting").sum()

print (Fog_count) # same here, its an example

fig = go.Figure(data=go.Heatmap(
                   z=[[Daylight_count +Fine_count, Daylight_count +Fine_wind_count, Daylight_count +Rain_count,Daylight_count +Rain_wind_count, Daylight_count +Snow_count, Daylight_count +Snow_wind_count, Daylight_count +Fog_count],
                    [Darkness_lit +Fine_count, Darkness_lit +Fine_wind_count, Darkness_lit +Rain_count,Darkness_lit +Rain_wind_count, Darkness_lit +Snow_count, Darkness_lit +Snow_wind_count, Darkness_lit +Fog_count], 
                    [Darkness_unlit +Fine_count, Darkness_unlit +Fine_wind_count, Darkness_unlit +Rain_count,Darkness_unlit +Rain_wind_count, Darkness_unlit +Snow_count, Darkness_unlit +Snow_wind_count, Darkness_unlit +Fog_count], 
                    [Darkness_no_light +Fine_count, Darkness_no_light +Fine_wind_count, Darkness_no_light +Rain_count,Darkness_no_light +Rain_wind_count, Darkness_no_light +Snow_count, Darkness_no_light +Snow_wind_count, Darkness_no_light +Fog_count]],
                   x=['Fine no high winds', 'Fine + high winds', 'Raining no high winds', 'Raining + high winds', 'Snowing no high winds',  'Snowing + high winds', 'Fog or mist'],
                   y=['Daylight', 'Darkness - lights lit', 'Darkness - lights unlit', 'Darkness - no lighting'],
                   hoverongaps = False))
fig.show()