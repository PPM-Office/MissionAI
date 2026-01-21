import requests
from geopy.geocoders import Nominatim

class missionary:
    def __init__(self, id, curArea, destination):
        self.id = id
        self.curArea = curArea
        self.destination = destination
        self.time = 0
        self.geolocator = Nominatim(user_agent="osrm_example")

    def _coordinates(self, address):
        loc = self.geolocator.geocode(address)
        if not loc:
            raise ValueError(f"Could not geocode: {address}")
        return loc.longitude, loc.latitude  # OSRM order


    def travelTime(self):
        startLon, startLat = self._coordinates(self.curArea)
        endLon, endLat = self._coordinates(self.destination)
        url = ("https://router.project-osrm.org/route/v1/driving/"f"{startLon},{startLat};{endLon},{endLat}""?overview=false")
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        self.time = data["routes"][0]["duration"] / 60

#mission list =[id, arriving, destination]
def StartThatJawn(mishList):
    missionaries = []
    for x in mishList:
        m = missionary(x[0], x[1], x[2])
        m.travelTime()
        missionaries.append()
    