from .day import Day
import json

def convert(d):
    l={}
    for a in d:
        i=d[a]
        m=i
        if isinstance(i,Day):
            m=i.__dict__
        if isinstance(i,list):
            m=convlist(i)
        l[a]=m
    return l    
def convlist(d):
    l=[]
    for i in d:
        m=i
        if isinstance(i,Day):
            m=i.__dict__
        l.append(m)
    return l
class Forecast:
    def __init__(self,temp,today,nxt):
        e=None
        if not isinstance(today,Day):
            raise TypeError(
            f"'today' argument must be weather.day.Day, not {today.__class__}'")
        try:
            iter(nxt)
        except:
            e=TypeError("'nxt' argument is not iterable")
        if e is not None:
            raise e
        for i in nxt:
            if not isinstance(i,Day):
                raise TypeError(
                f"all members of 'nxt' argument must be \"weather.day.Day\", not {i.__class__}'")
        self.temp=temp
        self.today=today
        self.nxt=nxt
    def __repr__(self):
        return repr(convert(self.__dict__))
  
