from .locdetect import iploc,curloc
CITY=curloc().city
COUNTRY=curloc().country
def refresh(ip=''):
    if not ip:
        city=curloc().city
        country=curloc().country
    else:
        city=iploc(ip).city
        country=iploc(ip).country

    return city,country

