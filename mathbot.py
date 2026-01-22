import requests
from geopy.geocoders import Nominatim

class Location:
    def __init__(self, address, state):
        self.address = address
        self.state = state
        self.issafe = False
        if address == "721 paxton hollow rd Broomall PA":
            self.issafe = True
        self.geolocator = Nominatim(user_agent="osrm_example")

    def _coordinates(self, address):
        loc = self.geolocator.geocode(address)
        if not loc:
            raise ValueError(f"Could not geocode: {address}")
        return loc.longitude, loc.latitude  # OSRM order
        

class Vehicle:
    def __init__(self, id, capcity, curArea, destination, missionaries):
        self.id = id
        self.capcity = capcity
        self.curArea = curArea
        self.destination = destination
        self.distance = 0
        self.time = 0
        self.route = [curArea, destination]
        self.geolocator = Nominatim(user_agent="osrm_example")
        self.missionaries = missionaries

    def _coordinates(self, address):
        loc = self.geolocator.geocode(address)
        if not loc:
            raise ValueError(f"Could not geocode: {address}")
        return loc.longitude, loc.latitude  # OSRM order
    
    def plotRoute(self):
        startLon, startLat = self._coordinates(self.curArea)
        endLon, endLat = self._coordinates(self.destination)
        url = ("https://router.project-osrm.org/route/v1/driving/"f"{startLon},{startLat};{endLon},{endLat}""?overview=false")
        data = requests.get(url).json()
        route = data["routes"][0]
        self.distance = route["distance"] / 1000
        self.time = route["duration"] / 60

    def insert_stop(self, location, index):
        """Insert a stop into the route at a specific position. index=1 means right after the start."""
        if index <= 0 or index >= len(self.route):
            raise ValueError("Invalid insertion index")
        self.route.insert(index, location)
        
    def remove_stop(self, index):
        """Remove a stop from the route (cannot remove start or destination)."""
        if index == 0 or index == len(self.route) - 1:
            raise ValueError("Cannot remove start or destination")
        self.route.pop(index)
    
    def can_move(vehicle):
        if len(vehicle.missionaries) >= 2:
            return True
        return False
        

class Missionary:
    def __init__(self, email, curArea, destination):
        self.email = email # used as ID
        self.curArea = curArea
        self.destination = destination
        self.time = 0
        self.geolocator = Nominatim(user_agent="osrm_example")

    def _coordinates(self, address):
        loc = self.geolocator.geocode(address)
        if not loc:
            raise ValueError(f"Could not geocode: {address}")
        return loc.longitude, loc.latitude  # OSRM order

    def plotRoute(self):
        startLon, startLat = self._coordinates(self.curArea)
        endLon, endLat = self._coordinates(self.destination)
        url = ("https://router.project-osrm.org/route/v1/driving/"f"{startLon},{startLat};{endLon},{endLat}""?overview=false")
        data = requests.get(url).json()
        route = data["routes"][0]
        self.distance = route["distance"] / 1000
        self.time = route["duration"] / 60


#missionList =[[email, arriving, destination],...]
#vehicleList = [[id, units, curArea, destination, [missionaryemail, missionaryemail]],...]
#locationList = [[address, sate # can be "chur" or "house"],...]
#StartThatJawn(missionList, vehicleList)
def StartThatJawn(mishList, veList, locList):
    missionaries = []
    vehicles = []
    locations = []

    for x in locList:
        l = Location(x[0], x[1])
        locations.append()
    for x in mishList:
        m = Missionary(x[0], x[1], x[2])
        m.plotRoute()
        missionaries.append()
    for x in veList:
        v = Vehicle(x[0], x[1], x[2], x[3], x[4])
        v.plotRoute()
        vehicles.append(v)
