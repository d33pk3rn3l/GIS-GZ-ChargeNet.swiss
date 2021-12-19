import pandas as pd
import functions
import numpy as np
import matplotlib.pyplot as plt

with open('SZ_GIS.csv') as Szenarien:
  SZ = pd.read_csv(Szenarien)

with open('Data/city_coords_pop.csv') as file:
  cities = pd.read_csv(file)

  
#Zahlen minimieren sodass sie den E-Autos entsprechen (Je nach Szenario anderst)
tankstellen = functions.read_geojson_with_power('./Data/tankstellen_belastung.geojson')
#EAutos auf den Strassen
for i in range(len(SZ["Name"])): 
  functions.minimizer(tankstellen, SZ["pct"][i], "E-Autos_" + SZ["Name"][i], 'max_ASP_PW')

#how many charge
#for timeframe in SZ["Name"]:
#    functions.charging(tankstellen, timeframe, "E-Autos charging " + timeframe, "E-Autos " + timeframe)
    #print(pct)

#Zahlen minimieren nach wie viele E-Autos in diesem Peak effektiv laden müssen (Schauen wie weit E-Autos kommen und wie weit sie im Schnitt fahren)--> einigung auf ca 300 km im schnitt (def capacity(tankstellen, SZ, consumption_per100km, winter, when, driven, bat_cap, max_power))
functions.charging(tankstellen, "Today", 25, 0.7, 0.8, 23.82, 70)
tankstellen["capacity_today"] = functions.capacity(tankstellen, 0.7, 70, 100)
tankstellen = functions.weighter(cities, tankstellen, "E-Autos_charging_Today", city_weight = 2)
tankstellen["sufficiency_today"] = functions.sufficiency(tankstellen, "E-Autos_charging_Today", "capacity_today")

functions.charging(tankstellen, "BAU", 20, 0.8, 0.8, 25, 140)
tankstellen["capacity_BAU"] = functions.capacity(tankstellen, 0.8, 140, 150) #weniger Geld in Technologie wegen weniger use, tiefere Kapazitäten / Reichweite
tankstellen = functions.weighter(cities, tankstellen, "E-Autos_charging_BAU", city_weight = 2)
tankstellen["sufficiency_BAU"] = functions.sufficiency(tankstellen, "E-Autos_charging_BAU", "capacity_BAU")

functions.charging(tankstellen, "ZERO", 20, 0.8, 0.8, 25, 150)
tankstellen["capacity_zero"] = functions.capacity(tankstellen, 0.8, 150, 200) 
tankstellen = functions.weighter(cities, tankstellen, "E-Autos_charging_ZERO", city_weight = 2)
tankstellen["sufficiency_ZERO"] = functions.sufficiency(tankstellen, "E-Autos_charging_ZERO", "capacity_zero")

functions.charging(tankstellen, "ZERO_E", 20, 0.8, 0.8, 25, 150)
tankstellen["capacity_zero_e"] = functions.capacity(tankstellen, 0.8, 200, 200) #Reichweite & bat_cap deutlich höher (20kWh / 100km => 200 kWh Kapa), Winter bessere Akku, gefahrene km höher (BFS +7% auf 2050)
tankstellen = functions.weighter(cities, tankstellen, "E-Autos_charging_ZERO_E", city_weight = 2)
tankstellen["sufficiency_ZERO_E"] = functions.sufficiency(tankstellen, "E-Autos_charging_ZERO_E", "capacity_zero_e")

#plot a graph where the sufficiency is subordinate to the pct of e cars, pass start, finish and step in percentage
sufficiency_pct = functions.sufficiency_pct(0.5, 20, 0.1, tankstellen, cities, SZ, 25, 0.7, 0.8, 23.82, 70, 100)
#sufficiency_pct.plot(x = "pct_of_e_cars_on_roads", y = "sufficiency")
#sufficiency_pct.plot()
plt.plot(sufficiency_pct["pct_of_e_cars_on_roads"]*100, sufficiency_pct["sufficiency"])
plt.xlabel("% an E-Autos aller Autos")
plt.ylabel("Ausreichende Ladestationen")

plt.show()
#print(tankstellen)  
#Je nach grösse dieser endgültigen Zahl kann man die Belastung der E-Tankstellen an jedem Standort berechnen (Gewichtung)

#Ansatz: Addiert alle Zahlen zusammen -> Dividiert die Zahl am Standort durch die gesamt Zahl -> Bekommt Gewichtung in Prozent über -> Kann somit alle E-Autos an den verschiedenen Tankstellen verteilen
#Wieso nicht direkt die Zahlen entnehmen? Weil andere Faktoren die die Gewichtung beeinflussen noch hinzugefügt werden.

#Man schaut wie lange die E-Autos jeweils diese E-Tankstellen besetzen. -> Je nach E-Tankstellen gibt es mehrere Ladestationen mit je unterschiedlichem Ladepotenzial (abhängig von kW), demzufolge hat jede Ladestation eine andere Kapazität
# DBK = 70 #Durchschittliche Batteriekapazität kWh

#Zusammen mit der Anzahl E-Autos die eine solche Tankstelle besetzen würden, mit deren Ladedauer und mit der Kapazität der E-Tankstellen kann man berechnen ob diese Tankstellen auch wirklich genug sind (Je nach Szenario).
#E-Autos charging Today     
#E-Autos charging BAU       
#E-Autos charging ZERO      
#E-Autos charging ZERO E 


#print(tankstellen.sufficiency_today)
#print("sufficient t",tankstellen[tankstellen.sufficiency_today < 1].count().sufficiency_today)
#print("sufficient b",tankstellen[tankstellen.sufficiency_BAU < 1].count().sufficiency_BAU)
#print("sufficient z",tankstellen[tankstellen.sufficiency_ZERO < 1].count().sufficiency_ZERO)
#print("sufficient ze",tankstellen[tankstellen.sufficiency_ZERO_E < 1].count().sufficiency_ZERO_E)
#print(tankstellen[tankstellen.sufficiency_ZERO_E < 1].geometry)
#print(tankstellen[tankstellen.sufficiency_model_1 >= 1].count())
#print(tankstellen.sufficiency_model_1)
#print(sum(tankstellen.sufficiency_ZERO_E)/237)

tankstellen.drop(["power"], inplace=True, axis = 1)

tankstellen.to_file("./Data/Export/tankstellen_sufficency_models.geojson", driver = "GeoJSON")