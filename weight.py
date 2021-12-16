import pandas as pd

with open("./Data/bevoelkerung.csv") as csv:
    pop = pd.read_csv(csv, delimiter=";")
    csv.close()

pop.drop(pop[pop.VARIABLE != "pop2019"].index, inplace=True)

pop.drop(["GEONR", "CLASS_HAB", "VARIABLE", "STATUS"], inplace=True, axis = 1)
pop.drop(pop[pop.GEONAME == "Schweiz / Suisse"].index, inplace=True)
print(len(pop))
print(pop.columns)


pop.drop(pop[pop.VALUE <= 50000].index, inplace=True)
print(pop)

"""for population in pop.VALUE:
  if population < 500000: 
    pop.drop(pop.VALUE[, inplace=True)
print(pop)"""
