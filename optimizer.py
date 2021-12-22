import pandas as pd
import functions
import matplotlib.pyplot as plt
import folium
from folium import plugins
import branca


""" Prepare for calculation, initialize all data """
# Scenarios for how many e cars drive on Swiss roads
with open('Data/SZ_GIS.csv') as Szenarien:
    SZ = pd.read_csv(Szenarien)

# Cities with more than 50'000 inhabitants get a different weight, import the cities
with open('Data/city_coords_pop.csv') as file:
    cities = pd.read_csv(file)

# Get all charging points in CH in vicinity of a ramp onto or off the "Nationalstrassenachsen"
tankstellen = functions.read_geojson_with_power(
    './Data/tankstellen_belastung.geojson')

# Multiply the the number of cars in traffic hour (17-1800) by scenario percentage of e-cars on Swiss roads
for i in range(len(SZ["Name"])):
    functions.minimizer(
        tankstellen, SZ["pct"][i], "E-Autos_" + SZ["Name"][i], 'max_ASP_PW')


""" Calculate the different scenarios """
# Scenario 1 - Situation today
timeframe = "Today"
consumption = 25
winter = 0.7
when = 0.8
driven = 23.82
bat_cap = 70
max_power = 100
functions.charging(tankstellen, timeframe, consumption,
                   winter, when, driven, bat_cap)
tankstellen["capacity_today"] = functions.capacity(
    tankstellen, when, bat_cap, max_power)
tankstellen = functions.weighter(
    cities, tankstellen, "E-Autos_charging_Today", city_weight=2)
tankstellen["sufficiency_today"] = functions.sufficiency(
    tankstellen, "E-Autos_charging_Today", "capacity_today")

# All the following scenarios have more km (BFS +7% in 2050) and better batteries in winter (80% range), they also charge quicker (max. 200 kW)
# Scenario 2 - slow linear increase of cars as today. Less money in technology therefore lower capacities / range
timeframe = "BAU"
consumption = 20
winter = 0.8
when = 0.8
driven = 25
bat_cap = 140
max_power = 200
functions.charging(tankstellen, timeframe, consumption,
                   winter, when, driven, bat_cap)
tankstellen["capacity_BAU"] = functions.capacity(
    tankstellen, when, bat_cap, max_power)
tankstellen = functions.weighter(
    cities, tankstellen, "E-Autos_charging_BAU", city_weight=2)
tankstellen["sufficiency_BAU"] = functions.sufficiency(
    tankstellen, "E-Autos_charging_BAU", "capacity_BAU")

# Scenario 3 - high usage e cars
timeframe = "ZERO"
consumption = 20
winter = 0.8
when = 0.8
driven = 25
bat_cap = 150
max_power = 200
functions.charging(tankstellen, timeframe, consumption,
                   winter, when, driven, bat_cap)
tankstellen["capacity_zero"] = functions.capacity(
    tankstellen, when, bat_cap, max_power)
tankstellen = functions.weighter(
    cities, tankstellen, "E-Autos_charging_ZERO", city_weight=2)
tankstellen["sufficiency_ZERO"] = functions.sufficiency(
    tankstellen, "E-Autos_charging_ZERO", "capacity_zero")

# Scenario 4 - no gas cars are on road, 100% e-cars. Range / capacity higher
timeframe = "ZERO_E"
consumption = 20
winter = 0.8
when = 0.8
driven = 25
bat_cap = 150
max_power = 200
functions.charging(tankstellen, timeframe, consumption,
                   winter, when, driven, bat_cap)
tankstellen["capacity_zero_e"] = functions.capacity(
    tankstellen, when, bat_cap, max_power)
tankstellen = functions.weighter(
    cities, tankstellen, "E-Autos_charging_ZERO_E", city_weight=2)
tankstellen["sufficiency_ZERO_E"] = functions.sufficiency(
    tankstellen, "E-Autos_charging_ZERO_E", "capacity_zero_e")


