from twisted.python import defer, delay
from twisted.internet import main
from urlparse import urlparse
import ltodolist
import lserverbase
import time, random
import logging

db = []
deferredStack = []
hostLaterList = {}

log = logging.getLogger('frontier')
log.setLevel(20)

def getInfo():
    return ("frontier", ["db size: %d" % len(db),
                         "hostLaterList: %d" % len(hostLaterList),
                         "deferredStack size: %d" % len(deferredStack)])        
            

def cleanHostLaterList():
    """remove old entrys from host later list"""
    log.debug("cleaning hostLaterList (%d entries)" % len(hostLaterList.keys()))
    barrier = time.time() - config.server_min_pause 
    for x in hostLaterList.keys():
        if hostLaterList[x] < barrier:
            del(hostLaterList[x])
    # rerun in 10 minutes
    main.addTimeout(lambda : cleanHostLaterList(), 600)
    log.debug("hostLaterList now %d entries" % len(hostLaterList.keys()))


def addHostLaterList(host, wait = None):
    if wait == None:
        wait = config.server_min_pause
    hostLaterList[host] = time.time() + wait
    log.debug("host %r added for %r seconds to laterList ", host, wait)
    

def checkHostLaterListOk(host):
    if host in hostLaterList:
        if hostLaterList[host] > time.time():
            return 0
        else:
            del hostLaterList[host]
            log.debug("host %r removed from laterList ", host)
    return 1
    

def refillDb():
    "refills db from todolist"
    log.debug("refilling db (now %d entries) from todolist", len(db))
    x = ltodolist.get()
    while x:
        db.insert(-1, x)
        x = ltodolist.get()
    log.debug("db now %d entries" % len(db))



def handleDeferredStack():
    #if len(db) == 0:
    #    refillDb()

    while len(deferredStack) > 0:
        x = deferredStack.pop(0)
        log.debug('poping one callback from deferredStack')        
        if not getUrl(x):
            log.debug("couldn't clean deferredStack")
            return 0
        return 1
            

# callbacks

def urlProhibited(url, ip, deferred):
    log.debug("prohibited: %s", url)
    # retry later to get another url
    deferredStack.append(deferred)
    

def urlDelayed(url, host, wait, deferred):
    "we should try later"
    log.debug("delayed: %s %r", url, wait)
    # reinsert it to our todolist
    db.append(url)
    addHostLaterList(host, wait)
    # retry later to get another url
    # we can't call getUrl ourself becaouse this would bring us in recursion hell
    #deferredStack.append(deferred)
    getUrl(deferred)
                
        
def accessOk(url, ip, deferred):
    log.debug("allowed: %s", url)
    deferred.callback((url, ip))


def getUrl(deferred):
    log.debug("new URL is requested")
    dbRefilled = 0
    loopDetector = None
    # first work through our backlog
    if len(deferredStack) > 0 and len(deferredStack) < 5:
        # if deferredStack is big this can lead to an very deep recursion,
        # so we will let twisted.loop do the invocation in this case
        handleDeferredStack()
    while 1:
        if len(db) == 0:
            # we are out of data. try to aquire some more
            if not dbRefilled:
                # just try once
                dbRefilled = 1
                refillDb()
                # retry this loop
                continue
            else:
                log.error("completely out of urls - waiting 20s to try again - hope this helps")
                main.addTimeout(lambda : getUrl(deferred), 11)
                return 1
        else:
            url = db.pop(0)
            if loopDetector == None:
                loopDetector = url
            elif url == loopDetector:
                # we had the first loop
                # put url back
                db.append(url)
                if not dbRefilled:
                    # just try once
                    dbRefilled = 1
                    refillDb()
                    log.debug("tested whole db, refilling")
                    continue
                else:
                    log.info("tested whole db and already refilled retrying later")
                    main.addTimeout(lambda : getUrl(deferred), 10)
                    return 1
            # first check it with hostLaterList.
            (foo, host, foo, foo, foo, foo) = urlparse(url)
            if not checkHostLaterListOk(host):
                db.append(url)
                continue
            else:
                log.debug("checking %s", url)            
                lserverbase.isAllowed(url, accessOk, urlProhibited, urlDelayed, deferred)
                return 1


# call handleDeferredStack every 10 Seconds
d = delay.Delayed()
d.loop(handleDeferredStack, 2)
main.addDelayed(d)


if __name__ == '__main__':
    from twisted.internet import main

    def callback(*args):
        print repr(args)

    deferred = defer.Deferred()
    deferred.addCallback(callback)
    getUrl(deferred)
    deferred.arm()
    main.run()

