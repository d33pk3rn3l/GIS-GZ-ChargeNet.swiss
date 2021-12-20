import pandas as pd
import functions
import matplotlib.pyplot as plt


""" Prepare for calculation, initialize all data """
# Scenarios for how many e cars drive on Swiss roads
with open('Data/SZ_GIS.csv') as Szenarien:
    SZ = pd.read_csv(Szenarien)

# Cities with more than 50'000 inhabitants get a different weight
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

# Scenario 2 - slow linear increase of cars as today
timeframe = "BAU"
consumption = 20
winter = 0.8
when = 0.8
driven = 25
bat_cap = 140
max_power = 200
functions.charging(tankstellen, timeframe, consumption,
                   winter, when, driven, bat_cap)
# weniger Geld in Technologie wegen weniger use, tiefere Kapazitäten / Reichweite
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

# Scenario 4 - no gas cars are on road, 100% e-cars
timeframe = "ZERO_E"
consumption = 20
winter = 0.8
when = 0.8
driven = 25
bat_cap = 150
max_power = 200
# Reichweite & bat_cap deutlich höher (20kWh / 100km => 200 kWh Kapa), Winter bessere Akku, gefahrene km höher (BFS +7% auf 2050)
functions.charging(tankstellen, timeframe, consumption,
                   winter, when, driven, bat_cap)
tankstellen["capacity_zero_e"] = functions.capacity(
    tankstellen, when, bat_cap, max_power)
tankstellen = functions.weighter(
    cities, tankstellen, "E-Autos_charging_ZERO_E", city_weight=2)
tankstellen["sufficiency_ZERO_E"] = functions.sufficiency(
    tankstellen, "E-Autos_charging_ZERO_E", "capacity_zero_e")

"""
# plot a graph where the sufficiency is subordinate to the pct of e cars, pass start, finish and step in percentage
start, finish, step = 1,100,1
sufficiency_pct = functions.sufficiency_pct(
    start, finish, step, tankstellen, cities, SZ, 25, 0.7, 0.8, 23.82, 70, 100)
sufficiency_pct_2 = functions.sufficiency_pct(
    start, finish, step, tankstellen, cities, SZ, 25, 0.7, 0.8, 23.82, 70, 300)
sufficiency_pct_3 = functions.sufficiency_pct(
    start, finish, step, tankstellen, cities, SZ, 15, 0.7, 0.8, 23.82, 70, 100)
sufficiency_pct_4 = functions.sufficiency_pct(
    start, finish, step, tankstellen, cities, SZ, 25, 0.7, 0.95, 23.82, 70, 100)

# Plotting
plt.plot(sufficiency_pct["pct_of_e_cars_on_roads"] * 100, sufficiency_pct["sufficiency"], label="Model Today")
plt.plot(sufficiency_pct_2["pct_of_e_cars_on_roads"] * 100, sufficiency_pct_2["sufficiency"], label="300 kW Leistung schweizweit")
plt.plot(sufficiency_pct_3["pct_of_e_cars_on_roads"] * 100, sufficiency_pct_3["sufficiency"], label="Verbrauch 15 kwh/100 km")
plt.plot(sufficiency_pct_4["pct_of_e_cars_on_roads"] * 100, sufficiency_pct_4["sufficiency"], label="Laden erst bei 5%")

# Labelling
plt.title("Vergleich Modell 'Today' mit Parametern")
plt.xlabel("% an E-Autos aller PKW")
plt.ylabel("Ausreichende Ladestationen (Auslastung <=1)")
plt.legend()

plt.savefig("Data/Export/comparison_parameters_today.png", dpi=240)

# print(tankstellen)
# Je nach grösse dieser endgültigen Zahl kann man die Belastung der E-Tankstellen an jedem Standort berechnen (Gewichtung)

# Ansatz: Addiert alle Zahlen zusammen -> Dividiert die Zahl am Standort durch die gesamt Zahl -> Bekommt Gewichtung in Prozent über -> Kann somit alle E-Autos an den verschiedenen Tankstellen verteilen
# Wieso nicht direkt die Zahlen entnehmen? Weil andere Faktoren die die Gewichtung beeinflussen noch hinzugefügt werden.

# Man schaut wie lange die E-Autos jeweils diese E-Tankstellen besetzen. -> Je nach E-Tankstellen gibt es mehrere Ladestationen mit je unterschiedlichem Ladepotenzial (abhängig von kW), demzufolge hat jede Ladestation eine andere Kapazität
# DBK = 70 #Durchschittliche Batteriekapazität kWh

# Zusammen mit der Anzahl E-Autos die eine solche Tankstelle besetzen würden, mit deren Ladedauer und mit der Kapazität der E-Tankstellen kann man berechnen ob diese Tankstellen auch wirklich genug sind (Je nach Szenario).
# E-Autos charging Today
# E-Autos charging BAU
# E-Autos charging ZERO
# E-Autos charging ZERO E"""

# print(tankstellen.sufficiency_today)
print("sufficient t",tankstellen[tankstellen.sufficiency_today < 1].count().sufficiency_today)
print("sufficient b",tankstellen[tankstellen.sufficiency_BAU < 1].count().sufficiency_BAU)
print("sufficient z",tankstellen[tankstellen.sufficiency_ZERO < 1].count().sufficiency_ZERO)
print("sufficient ze",tankstellen[tankstellen.sufficiency_ZERO_E < 1].count().sufficiency_ZERO_E)
#print(max(tankstellen.sufficiency_ZERO_E))
#print(tankstellen[tankstellen.sufficiency_BAU < 1].geometry)
#print(tankstellen[tankstellen.sufficiency_model_1 >= 1].count())
# print(tankstellen.sufficiency_model_1)
# print(sum(tankstellen.sufficiency_ZERO_E)/237)

tankstellen.drop(["power"], inplace=True, axis=1)

tankstellen.to_file(
    "./Data/Export/tankstellen_sufficency_models.geojson", driver="GeoJSON")

