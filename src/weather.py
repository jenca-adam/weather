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
import platform
import subprocess
from pathlib import Path
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
class SetupError(WeatherError):pass
class ReadonlyError(Exception):pass
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
        def __init__(self,wind,precip,temp):
            self.temp=temp
            self.precip=precip
            self.wind=wind
    class Day:
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
            return self.gettemp(i)
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
        def __init__(self,temp,today,nxt):
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
                    f"all members of 'nxt' argument must be \"_WeatherChannel.Day\", not {i.__class__}'")
            self.temp=temp
            self.today=today
            self.days=nxt
            self.tomorrow=nxt[0]
        def day(self,num):
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
        svg=self.getsvg(ch,unit)
        precip=self.getprecip(ch)
        wind=self.getwind(ch)

        svglist=[list(a.keys()) for a in svg]
        preciplist=[list(a.keys()) for a in precip]
        windlist=[list(a.keys()) for a in wind]
        wthrs=[]
        wthrs_inner=[]
        ind=0
        for a in wind:
            inner=0
            wthrs_inner=[]
            
            for j in a:
                t=a[j]
                wthrs_inner.append(
                             self.Weather(
                                          t,
                                          precip[ind][j],
                                          svg[ind][j]
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
                                          t,
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

    def parsefcast(self,days,temp,unit=CELSIUS):
        first=days[0]
        nxt=days[1:]
        return self.Forecast(temp,first,nxt)
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
        if cityname==CITY and not countryname:
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
        
            return self.parsefcast(svg,tempnow,unit=unit)
        except Exception as e:
            raise e
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
class _YR_NORI:
    class SearchResults:
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
        def __init__(self,wlst,wdict):
            self.wlst=wlst
            self.wdict=wdict

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
            if len(time)>2:
                raise ValueError('not 2-digit or 1-digit time')
            if len(time)<2:
                return "0"+time
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
        def __init__(self,days):
            self.days=days
        def __getitem__(self,i):
            return self.day(i)
        def __setitem__(self,item,what):
            raise ReadonlyError('read-only')

        def day(self,daynum):
            return self.days[daynum]
    def searchurl(self,q):
        return f'https://yr.no/en/search?q={q}'
    def expandhref(self,href):
        return f'https://yr.no{href}'
    def search(self,q):
        self.driver=_driverSearch().best()
        self.driver.get(
            self.searchurl(q)
            )
        results=bs(self.driver.find_elements_by_class_name('search-results-list')[0].get_attribute('outerHTML'),
        'html.parser')
        results=results.findAll('li')
        results=[self.expandhref(result.a['href']) for result in results]
        return self.SearchResults(results) 
    def forecast(self,cityname=CITY,countryname=COUNTRY):
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
        if cityname==CITY and not countryname:
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
        c=search(query).result(0)
        return self.ForecastParser(c)

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
                    Alternatively, you can use weather.NOAA instead of weather.google .
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
class _SetterUp:
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
        os.mkdir('.local')
        os.mkdir('.local/bin')
        os.chdir(p)
    elif 'bin' not in os.listdir(os.path.join(HOME,'.local')):
        p=os.getcwd()
        os.chdir(HOME)
        os.mkdir('.local/bin')
        os.chdir(p)
    if INSTALL_DIR not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"]+=os.pathsep+INSTALL_DIR
    CHROMEDRIVER_INSTALL=os.path.join(INSTALL_DIR,CHROMEDRIVER_URL.split('/')[-1])
    GECKODRIVER_INSTALL=os.path.join(INSTALL_DIR,GECKODRIVER_URL.split('/')[-1])
    def install_cdr(self):
        
        h=Http()
        r,content=h.request(self.CHROMEDRIVER_URL)
        with open(self.CHROMEDRIVER_INSTALL,'wb')as f:
            f.write(content)
        os.chmod(self.CHROMEDRIVER_INSTALL,0o777)
    def install_gecko(self):
        h=Http()
        r,content=h.request(self.GECKODRIVER_URL)
        with open(self.GECKODRIVER_INSTALL,'wb')as f:
            f.write(content)
        os.chmod(self.GECKODRIVER_INSTALL,0o777)

    def setup(self,drivers=['chromedriver','geckodriver']):
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
yrno=_YR_NORI()
setup=_SetterUp()
