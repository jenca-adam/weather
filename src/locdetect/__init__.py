from .ipapi import track
class Location:
    def __init__(self,lat,lon,country,country_code,region_code,region,city,zipcode,tzone):
        self.lat=lat
        self.lon=lon
        self.country=country
        self.country_code=country_code
        self.region=region
        self.region_code=region_code
        self.city=city
        self.zipcode=zipcode
        self.tzone=tzone
def _parse_loc(resp):
    return Location(
                    resp['lat'],
                    resp['lon'],
                    resp['country'],
                    resp['countryCode'],
                    resp['region'],
                    resp['regionName'],
                    resp['city'],
                    resp['zip'],
                    resp['timezone'],
                    )
def iploc(ip):
    return _parse_loc(track(ip))
def curloc():
    return iploc('')
