# --drt@un.bewaff.net - http://c0re.jp/

from twisted.python import defer 
from twisted.internet import tcp
from twisted.protocols import http
from pprint import pprint
import logging
from lconfig import config

log = logging.getLogger(__name__)

_returntypes = {}
_bytes_bodys = 0
_bytes_headers = 0

def getInfo():
    urls_checked = 0
    for x in _returntypes.values():
        urls_checked += x
    return ('httpclient', ['urls checked: %d' % urls_checked,
                           'byted read: %d (%d header, %d body)' % (_bytes_bodys + _bytes_headers,
                                                                      _bytes_headers,
                                                                      _bytes_bodys),
                           'returncodes: %r' % _returntypes])


class lenzHTTPClient(http.HTTPClient):
    def __init__(self, host, path, deferred=None):
        self.host = host
        self.path = path
        self.headers = {}
        self.data = None
        self.status = 0
        if deferred == None:
            self.deferred = defer.Deferred()
        else:
            self.deferred = deferred
        
    def connectionMade(self):
        self.sendCommand('GET', self.path)
        self.sendHeader('Host', self.host)
        self.sendHeader('User-Agent', config.user_agent_full)
        self.endHeaders()
        # I  don't fully understand why http.py doesn't handle this itself
        self.firstLine = 1

    def connectionFailed(self):
        if self.deferred:
            self.deferred.errback('Connection failed while getting %s %s' % (self.host, self.path))
        self.deferred = None

    def connectionLost(self):
        global _returntypes
        global _bytes_bodys
        global _bytes_headers
        http.HTTPClient.connectionLost(self)
        _returntypes[self.status] = _returntypes.setdefault(self.status, 0) + 1
        try:
            _bytes_bodys += len(self.data)
        except TypeError:
            pass
        for (x, y) in self.headers.items():
            # 3 is for ": " and \n
            _bytes_headers += len(x) + len(y) + 3
        if self.deferred:
            if self.data == '':
                # our data wasn't collected by handle_response up to now
                http.HTTPClient.rawDataReceived(self, None):
            self.deferred.callback((self.status, self.headers, self.data))
        self.deferred = None

    def handleStatus(self, version, status, message):
        self.status = int(status)

    def handleHeader(self, key, val):
        self.headers[key] = val

    def handleResponse(self, requestData):
        self.data = requestData
        # just to be sure
        try:
            self.transport.socket.shutdown(1)
        except AttributeError:
            # if the socket is already gone, we don't care
            pass


class Fetcher:
    def __init__(self, resource, deferred):
        self.deferred = deferred
        self.resource = resource

    def callback(self, (status, headers, body)):
        self.resource.body = body
        self.resource.headers = headers
        self.resource.status = status
        if status == 301:
            self.resource.redirectlist.append(self.resource.url)
            self.resource.setUrl(headers['Location'])
            if len(self.resource.redirectlist) > 200:
                log.warning("too much redirections at %s" % self.resource.redirectlist[0])
                self.deferred.errback(self.resource)
                self.deferred = None
            else:
                self.start()
        elif status == 200:
            self.deferred.callback(self.resource)
            self.deferred = None
        else:
            log.warn("http error %s - %s" % (status, self.resource.url))
            pprint(self.deferred)
            self.deferred.errback("http error %s - %s %r" % (status, self.resource.url, headers))
            self.deferred = None
            
    def errback(self, *args):
        print "***error", repr(args)

    def start(self):
        d = defer.Deferred()
        d.addCallback(self.callback)
        d.addErrback(self.errback)
        client = lenzHTTPClient(self.resource.host, self.resource.path, d)
        tcp.Client(self.resource.ip, self.resource.port, client)
        d.arm()

def _test():
    from twisted.internet import main
    from pprint import pprint
    import lresource
    def callback(*args):
        print pprint(vars(args[0]))
        main.stopMainLoop()
        
    r = lresource.Resource('http://md.hudora.de/jura')
    d = defer.Deferred()
    d.addCallback(callback)
    f = Fetcher(r, d)
    d.arm()
    f.start()

    main.run()

if __name__ == '__main__':
    _test()
