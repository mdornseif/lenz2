# --drt@un.bewaff.net - http://c0re.jp/

from urlparse import urlparse, urlunparse

# get service by name would be cleaner bit is sometimes broken on MacOS X
_default_port = { 'http': 80,
                  'https': 443,
                  'gopher': 70,
                  'news': 119,
                  'snews': 563,
                  'nntp': 119,
                  'snntp': 563,
                  'ftp': 21,
                  'telnet': 23,
                  'prospero': 191
                  } 

class Resource:
    """Resource saves Infomation about a resource on the
    internet. Mainly an url and if needed URLs which redirect to this
    resource http header and body data."""
    
    def __init__(self, url, ip = None):
        """ip can be given to get arround dns delays"""
        self.redirectlist = []
        self.headers = {}
        self.body = None
        self.status = 0
        self.setUrl(url, ip)

    def setUrl(self, url, ip = None):
        self.url = url
        (self.scheme, self.host, self.path, self.parameters, self.query, self.fragment) = urlparse(url)
        if self.fragment != '':
            self.url = urlunparse((self.scheme, self.host, self.path, self.parameters, self.query, ''))
        x = self.host.find(':')
        if x == -1:
            # use default port
            if self.scheme in _default_port:
                self.port = _default_port[self.scheme]
            else:
                print "unknown scheme %r" % (self.scheme)
                self.port = 0
        else:
            self.port = int(self.host[x+1:])
            self.host = self.host[:x]
        if ip == None:
            # TODO: start async lookup
            self.ip = self.host
        else:
            self.ip = ip
