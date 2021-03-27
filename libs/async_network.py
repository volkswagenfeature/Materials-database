# Functions for use with async native, coordnating with other libraies, etc.
import requests as req
  



# Jobs and tools for use with async_native paralell stuff above
def run_get (url, session, *args, **kwargs):
    return session.get(url, *args, **kwargs)

def get_matID(urls,session = req.Session(),postprocess = md.pageprocess):
    def shimfunc(url):
        # Fetching URL
        d_out = postprocess(session.get(url))
        return d_out
    
    for url in urls:
        yield lambda _ = url : shimfunc(_)

def get_page (url,ses, postprocess = md.pageprocess):
    rval = ses.get(url)
    matdict = postprocess(rval)
    return matdict
