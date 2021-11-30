from numpy import true_divide
import plotly.express as px
import pandas as pd
df = pd.read_csv(r'dft-road-casualty-statistics-accident-2020.csv', delimiter=',')

# df = df[["BreathAlcoholLevel(microg/100ml)", "AgeBand"]]
# df.drop(df[df["BreathAlcoholLevel(microg/100ml)"]>500].index)

# print(df.head(5))

# fig = px.bar(df, x="BreathAlcoholLevel(microg/100ml)", y="AgeBand", title="dis")
# fig.show()

df = df[["speed_limit", "number_of_casualties", "day_of_week"]]
df = df[df["number_of_casualties"] > 5]
# df.drop(df[df["BreathAlcoholLevel(microg/100ml)"]>500].index)

print(df.head(5))

fig = px.bar(df, x="day_of_week", y="number_of_casualties", color = 'number_of_casualties',
                labels={'number_of_casualties':'Number of Casualties', 'day_of_week' : 'Day of the Week: Monday to Sunday'}, title="dis")
fig.show()