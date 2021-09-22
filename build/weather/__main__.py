#!/usr/bin/env python3
if __name__=='__main__':
    print('Importing module, please wait...\r',end='')
import json
import urllib3
from bs4 import BeautifulSoup as bs
from httplib2 import Http
import httplib2
import random
import time
from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver import *
import warnings
import os
import re
import platform
import subprocess
from pathlib import Path
import selenium
import colorama
import inspect
import sys
import importlib
import difflib
from unitconvert.temperatureunits import TemperatureUnit as tu
from lxml import etree
import locale
import langdetect
import argparse
import termcolor
import tabulate
import calendar
import datetime
import termutils
import getchlib
'''Python library for getting weather from different sources.
Example:
>>> import weather
#Get temperature in Chicago tommorow at midnight ( Returns temperature in Fahrenheits )
>>> weather.forecast("Chicago").tomorrow["0:00"].temp
#Get temperature in current location today at noon
>>> weather.forecast().today["12:00"].temp
#Get precipitation amount after two days in Seoul at 4 o'clock
>>> weather.forecast('Seoul').day(2)["16:00"].precip

'''
termcolor.COLORS={key:value+60 for key,value in termcolor.COLORS.items()}
#__OWM_TOKEN="84e57133df9ae058f3e26f7e60ae5cad"
DEBUG=False
locator=Nominatim(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36")
_h=Http('.cache')
CELSIUS=0
UNIT=CELSIUS
FAHRENHEIT=1
_DONTCHECK=-1
'''Google chrome headers, used in BetaChrome'''
_HDR={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"}
_URL="https://translate.googleapis.com/translate_a/single?client=gtx&ie={pe}&oe={pe}dt=bd&dt=ex&dt=ld&dt=md&dt=rw&dt=rm&dt=ss&dt=t&dt=at&dt=qc&sl={sl}&tl={tl}&hl={tl}&q={string}"
def dateadd1(date):
    date=[date.year,date.month,date.day]
    if date[-1]==calendar.monthrange(2021,date[1])[1]:
        date[-1]=1
        if date[1]==12:
            date[1]=1
            date[0]+=1
        else:
            date[1]+=1
    else:
        date[-1]+=1
    return datetime.date(*date)
def foc2t(foc):
    u=makeunit(foc.today.weather_as_list[0].unit)
    date=datetime.date.today()
    dayc=0
    table=[]
    while True:
        begintime=datetime.datetime.now().hour if not dayc else 1
        try:
            day=foc.day(dayc)
        except IndexError:
            break
        for h in range(begintime,24):
            weah=day[f'{h}:00']
            table.append([str(date),f'{h}:00',str(weah.temp)+"°"+u,weah.precip,weah.humid,weah.wind.direction.direction,weah.wind.speed])
        dayc+=1
        date=dateadd1(date)
    return tabulate.tabulate(table,['Date','Time',"Temperature",'Precipitation','Humidity','Wind direction','Wind speed'],tablefmt='fancy_grid')

class TooManyRequestsError(ValueError):pass
class Translator:
    def __init__(self,sl,tl):
        self._pe=locale.getpreferredencoding()
        self._h=httplib2.Http('.cache')
        self.sl=sl
        self.tl=tl
    def translate(self,string):
        if self.sl is None:
            self.sl=langdetect.detect(string)
        u=_URL.format(pe=self._pe,sl=self.sl,tl=self.tl,string=string)
        resp,c=self._h.request(u)
        if resp.status==419:
            raise TooManyRequestsError('server replied 419. Try again later')
        return json.loads(c.decode(self._pe))[0][0][0]

def translate(string,sl=None,tl='en'):
    t=Translator(sl,tl)
    return t.translate(string)
class _debugger:
    class BadStatus(Exception):pass
    def debug(self,text,status="INFO"):
        if not DEBUG:
            return
        colors={"INFO":colorama.Fore.LIGHTBLUE_EX,"ERROR":colorama.Fore.LIGHTRED_EX,"DEBUG":colorama.Fore.LIGHTMAGENTA_EX,"WARNING":colorama.Fore.LIGHTYELLOW_EX}
        if status not in colors:
            raise self.BadStatus("BAD STATUS")
        previous_frame = inspect.currentframe().f_back
        (filename, lineno, 
         function_name, lines, index) = inspect.getframeinfo(previous_frame)
        sys.stdout.write( f'{colorama.Fore.CYAN}{filename}:{lineno}:{function_name} {colorama.Fore.RESET}-> {colors[status]}{status}{colorama.Style.RESET_ALL}:{colors[status]}{text}{colorama.Style.RESET_ALL}\n')
debugger=_debugger()
class Browser:
    '''Metaclass of BetaChrome used to bypass Google bot detection'''
    def request(self,url,headers={}):
        '''Request url and set USER-AGENT headers'''
        debugger.debug('requested url')
        hdr=self.HEADERS
        hdr.update(headers)
        return _h.request(url,headers=hdr)
class BetaChrome(Browser):
    '''Used to bypass Google bot detection'''
    HEADERS=_HDR
class DriverWarning(Warning):
    '''Metaclass of NoHeadlessWarning'''
class WeatherWarning(Warning):
    '''Metaclass of SVGWarning'''
class SVGWarning(WeatherWarning):
    '''User is warned when SVG passed to analyzesvg() is already analyzed.
    For debugging'''
class NoHeadlessWarning(DriverWarning):
    '''User is warned when no headless driver is not avaliable'''
class WeatherError(BaseException):
    '''Metaclass of most errors defined here'''
class NoSuchCityError(WeatherError):
    '''Raised when city was not found using Nominatim'''
class DriverError(Exception):
    '''Raised when no driver is avaliable'''
h=httplib2.Http('.cache')
class IpError(ValueError):
    '''Metaclass of  Fail'''
class Fail(IpError):
    '''Metaclass of InvalidQuery and ReservedRange'''
class InvalidQuery(Fail):
    '''Raised when user entered non-existing IP to track()'''
class ReservedRange(Fail):
    '''Raised when user entered 
       localhost or 127.0.0.1 or 0.0.0.0 to track()'''

class SetupError(WeatherError):
    '''
    Raised when setup.setup() was called but Chrome neither Firefox are installed
    '''
class ReadonlyError(Exception):
    '''
    Raised when user want to change Forecast, Day or SearchResult's attributes'''
class UnknownServiceError(WeatherError):
    '''
    Raised when user tried to use service that does not exist. 
    Should be served along with some " Did you mean <>?" suggestions
    '''
class PropertyError(WeatherError):
    '''
    Metaclass of WindError
    '''
class WindError(PropertyError):
    '''
    Raised when invalid wind properties are given
    '''
class DirectionError(WindError):
    '''
    Raised when direction is not "N","NE","E","SE","S","SW","W" or "NW"(if it is a string) or higher than 360(if it is a integer)
    '''
class _fastener:
    def __init__(self):
        os.makedirs('.cache/weather/',exist_ok=True)
        if not os.path.exists('.cache/weather/citycountry.json'):
            self.file=open('.cache/weather/citycountry.json','w')
            self.file.write('{}')
            self.file.close()
        self.file=open('.cache/weather/citycountry.json')
        self.data=json.load(self.file)
    def dump(self):
        c=open('.cache/weather/citycountry.json','w')
        json.dump(self.data,c)
        c.close()

    
    def isrg(self,city):
        return city in self.data
    def register(self,city,country):
        self.data[city]=country
        self.dump()
    def getcountry(self,city):
        if self.isrg(city):
            return self.data[city]
        else:
            country=_getcountry(city)
            self.register(city,country)
            return country
def makeunit(u):
    if u==CELSIUS:
        return 'C'
    elif u==FAHRENHEIT:
        return "F"
    return u
def searchurl(query):
    '''Returns Google Search URL according to query'''  
    return f'https://google.com/search?q={query}'
def _getcountry(city):
    '''Return country that city is located in''' 
    a=locator.geocode(city).address.split(',')[-1].strip()
    return translate(a)
def _rq(h,u):
    '''Handles IpApi ConnectionResetError'''
    try:
        return h.request(u)
    except ConnectionResetError:
        return _rq(h,u)
def _track(ip):
    '''Requests IpApi and returns result as dict'''
    r,c=_rq(h,f'http://ip-api.com/json/{ip}')
    return json.loads(c)
def _checkresp(msg,stat):
    '''Raises error according to message and status returned by track()'''
    if stat=='success':return
    if stat=='fail':
        if msg=='reserved range':
            raise ReservedRange(msg)
        elif msg=='invalid query':
            raise InvalidQuery(msg)
        raise Fail(msg)
    raise IpError(msg)
def checkresp(resp,ip=''):
    '''Calls _checkresp with resp'''
   
    if 'message' not in resp:return
    _checkresp(resp['message'],resp['status'])
def track(ip=''):
    '''Tracks according to IP. Used to detect location (when is called with no arguments,  returns data for current IP)'''
    resp=_track(ip)
    checkresp(resp,ip)
    return resp
class Direction:
    __ANGLEDICT={0:'N',45:'NE',90:'E',135:'SE',180:'S',225:'SW',270:'W',315:'NW',360:'N'}
    __rvang={value:key for key,value in __ANGLEDICT.items()}
    def __init__(self,ang):
        if isinstance(ang,bool):
            raise TypeError(
                    f"angle must be 'str' or 'int', not {ang.__class__.__name__!r}"
                    )
        if ang is None:
            self.direction='UNKNOWN'
            self.angle=None
            return
        if isinstance(ang,(int,float)):
            ang=int(ang)
            if ang>360:
                raise DirectionError("wind angle is more than 360")
            self.direction=self.__ANGLEDICT[min(self.__ANGLEDICT, key=lambda x:abs(x-ang))]
            self.angle=ang
        elif isinstance(ang,str):
            if ang.upper() not in self.__rvang:
                raise DirectionError(
                        f"invalid wind direction : {ang!r} ( valid are {','.join(self.__ANGLEDICT.values())} )"
                        )
            self.direction=ang.upper()
            self.angle=self.__rvang[ang.upper()]
        else:
            raise TypeError(
                    f"angle must be 'str' or 'int', not {ang.__class__.__name__!r}"
                    )
    def __repr__(self):
        return self.direction
class Location:
    '''Implementation of location'''
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

class Wind():
    def __init__(self,speed=None,direction=None):
        self.direction=Direction(direction)
        self.speed=speed

def _parse_loc(resp):
    '''Returns Location object from data returned by track''' 
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
    '''Gets location according to IP'''
    return _parse_loc(track(ip))
def curloc():
    '''Gets current location'''
    return iploc('')
_br=BetaChrome()
request=_br.request
def search(query):
    '''Return search results from query'''
    return request(searchurl(query))[1]

### Set global variables according to current location
LOCATION=curloc()
CITY=LOCATION.city
COUNTRY=LOCATION.country
### Set temperature unit to Fahrenheit if user is in US
if COUNTRY=='United States':
    UNIT=FAHRENHEIT
def refresh(ip=''):
    '''Gets city and country from current location(or IP location)'''
    if not ip:
        city=curloc().city
        country=curloc().country
    else:
        city=iploc(ip).city
        country=iploc(ip).country

    return city,country
class _fcdumper:
    def dump(self,forecast,file):
        debugger.debug(f'Dumping data into {file!r}')
        if isinstance(forecast,_WeatherChannel.Forecast):
            source='google'
        elif isinstance(forecast,_YR_NORI.Forecast):
            source='yrno'
        elif isinstance(forecast,_7Timer.Forecast):
            source='7timer'
        else:
            raise TypeError("bad forecast type")
        froot=etree.Element('forecast')
        debugger.debug('Created root element')
        forelem=etree.SubElement(froot,'location')
        cityelem=etree.SubElement(forelem,'city')
        countryelem=etree.SubElement(forelem,'country')
        countryelem.text=forecast.country
        unt=forecast.today.weather_as_list[0].unit
        untel=etree.SubElement(froot,'unit')
        untel.text='C' if unt==CELSIUS else 'F'
        cityelem.text=forecast.city
        srcel=etree.SubElement(froot,'source')
        srcel.text=source
        root=etree.SubElement(froot,'days')
                 
        dind=0
        debugger.debug('iterating days')
        for d in forecast.days:
            delem=etree.SubElement(root,'day',index=str(dind))
            debugger.debug(f'iterating weather for day {dind}')
            for w in d.weather_as_dict:
                
                recelem=etree.SubElement(delem,'record')
                wa=d.weather_as_dict[w]
                timelem=etree.SubElement(recelem,'time')
                timelem.text=w
                weather=etree.SubElement(recelem,'weather')

                telem=etree.SubElement(weather,'temp')
                telem.text=str(wa.temp)
                pelem=etree.SubElement(weather,'precip')
                pelem.text='0.0' if not wa.precip else str(float(wa.precip))
                welem=etree.SubElement(weather,'wind')
                wspeed=etree.SubElement(welem,'speed')
                wdir=etree.SubElement(welem,'direction')
                wang=etree.SubElement(wdir,'angle')
                wcomp=etree.SubElement(wdir,'compass')

                wspeed.text=str(wa.wind.speed)
                wang.text=str(wa.wind.direction.angle)
                wcomp.text=wa.wind.direction.direction
                helem=etree.SubElement(weather,'humid')
                helem.text="0" if not wa.humid else str(wa.humid)
            dind+=1
        with open(file,'w') as f:
            debugger.debug('saving file')
            f.write(etree.tounicode(froot,pretty_print=True))
    def load(self,xmlfile):
        debugger.debug('loading weather from cache')
        t=etree.parse(open(xmlfile))
        unit=t.find('.//unit').text
        city=t.find('.//city').text
        src=t.find('.//source').text
        srcsvc=SERVICES[src]
        country=t.find('.//country').text
        times=t.findall('.//time')
        temps=t.findall('.//temp')
        precps=t.findall('.//precip')
        humids=t.findall('.//humid')
        wspeeds=t.findall('.//speed')
        wangs=t.findall('.//angle')
        wcomps=t.findall('.//compass')
        records=len(times)
        cdix=0
        weather_as_dict={}
        forecast=[]
        debugger.debug(f'{records} records found')
        for wi in range(records):
            
            tm=times[wi].text
            temp=float(temps[wi].text)
            precip=float(precps[wi].text)
            humid=float(humids[wi].text)
            wind=float(wspeeds[wi].text)
            wdirct=float(wangs[wi].text)
            dix=int(temps[wi].getparent().getparent().getparent().attrib['index'])

            if dix>cdix:
                forecast.append(srcsvc.__class__.Day(list(weather_as_dict.values()),weather_as_dict))
                weather_as_dict={}
            weather_as_dict[tm]=srcsvc.__class__.Weather(Wind(wind,wdirct),precip,temp,humid,unit)
            cdix=dix
        return srcsvc.__class__.Forecast(forecast,city,country)
class _cacher:
    def __init__(self):
        os.makedirs('.cache/weather/fc/xml',exist_ok=True)
    def iscached(self,cityname,ctr):
        pt=f'.cache/weather/fc/xml/{ctr}/{cityname}/'
        return os.path.exists(pt) and os.listdir(pt)
    def getcached(self,city,ctr):
        if not self.iscached(city,ctr):
            return []
        pt=f'.cache/weather/fc/xml/{ctr}/{city}/'
        t=time.time()
        ress=[]
        for file in os.listdir(pt):
            rt=int(file)
            if -1<t-rt<3600:
                ress.append(os.path.join(pt,file))

        return ress
    def cache(self,forecast):
        pt=f'.cache/weather/fc/xml/{forecast.country}/{forecast.city}/'
        os.makedirs(pt,exist_ok=True)

        dumper.dump(forecast,os.path.join(pt,str(int(time.time()))))


        

    

        
class _WeatherChannel:
    '''weather.google type'''
    def __init__(self):
        '''Set driver to None for fututre forecast requests will be faster'''
        self.driver=None
    class Weather:
        '''Implementation of weather'''
        def __init__(self,wind,precip,temp,humid=None,unit=CELSIUS):
            self.temp=temp
            self.precip=precip/10
            self.wind=wind
            self.humid=humid
            self.unit=unit
            
    class Day:
        '''Implementation of day'''
        def __init__(self,weatherlist,wdict):
            '''
            self.highest=max(
                            max(i.temp for i in weatherlist)
                            )
            self.lowest=min(
                            min(i.temp for i in weatherlist)
                            )'''
            self.weather_as_list=weatherlist
            self.weather_as_dict=wdict
        def __getitem__(self,i):
            '''Return weather at time'''
            return self.gettemp(i)
        def splittime(self,time,after=int):
            '''Splits time to hours and minutes and calling to result after'''
            try:
                return tuple(after(i) for i in time.split(':'))
            except ValueError:
                raise ValueError(
                                f"invalid value for 'splittime':{time}"
                                )
        def fillin(self,time):
            '''Fills the time in. E.g.:fillin("8:00")="08:00"'''
            return self.jointime(self.formatsec(i) for i in  self.splittime(time,after=str))
        def formatsec(self,time):
            '''Formats seconds E.g:formatsec("8")="08"'''
            if len(str(time))>2:
                raise ValueError('not 2-digit or 1-digit time')
            if not time:
                return "00"
            if len(str(time))<2:
                return "0"+time
            return time
        def jointime(self,time):
            '''Gets analog time according to hours and minutes'''
            return ':'.join(str(i) for i in time)
        def gettemp(self,time):
            '''Returns weather at time'''
            if isinstance(time,str):
                time=self.splittime(time)
            return self.weather_as_dict[self.fillin(self.repairtime(self.jointime(time)))]
        def timetoint(self,time):
            '''Converts time to integer'''
            if isinstance(time,str):
                return self.splittime(time)[1]+self.splittime(time)[0]*60
            return time[1]+time[0]*60
        def inttotime(self,i):
            '''Converts integer to time. Reverse function to timetoint'''
            return (i//60,i%60)

        def repairtime(self,time):
            '''Gets closest time that is in weather list'''
            closest=lambda num,collection:min(collection,key=lambda x:abs((x-num)+1))
            dy=self.weather_as_dict

            dy=[self.timetoint(time) for time in dy]
            qr=self.timetoint(self.roundtime(time))
            return self.jointime(self.inttotime(closest(qr,dy)))
            
        def roundtime(self,time):
            '''Rounds time; e.g. roundtime("8:10")="08:00"'''
            mins=int(time.split(':')[-1])
            if mins==0:
                return time
            hrs=int(time.split(':')[0])
            if mins<30:
                return f'{self.formatsec(hrs)}:00'
            return f'{self.formatsec(hrs+1)}:00'

    def convert(self,d):
        ''' Converts dictionary to JSON serializable form'''
        l={}
        for a in d:
            i=d[a]
            m=i
            if isinstance(i,self.Day):
                m=i.__dict__
            if isinstance(i,list):
                m=self.convlist(self,i)
            l[a]=m
        return l    
    def convlist(self,d):
        '''Converts list to JSON serializable form'''
        l=[]
        for i in d:
            m=i
            if isinstance(i,self.Day):
                m=i.__dict__
            l.append(m)
        return l
    class Forecast:
        '''Implemantation of weather forecast'''
        def __init__(self,days,city,ctr):
            self.city=city
            self.country=ctr
            debugger.debug("created forecast")
            e=None
            self.temp=days[0].weather_as_list[0].temp
            self.today=days[0]
            self.days=days
            self.tomorrow=days[1]

            '''if not isinstance(self.today,_WeatherChannel.Day):
                raise TypeError(
                f"'today' argument must be weather._WeatherChannel.Day, not {today.__class__.__name__}'")
            try:
                iter(nxt)
            except:
                e=TypeError("'nxt' argument is not iterable")
            if e is not None:
                raise e
            for i in nxt:
                if not isinstance(i,_WeatherChannel.Day):
                    raise TypeError(
                    f"all members of 'nxt' argument must be \"_WeatherChannel.Day\", not {i.__class__.__name__}'")'''
        def day(self,num):
            '''Returns weather at day n'''
            return self.days[num]
        def splittime(self,time,after=int):
            try:
                return tuple(after(i) for i in time.split(':'))
            except ValueError:
                raise ValueError(
                                f"invalid value for 'splittime':{time}"
                                )
        def fillin(self,time):
            return self.jointime(self.formatsec(i) for i in  self.splittime(time,after=str))
        def formatsec(self,time):
            if len(time)>2:
                raise ValueError('not 2-digit or 1-digit time')
            if len(time)<2:
                return "0"+time
            return time
        def jointime(self,time):
            return ':'.join(str(i) for i in time)
        def gettemp(self,daynum,time):
            if isinstance(time,str):
                time=self.splittime(time)
            return self.days[daynum][self.fillin(self.repairtime(self.jointime(time),daynum))]
        def timetoint(self,time):
            if isinstance(time,str):
                return self.splittime(time)[1]+self.splittime(time)[0]*60
            return time[1]+time[0]*60
        def inttotime(self,i):
            return (i//60,i%60)

        def repairtime(self,time,day):
            closest=lambda num,collection:min(collection,key=lambda x:abs((x-num)+1))
            dy=self.days[day]
            dy=[self.timetoint(time) for time in dy]
            qr=self.timetoint(self.roundtime(time))
            return self.jointime(self.inttotime(closest(qr,dy)))
            
        def roundtime(self,time):

            mins=int(time.split(':')[-1])
            if mins==0:
                return time
            hrs=int(time.split(':')[0])
            if mins<50:
                return f'{self.formatsec(hrs)}:00'
            return f'{self.formatsec(hrs+1)}:00'
    def splittime(self,time,after=int):
            try:
                return tuple(after(i) for i in time.split(':'))
            except ValueError:
                raise ValueError(
                                f"invalid value for 'splittime':{time}"
                                )

    def parsetemp(self,t,unit=UNIT):
        '''Parses temperature HTML'''
        return int(t.find_all(class_="wob_t")[unit].text)
    def parseday(self,d,unit=UNIT):
        '''Parses one day'''
        s=bs(str(d),'html.parser')
        dayname=s.find(class_="QrNVmd Z1VzSb")['aria-label']
        desc=s.find(class_="DxhUm").img['alt']
        tmps=bs(str(s.find(class_="wNE31c")),'html.parser')
        highest=self.parsetemp(tmps.find(class_="vk_gy gNCp2e"),unit=unit)
        lowest=self.parsetemp(tmps.find(class_="QrNVmd ZXCv8e"),unit=unit)
        return self.Day(dayname,highest,lowest,desc)
    def getsvg(self,ch,unit):
        debugger.debug("Getting temperature") 
        '''Gets SVG with temperature'''
        try:
                ch.find_elements_by_class_name("jyfHyd")[1].click()
        except:pass
        #wait until forecast loads 
        time.sleep(0.7)
        svg=ch.find_element_by_id('wob_gsvg')
        svg=svg.get_attribute('outerHTML')
        return self.analyzesvg(svg,unit)
    def getprecip(self,ch):
        '''Gets precipitation data'''
        debugger.debug("Analyzing precipitation")
        precip_html_element=ch.find_element_by_id('wob_pg')
        precip_html=precip_html_element.get_attribute('outerHTML')
        precip_soup=bs(precip_html,
                        'html.parser')
        columns=precip_soup.findAll(class_="wob_hw")
        days=[]
        graph={}
        lastTime=0
        for col in columns:
            
            time=col.div['aria-label'].split(' ')[-1]
            perc=int(
                    col.div['aria-label'].
                    split(' ')[0].
                    replace('%',''))
            if self.splittime(time)[0]<lastTime:
                    days.append(graph)
                    graph={}
            graph[time]=perc
            lastTime=self.splittime(time)[0]
        return days

            
    def getwind(self,ch):
        '''Gets wind data'''
        debugger.debug("Analyzing wind")
        wind_html_element=ch.find_element_by_id('wob_wg')
        wind_html=wind_html_element.get_attribute('outerHTML')
        wind_soup=bs(wind_html,
                        'html.parser')
        spds=wind_soup.findAll(class_="wob_hw")
        days=[]
        graph={}
        lastTime=0
        for selem in spds:
            time=selem.div.span['aria-label'].split(' ')[-1]
            spd=selem.div.span.text.split(' ')[0]
            if self.splittime(time)[0]<lastTime:
                days.append(graph)
                graph={}
            graph[time]=int(spd)
            lastTime=self.splittime(time)[0]

        return days

    def getgraph(self,ch,unit):
        '''Gets full data and formats them into Forecast object'''
        debugger.debug("Parser has started!")
        svg=self.getsvg(ch,unit)
        precip=self.getprecip(ch)
        wind=self.getwind(ch)

        svglist=[list(a.keys()) for a in svg]
        preciplist=[list(a.keys()) for a in precip]
        windlist=[list(a.keys()) for a in wind]
        wthrs=[]
        wthrs_inner=[]
        ind=0
        debugger.debug("Formating weather data into forecast")
        for a in wind:
            inner=0
            wthrs_inner=[]
            
            for j in a:
                t=a[j]
                wthrs_inner.append(
                             self.Weather(
                                          Wind(t*3.6666667,0),
                                          precip[ind][j],
                                          svg[ind][j],
                                          unit=unit
                                          )
                                )
                inner+=1
            ind+=1
            wthrs.append(wthrs_inner)
        wtdct=[]
        wtdc_inner={}
        ind=0
        for s in wind:
            inner=0
            wtdc_inner={}
            for j in s:
                t=a[j]
                wtdc_inner[j]=self.Weather(
                                          Wind(t,0),
                                          precip[ind][j],
                                          svg[ind][j]
                                          )
                                
                inner+=1
            ind+=1
            wtdct.append(wtdc_inner)
        days=[]
        yndex=0
        for day in wtdct:
            days.append(
                        self.Day(
                            wthrs[yndex],
                            wtdct[yndex],
                            )
                        )
            yndex+=1
        return days
    
        

                                     
    def analyzesvg(self,svg,unit):
        '''Changes svg to dict of temperatures'''
        debugger.debug("Analyzing temperature")
        if isinstance(svg,list) :
            warnings.warn(
                          SVGWarning(
                                    '''Looks like temperature SVG file is already analyzed, 
                                    but check it twice!'''
                                    )
                            )
                          
            return svg
        soup=bs(svg,'html.parser')
        labels=soup.findAll('text')
        days=[]
        graph={}
        curcels=not unit
        lastTime=0
        for l in labels:
            if curcels:
                time=l['aria-label'].split(' ')[-1]
                tu=self._prstmpstr(l['aria-label'])
                if self.splittime(time)[0]<lastTime:
                    days.append(graph)
                    graph={}
    
                graph[time]=tu
                lastTime=self.splittime(time)[0]
            curcels=not curcels
        return days

    def parsefcast(self,days,temp,unit,city,ctr):
        '''Parses forecast'''
        return self.Forecast(days,city,ctr)
    def forecast(self,cityname=CITY,countryname='',unit=None,driver=None):
        '''Gets forecast'''
        err=None
        self.driver=driver
        if self.driver is None:
            driver=_driverSearch()
            self.driver=driver.best()
        wd=self.driver
        if not countryname:
            try:
                countryname=getcountry(cityname)
            except AttributeError:
                err=NoSuchCityError(f"no such city: '{cityname}'")
        if err:
            raise err
        if cityname==CITY and not countryname:
            countryname=COUNTRY
        if unit is None:
            if countryname.lower()=='united states':
                unit=FAHRENHEIT
            else:
                unit=CELSIUS
        ca=cacher.getcached(cityname,countryname)
        
        for caf in ca:
            foc=dumper.load(caf)
            if isinstance(foc,self.__class__.Forecast):
                return foc
        if countryname==_DONTCHECK:
            query=f'weather {cityname}'
        else:
            query=f'weather {cityname} {countryname}'
        c=search(query)
        soup=bs(c,'html.parser')
        wd.get(searchurl(query))
        try:
            svg=self.getgraph(wd,unit)

            tempnow=int(soup.body.find_all('span',class_="wob_t")[unit].text)
            fli=soup.body.find('div',id="wob_dp")
        
            foc=self.parsefcast(svg,tempnow,unit,cityname,countryname)
            cacher.cache(foc)
            return foc
        except Exception as e:
            debugger.debug(f"could not load forecast for {cityname}, trying without country; ({str(e)} throwed)","ERROR")
            err=WeatherError(f"could not get forecast for city {cityname}({str(e)} throwed)")
            if countryname==_DONTCHECK:
                raise err
            return self.forecast(cityname,_DONTCHECK,unit)
    def ipforecast(self,ip):
        return self.forecast(*refresh(ip))
    def _prstmpstr(self,string):
        pattern=re.compile(r'^([0-9\-]+)°')
        match=pattern.search(string)

        if not match:
            raise ValueError(
                            'Could not parse temperature string')
        return int(match.group(0).replace('°',''))
class _YR_NORI:
    '''yr.no source'''
    def __init__(self):
        self.driver=None
        self.ForecastParser=self._ForecastParser()
    class SearchResults:
        '''Implementation of search results'''
        def __init__(self,l):
            self.res=l
            self.first=l[0]
        def __getitem__(self,item):
            return self.result(item)
        def __setitem__(self,item,what):
            raise ReadonlyError('read-only')
        def result(self,i):
            return self.res[i]
        def __repr__(self):
            return repr(self.res)
    class Day:
        '''Implementation of one day'''
        def __init__(self,wlst,wdict):
            self.weather_as_list=wlst
            self.weather_as_dict=wdict

        def __getitem__(self,i):
            return self.gettemp(i.split(':')[0])
        def splittime(self,time,after=int):
            try:
                return tuple(after(i) for i in time.split(':'))
            except ValueError:
                raise ValueError(
                                f"invalid value for 'splittime':{time}"
                                )
        def fillin(self,time):
            return self.jointime(self.formatsec(i) for i in  self.splittime(time,after=str))
        def formatsec(self,time):
            if len(str(time))>2:
                raise ValueError('not 2-digit or 1-digit time')
            if not time:
                return ""
            if len(str(time))<2:
                return "0"+str(time)
            
            return time
        def jointime(self,time):
            return ':'.join(str(i) for i in time)
        def gettemp(self,time):
            if isinstance(time,str):
                time=self.splittime(time)
            return self.weather_as_dict[self.fillin(self.repairtime(self.jointime(time)))]
        def timetoint(self,time):
            if isinstance(time,str):
                return self.splittime(time)[1]+self.splittime(time)[0]*60
            return time[1]+time[0]*60
        def inttotime(self,i):
            return (i//60,i%60)

        def repairtime(self,time):
            closest=lambda num,collection:min(collection,key=lambda x:abs((x-num)+1))
            dy=self.weather_as_dict

            dy=[self.timetoint(time) for time in dy]
            qr=self.timetoint(self.roundtime(time))
            return self.jointime(self.inttotime(closest(qr,dy)))
            
        def roundtime(self,time):

            mins=int(time.split(':')[-1])
            if mins==0:
                return time
            hrs=int(time.split(':')[0])
            if mins<50:
                return f'{self.formatsec(hrs)}:00'
            return f'{self.formatsec(hrs+1)}:00'

    class Forecast:
        '''implementation of weather forecast'''
        def __init__(self,days,city,country,*args,**kwargs):
            self.today=days[0]
            self.tomorrow=days[1]
            self.days=days
            self.city=city
            self.country=country
        def __getitem__(self,i):
            return self.day(i)
        def __setitem__(self,item,what):
            raise ReadonlyError('read-only')

        def day(self,daynum):
            return self.days[daynum]
    class Weather:
        '''Implementation of weather'''
        def __init__(self,wind,precip,temp,humid=None,unit=CELSIUS):
            self.temp=temp
            self.precip=precip
            self.wind=wind
            self.humid=humid
            self.unit=unit
    class _ForecastParser:
        '''Parses forecast'''
        def parse(self,content,unit,ci,co):
            content=json.loads(content)
            timeseries=content["properties"]["timeseries"]
            weather_as_dict={}
            fcast=[]
            lastday=None
            for wr in timeseries:
                war=wr["data"]
                tm=self.parsetime(wr["time"])
                dy=self.parseday(wr["time"])
                instant=war["instant"]["details"]
                temp=instant["air_temperature"]
                wind=instant["wind_speed"]
                wdirct=instant["wind_from_direction"]
                precip=war["next_1_hours"]["details"]["precipitation_amount"] if "next_1_hours" in war else 0.0
                humid=instant["relative_humidity"]
                weather_as_dict[tm]=_YR_NORI.Weather(Wind(wind,wdirct),precip,temp,humid,unit)
                if lastday is not None:
                    if dy!=lastday:
                        fcast.append(_YR_NORI.Day(list(weather_as_dict.values()),weather_as_dict))
                        weather_as_dict={}
                lastday=dy
            foc= _YR_NORI.Forecast(fcast,ci,co)
            cacher.cache(foc)
            return foc

        def close_ad(self,driver):
            '''Closes "We have a new graph" pop-up'''
            try:
                driver.find_elements_by_class_name("feature-promo-modal-meteogram__link")[0].click()
            except:pass
        def parsetime(self,time):
            pattern=re.compile('(\d{2}\:\d{2})\:\d{2}')
            return pattern.search(time).group(1)
        def parseday(self,time):
            pattern=re.compile('\d{4}-\d{2}-(\d{2})')
            return pattern.search(time).group(1)


             
    def searchurl(self,q):
        '''Returns yr.no search URL'''
        return f'https://www.yr.no/en/search?q={q}'
    def expandhref(self,href):
        '''Expands href'''
        return f'https://www.yr.no{href}'
    def search(self,q):
        '''Searches yr.no'''
        self.driver=_driverSearch().best()
        self.driver.get(
            self.searchurl(q)
            )
        results=bs(self.driver.find_elements_by_class_name('search-results-list')[0].get_attribute('outerHTML'),
        'html.parser')
        results=results.findAll('li')
        results=[self.expandhref(result.a['href']) for result in results]
        return self.SearchResults(results) 
    def forecast(self,cityname=CITY,countryname=None,unit=None):
        '''Gets forecast'''
        err=None
        if not countryname:
            if cityname==CITY:
                countryname=COUNTRY
            try:
                countryname=getcountry(cityname)
            except AttributeError:
                err=NoSuchCityError(f"no such city: '{cityname}'")
        if err:
            raise err
        if cityname==CITY and not countryname:
            countryname=COUNTRY
        ca=cacher.getcached(cityname,countryname)
        
        for caf in ca:
            
            foc=dumper.load(caf)
            if isinstance(foc,self.__class__.Forecast):
                return foc

        if cityname==CITY and countryname==COUNTRY:
            lat,lon=LOCATION.lat,LOCATION.lon
        else:
            loct=locator.geocode(f'{cityname},{countryname}')
            lat,lon=loct.latitude,loct.longitude
        if unit is None:
            if countryname.lower()=='united states':
                unit=FAHRENHEIT
            else:
                unit=CELSIUS

        apiurl=f'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}'        
        return self.ForecastParser.parse(BetaChrome().request(apiurl)[1],unit,cityname,countryname)
class _7Timer:
    '''7timer.info source'''
    def __init__(self):
        self.driver=None
        self.ForecastParser=self._ForecastParser()
    class Day:
        '''Implementation of one day'''
        def __init__(self,wlst,wdict):
            self.weather_as_list=wlst
            self.weather_as_dict=wdict

        def __getitem__(self,i):
            return self.gettemp(i.split(':')[0])
        def splittime(self,time,after=int):
            try:
                return tuple(after(i) for i in time.split(':'))
            except ValueError:
                raise ValueError(
                                f"invalid value for 'splittime':{time}"
                                )
        def fillin(self,time):
            return self.jointime(self.formatsec(i) for i in  self.splittime(time,after=str))
        def formatsec(self,time):
            if len(str(time))>2:
                raise ValueError('not 2-digit or 1-digit time')
            if not time:
                return ""
            if len(str(time))<2:
                return "0"+str(time)
            
            return time
        def jointime(self,time):
            return ':'.join(str(i) for i in time)
        def gettemp(self,time):
            if isinstance(time,str):
                time=self.splittime(time)
            return self.weather_as_dict[self.fillin(self.repairtime(self.jointime(time)))]
        def timetoint(self,time):
            if isinstance(time,str):
                return (self.splittime(time)[1]+self.splittime(time)[0]*60)%1440
            return (time[1]+time[0]*60)%1440
        def inttotime(self,i):
            return (i//60,i%60)

        def repairtime(self,time):
            closest=lambda num,collection:min(collection,key=lambda x:abs((x-num)+1))
            dy=self.weather_as_dict

            dy=[self.timetoint(time) for time in dy]
            qr=self.timetoint(self.roundtime(time))
            return self.jointime(self.inttotime(closest(qr,dy)))
            
        def roundtime(self,time):

            mins=int(time.split(':')[-1])
            if mins==0:
                return time
            hrs=int(time.split(':')[0])
            if mins<50:
                return f'{self.formatsec(hrs)}:00'
            return f'{self.formatsec(hrs+1)}:00'

    class Forecast:
        '''implementation of weather forecast'''
        def __init__(self,days,ci,co):
            self.days=days
            self.today=days[0]
            self.tomorrow=days[1]
            self.city=ci
            self.country=co
        def __getitem__(self,i):
            return self.day(i)
        def __setitem__(self,item,what):
            raise ReadonlyError('read-only')

        def day(self,daynum):
            return self.days[daynum]
    class Weather:
        '''Implementation of weather'''
        def __init__(self,wind,precip,temp,humid=None,unit=CELSIUS):
            self.temp=temp
            self.precip=precip
            self.wind=wind
            self.humid=humid
            self.unit=unit
 
    class _ForecastParser:
        '''Parses forecast'''
        def parse(self,content,unit,ci,co):
            content=json.loads(content)
            lit=content['dataseries']
            weather_as_dict={}
            fcast=[]
            dnum=1
            for qeqeq in lit:
                tm=self.mktime(
                        self.inttotime(
                        self.timetoint(
                            str(
                                qeqeq['timepoint']
                                )+':00'
                            )+self.timetoint(
                                self.roundtime(
                                    self.parsetime(
                                        time.ctime(
                                            time.time()
                                            )
                                        )
                                    )
                                )
                            )
                        )
                tmp=self.c2f(qeqeq['temp2m'],unit)
                humd=None
                precip=False if qeqeq['prec_type']=='none' else True
                wind=qeqeq['wind10m']['speed']
                windir=qeqeq['wind10m']['direction']
                weather_as_dict[tm]=_7Timer.Weather(Wind(wind,windir),precip,tmp,humd,unit)
                if qeqeq['timepoint']>=dnum*24:

                    fcast.append(_7Timer.Day(list(weather_as_dict.values()),weather_as_dict))
                    weather_as_dict={}
                    dnum+=1
                ltime=self.timetoint(tm)
            foc= _7Timer.Forecast(fcast,ci,co)
            cacher.cache(foc)
            return foc
        
        def splittime(self,time,after=int):
            try:
                return tuple(after(i) for i in time.split(':'))
            except ValueError:
                raise ValueError(
                                f"invalid value for 'splittime':{time}"
                                )
        def fillin(self,time):
            return self.jointime(self.formatsec(i) for i in  self.splittime(time,after=str))
        def formatsec(self,time):
            if len(str(time))>2:
                raise ValueError('not 2-digit or 1-digit time')
            if not time:
                return ""
            if len(str(time))<2:
                return "0"+str(time)
            
            return time
        def jointime(self,time):
            return ':'.join(str(i) for i in time)
        def gettemp(self,time):
            if isinstance(time,str):
                time=self.splittime(time)
            return self.weather_as_dict[self.fillin(self.repairtime(self.jointime(time)))]
        def timetoint(self,time):
            if isinstance(time,str):
                return (self.splittime(time)[1]+self.splittime(time)[0]*60)%1440
            return (time[1]+time[0]*60)%1440
        def inttotime(self,i):
            return (i//60,i%60)

        def repairtime(self,time):
            closest=lambda num,collection:min(collection,key=lambda x:abs((x-num)+1))
            dy=self.weather_as_dict

            dy=[self.timetoint(time) for time in dy]
            qr=self.timetoint(self.roundtime(time))
            return self.jointime(self.inttotime(closest(qr,dy)))
            
        def roundtime(self,time):

            mins=int(time.split(':')[-1])
            if mins==0:
                return time
            hrs=int(time.split(':')[0])
            if mins<50:
                return f'{self.formatsec(hrs)}:00'
            return f'{self.formatsec(hrs+1)}:00'

        def mktime(self,time):
            return self.fillin(self.jointime(self.inttotime(self.timetoint(time))))



            
        def parsetime(self,time):
            pattern=re.compile('(\d{2}\:\d{2})\:\d{2}')
            return pattern.search(time).group(1)
        def parseday(self,time):
            pattern=re.compile('\d{4}-\d{2}-(\d{2})')
            return pattern.search(time).group(1)
        def c2f(self,fah,unit=CELSIUS):
            if unit==FAHRENHEIT:
                return tu(fah,'C','F').doconnvert()
            return fah

             
    def forecast(self,cityname=CITY,countryname=COUNTRY,unit=None):
        '''Gets forecast'''
        err=None
        if not countryname:
            try:
                countryname=getcountry(cityname)
            except AttributeError:
                err=NoSuchCityError(f"no such city: '{cityname}'")
        if err:
            raise err
        if cityname==CITY and not countryname:
            countryname=COUNTRY
        if unit is None:
            if countryname.lower()=='united states':
                unit=FAHRENHEIT
            else:
                unit=CELSIUS
        if cityname==CITY and countryname==COUNTRY:
            lat,lon=LOCATION.lat,LOCATION.lon
        else:
            loct=locator.geocode(f'{cityname},{countryname}')
            lat,lon=loct.latitude,loct.longitude
        ca=cacher.getcached(cityname,countryname)
        
        for caf in ca:
            foc=dumper.load(caf)
            if isinstance(foc,self.__class__.Forecast):
                return foc

        apiurl=f'https://www.7timer.info/bin/astro.php?lon={lon}&lat={lat}&ac=0&lang=en&unit=metric&output=json&tzshift=0'        
        return self.ForecastParser.parse(BetaChrome().request(apiurl)[1],unit,cityname,countryname)
    ForecastParser=_ForecastParser()

class _driverSearch:
    '''Search drivers'''
    def __init__(self,throw=False):
        if throw:
             debugger.debug("Lost connection to the driver,attempting reconnect...","ERROR")

        debugger.debug("initialized driver search")
        self.browsers=[Chrome,Firefox,Safari,Ie,Edge]
        self.reprs={repr(i):i for i in self.browsers}
        '''If it is possible, initiate in headless mode'''
        _CHOPT=chrome.options
        _FFXOPT=firefox.options
        _IEXOPT=ie.options
        opt=[_CHOPT,
             _FFXOPT,
             _IEXOPT,]
        opt=[i.Options() for i in opt]
        headlessopt=opt[:]
        hopt=[]
        for br in headlessopt:
            br.headless=True
            hopt.append(br)
        headlessopt=hopt
        self.headlessopt=[[Chrome,headlessopt[0]],[Firefox,headlessopt[1]],[Ie,headlessopt[2]]]
        del hopt
        if ('.cache/weather')not  in os.listdir():
            os.makedirs('.cache/weather',exist_ok=True)
        debugger.debug("Getting browser avaliability data")
        if ('aval') not in os.listdir('.cache/weather'):
            debugger.debug("Avaliability data not in cache!","WARNING")
            chrome_aval=False
            firefox_aval=False
            safari_aval=False
            ie_aval=False
            pjs_aval=False

            try:
                c=Chrome()
                c.quit()
                chrome_aval=True
            except:
                try:
                    f=Firefox()
                    f.quit()
                    firefox_aval=True
                except:

                    try:        
                        s=Safari()
                        s.quit()
                        safari_aval=True
                    except:
                        try:
                            i=Ie()
                            i.quit()
                            ie_aval=True
                       
            self.aval=[[Chrome,chrome_aval],[Firefox,firefox_aval],[Safari,safari_aval],[Ie,ie_aval]]
            with open('.cache/weather/aval','w')as f:
                res=[]
                for i,j in self.aval:
                    res.append([repr(i),j])
                debugger.debug("Json dumping data")
                json.dump(res,f)
        else:
            debugger.debug("Loading data from cache")
            with open('.cache/weather/aval')as f:
                try:
                    self.aval=json.load(f)
                except:
                    raise WeatherError(
                    'Could not get browser avaliability data because file .cache/weather/aval is malformed, maybe try to delete it?'
                    )
            result=[]
            for i in self.aval:
                if i[0] in self.reprs:
                    result.append([self.reprs[i[0]],i[1]])
                else:
                    result.append(i)
            self.aval=result
        if all([not i for i in [a[1] for a in self.aval]]):
            raise DriverError(
                '''None of web drivers installed. 
                    Check https://jenca-adam.github.io/projects/weather/docs.html#special_requirements .
                    Alternatively, you can use weather.yrno instead of weather.google .
                ''')
    def _checkin(self,a,b,index=0):
        for i in a:
            if b==i[index]:
                return True
        return False
    def _isaval(self,dr):
        for i in self.aval:
            if i[0]==dr and i[1]:
                return True
        return False
    def _gethopt(self,dr):
        for i in self.headlessopt:
            if i[0]==dr:
                return i[1]
    def best(self,reload=False):
        debugger.debug("Getting best driver")
        '''Get best driver'''
        if '.cache/weather' not in os.listdir() or reload:
            if '.cache/weather' not in os.listdir():
                debugger.debug("Could not load data from cache, parsing manually","WARNING")
            os.makedirs('.cache/weather',exist_ok=True)
            hdlsxst=False
            
            for b in self.browsers:
                if self._checkin(self.headlessopt,b):
                    hdlsxst=True
            if not hdlsxst:
                warnings.warn(
                    NoHeadlessWarning(
                                      '''
                                      No headless web driver, browser will open while searching for forecast.
                                      Headless web drivers are: chromedriver (Chrome),geckodriver (Mozilla Firefox),IEDriverServer.exe(Internet Explorer).
                                      Check https://jenca-adam.github.io/projects/weather/docs.html#headless_drivers'''
                                      )
                                    )
            for b in self.browsers:
                if  self._isaval(b):
                    with open('.cache/weather/browser','w') as f:
                        f.write(repr(b))
                    if self._checkin(self.headlessopt,b):
                        return b(options=self._gethopt(b))
                    return b()
        elif 'browser' not in os.listdir('.cache/weather'):
            debugger.debug("Could not load data from cache, parsing manually","WARNING")

            hdlsxst=False
            for b in self.browsers:
                if self._checkin(self.headlessopt,b):
                    hdlsxst=True
            if not hdlsxst:
                warnings.warn(
                    NoHeadlessWarning(
                                      '''
                                      No headless web driver, browser will open while searching for forecast.
                                      Headless web drivers are: chromedriver (Chrome),geckodriver (Mozilla Firefox),IEDriverServer.exe(Internet Explorer).
                                      Check https://jenca-adam.github.io/projects/weather/docs.html#headless_drivers'''
                                      )
                                    )
            for b in self.browsers:
                if  self._isaval(b):
                    with open('.weather/browser','w') as f:
                        f.write(repr(b))
                    if self._checkin(self.headlessopt,b):
                        return b(options=self._gethopt(b))
                    return b()
        else:
            debugger.debug("loading data from cache")
            cont=open('.weather/browser').read()
            b=self.reprs[cont]
            if self._checkin(self.headlessopt,b):
                    return b(options=self._gethopt(b))
            return b()
class _SetterUp:
    '''Sets up chromedriver and geckodriver'''
    SYSTEM=platform.system()
    if SYSTEM=='Windows':
        CHROMEDRIVER_URL="https://github.com/jenca-adam/jenca-adam.github.io/raw/master/projects/weather/extras/bin/win/chromedriver.exe"
        GECKODRIVER_URL="https://github.com/jenca-adam/jenca-adam.github.io/raw/master/projects/weather/extras/bin/win/geckodriver.exe"
    elif SYSTEM == 'Linux':
        CHROMEDRIVER_URL="https://github.com/jenca-adam/jenca-adam.github.io/raw/master/projects/weather/extras/bin/linux/chromedriver"
        GECKODRIVER_URL="https://github.com/jenca-adam/jenca-adam.github.io/raw/master/projects/weather/extras/bin/linux/geckodriver"
    else:
        CHROMEDRIVER_URL="https://github.com/jenca-adam/jenca-adam.github.io/raw/master/projects/weather/extras/bin/mac/chromedriver"
        GECKODRIVER_URL="https://github.com/jenca-adam/jenca-adam.github.io/raw/master/projects/weather/extras/bin/mac/geckodriver"
    
    HOME=str(Path.home())
    INSTALL_DIR=os.path.join(HOME,'.local/bin')
    if '.local' not in os.listdir(HOME):
        p=os.getcwd()
        os.chdir(HOME)
        os.makedirs('.local/bin')
        os.chdir(p)
    elif 'bin' not in os.listdir(os.path.join(HOME,'.local')):
        p=os.getcwd()
        os.chdir(HOME)
        os.makedirs('.local/bin')
        os.chdir(p)
    if INSTALL_DIR not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"]+=os.pathsep+INSTALL_DIR
    CHROMEDRIVER_INSTALL=os.path.join(INSTALL_DIR,CHROMEDRIVER_URL.split('/')[-1])
    GECKODRIVER_INSTALL=os.path.join(INSTALL_DIR,GECKODRIVER_URL.split('/')[-1])
    def install_cdr(self):
        debugger.debug("Installing chromedriver")
        h=Http()
        debugger.debug("Downloading chromedriver")
        r,content=h.request(self.CHROMEDRIVER_URL)
        
        with open(self.CHROMEDRIVER_INSTALL,'wb')as f:
            f.write(content)
        os.chmod(self.CHROMEDRIVER_INSTALL,0o777)
    def install_gecko(self):
        debugger.debug("Installing geckodriver")
        h=Http()
        r,content=h.request(self.GECKODRIVER_URL)
        with open(self.GECKODRIVER_INSTALL,'wb')as f:
            f.write(content)
        os.chmod(self.GECKODRIVER_INSTALL,0o777)

    def setup(self,drivers=['chromedriver','geckodriver']):
        debugger.debug("setting up")
        if not drivers:
            raise SetupError('please specify at least one driver')
        chopt=chrome.options.Options()
        ffxopt=firefox.options.Options()
        chopt.headless=True
        ffxopt.headless=True
        if 'chromedriver' in drivers:
            
            try:
                Chrome(options=chopt)
            except:
                self._setup(drivers=['chromedriver'])
        if 'geckodriver' in drivers:
            try:
                Firefox(options=ffxopt)
            except:
                self._setup(drivers=['geckodriver'])

    def _setup(self,drivers):
        
        if not drivers:
            raise SetupError('please specify at least one driver')
        if 'chromedriver' in drivers:
            self.install_cdr()
        if 'geckodriver' in drivers:
            self.install_gecko()
        chopt=chrome.options.Options()
        ffxopt=firefox.options.Options()
        chopt.headless=True
        ffxopt.headless=True
        try:
            Chrome(options=chopt)
        except:
            try:
                Firefox(options=ffxopt)
            except:
                raise SetupError('''
                                 Please note that weather.setup() works only for Firefox and Chrome for now.
                                 You have 2 options:
                                    1.Install Firefox or Chrome
                                    2.Don't call weather.setup on initializing and install one of the drivers manually.
                                    ''')
                
        
class _cukor:
    '''Advanced list comprehension'''
    def cukor(a,b,c,d,e):
        result=[]
        exec(
            f'''for {b} in {c}:
                    if {d}:
                        result.append({a})
                    else:
                        result.append({e})'''
            ,{
                'result':result})
        return result
                


class parser:
    '''Parses temperature and time strings'''
    class ParsingError(ValueError):pass
    def detectint(self,st):
        p=re.compile(r"(\-?\d+)")
        match=p.search(st)
        if not match:
            raise self.ParsingError(
                                    "no int detected"
                                    )
        return int(match.group(0))
    def is_inaccurate(self,st):
        i=self.detectint(st)
        return '-' in st
    def parse_inaccurate(self,t):
        if not self.is_inaccurate(t):
            try:
                return int(t)
            except ValueError:
                raise self.ParsingError("not a valid time")

        else:
            f,l=t.split('-')
            try:
                f=int(f)
                l=int(l)
            except ValueError:
                raise self.ParsingError("not a valid time")
            d=(l-f)//2
            if d<0:
                raise self.ParsingError(
                "not a valid time -- second int is larger than first")
            return f+d

class _Avg:
    '''get best forecast result'''
    SVC=['yrno','google']
    def forecast(self,*a,**k):
        ress=[]
        for service in self.SVC:
            debugger.debug(f"running service \"{service}\"")
            try:
                ress.append( SERVICES[service].forecast(*a,**k))
            except KeyboardInterrupt:
                raise SetupError("lost connection to service")
            except urllib3.exceptions.MaxRetryError:
                try:
                    debugger.debug("Lost connection to the driver,attempting reconnect...","ERROR")
                    importlib.reload(selenium)
                    ress.append(SERVICES[service].forecast(*a,**k))
                except urllib3.exceptions.MaxRetryError:
                    raise DriverError(
                                  """Because of unknown error in Selenium was lost connection to driver.
                                     Consider restarting your script/module"""
                                     )

            except WeatherError as e:
                
                if e==NoSuchCityError:
                    raise
                debugger.debug(f'service \"{service}\" does not recognise place',"ERROR")
            except selenium.common.exceptions.WebDriverException:
                raise DriverError(
                                 """Could not set up the driver, probably keyboard interrupt?"""
                                 )

            except Exception as e:
                
                if e==KeyboardInterrupt:
                    raise KeyboardInterrupt("interrupted while searching for forecast")
                raise
        if not ress:
            raise WeatherError("could not find service matching your search")
        fcast=[]
        city=ress[0].city
        country=ress[0].country
        for i in ress:
            dayc=0
            for day in i.days:
                if len(fcast)<dayc+1:
                    wdict={}
                else:
                    wdict=fcast[dayc].weather_as_dict
                for time,weather in day.weather_as_dict.items():
                    if time not in wdict:
                        wdict[time]=weather
                    else:
                        olw=wdict[time]
                        olw.temp=(olw.temp+weather.temp)//2
                        if weather.humid is not None:
                            olw.humid=(olw.humid+weather.humid)//2
                        olw.wind.speed=(olw.wind.speed+weather.wind.speed)/2
                        olw.wind.direction=Direction((olw.wind.direction.angle+weather.wind.direction.angle)//2)
                        if type(weather.precip) in [int,float]:
                            olw.precip=(weather.precip+olw.precip)/2
                        wdict[time]=olw
                fcast.append(yrno.Day(list(wdict.values()),wdict))
        return yrno.Forecast(fcast,city,country)

parser=parser()
google=_WeatherChannel()
yrno=_YR_NORI()
setup=_SetterUp()
average=_Avg()
debugger=_debugger()
f7timer=_7Timer()
dumper=_fcdumper()
DEBUG=False
debugger.debug=debugger.debug
cacher=_cacher()
fastener=_fastener()
getcountry=fastener.getcountry
SERVICES={'google':google,'yrno':yrno,'metno':yrno,'7timer':f7timer,'average':average}
def fix(svc):
    fxd = difflib.get_close_matches(svc,SERVICES.keys(),n=1,cutoff=0.7)
    if len(fxd)>0:
        return fxd[0]
    else:
        return svc
def forecast(cityname=CITY,countryname=None,unit=None,service=average,debug=False):
    global DEBUG,selenium
    DEBUG=debug
    if isinstance(service,str):
        try:
            service=SERVICES[service]
        except KeyError:
            afms=""
            excm="!"
            if fix(service)!=service:
                excm="?"
                afms=f", did you mean {fix(service)!r}"
            raise UnknownServiceError(f'unknown service : {service!r}{afms}{excm}') 
    debugger.debug("Debugger has started","INFO")
    if service==average:
        return service.forecast(cityname,countryname,unit)
    else:
        try:
            return service.forecast(cityname,countryname,unit)
        except KeyboardInterrupt:
                raise SetupError("lost connection to service")
        except urllib3.exceptions.MaxRetryError:
            debugger.debug("Lost connection to the driver,attempting reconnect...","ERROR")

            try:
                return service.forecast(cityname,countryname,unit,driver=_driverSearch(throw=True).best())
            except urllib3.exceptions.MaxRetryError:
                raise DriverError(
                              """Because of unknown error in Selenium was lost connection to driver.
                                 Consider restarting your script/module"""
                                 )
        except WeatherError as e:
            
            if e==NoSuchCityError:
                raise
            debugger.debug(f'service \"{service}\" does not recognise place ;{e} raised',"ERROR")
        except selenium.common.exceptions.WebDriverException:
            raise DriverError(
                             """Could not set up the driver, probably keyboard interrupt?"""
                             )
        except Exception as e:
            
            if e==KeyboardInterrupt:
                raise KeyboardInterrupt("interrupted while searching for forecast")
            raise

class More(object):
    def __init__(self, num_lines,debug=False):
        self.num_lines = num_lines
        self.debug=debug
    def __ror__(self, other):
        s = str(other).split("\n")
        print(*s[:self.num_lines], sep="\n")

        for i in range( self.num_lines,len(s)):
            print("--MORE--\r",end="")
            key=getchlib.getkey()
            
            if key.lower()=='q' :
                if not self.debug:
                    termutils.clear()
                quit()
            if key in ['\x1b[B','\x1b[6~',' ','\n']:
                print(s[i])
        time.sleep(0.1)

class CLI:
    def main(self):
        parser=argparse.ArgumentParser(description='Python app for getting weather forecast')
        parser.add_argument('--city',type=str,help='City for forecast (if not passed, using current location)',nargs=1)
        parser.add_argument('--country',type=str,help='Country for forecast (see above)',nargs=1)
        parser.add_argument('-d','--debug',action='store_true',help='Debug')
        parser.add_argument('-s','--service',type=str,help='Service to use (e.g. "yrno","7timer","google"). Implied with "average"(try to optimise the service)')
        args=parser.parse_args()
        if not args.city:
            args.city=[CITY]
        if not args.country:
            args.country=[None]
        if not args.service:
            args.service="average"
        
        if not args.debug:
            termutils.clear()
            print('Loading ...')
        foc=forecast(args.city[0],args.country[0],service=args.service,debug=args.debug)
        if foc is None:
            raise NoSuchCityError(f'no such city :{args.city[0]!r}')
        if not args.debug:
            termutils.clear()
        termcolor.cprint('Weather forecast for',end=' ',color='cyan')
        termcolor.cprint(','.join([foc.city,foc.country]),color='yellow')
        if isinstance(foc,yrno.Forecast):
            source='Yr.no'
        elif isinstance(foc,google.Forecast):
            source='Google'
        elif isinstance(foc,f7timer.Forecast):
            source='7timer!'
        else:
            source=None
        lac=2
        if source:
            print('Source : '+source)
            lac+=1
        foc2t(foc)|More(num_lines=os.get_terminal_size().lines-lac,debug=args.debug)  
        
cli=CLI()
main=cli.main
if __name__=='__main__':
    main()
