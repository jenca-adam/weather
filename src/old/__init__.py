from bs4 import BeautifulSoup as bs
from .forecast import Forecast
from .gsearch import search
from .city import *
from .parse import parsefcast
from .error import *
def forecast(cityname=CITY,countryname=''):

    if cityname==CITY:
        countryname=COUNTRY
    query=f'weather {cityname} {countryname}'
    c=search(query)
    soup=bs(c,'html.parser')
    try:
        tempnow=int(soup.body.find('span',id="wob_tm",class_="wob_t TVtOme").text)
        fli=soup.body.find('div',id="wob_dp")
    
        return parsefcast(str(fli),tempnow)
    except:
        err=NoSuchCityError(f"no such city: '{cityname}'")
    raise err
def ipforecast(ip):
    return forecast(*refresh(ip))    
