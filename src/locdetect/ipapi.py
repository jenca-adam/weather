import httplib2
import json

h=httplib2.Http()
class IpError(ValueError):pass
class Fail(IpError):pass
class InvalidQuery(Fail):pass
class ReservedRange(Fail):pass
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

