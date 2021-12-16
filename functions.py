import math
import numpy as np
import pandas as pd
import geopandas
import json
from shapely.geometry import MultiPoint

def read_geojson_with_power(path_to_geojson):
    with open(path_to_geojson, "r") as infile:
        inp = json.load(infile)
    # iterate over entries
    power, rest, geom = [], [], []
    for feat in inp["features"]:
        power.append(feat["properties"]["power"])
        geometry = MultiPoint([feat["geometry"]["coordinates"][0]])
        geom.append(geometry)
        props = feat["properties"]
        rest.append([props["max_ASP_FZG"], props["max_ASP_PW"], props["max_ASP_LI"], props["max_ASP_LW"], props["max_ASP_LZ"]])
    rest = np.array(rest)   
    df = pd.DataFrame(rest, columns = ["max_ASP_FZG", "max_ASP_PW", "max_ASP_LI", "max_ASP_LW", "max_ASP_LZ"])
    df["geometry"] = geom
    df["power"] = power
    return df

def minimizer(file, pct, what, column): 
  liste = []
  for i in range(len(file)):
    EAutos = file[column][i] * pct
    liste.append(EAutos)
  file[what] = liste

def capacity(tankstellen, SZ, consumption, winter, when, driven, bat_cap, max_power):
  #dist = Wie weit E-Auto kommt im Schnitt in km
  #winter = Worstcase Winter, Multiplikator wie weit sie dann kommen
  #when E-Autos laden schon bei ca. 20% Akku
  #driven durchschnittlich zurückgelegte Distanz pro Tag in km
  #bat_cap = 70 #Durchschittliche Batteriekapazität kWh
  #SZ = Szenarien
  #bat_cap = battery capacity EAutos
  dist = 100 * bat_cap / consumption #100 * kwh / (kwh / 100km)
  pct = driven / (dist * winter * when) 
  
  for timeframe in SZ["Name"]:
    minimizer(tankstellen, pct, "E-Autos charging " + timeframe, "E-Autos " + timeframe)
  
  list_capacity = []
  for i in range(len(tankstellen["power"])):
    summe = 0
    for j in range(len(tankstellen["power"][i])):
      if max_power >=250:
        summe += max_power
      elif tankstellen["power"][i][j] > max_power:
        summe += max_power
      else:
        summe += tankstellen["power"][i][j]
    list_capacity.append(summe/(bat_cap * (0.8 - (1 - when)))) #charges only to 80% and was at given percentage (when)
  
  #tankstellen["capacity"] = list_capacity
  
  return list_capacity

def sufficiency(tankstellen, scenario, capacity):
  list_sufficiency = []
  for j in range(len(tankstellen)):
    list_sufficiency.append(tankstellen[scenario][j]/tankstellen[capacity][j])
    
  return list_sufficiency

def weighter(cities, tankstellen, scenario, city_weight):
  #print(tankstellen.geometry)
  tankstellen = geopandas.GeoDataFrame(tankstellen, crs="EPSG:4326", geometry=tankstellen.geometry)
  #print(tankstellen)
  in_a_city = []
  for i in range(len(tankstellen)):
    in_a_city.append(0) #print(tankstellen["in_a_city"])

  for i in range(len(cities)):
    emin, nmin, emax, nmax = cities.e[i]-5000, cities.n[i]-5000, cities.e[i]+5000, cities.n[i]+5000
    
      #print(tankstellen)
      #charging_in_a_city = tankstellen.feature.geometry.coordinates.cx[emin:emax, nmin:nmax]
      #print(charging_in_a_city)
    
    charging_in_a_city = tankstellen.cx[emin:emax, nmin:nmax]
    #print(charging_in_a_city)
    for point in charging_in_a_city.iterrows():
      in_a_city[point[0]] = 1
  tankstellen["in_a_city"] = in_a_city
  #print(tankstellen.in_a_city.sum())
  return weighter_multiply(tankstellen, scenario, city_weight)
  
  

  #take number of the cars driving by the charging points and multiply them by the weighter
def weighter_multiply(tankstellen, scenario, city_weight = 1):
  #print(tankstellen.columns)
  sum_charging_points_in_cities = tankstellen.in_a_city.sum()
  for i in range(len(tankstellen)):
    if tankstellen["in_a_city"][i] == 1:
      tankstellen[scenario][i] = tankstellen[scenario][i] * city_weight
    else:
      #print()
      tankstellen[scenario][i] = tankstellen[scenario][i] * (len(tankstellen) - city_weight * sum_charging_points_in_cities) / (len(tankstellen) - sum_charging_points_in_cities)
    #print(tankstellen["E-Autos charging Today"][i])
  #print("from weigher",tankstellen["E-Autos charging Today"])
  return tankstellen

#weighter: every charging point has a weight of 237 * 1/237 (same weighing), we erase that and say if its in a city it gets a weight of city_weight and the rest percentage which isnt in the cities gets distributed equally ((237 - city_weight * 10) / 237)