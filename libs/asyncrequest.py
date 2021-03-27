#import asyncio as aio

# Used for asynchronous webpage fetching
import twisted.internet as tin 
from twisted.internet.defer import inlineCallbacks, DeferredList, Deferred
from twisted.internet.task import react

import requests_threads as ret

# Used for delays and tracking execution time
import time

# Used to handle results
import libs.mat_definitions as md

def in_notebook():
    try:
        from IPython import get_ipython
        if 'IPKernelApp' not in get_ipython().config:  # pragma: no cover
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True
notebook = in_notebook()

@inlineCallbacks
def matIDasyncfetch (url,session): 
    pg = yield session.get(url)
    res = md.pageprocess(pg)
    return res 

def pause_gather (waittime,mats):
    def pausehook(results):
        for page in results:
            mats.update(page)
        print(f"Sleeping for {waittime} seconds")
        time.sleep(waittime)
        return results
    return pausehook
    

def cleanup (results):
    print("cleaning up!")
    tin.reactor.stop()
    return results


class batch_page_request:
    def __init__(self, url_list=[], page_processor=matIDasyncfetch,
                 concurrent_reqs=5, batch_size=10, wait_time=0):

        """
        Sets up the fetching behavior, and initial url-list
        url_list is the urls to fetch
        concurrent_reqs is the number of open connections
        batch_size is the number of items in a batch
        wait_time is how long to wait inbetween batches.
        """
        self.url_list = url_list
        self.concurrent_reqs = concurrent_reqs
        self.batch_size = batch_size
        self.wait_time = wait_time
        self.session = ret.AsyncSession(n=concurrent_reqs)
        self.processor = page_processor
   
    def run (self):
            rollingresult = {}
            deferredchain = Deferred()
            print("Setting up defered chain")
            while self.url_list:
                if self.batch_size < len(self.url_list):
                    batch_actual = self.batch_size
                    terminator = pause_gather(self.wait_time,rollingresult)
                else:
                    batch_actual = len(self.url_list)
                    terminator = cleanup
                #thisbatch = [self.url_list.pop() for _ in range(batch_actual)]
                thisbatch = self.url_list[-batch_actual:]
                print("built: \n\t-"+"\n\t-".join(thisbatch))
                PFR_list = [self.processor(url, self.session) for url in thisbatch]
                delta = tin.defer.gatherResults(PFR_list)
                delta.addCallback(terminator)
                deferredchain.chainDeferred(delta)
            self.downloadedvalues = rollingresult
            
            
            tin.reactor.run()
            return rollingresult
        
        

    def save (self, filepath="./materialdump.csv"):
        with open(filepath,'w') as data:
            data.write("Hexadecimal matID , Material Name\n")
            for key,entry in self.downloadedvalues.items():
                data.write(f"{key:x} , {entry}\n")
