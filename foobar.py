# --drt@un.bewaff.net - http://c0re.jp/

import logging

# wh have to do this first, so imported modules can use alredy the loggers
log = logging.getLogger('scheduler')
log.setLevel(20)
logging.basicConfig()

from twisted.internet import main
from twisted.python import delay
from twisted.python import defer 
from lresource import Resource
from lhttpclient import Fetcher
from extractlinks import parseForUrlsInHtml
from pprint import pprint
from urlparse import urlparse, urlunparse
import sys
import time
import ldupecheck, ltodolist
import archivemanager
import lfrontier
import lgetinfo

active_fetchers = 0
max_fetchers = 1


class HandleUrl:
    def __init__(self, url, deferred, ip = None):    
        r = Resource(url, ip)
        self.starttime = time.time()
        deferred.addCallback(self.callback)
        deferred.addErrback(printError)
        log.debug('starting fetcher')
        f = Fetcher(r, deferred)
        deferred = None
        f.start()
        
    def callback(self, resource):
        global active_fetchers
        
        self.arrivedtime = time.time()
        log.debug('resource arrived: %s %r', resource.url, resource.headers['Content-Type'])
        if resource.headers.has_key('Content-Type'):
            if resource.headers['Content-Type'].startswith('text/html'):
                # snarf new urls
                try:
                    parseForUrlsInHtml(resource.body, resource.url)
                except:
                    log.error("*** parsing error: %r - %r", resource.body, vars(resource))
                for newurl in parseForUrlsInHtml(resource.body, resource.url):
                    (scheme, host, path, parameters, query, fragment) = urlparse(newurl)
                    newurl = urlunparse((scheme, host, path, parameters, query, ''))
                    if newurl.startswith('http://'):
                        if ldupecheck.checkIfOkAndAdd(newurl):
                            ltodolist.add(newurl)
                # save data
                log.debug('archiving')
                archivemanager.store(resource)
            else:
                log.info("ignoring Content-Type: %s %s" % (resource.headers['Content-Type'], resource.url))
        else:
            log.warn("no Content-Type: %s %r" % (resource.url, vars(resource)))

        self.handledtime = time.time()
        active_fetchers -= 1
        try:
            l = len(resource.body)
        except TypeError:
            l = 0
        log.info('done %db in %.3fs (%.3f net, %.3f handl.): %s', l,
                 self.handledtime - self.starttime,
                 self.arrivedtime - self.starttime,
                 self.handledtime - self.arrivedtime,
                 resource.url)
        checkNextUrl()

def printError(*args):
    print "*** error %r" % args
    checkNextUrl()

    
def checkNextUrl(*args):
    global active_fetchers
        
    def getUrlError(*args):
        global active_fetchers
        log.error("getUrl raised an error: %r" % args)
        active_fetchers -= 1
        checkNextUrl()

    def callback((url, ip)):
        deferred = defer.Deferred()
        log.debug('fetching new url: %r %r', url, ip)
        h = HandleUrl(url, deferred, ip)
        deferred.addErrback(printError)
        deferred.arm()
        deferred = None

    active_fetchers += 1
    deferred = defer.Deferred()
    deferred.addCallback(callback)
    deferred.addErrback(getUrlError)
    log.debug('requesting new url from frontier')
    x = lfrontier.getUrl(deferred)
    deferred.arm()
    if not x:
        # TODO: finished
        #pprint(ldupecheck.db.keys())
        main.stopMainLoop()
        return

def monitor():
    """Should be run once a minute."""
    for i in range(max_fetchers - active_fetchers):
        log.warn('monitor is starting new checker')
        checkNextUrl()
            

def _test():
    # create a delayed object
    d1 = delay.Delayed()
    # run monitor every x ticks
    d1.loop(monitor, 6)
    # register the Delayed object with the Twisted event loop:
    main.addDelayed(d1)

    d2 = delay.Delayed()
    d2.loop(lgetinfo.dumpInfo, 12)
    main.addDelayed(d2)

    monitor()
    log.debug('staring event loop')
    sys.setrecursionlimit(10000)
    main.run()


if __name__ == '__main__':
    _test()
    
