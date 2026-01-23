import weird_dijstra
import json

areasjson = []
missionariesjson = []

with open('data/areas.json', 'r') as l:
    areasjson = json.load(l)

with open('data/missionaries.json', 'r') as f:
    missionariesjson = json.load(f)

broomall = "721 paxton hollow rd Broomall PA"
eldlocList = []
eldmishList = []
eldveList = []
sislocList = []
sismishList = []
sisveList = []

for i in missionariesjson:
    if not (i['statusCode'] == "IN_FIELD"):
        continue
    elif i['district'] in ('Service Missionaries',None):
        continue
    elif i['missTypeCode'] in ('SENIOR_COUPLE_ELDER', 'SENIOR_COUPLE_SISTER', 'SENIOR_ELDER', 'SENIOR_SISTER'):
        continue
    thing = i['normalizedHouseAddress'] +' '+ i['houseCity'] +' '+ i['houseState']
    othing = weird_dijstra.Missionary(i['email'],thing)
    if i['missTypeCode'] == 'ELDER':
        eldmishList.append(othing)
    elif i['missTypeCode'] == 'SISTER':
        sismishList.append(othing)

for i in areasjson:
    if i['vehicle'] is None:
        continue
    elif len(i['missionaries']) == 0:
        continue
    elif i['missionaries'][0]['missionaryType'] is ('SENIOR_COUPLE_ELDER' or 'SENIOR_COUPLE_SISTER'):
        continue
    thing = i['house']['normalizedAddress'] +' '+ i['house']['city'] +' '+ i['house']['state']
    othing = weird_dijstra.Vehicle(i['vehicle']['vehicleId'],4,thing)
    rthing = weird_dijstra.Location(thing)
    if i['missionaries'][0]['missionaryType'] == 'ELDER':
        eldveList.append(othing)
        eldlocList.append(rthing)
    elif i['missionaries'][0]['missionaryType'] == 'SISTER':
        sisveList.append(othing)
        sislocList.append(rthing)

sislocList.append(weird_dijstra.Location(broomall,True, True))
eldlocList.append(weird_dijstra.Location(broomall,True, True))

f.close()
l.close()
    