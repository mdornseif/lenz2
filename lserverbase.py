from twisted.python import defer 
from lserver import webserver
from urlparse import urlparse
import time, random
import logging

log = logging.getLogger('serverbase')
log.setLevel(20)

db = {}

def getInfo():
    return ('serverbase', ['serverbase size: %s' % len(db)])


def callback((url, allowed, ip), (host, yesfunc, nofunc, laterfunc, d)):
    log.debug('got info for %r (%s): %r' % (url, ip, allowed))
    if allowed:
        x = db[host].isTooEarly(host)
        log.debug('isTooEarly(%s): %r' % (host, x))
        if x:
            laterfunc(url, host, x, d)
        else:
            yesfunc(url, ip, d)
    else:
        nofunc(url, ip, d)
    
def isAllowed(url, yesfunc, nofunc, laterfunc, d):    
    """Checks if url should be addressed and resolfes the IP for the
    host url points to.

    Calls yesfunc(url, ip) if access is permitted, nofunc(url, ip) if
    access is denyed (e.g. by robots.txt) and laterfunc(url, wait) if
    url should be retried not less than wait seconds later."""
    
    log.debug('checking %r' % url)
    (foo, hostport, foo, foo, foo, foo) = urlparse(url)
    x = hostport.find(':')
    if x == -1:
        # use default port
        port = 80
        host = hostport
    else:
        port = int(hostport[x+1:])
        host = hostport[:x]
    if not db.has_key(hostport):
        log.debug('creating new db entry for %r' % hostport)
        db[hostport] = webserver(host, port)
    deferred = defer.Deferred()
    deferred.addCallback(callback, (host, yesfunc, nofunc, laterfunc, d))
    # TODO: errback?
    db[host].isAllowed(url, deferred) 
    deferred.arm()

if __name__ == '__main__':
    laterdb = {}
    def yesfunc(url, ip, deferred):
        print "OK %s" % url
    
    def nofunc(url, ip, deferred):
        print "prohibited %s" % url

    def laterfunc(url, wait, deferred):
        "we should try later"
        
        print "later %s %d" % (url, wait)
        key = time.time() + wait
        while 1:
            if key in laterdb:
                key += random.random()
            else:
                break
        laterdb[key] = url

            
    from twisted.internet import main
    isAllowed('http://md.hudora.de/', yesfunc, nofunc, laterfunc)
    isAllowed('http://lolitacoders.org/', yesfunc, nofunc, laterfunc, deferred)
    isAllowed('http://lolitacoders.org/', yesfunc, nofunc, laterfunc, deferred)
    isAllowed('http://lolitacoders.org/', yesfunc, nofunc, laterfunc, deferred)
    isAllowed('http://lolitacoders.org/', yesfunc, nofunc, laterfunc, deferred)
    isAllowed('http://lolitacoders.org/', yesfunc, nofunc, laterfunc, deferred)
    main.run()
