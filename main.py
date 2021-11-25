import json

with open("ladestellenbig.json") as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()
    
#print(jsonObject["["])

newi = jsonObject["EVSEData"]
#print(jsonObject)

newvii = dict()
#print(newi[0])
for x in range(len(newi)):

    newii = newi[x]
    newiii = newii['EVSEDataRecord']
    for y in range(len(newiii)):
        newiiii = newiii[y]
        newv  = newiiii["ChargingFacilities"]
        
        if(newv != None):
          #print(newv[0])
          for z in range(len(newv)):
              newvi = newv[z]
              for key in newvi:
                  #print(newvi["power"])
                  #if type(newvi["power"]) == str:
                    #print(newvi["power"])
        
                  if (float(newvi["power"]) >= 50):
                        a = newiiii['GeoCoordinates']
                        b = a["Google"]
                        c = float(newvi["power"])
                        d = []
                        if b in newvii:
                          newvii[b].append(c)
                        else:
                          newvii[b] = [c]

with open('cleaned.json', 'w', encoding='utf-8') as f:
    json.dump(newvii, f, ensure_ascii=False, indent=4)