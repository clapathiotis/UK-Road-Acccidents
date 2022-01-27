import plotly.express as px
import pandas as pd

def get_data():
    # Read data
    df = pd.read_csv('decoded-dft-road-casualty-statistics-accident-2020.csv', low_memory=False)
    # df = df.drop(labels=["accident_index", "accident_year", "accident_reference","location_easting_osgr","location_northing_osgr","longitude","latitude","police_force","accident_severity","number_of_vehicles","number_of_casualties","date","day_of_week","local_authority_district","local_authority_ons_district","local_authority_highway","first_road_class","first_road_number","road_type","speed_limit","junction_detail","junction_control","second_road_class","second_road_number","pedestrian_crossing_human_control","pedestrian_crossing_physical_facilities","special_conditions_at_site","carriageway_hazards","urban_or_rural_area","did_police_officer_attend_scene_of_accident","trunk_road_flag","lsoa_of_accident_location"], axis=1)

    
    # Any further data preprocessing can go her
    # df = df[df["number_of_casualties"]>1]
    df = df[df["weather_conditions"] != "Other"]
    df = df[df["weather_conditions"] != "Unknown"]
    df = df[df["road_surface_conditions"] != "unknown (self reported)"]

    # For counts of accidents per weather condition
    Fog_count = (df.weather_conditions == "Fog or mist").sum() #this does nothing here just an example
    print (Fog_count) # same here, its an example
    return df
