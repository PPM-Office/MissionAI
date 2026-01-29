import weird_dijstra
import json

areasjson = []
missionariesjson = []
newareasjson = []
newmissionariesjson = []

with open('data/areas.json', 'r') as l:
    areasjson = json.load(l)

with open('data/missionaries.json', 'r') as f:
    missionariesjson = json.load(f)

with open('data/newareas.json', 'r') as a:
    newareasjson = json.load(a)

with open('data/newmissionaries.json', 'r') as m:
    newmissionariesjson = json.load(m)

broomall = "721 paxton hollow rd, Broomall, PA, USA"
locList = []
eldmishList = []
eldveList = []
sismishList = []
sisveList = []
x=0

for i in missionariesjson:
    if not (i['statusCode'] == "IN_FIELD"):
        x+=1
        continue
    elif i['district'] in ('Service Missionaries',None):
        x+=1
        continue
    elif i['missTypeCode'] in ('ELDER','SISTER'):
        pass
    else:
        x+=1
        continue
    thing = i['normalizedHouseAddress'] +', '+ i['houseCity'] +', '+ i['houseState'] +', USA'
    if newmissionariesjson[x]['email'] != i['email']:
        x=0
    while newmissionariesjson[x]['email'] != i['email']:
        x+=1
    dest = ''
    if not newmissionariesjson[x]['district']:
        dest = broomall
    else:
        dest = newmissionariesjson[x]['normalizedHouseAddress'] +', '+ newmissionariesjson[x]['houseCity'] +', '+ newmissionariesjson[x]['houseState'] +', USA'
    othing = weird_dijstra.Missionary(i['email'],thing,dest)
    if i['missTypeCode'] == 'ELDER':
        eldmishList.append(othing)
    elif i['missTypeCode'] == 'SISTER':
        sismishList.append(othing)
    x+=1

x=0
for i in areasjson:
    if i['house'] is None:
        x+=1
        continue
    thing = i['house']['normalizedAddress'] +', '+ i['house']['city'] +', '+ i['house']['state'] +', USA'
    dest = thing
    rthing = weird_dijstra.Location(thing)
    locList.append(rthing)
    if i['vehicle'] is None:
        x+=1
        continue
    elif len(i['missionaries']) == 0:
        x+=1
        continue
    elif i['missionaries'][0]['missionaryType'] in ('ELDER', 'SISTER'):
        pass
    else:
        x+=1
        continue
    othing = weird_dijstra.Vehicle(i['vehicle']['ccId'],4,thing,dest)
    
    if i['missionaries'][0]['missionaryType'] == 'ELDER':
        eldveList.append(othing)
    elif i['missionaries'][0]['missionaryType'] == 'SISTER':
        sisveList.append(othing)
    x+=1

locList.append(weird_dijstra.Location(broomall,True, True))

f.close()
l.close()
a.close()
m.close()

weird_dijstra.StartThatJawn(eldmishList, eldveList, locList)
