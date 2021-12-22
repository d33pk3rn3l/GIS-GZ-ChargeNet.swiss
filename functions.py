import numpy as np
import pandas as pd
import geopandas
import json
from shapely.geometry import MultiPoint
from tqdm import tqdm


def read_geojson_with_power(path_to_geojson):
    """Reads a GeoJSON with a list in one of the features

    GeoPandas does not import lists from GeoJSON. 
    We need a power list for each charging point to calculate the charging time

    Args:
        path_to_geojson (string): Path to file.

    Returns:
        df: Pandas dataframe containing all features as columns with respective data per entry
    """
    with open(path_to_geojson, "r") as infile:
        inp = json.load(infile)
    # iterate over entries
    power, rest, geom = [], [], []
    for feat in inp["features"]:
        power.append(feat["properties"]["power"])
        geometry = MultiPoint([feat["geometry"]["coordinates"][0]])
        geom.append(geometry)
        props = feat["properties"]
        rest.append([props["max_ASP_FZG"], props["max_ASP_PW"],
                    props["max_ASP_LI"], props["max_ASP_LW"], props["max_ASP_LZ"]])
    rest = np.array(rest)
    df = pd.DataFrame(rest, columns=[
                      "max_ASP_FZG", "max_ASP_PW", "max_ASP_LI", "max_ASP_LW", "max_ASP_LZ"])
    df["geometry"] = geom
    df["power"] = power
    return df


def minimizer(file, pct, what, column):
    """Minimizes the numbers in column of df by pct

    We use it to calculate how many cars are e-cars or e-cars charging.

    Args:
        file (df): A dataframe with column.
        pct (float/int): Percentage to multiply with column.
        what (str): Name of new column in df.
        column (str): Name of column in df to minimize.

    Returns:
        None
    """
    liste = []
    for i in range(len(file)):
        EAutos = file[column][i] * pct
        liste.append(EAutos)
    file[what] = liste


def charging(tankstellen, timeframe, consumption, winter, when, driven, bat_cap):
    """Calculate how many e-cars are charging based on params

    Args:
        tankstellen (gdf): Df containing all charging points with respective load (Belastung)
        winter (float): Worstcase winter, multiplicator how much capacity will be left in cold weather (0.8 => 80%)
        when (float): People charge not at zero percent state of charge
        driven (float): How many km people drive in a day by car
        bat_cap (int): Battery capacity in kWh
        consumption (int/float): Consumption of average e-car in kwh/100km

    Returns:
        None
    """
    dist = 100 * bat_cap / consumption  # 100 * kwh / (kwh / 100km)
    pct = driven / (dist * winter * when)

    minimizer(tankstellen, pct, "E-Autos_charging_" +
              timeframe, "E-Autos_" + timeframe)


def capacity(tankstellen, when, bat_cap, max_power):
    """Calculate how many e-cars can charge in an hour at each charging point with max given charging power

    When technology is quickly transformed in e-cars, the charging points will also get stronger. 
    If you pass a average charging power of 250 kW, every charging point is calculated as it is having 250 kW, despite it may not be that strong atm

    Args:
        tankstellen (gdf): Df containing all charging points with respective load (Belastung)
        when (float): People charge not at zero percent state of charge
        bat_cap (int): Battery capacity in kWh
        max_power (int/float): Average charging power for a charging process in kW

    Returns:
        list_capacity (list): List containing capacity per charging point
    """
    list_capacity = []
    for i in range(len(tankstellen["power"])):
        summe = 0
        for j in range(len(tankstellen["power"][i])):
            if max_power >= 250:
                summe += max_power
            elif tankstellen["power"][i][j] > max_power:
                summe += max_power
            else:
                summe += tankstellen["power"][i][j]
        # charges only to 80% and was at given percentage (when)
        list_capacity.append(summe/(bat_cap * (0.8 - (1 - when))))

    return list_capacity


def sufficiency(tankstellen, scenario, capacity):
    """Calculate ratio if charging point is sufficient for e cars that want to charge.

    Args:
        tankstellen (gdf): Df containing all charging points with respective load (Belastung)
        scenario (string): Name of scenario column to calculate sufficiency
        capacity (string): Name of capacity column to calculate sufficiency

    Returns:
        list_sufficiency (list): List containing sufficiency per charging point based on capacity and load
    """
    list_sufficiency = []
    for j in range(len(tankstellen)):
        list_sufficiency.append(
            tankstellen[scenario][j]/tankstellen[capacity][j])

    return list_sufficiency


