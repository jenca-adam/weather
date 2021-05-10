from bs4 import BeautifulSoup as bs
from .forecast import Forecast
from .day import Day
def parsetemp(t):
    return int(t.find(class_="wob_t").text)
def parseday(d):
    s=bs(str(d),'html.parser')
    dayname=s.find(class_="QrNVmd Z1VzSb")['aria-label']
    desc=s.find(class_="DxhUm").img['alt']
    tmps=bs(str(s.find(class_="wNE31c")),'html.parser')
    highest=parsetemp(tmps.find(class_="vk_gy gNCp2e"))
    lowest=parsetemp(tmps.find(class_="QrNVmd ZXCv8e"))
    return Day(dayname,highest,lowest,desc)
def parsefcast(d,temp):

    soup=bs(d,'html.parser')
    g=soup.find_all(class_="wob_df")
    g=[parseday(i) for i in g]
    first=g[0]
    nxt=g[1:]
    return Forecast(temp,first,nxt)


