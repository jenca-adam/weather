from .chrome import Chrome as _chr
_br=_chr()
request=_br.request
def search(query):
    return request(f'https://google.com/search?q={query}')[1]
