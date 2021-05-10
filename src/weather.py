import json
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
locator=Nominatim(user_agent="geoapiExercises")
_h=Http()
CELSIUS=0
UNIT=CELSIUS
FAHRENHEIT=1
_DONTCHECK=-1

_HDR={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"}
class Browser:
    def request(self,url):
        return _h.request(url,headers=self.HEADERS)
class BetaChrome(Browser):
    HEADERS=_HDR
class DriverWarning(Warning):pass
class WeatherWarning(Warning):pass
class SVGWarning(WeatherWarning):pass
class NoHeadlessWarning(DriverWarning):pass
class WeatherError(BaseException):pass
class NoSuchCityError(WeatherError):pass
class DriverError(Exception):pass
h=httplib2.Http()
class IpError(ValueError):pass
class Fail(IpError):pass
class InvalidQuery(Fail):pass
class ReservedRange(Fail):pass
def searchurl(query):
    return f'https://google.com/search?q={query}'
def getstate(city):
    return locator.geocode(city).address.split(',')[-1][1:]
def _rq(h,u):
    try:
        return h.request(u)
    except ConnectionResetError:
        return _rq(h,u)
def _track(ip):
    r,c=_rq(h,f'http://ip-api.com/json/{ip}')
    return json.loads(c)
def _checkresp(msg,stat):
    
    if stat=='success':return
    if stat=='fail':
        if msg=='reserved range':
            raise ReservedRange(msg)
        elif msg=='invalid query':
            raise InvalidQuery(msg)
        raise Fail(msg)
    raise IpError(msg)
def checkresp(resp,ip=''):
    if ip:
        r2=track()
        if r2==resp:
            if r2.query!=resp.query:
                raise InvalidQuery('invalid query')
    if 'message' not in resp:return
    _checkresp(resp['message'],resp['status'])
def track(ip=''):
    resp=_track(ip)
    checkresp(resp,ip)
    return resp
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
_br=BetaChrome()
request=_br.request
def search(query):
    return request(searchurl(query))[1]

CITY=curloc().city
COUNTRY=curloc().country
if COUNTRY=='United States':
    UNIT=FAHRENHEIT
def refresh(ip=''):
    if not ip:
        city=curloc().city
        country=curloc().country
    else:
        city=iploc(ip).city
        country=iploc(ip).country

    return city,country
class _WeatherChannel:
    def __init__(self):
        self.driver=None
    class Weather:
        def __init__(self,temp,humidity,wind):
            self.temp=temp
            self.humidity=humidity
            self.wind=wind
    class Day:
        def __init__(self,dayname,highest,lowest,desc):
            self.dayname=dayname
            self.highest=highest
            self.lowest=lowest
            self.desc=desc
        def __repr__(self):
            return repr(self.__dict__)
    def convert(self,d):
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
        l=[]
        for i in d:
            m=i
            if isinstance(i,self.Day):
                m=i.__dict__
            l.append(m)
        return l
    class Forecast:
        def __init__(self,temp,today,nxt,temps):
            e=None
            if not isinstance(today,_WeatherChannel.Day):
                raise TypeError(
                f"'today' argument must be weather._WeatherChannel.Day, not {today.__class__}'")
            try:
                iter(nxt)
            except:
                e=TypeError("'nxt' argument is not iterable")
            if e is not None:
                raise e
            for i in nxt:
                if not isinstance(i,_WeatherChannel.Day):
                    raise TypeError(
                    f"all members of 'nxt' argument must be \"weather.day.Day\", not {i.__class__}'")
            self.temp=temp
            self.today=today
            self.nxt=nxt
            self.temps=temps           
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
        def __repr__(self):
            return repr(_WeatherChannel.convert(_WeatherChannel,self.__dict__))
    def splittime(self,time,after=int):
            try:
                return tuple(after(i) for i in time.split(':'))
            except ValueError:
                raise ValueError(
                                f"invalid value for 'splittime':{time}"
                                )

    def parsetemp(self,t,unit=UNIT):
        return int(t.find_all(class_="wob_t")[unit].text)
    def parseday(self,d,unit=UNIT):
        s=bs(str(d),'html.parser')
        dayname=s.find(class_="QrNVmd Z1VzSb")['aria-label']
        desc=s.find(class_="DxhUm").img['alt']
        tmps=bs(str(s.find(class_="wNE31c")),'html.parser')
        highest=self.parsetemp(tmps.find(class_="vk_gy gNCp2e"),unit=unit)
        lowest=self.parsetemp(tmps.find(class_="QrNVmd ZXCv8e"),unit=unit)
        return self.Day(dayname,highest,lowest,desc)
    def getsvg(self,ch,unit):
        try:
                ch.find_elements_by_class_name("jyfHyd")[1].click()
        except:pass
        #wait until forecast loads 
        time.sleep(0.7)
        svg=ch.find_element_by_id('wob_gsvg')
        svg=svg.get_attribute('outerHTML')
        return self.analyzesvg(svg,unit)
    def getprecip(self,ch):
        precip_html_element=ch.find_element_by_id('wob_pg')
        precip_html=precip_html_element.get_attribute('outerHTML')
        precip_soup=bs(precip_html,
                        'html.parser')
        columns=precip_soup.findAll(class_="wob_hw")
    def getwind(self,ch):pass
    def getgraph(self,ch,unit):
        svg=self.getsvg(ch,unit)
        precip=self.getprecip(ch)
        wind=self.getwind(ch)
        return svg
    def analyzesvg(self,svg,unit):
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

    def parsefcast(self,d,temp,svg,unit=CELSIUS):

        soup=bs(d,'html.parser')
        g=soup.find_all(class_="wob_df")
        g=[self.parseday(i,unit=unit) for i in g]
        first=g[0]
        nxt=g[1:]
        return self.Forecast(temp,first,nxt,svg)
    def forecast(self,cityname=CITY,countryname='',unit=None):
        err=None
        if self.driver is None:
            driver=_driverSearch()
            self.driver=driver.best()
        wd=self.driver
        if not countryname:
            try:
                countryname=getstate(cityname)
            except AttributeError:
                err=NoSuchCityError(f"no such city: '{cityname}'")
        if err:
            raise err
        if cityname==CITY:
            countryname=COUNTRY
        if unit is None:
            if countryname.lower()=='united states':
                unit=FAHRENHEIT
            else:
                unit=CELSIUS
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
        
            return self.parsefcast(str(fli),tempnow,svg,unit=unit)
        except:
            err=WeatherError(f"could not get forecast for city {cityname}")
            if countryname==_DONTCHECK:
                raise err
            return self.forecast(cityname,_DONTCHECK,unit)
    def ipforecast(self,ip):
        return self.forecast(*refresh(ip))
    def _prstmpstr(self,string):
        pattern=re.compile('^(\d+)°')
        match=pattern.search(string)

        if not match:
            raise ValueError(
                            'Could not parse temperature string')
        return int(match.group(0).replace('°',''))
class _driverSearch:
    def __init__(self):
        
        self.browsers=[Chrome,Firefox,Safari,Ie,Edge,PhantomJS]
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
        if ('.weather')not  in os.listdir():
            os.mkdir('.weather')
        if ('aval') not in os.listdir('.weather'):
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
                    ffx_aval=True
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
                        except:
                            try:
                                pjs=PhantomJS()
                                pjs.quit()
                                pjs_aval=True
                            except:pass

            self.aval=[[Chrome,chrome_aval],[Firefox,firefox_aval],[Safari,safari_aval],[Ie,ie_aval],[PhantomJS,pjs_aval]]
            with open('.weather/aval','w')as f:
                res=[]
                for i,j in self.aval:
                    res.append([repr(i),j])
                json.dump(res,f)
        else:
            with open('.weather/aval')as f:
                try:
                    self.aval=json.load(f)
                except:
                    raise WeatherError(
                    'Could not get browser avaliability data because file .weather/aval is malformed, maybe try to delete it?'
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
                    Alternatively, you can use weather.NOAA or weather.yrno instead of weather.google .
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
        return True
    def _gethopt(self,dr):
        for i in self.headlessopt:
            if i[0]==dr:
                return i[1]
    def best(self):
        if '.weather' not in os.listdir():
            os.mkdir('.weather')
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
        elif 'browser' not in os.listdir('.weather'):
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
            cont=open('.weather/browser').read()
            b=self.reprs[cont]
            if self._checkin(self.headlessopt,b):
                    return b(options=self._gethopt(b))
            return b()
class _cukor:
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

                    
                


        

google=_WeatherChannel()

