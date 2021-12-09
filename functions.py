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