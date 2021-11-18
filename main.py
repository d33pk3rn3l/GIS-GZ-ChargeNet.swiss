import json

with open("ladestellenbig.json") as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()
    
#print(jsonObject["["])

newi = jsonObject["EVSEData"]
#print(jsonObject)

newvii = []
#print(newi[0])
for x in range(len(newi)):

    newii = newi[x]
    newiii = newii['EVSEDataRecord']
    for y in range(len(newiii)):
        newiiii = newiii[y]
        newv  = newiiii["ChargingFacilities"]
        if(newv != None):
            for z in range(len(newv)):
                newvi = newv[z]
                for key in newvi:
                    if(key == "power" and type(newvi["power"]) != str):
                        if (newvi["power"] >= 50):
                            a = newiiii['GeoCoordinates']
                            b = a["Google"]
                            c = newvi["power"]
                            d = []
                            #for b in newvi:
                            
                              
                            newvii.append({b : [c]})
                            
                            
                            #print(newiiii['GeoCoordinates'])
                            #print(newiiii["ChargingFacilities"])
#print(newvii)

with open('cleaned.json', 'w', encoding='utf-8') as f:
    json.dump(newvii, f, ensure_ascii=False, indent=4)