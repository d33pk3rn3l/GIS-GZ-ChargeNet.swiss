import json
import geopandas

#Gefilterte Strassenverkehrszählungen, Zahlen extrahieren
#Wie? Jede Tankstelle hat Radius, nehmen Strassenabschnitt im Radius mit grösstem Peak-Hour-Wert 

with open("./Data/clipped_belastung_1000m_neu.geojson") as jsonFile:
    belastung = geopandas.read_file(jsonFile)
    jsonFile.close()

with open("./Data/clipped_tankstellen.geojson") as jsonFile:
    tankstellen = json.load(jsonFile)
    jsonFile.close()

#print(tankstellen.keys())
#print(belastung.keys())
#print(tankstellen["features"][0]["properties"])
#print(belastung["features"][1]["geometry"]["coordinates"][0][0])
#print(int(belastung["features"][1]["properties"]["ASP_PW"]))
#print(buffer["features"][0])

c=0
for tankstelle in tankstellen["features"]:
  coordinate = tankstelle["geometry"]["coordinates"][0]
  bbox = (coordinate[0]-1000, coordinate[1]-1000, coordinate[0]+1000, coordinate[1]+1000)
  belastungf = open("./Data/clipped_belastung_1000m_neu.geojson")
  gdf = geopandas.read_file(
    belastungf,
    bbox=bbox)
  if gdf.empty: print(c + 1, " of ", len(tankstellen["features"]), " bei ", tankstelle, gdf)
  tankstelle["properties"]["max_ASP_FZG"] = max(gdf.ASP_FZG)
  tankstelle["properties"]["max_ASP_PW"] = max(gdf.ASP_PW)
  tankstelle["properties"]["max_ASP_LI"] = max(gdf.ASP_LI)
  tankstelle["properties"]["max_ASP_LW"] = max(gdf.ASP_LW)
  tankstelle["properties"]["max_ASP_LZ"] = max(gdf.ASP_LZ)
  print(c + 1, " of ", len(tankstellen["features"]))

  
  # only first 10 entries because of speeeeeed
  c += 1
  #if c == 10: break

with open('./Data/tankstellen_belastung.geojson', 'w', encoding='utf-8') as f:
    json.dump(tankstellen, f, ensure_ascii=False, indent=4)

#Zahlen minimieren sodass sie den E-Autos entsprechen (Je nach Szenario anderst)
#Zahlen minimieren nach wie viele E-Autos in diesem Peak effektiv laden müssen (Schauen wie weit E-Autos kommen und wie weit sie im Schnitt fahren)--> einigung auf ca 300 km im schnitt
#Je nach grösse dieser endgültigen Zahl kann man die Belastung der E-Tankstellen an jedem Standort berechnen (Gewichtung)
#Ansatz: Addiert alle Zahlen zusammen -> Dividiert die Zahl am Standort durch die gesamt Zahl -> Bekommt Gewichtung in Prozent über -> Kann somit alle E-Autos an den verschiedenen Tankstellen verteilen
#Wieso nicht direkt die Zahlen entnehmen? Weil andere Faktoren die die Gewichtung beeinflussen noch hinzugefügt werden.
#Man schaut wie lange die E-Autos jeweils diese E-Tankstellen besetzen. -> Je nach E-Tankstellen gibt es mehrere Ladestationen mit je unterschiedlichem Ladepotenzial (abhängig von kW), demzufolge hat jede Ladestation eine andere Kapazität
#Zusammen mit der Anzahl E-Autos die eine solche Tankstelle besetzen würden, mit deren Ladedauer und mit der Kapazität der E-Tankstellen kann man berechnen ob diese Tankstellen auch wirklich genug sind (Je nach Szenario).