from enum import Enum

class Country(Enum):
    GERMANY = "D"

class City(Enum):
    BERLIN = "Berlin"
    MUNICH = "München"

class LocationRadius(Enum):
    DIST_MAX = ""
    DIST_10km = "10"
    DIST_20km = "20"
    DIST_50km = "50"
    DIST_100km = "100"
    DIST_150km = "150"
    DIST_200km = "200"
    DIST_250km = "250"
    DIST_300km = "300"
    DIST_400km = "400"