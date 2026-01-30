from geopy.geocoders import Nominatim

g = Nominatim(user_agent="test_app")
print(g.geocode("Paxton Hollow Rd, Broomall, PA 19008, USA", timeout=10))