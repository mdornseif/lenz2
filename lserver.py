# --drt@un.bewaff.net - http://c0re.jp/

import time
import robotparser
import texttools
from twisted.python import defer 
from twisted.names import dns
from twisted.internet import main
from twisted.internet import tcp
from twisted.protocols import http
from lconfig import config
import logging

log = logging.getLogger('server')
log.setLevel(20)

robotparser.debug = config.robotparser_debug
resolver = dns.ResolveConfResolver()

class _RobotsHTTPClient(http.HTTPClient):
    def __init__(self, host, deferred=None):
        self.host = host
        if deferred == None:
            self.deferred = defer.Deferred()
        else:
            self.deferred = deferred
        
    def connectionMade(self):
        self.sendCommand('GET', '/robots.txt')
        self.sendHeader('Host', self.host)
        self.sendHeader('User-Agent', config.user_agent_full)
        self.endHeaders()
        # I  don't fully understand why http.py doesn't handle this itself
        self.firstLine = 1
        
    def connectionLost(self):
        http.HTTPClient.connectionLost(self)
        if self.deferred:
            log.info("connection lost before data recived")
            http.HTTPClient.rawDataReceived(self, None):
            self.handleResponse(b)
        self.deferred = None

    def connectionFailed(self):
        if self.deferred:
            self.deferred.errback('%s: connection failed while getting robots.txt' % self.host)
        self.deferred = None

    def handleStatus(self, version, status, message):
        # TODO: Handle Expires header
        if status == '401' or status == '403':
            # http://www.robotstxt.org/wc/norobots-rfc.html
            #     - On server response indicating access restrictions (HTTP Status
            #       Code 401 or 403) a robot should regard access to the site
            #       completely restricted.
            # this is one by simulating a certain robots.txt
            self.deferred.callback('\nUser-agent: *\nDisallow: /\n')
            self.deferred = None            
        elif int(status) >= 400:
            # robots.txt was not found. Everything is allowed
            self.deferred.callback('')
            self.deferred = None            
        elif status != '200':
            # TODO: handle redirects
            if self.deferred:
                self.deferred.errback('%s: bad Status from while getting robots.txt %s %s'
                                      % (self.host, status, message))
            self.deferred = None

    def handleResponse(self, requestData):
        # TODO: DoS prefention, Size limitation
        if self.deferred:
            self.deferred.callback(requestData)
        self.deferred = None


class webserver:
    def __init__(self, host, port = 80):
        log.debug('new webserver object: %r' % host)
        self.host = host
        self.port = port
        self.ip = None
        self._iptime = 0
        self._robots = None
        self._robotstime = 0
        self._robotsparser = robotparser.RobotFileParser()
        self.lasterrordesc = None
        self.lastcontact = 0
        self.lasterror = 0
        self.lasttry = 0
        self.lastaccess = 0
        self._outstandingrobotsrequests = []

        # get IP which triggers an get robots when ready
        dnsdeferred = self._getIP()
        dnsdeferred.addCallback(self._getRobots)
        dnsdeferred.arm()

    def _setError(self, text):
        """sets error status"""
        self.lasterrordesc = text
        self.lasterror = time.time()

    def _trying(self):
        """update self.lasttry"""
        self.lasttry = time.time()

    def _getIP(self):
        global resolver
        
        """gets the IP for the hostname in async manner"""

        def _dnsAnswer(answer):
            log.debug("got ip %r for host %r" % (answer, self.host))
            self.ip = answer
            self._iptime = time.time()
            return "firstrun"

        def _dnsFailure(arg):
            log.error('error while resolving IP: %r, %r' % (self.host, arg))
            self._setError("could not resolve: %s" % arg)

        log.debug('resolving IP: %r' % self.host)
        dnsdeferred = resolver.resolve(self.host)
        dnsdeferred.addCallback(_dnsAnswer)
        # after we got the IP we will fetch the robots.txt
        dnsdeferred.addErrback(_dnsFailure)
        self._trying() 
        return dnsdeferred

    def _genericFailure(msg):
            print "error: %s" % arg
            self._setError(arg)

    def _getRobots(self, foo = None):
        """get robots.txt"""

        def _robotsAnswer(answer):
            self._robots = answer
            self._robotstime = time.time()
            lines = texttools.splitlines(answer)
            self._robotsparser.parse(lines)
            log.debug("recived robots.txt for %r: doing %d callbacks" % (self.host, len(self._outstandingrobotsrequests)))
            for x in self._outstandingrobotsrequests:
                x.callback(answer)
            self._outstandingrobotsrequests = []
            return answer
    
        def _requestRobots():
            log.debug("starting http request for robots.txt for %r" % (self.host))
            deferred = defer.Deferred()
            deferred.addCallback(_robotsAnswer)
            client = _RobotsHTTPClient(self.host, deferred)
            tcp.Client(self.ip, self.port, client)
            self._trying()
            return deferred

        if foo == "firstrun":
            log.debug("IP just arrived, getting robots.txt for %r" % (self.host))
            deferred = _requestRobots()
            deferred.arm()
            return deferred
        elif self.ip != None:
            log.debug("calling outstanding requests for getting robots.txt for %r" % (self.host))
            for x in self._outstandingrobotsrequests:
                x.callback(self._robots)
            self._outstandingrobotsrequests = []
            return _requstRobots()
        else:
            # we are still waiting for the DNS to resolve
            # so crete a deferred we will return and fire it when dns is done
            log.debug("we still have no ip, delayed getting robots.txt for %r" % (self.host))
            deferred = defer.Deferred()
            self._outstandingrobotsrequests.append(deferred)
            return deferred
        
    def _checkRobotsCallback(self, data, url, resultcb = None):
        if resultcb != None:
            # check if the actual url is not exluded by robots.txt                    
            resultcb.callback((url, self._robotsparser.can_fetch(config.user_agent, url), self.ip))
        resultcb = None

    def isAllowed(self, url, resultcb = None):
        if self._robots == None:
            # TODO: here we could also check for expired robots.txt
            deferred = self._getRobots()
            deferred.addCallback(self._checkRobotsCallback, url, resultcb)
            deferred.arm()
        else:
            self._checkRobotsCallback(self._robots, url, resultcb)

    def isTooEarly(self, url):
        if time.time() - self.lastaccess < config.server_min_pause:
            return self.lastaccess + config.server_min_pause - time.time()  
        else:
            self.lastaccess = time.time()
            return 0
        

def _test():
    w = webserver('md.hudora.de')

    def bar(data):
        # TODO
        log.error('unhandled error')
        print repr(data)

    deferred = defer.Deferred()
    deferred.addCallback(bar)
    w.isAllowed('http://md.hudora.de/dornet/', deferred)
    deferred.arm()
    deferred = defer.Deferred()
    deferred.addCallback(bar)
    w.isAllowed('http://md.hudora.de/jura/', deferred)
    deferred.arm()
    
    main.run()



if __name__ == '__main__':
    _test()
