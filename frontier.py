__doc__ = "managment of URLs to crawl"

import urlparse
import socket
import time
import pickle
import urldupcheck

# minimum seconds do wait before we hit a server again
overloadtime = 60
overloadlist = {}

def isOverloaded(host):
    if time.time() - overloadlist[host] > overloadtime:
        del overloadlist[host]
        return None
    else:
        return 1
    
def overloadAdd(host):
    overloadlist[host] = time.time()

def ageOverload():
    now = time.time()
    for (host, t) in overloadlist.values():
        if now - t > overloadtime:
            del overloadlist[host]

class Frontier:
    def __init__(self):
        try:
            self.queue = pickle.load(open('frontier.pyk'))
        except:
            print "creating new frontier"
            self.queue = []
            

    def __del__(self):
        pickle.dump(self.queue, open('frontier.pyk', 'w'))
        

    def add(self, protocol='', host='', path='', parameters='', query='', fragment=''):
        "Add an entry to the frontier"
        #if urldupcheck.isDup(url):
        #    return

        # add portnumber if missing
        s = host.find(':')
        if s == -1:
            port = socket.getservbyname(protocol, 'tcp')
            host = host + ':' + str(port)
        self.queue.append((protocol, host, path, parameters, query, fragment))


    def addURL(self, url):
        "Add an URL to the frontier"
        self.add(urlparse.urlparse(url, 'http', 0))


    def getURL(self):
        "Get an URL from the frontier"
        ret = get()
        if ret == None:
            return None
        else:
            return urlparse.urlunparse(ret)


    def get(self):
        "Get an entry from the frontier"

        if len(self.queue) < 1:
            return None

        # rotate the queue until we find a suitable value
        for i in xrange(len(self.queue)):
            (protocol, host, path, parameters, query, fragment) = self.queue.pop(0)
            if isOverloaded(host):
                # reappend it to the end
                self.queue.append((protocol, host, path, parameters, query, fragment))
            else:
                overloadAdd(host)
                return (protocol, host, path, parameters, query, fragment)

        # all out entries are from overloaded servers

f = Frontier()
get = f.get
getURL = f.getURL
add = f.add
addURL = f.addURL

