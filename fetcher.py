#!/usr/bin/python

# $Id$ 

import httplib, socket
from urlparse import urlparse
import pycurl
import servers

from config import config

class response

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
    c.setopt(c.URL, url)
    c.setopt(c.HTTPHEADER, [config.http_useragent])
    c.setopt(pycurl.VERBOSE, 1)
    c.setopt(c.WRITEFUNCTION, page.body_callback)
    #CURLOPT_AUTOREFERER
    #CURLOPT_ENCODING identity
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    #for args in self.addheaders: h.putheader(*args)
    h.endheaders()
    h.sock.settimeout(config.http_timeout)
    c.perform()
    print c.getinfo(pycurl.HTTP_CODE)
    print c.getinfo(pycurl.EFFECTIVE_URL)
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
        