#""" Plot a graph where the sufficiency is subordinate to the pct of e cars, pass start, finish and step in percentage """
#start, finish, step = 1, 100, 1
#sufficiency_pct = functions.sufficiency_pct(
#    start, finish, step, tankstellen, cities, 25, 0.7, 0.8, 23.82, 70, 100)
#sufficiency_pct_2 = functions.sufficiency_pct(
#    start, finish, step, tankstellen, cities, 25, 0.7, 0.8, 23.82, 70, 300)
#sufficiency_pct_3 = functions.sufficiency_pct(
#    start, finish, step, tankstellen, cities, 15, 0.7, 0.8, 23.82, 70, 100)
#sufficiency_pct_4 = functions.sufficiency_pct(
#    start, finish, step, tankstellen, cities, 25, 0.7, 0.95, 23.82, 70, 100)
#
## Plotting
#plt.plot(sufficiency_pct["pct_of_e_cars_on_roads"] * 100,
#         sufficiency_pct["sufficiency"], label="Model Today")
#plt.plot(sufficiency_pct_2["pct_of_e_cars_on_roads"] * 100,
#         sufficiency_pct_2["sufficiency"], label="300 kW Leistung schweizweit")
#plt.plot(sufficiency_pct_3["pct_of_e_cars_on_roads"] * 100,
#         sufficiency_pct_3["sufficiency"], label="Verbrauch 15 kwh/100 km")
#plt.plot(sufficiency_pct_4["pct_of_e_cars_on_roads"] * 100,
#         sufficiency_pct_4["sufficiency"], label="Laden erst bei 5%")
#
## Labelling
#plt.title("Vergleich Modell 'Today' mit Parametern")
#plt.xlabel("% an E-Autos aller PKW")
#plt.ylabel("Ausreichende Ladestationen (Auslastung <=1)")
#plt.legend()
#
#plt.savefig("Data/Export/comparison_parameters_today.png", dpi=240)
#
## Short overview of the scenarios sufficient charging points
#print("sufficient t",
#      tankstellen[tankstellen.sufficiency_today <= 1].count().sufficiency_today)
#print("sufficient b",
#      tankstellen[tankstellen.sufficiency_BAU <= 1].count().sufficiency_BAU)
#print("sufficient z",
#      tankstellen[tankstellen.sufficiency_ZERO <= 1].count().sufficiency_ZERO)
#print("sufficient ze",
#      tankstellen[tankstellen.sufficiency_ZERO_E <= 1].count().sufficiency_ZERO_E)
#
## Get coordinates of sufficient charging points in BAU
#print(tankstellen[tankstellen.sufficiency_BAU < 1].geometry)


tankstellen = tankstellen.set_crs(epsg=2056, allow_override=True)
tankstellen = tankstellen.to_crs(epsg=4326)

colorscale = branca.colormap.linear.YlOrRd_09.scale(0, 50e3)

def sufficient_color(feature):
    sufficient = tankstellen["sufficiency_today"]
    return {"color": "#green" if sufficient <= 1 else colorscale(sufficient)}

m = folium.Map(
    location=[46.87, 8.3],
    tiles="openstreetmap",
    zoom_start=8,
)

def color_producer(suff):
    if suff <= 0.8:
        return 'green'
    elif 0.8 <= suff <= 1:
        return 'lightgreen'
    elif 1 < suff < 1.5:
        return 'orange'
    elif 1.5 <= suff < 10:
        return "red"
    elif 10 <= suff < 100:
        return "purple"
    else:
        return "black"

tk_today = folium.FeatureGroup(name = "Tankstellen Today")
tk_b = folium.FeatureGroup(name = "Tankstellen Business as usual", show=False)
tk_z = folium.FeatureGroup(name = "Tankstellen ZERO", show=False)
tk_ze = folium.FeatureGroup(name = "Tankstellen ZERO E", show=False)

for i in range(len(tankstellen)):
    y = tankstellen['geometry'][i][0].x
    x = tankstellen['geometry'][i][0].y
    suff = tankstellen["sufficiency_today"][i]
    folium.Marker([x,y], popup="Auslastung (eg. 0.5 => 50%): " + str(round(suff,3)), icon=folium.Icon(color=color_producer(suff), icon="flash", icon_color='#FFFFFF')).add_to(tk_today)

for i in range(len(tankstellen)):
    y = tankstellen['geometry'][i][0].x
    x = tankstellen['geometry'][i][0].y
    suff = tankstellen["sufficiency_BAU"][i]
    folium.Marker([x,y], popup="Auslastung (eg. 0.5 => 50%): " + str(round(suff,3)), icon=folium.Icon(color=color_producer(suff), icon="flash", icon_color='#FFFFFF')).add_to(tk_b)

for i in range(len(tankstellen)):
    y = tankstellen['geometry'][i][0].x
    x = tankstellen['geometry'][i][0].y
    suff = tankstellen["sufficiency_ZERO"][i]
    folium.Marker([x,y], popup="Auslastung (eg. 0.5 => 50%): " + str(round(suff,3)), icon=folium.Icon(color=color_producer(suff), icon="flash", icon_color='#FFFFFF')).add_to(tk_z)

for i in range(len(tankstellen)):
    y = tankstellen['geometry'][i][0].x
    x = tankstellen['geometry'][i][0].y
    suff = tankstellen["sufficiency_ZERO_E"][i]
    folium.Marker([x,y], popup="Auslastung (eg. 0.5 => 50%): " + str(round(suff,3)), icon=folium.Icon(color=color_producer(suff), icon="flash", icon_color='#FFFFFF')).add_to(tk_ze)


x,y = [],[]
for i in range(len(tankstellen)):
    y.append(tankstellen['geometry'][i][0].x)
    x.append(tankstellen['geometry'][i][0].y)
lat_long = list(zip(x,y))


m.add_child(tk_today)
m.add_child(tk_b)
m.add_child(tk_z)
m.add_child(tk_ze)

plugins.HeatMap(lat_long).add_to(folium.FeatureGroup(name="Tankstellendichte", show=False).add_to(m))

m.add_child(folium.LayerControl())
m.save("map.html")

# GeoJSON driver of geopandas does not support lists for export, drop it
tankstellen.drop(["power"], inplace=True, axis=1)

# Export as GeoJSON
tankstellen.to_file(
    "./Data/Export/tankstellen_sufficency_models.geojson", driver="GeoJSON")
