#!/usr/bin/python

# $Id$ 

import httplib, socket, mimetools
from urlparse import urlparse
import pycurl
import servers

from config import config

#class response
class HTTPMessage(mimetools.Message):

    def addheader(self, key, value):
        """Add header for field key handling repeats."""
        prev = self.dict.get(key)
        if prev is None:
            self.dict[key] = value
        else:
            combined = ", ".join((prev, value))
            self.dict[key] = combined

    def addcontinue(self, key, more):
        """Add more field data from a continuation line."""
        prev = self.dict[key]
        self.dict[key] = prev + "\n " + more

    def readheaders(self):
        self.dict = {}
        self.unixfrom = ''
        self.headers = hlist = []
        self.status = ''
        headerseen = ""
        firstline = 1
        startofline = unread = tell = None
        if hasattr(self.fp, 'unread'):
            unread = self.fp.unread
        elif self.seekable:
            tell = self.fp.tell
        while True:
            if tell:
                try:
                    startofline = tell()
                except IOError:
                    startofline = tell = None
                    self.seekable = 0
            line = self.fp.readline()
            if not line:
                self.status = 'EOF in headers'
                break
            # Skip unix From name time lines
            if firstline and line.startswith('From '):
                self.unixfrom = self.unixfrom + line
                continue
            firstline = 0
            if headerseen and line[0] in ' \t':
                # XXX Not sure if continuation lines are handled properly
                # for http and/or for repeating headers
                # It's a continuation line.
                hlist.append(line)
                self.addcontinue(headerseen, line.strip())
                continue
            elif self.iscomment(line):
                # It's a comment.  Ignore it.
                continue
            elif self.islast(line):
                # Note! No pushback here!  The delimiter line gets eaten.
                break
            headerseen = self.isheader(line)
            if headerseen:
                # It's a legal header line, save it.
                hlist.append(line)
                self.addheader(headerseen, line[len(headerseen)+1:].strip())
                continue
            else:
                # It's not a header line; throw it back and stop here.
                if not self.dict:
                    self.status = 'No headers'
                else:
                    self.status = 'Non-header line where header expected'
                # Try to undo the read.
                if unread:
                    unread(line)
                elif tell:
                    self.fp.seek(startofline)
                else:
                    self.status = self.status + '; bad seek'
                break

class HTTPResponse:

    # strict: If true, raise BadStatusLine if the status line can't be
    # parsed as a valid HTTP/1.0 or 1.1 status line.  By default it is
    # false because it prevents clients from talking to HTTP/0.9
    # servers.  Note that a response with a sufficiently corrupted
    # status line will look like an HTTP/0.9 response.

    # See RFC 2616 sec 19.6 and RFC 1945 sec 6 for details.

    def __init__(self):
        self.headerstmp = []
        self.bodytmp = []


    def header_callback(self, data):
        self.headerstmp.append(data)

    def body_callback(self, data):
        self.bodytmp.append(data)

    def finalize(self):
        print self.headerstmp
        print self.bodytmp
        self.header = ''.join(self.headerstmp) 
        self.body = ''.join(self.bodytmp)

def request(page, url):
    servers.noteAccess(url)
    print repr(url)
    (scheme, networklocation, path, parameters, query, fragment) = urlparse(url)
    host = networklocation.split(':')[0]
    c = pycurl.Curl() 
    try:
        h = httplib.HTTPConnection(networklocation)
    except httplib.InvalidURL, msg:
        # XXX we should try to parse things like http://bxyqwq:olacfy@213.239.160.18/flz/fdr/barely/index.htm
        print "***", msg
        return None
    h.set_debuglevel(config.http_debug)
    if query:
        h.putrequest('GET', '%s?%s' % (path, query))
    else:
        h.putrequest('GET', path)
    h.putheader('Accept', config.http_accept)
    h.putheader('User-agent', config.http_useragent)
    r = HTTPResponse()
    c.setopt(c.URL, url)
    c.setopt(c.HTTPHEADER, [config.http_useragent])
    c.setopt(pycurl.VERBOSE, 1)
    c.setopt(c.WRITEFUNCTION, r.body_callback)
    c.setopt(c.HEADERFUNCTION, r.header_callback)
    c.setopt(pycurl.DNS_CACHE_TIMEOUT, 3600)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(pycurl.USERAGENT, '212')
    c.setopt(pycurl.ENCODING, 'identity')
    c.setopt(pycurl.COOKIEJAR, 'c00kiejar')
    c.setopt(pycurl.CONNECTTIMEOUT, 60)
    c.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)
#for args in self.addheaders: h.putheader(*args)
    h.endheaders()
    h.sock.settimeout(config.http_timeout)
    c.perform()
    r.finalize()
    print c.getinfo(pycurl.HTTP_CODE)
    print c.getinfo(pycurl.EFFECTIVE_URL)
    print c.getinfo(pycurl.RESPONSE_CODE)
    print c.getinfo(pycurl.TOTAL_TIME)
    print c.getinfo(pycurl.NAMELOOKUP_TIME)
    print c.getinfo(pycurl.CONNECT_TIME)
    print c.getinfo(pycurl.REDIRECT_COUNT)
    print c.getinfo(pycurl.SIZE_DOWNLOAD)
    print c.getinfo(pycurl.SPEED_DOWNLOAD)
    print c.getinfo(pycurl.HEADER_SIZE)
    print c.getinfo(pycurl.REQUEST_SIZE)
    print c.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)
    print c.getinfo(pycurl.CONTENT_TYPE)
    
    c.close()
    

    try:
        response = h.getresponse()
    except httplib.BadStatusLine, msg:
        # XXX we should try to parse things like http://bxyqwq:olacfy@213.239.160.18/flz/fdr/barely/index.htm
        print "***", msg
        return None
    page.read = response.read
    page.header = response.msg
    #response.close()
    
    if response.status == 200:
        page.url = url
    elif response.status == 204:        # No Content
        return None
    elif response.status == 300:        # Multiple Choices
        # XXX this could be handled much smarter
        return None
    elif response.status in [301,
                             302,
                             303,
                             ]:
        page.urls.append(url)
        if len(page.urls) > 32:
            print vars(request)
            raise RuntimeError, "too many redirects"
        page.url = response.getheader('Location')
        print 'redirect: %r' % page.url
        (nscheme, nnetworklocation, npath, nparameters, nquery, nfragment) = urlparse(page.url)
        if scheme != nscheme:
            print "*** protocol change detected"
            return None 
        if page.url in page.urls:
            # we have a loop
            print "*** loop detected"
            return None
        request(page, page.url)
    elif response.status == 400:
        # bad request
        # XXX this should not happen
        return None    
    elif response.status in [401,       # unauthorized
                             403,       # access denied
                             404,       # not fond
                             405,       # method no supported
                             410,       # Gone
                             414,       # Request URI Too Large
                             423,       # Locked
                             ]:
        return None
    elif response.status in [500,
                             502,       # Bad Gateway
                             ]:
        # internal error
        return None    
    else:
        print vars(response)
        print vars(response.msg)
        raise RuntimeError, "unknown response code"

    return page


def fetch(page):
    try:
        return request(page, page.url)    
    except socket.error, msg:
        print "***", msg, page
        return None
    except UnicodeError, msg:
        print "***", msg, page
        return None

if __name__ == '__main__':
    import socket

    class Page:
        def __init__(self):
            self.urls = []

    request(Page(), 'http://md.hudora.de/blog')
    for x in open('starturls.txt'):
        try:
            request(Page(), x.strip())
        except socket.error:
            pass
        
