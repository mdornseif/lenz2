# $Id: urlbase.py,v 1.1 2002/01/28 22:26:22 drt Exp $

"""List of URLs to spider.

  --drt@un.bewaff.net
"""

import time

class urlObj:

    def __init__(self, server, url):
        self.server = server
        self.url = url

    def getID(self):
        return (self.server, self.url)

    def getURL(self):
        return self.url

    def getID(self):
        return ((self.server, self.url))

    def __repr__(self):
        return "<urlObj: %s, %s>" % (self.server, self.url)
    
urllist = {}

def addURL(server, url):
    if not urllist.has_key(server):
        urllist[server] = []
    urllist[server].append(urlObj(server, url))

def getURL(server):
    if (not urllist.has_key(server)) or (len(urllist[server]) == 0):
        return None

    ret = urllist[server].pop(0).url
    if len(urllist[server]) == 0:
        del urllist[server]

    return ret
