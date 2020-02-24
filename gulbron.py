import requests
from bs4 import BeautifulSoup
from math import sin, cos, sqrt, atan2, radians

# Approximate radius of earth in km
R = 6373.0
# Alert distance in km
D = 10
# Slack webhook URL
SLACK_URL = "https://hooks.slack.com/services/[WORKSPACE]/[CHANNEL]/[KEY]"


headers = {
    "Host": "www.vesselfinder.com",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0",
    "Accept": "text/html",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.vesselfinder.com/?imo=9808223",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}
r = requests.get(
    "https://www.vesselfinder.com/vessels/ZHEN-HUA-33-IMO-9808223-MMSI-414272000",
    headers=headers,
)
soup = BeautifulSoup(r.text, features="html.parser")
params = soup.findAll("table", {"class": "tparams"})[2]
coordinates = params.tbody.findAll("tr")[9].findAll("td")[1].contents[0].split("/")
lon_float = float(coordinates[0][:-2]) * (1 if coordinates[0][-1] == "N" else -1)
lat_float = float(coordinates[1][:-2]) * (1 if coordinates[0][-1] == "E" else -1)
lon = radians(lon_float)
lat = radians(lat_float)

file = open("coords.txt")
coords = [l for l in file.read().split("\n") if l]
coords = coords[-1].split(" ")

lon_old = float(coords[0])
lat_old = float(coords[1])

dlon = lon_old - lon
dlat = lat_old - lat

a = sin(dlat / 2)**2 + cos(lat) * cos(lat) * sin(dlon / 2)**2
c = 2 * atan2(sqrt(a), sqrt(1 - a))
distance = R * c

lon_slussen = radians(59.321267)
lat_slussen = radians(18.072874)

dlon_slussen = lon - lon_slussen
dlat_slussen = lat - lat_slussen

a_slussen = sin(dlat_slussen / 2)**2 + cos(lat_slussen) * cos(lat_slussen) * sin(dlon_slussen / 2)**2
c_slussen = 2 * atan2(sqrt(a_slussen), sqrt(1 - a_slussen))
distance_slussen = R * c_slussen
distance_slussen_str = "{:,.2f}".format(distance_slussen).replace(",", ";").replace(".", ",").replace(";", ".") + "km"

print("Distance:", "{:,.2f}".format(distance).replace(",", ";").replace(".", ",").replace(";", ".") + "km")
print("Distance to Slussen:", distance_slussen_str)
if distance >= D:
    with open("coords.txt", "a") as file:
        file.write(str(lon) + " " + str(lat) + "\n")
    print("10km!")
    message = "I advanced 10 kilometres! The bridge :bridge_at_night: is currently at <https://www.vesselfinder.com/?imo=9808223|" + coordinates[0].replace(" ", "") + " " + coordinates[1].replace(" ", "") + ">, only " + distance_slussen_str + " from Slussen."
    requests.post(SLACK_URL, json={"text": message})
