import pandas as pd
import functions

with open('SZ_GIS.csv') as Szenarien:
  SZ = pd.read_csv(Szenarien)


#Zahlen minimieren sodass sie den E-Autos entsprechen (Je nach Szenario anderst)
tankstellen = functions.read_geojson_with_power('./Data/tankstellen_belastung.geojson')
#EAutos auf den Strassen
for i in range(len(SZ["Name"])): 
   
  functions.minimizer(tankstellen, SZ["pct"][i], "E-Autos " + SZ["Name"][i], 'max_ASP_PW')


#Zahlen minimieren nach wie viele E-Autos in diesem Peak effektiv laden müssen (Schauen wie weit E-Autos kommen und wie weit sie im Schnitt fahren)--> einigung auf ca 300 km im schnitt
Distanz = 300 #Wie weit E-Auto kommt im Schnitt in km
Winter = 0.7 #Worstcase Winter, Multiplikator wie weit sie dann kommen
Wann = 0.8 #E-Autos laden schon bei ca. 20% Akku
GK = 23.82 #durchschnittlich zurückgelegte Distanz pro Tag (gefahrene Km)
pct_LB = GK / (Distanz * Winter * Wann) #Wieviele Laden müssen

for i in range(len(SZ["Name"])):
  #if SZ["Name"][i] in tankstellen.columns:
  functions.minimizer(tankstellen, pct_LB, "E-Autos charging " + SZ["Name"][i], "E-Autos " + SZ["Name"][i])

#print(tankstellen)  
#Je nach grösse dieser endgültigen Zahl kann man die Belastung der E-Tankstellen an jedem Standort berechnen (Gewichtung)

#Ansatz: Addiert alle Zahlen zusammen -> Dividiert die Zahl am Standort durch die gesamt Zahl -> Bekommt Gewichtung in Prozent über -> Kann somit alle E-Autos an den verschiedenen Tankstellen verteilen
#Wieso nicht direkt die Zahlen entnehmen? Weil andere Faktoren die die Gewichtung beeinflussen noch hinzugefügt werden.

#Man schaut wie lange die E-Autos jeweils diese E-Tankstellen besetzen. -> Je nach E-Tankstellen gibt es mehrere Ladestationen mit je unterschiedlichem Ladepotenzial (abhängig von kW), demzufolge hat jede Ladestation eine andere Kapazität
DBK = 70 #Durchschittliche Batteriekapazität kWh
list_capacity = []
list_sufficiency = []
for i in range(len(tankstellen["power"])):
  summe = sum(tankstellen["power"][i])
  list_capacity.append(summe/DBK)
tankstellen["capacity"] = list_capacity


#Zusammen mit der Anzahl E-Autos die eine solche Tankstelle besetzen würden, mit deren Ladedauer und mit der Kapazität der E-Tankstellen kann man berechnen ob diese Tankstellen auch wirklich genug sind (Je nach Szenario).
for j in range(len(tankstellen)):
  list_sufficiency.append(tankstellen["capacity"][j]/tankstellen["E-Autos charging Today"][j])

tankstellen["sufficiency"] = list_sufficiency

print(tankstellen[tankstellen.sufficiency < 1].count())
print(tankstellen[tankstellen.sufficiency >= 1].count())
  