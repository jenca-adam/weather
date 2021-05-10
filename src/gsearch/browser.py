from httplib2 import Http
_h=Http()

class Browser:
    def request(self,url):
        return _h.request(url,headers=self.HEADERS)

