#!/usr/bin/python

# $Id$ 

import time, random
from urlparse import urlparse, urlunparse

from pprint import pprint

from config import config


serverlist = {}

class ServerInfo:
    def __init__(self):
        self.accesses = 0
        self.lastaccess = 0

    def __repr__(self):
        return repr(vars(self))
    

def normalizeName(name):
    name = name.lower()
    (scheme, netloc, path, params, query, fragment) = urlparse(name, 'http', 0)
    return urlunparse((scheme, netloc, '', '', '', ''))


def noteAccess(name):
    name = normalizeName(name)
    server = serverlist.setdefault(name, ServerInfo())
    server.lastaccess = int(time.time())
    server.accesses += 1
    

def mayAccess(name):
    name = normalizeName(name)
    server = serverlist.setdefault(name, ServerInfo())
    graceperiod = config.minservergraceperiod \
                  + (random.random() * ((config.averageservergraceperiod * 2) - config.minservergraceperiod))
    if server.lastaccess + graceperiod < time.time():
        return True
    else:
        return False

