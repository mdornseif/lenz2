__doc__ = "managment of URLs to crawl"

import urlparse
import socket
import serverbase
import serverblacklist
import urlbase
import urldupcheck

def add(url, protocol = None, host = None, port = None):

    if urldupcheck.isDup(add):
        return
    
    (protocol, host, path, parameters, query, fragment) = urlparse.urlparse(url, 'http', 0)

    # find out which URL to parse
    s = host.find(':')
    if s == -1:
        port = socket.getservbyname(protocol, 'tcp')
        phost = host + ':' + str(port)
    else:
        port = int(host[s+1:])
        phost = host
        host = host[:s]

    nurl = urlparse.urlunparse((protocol, phost, path, parameters, query, fragment))
    serverbase.addServer((protocol, host, port))
    urlbase.addURL((protocol, host, port), nurl) 

def getURL():

    s = serverbase.getServer()
    if s == None:
        return None

    firstserver = s

    url = urlbase.getURL(s)

    while url == None:
        s = serverbase.getServer()
        if s == None:
            return None

        # check if we are in a loop
        if s == firstserver:
            return None
        
        url = urlbase.getURL(s)

    if serverblacklist.has_key(s):
        url = getURL()
        
    return url

def get():
    ret = getURL()

    if ret != None:
        (protocol, host, path, parameters, query, fragment) = urlparse.urlparse(ret, 'http', 0)

        s = host.find(':')
        port = int(host[s+1:])
        host = host[:s]

        ret = (protocol, host, port, path, ret)

    return ret
