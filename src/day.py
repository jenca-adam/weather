import json
class Day:
    def __init__(self,dayname,highest,lowest,desc):
        self.dayname=dayname
        self.highest=highest
        self.lowest=lowest
        self.desc=desc
    def __repr__(self):
        return repr(self.__dict__)