def weighter(cities, tankstellen, scenario, city_weight):
    """Weight charging points in 5km vicinity of coordinates in cities based on city_weight.

    If you weigh some areas more, the rest of the charging points will get less cars (distributed in whole Switzerland)

    Args:
        cities (gdf): Df containing coordinates of important areas (cities)
        tankstellen (gdf): Df containing all charging points with respective load (Belastung)
        scenario (string): Name of scenario column to calculate sufficiency
        city_weight (int/float): Weight for area (2 for twice as many cars charge here than rest)

    Returns:
        tankstellen (df): Dataframe which has updated load of each charging point based on weight
    """
    tankstellen = geopandas.GeoDataFrame(
        tankstellen, crs="EPSG:4326", geometry=tankstellen.geometry)  # Convert df to gdf to call .cx

    in_a_city = []
    for i in range(len(tankstellen)):  # init list base case NOT in a city
        in_a_city.append(0)

    for i in range(len(cities)):
        emin, nmin, emax, nmax = cities.e[i]-5000, cities.n[i] - \
            5000, cities.e[i]+5000, cities.n[i]+5000

        # only charging points in bbox are in city (1)
        charging_in_a_city = tankstellen.cx[emin:emax, nmin:nmax]
        for point in charging_in_a_city.iterrows():
            in_a_city[point[0]] = 1
    tankstellen["in_a_city"] = in_a_city

    return weighter_multiply(tankstellen, scenario, city_weight)


def weighter_multiply(tankstellen, scenario, city_weight=1):
    """Weight charging points in 5km vicinity of coordinates in cities based on city_weight.

    This is a helper function for weighter(), which multiplies the given charging points with the given weight (default 1).

    Args:
        tankstellen (gdf): Df containing all charging points with respective load (Belastung)
        scenario (string): Name of scenario column to calculate sufficiency
        city_weight (int/float): Weight for area (2 for twice as many cars charge here than rest)

    Returns:
        tankstellen (df): Dataframe which has updated load of each charging point based on weight
    """
    sum_charging_points_in_cities = tankstellen.in_a_city.sum()
    for i in range(len(tankstellen)):
        if tankstellen["in_a_city"][i] == 1:
            tankstellen[scenario][i] = tankstellen[scenario][i] * city_weight
        else:
            # print()
            tankstellen[scenario][i] = tankstellen[scenario][i] * (len(
                tankstellen) - city_weight * sum_charging_points_in_cities) / (len(tankstellen) - sum_charging_points_in_cities)
    return tankstellen


def sufficiency_pct(start, finish, step, tankstellen, cities, consumption, winter, when, driven, bat_cap, max_power):
    """Finds the number of sufficient (sufficiency <= 1) charging points with a percentage range of e cars on roads 

    With this you can analyze how the model reacts to parameter changes with over a load range.

    Args:
        start (float): start of range
        finish (float): end of range
        step (float): step in range
        tankstellen (gdf): Df containing all charging points with respective load (Belastung)
        cities (gdf): Df containing coordinates of important areas (cities)
        winter (float): Worstcase winter, multiplicator how much capacity will be left in cold weather (0.8 => 80%)
        when (float): People charge not at zero percent state of charge
        driven (float): How many km people drive in a day by car
        bat_cap (int): Battery capacity in kWh
        consumption (int/float): Consumption of average e-car in kwh/100km
        max_power (int/float): Average charging power for a charging process in kW

    Returns:
        sufficiency_x_y (df): Dataframe which has the range in one column ("pct_of_e_cars_on_roads") and 
                              the number of sufficient charging points in an other ("sufficiency")
    """
    range_list = np.arange(start / 100, finish / 100, step / 100).tolist()
    sufficiency_x_y = pd.DataFrame()
    sufficiency_x_y["pct_of_e_cars_on_roads"] = range_list
    sufficiency_per_pct = []

    for pct in range_list:
        minimizer(tankstellen, pct, "E-Autos_" + str(pct), 'max_ASP_PW')

    tankstellen["capacity_pct"] = capacity(
        tankstellen, when, bat_cap, max_power)

    for pct in tqdm(range_list):
        charging(tankstellen, str(pct), consumption,
                 winter, when, driven, bat_cap)
        tankstellen = weighter(cities, tankstellen,
                               "E-Autos_charging_" + str(pct), city_weight=2)
        tankstellen["sufficiency_" + str(pct)] = sufficiency(
            tankstellen, "E-Autos_charging_" + str(pct), "capacity_pct")
        sum = 0
        for i in range(len(tankstellen["sufficiency_" + str(pct)])):
            if tankstellen["sufficiency_" + str(pct)][i] < 1:
                sum += 1
        sufficiency_per_pct.append(sum)

    sufficiency_x_y["sufficiency"] = sufficiency_per_pct

    return sufficiency_x_y
