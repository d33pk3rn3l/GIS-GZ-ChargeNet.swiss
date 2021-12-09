import pandas as pd
from IPython.display import display

with open("./Data/bevoelkerung.csv") as csv:
    pop = pd.read_csv(csv, delimiter=";")
    csv.close()

pop.drop(pop[pop.VARIABLE != "pop2019"].index, inplace=True)