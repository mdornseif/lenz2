#!/usr/bin/python

# $Id:$ 

import logging
log = logging.getLogger(__name__)

import httplib, socket, mimetools
from urlparse import urlparse
import pycurl
import servers

from config import config


class Download(mimetools.Message):
    """Handler for downloading data from URLs.

    Somewhat reesembling httplibs HTTPReply
    """
    
    def __init__(self, curl):
        self.headerstmp = []
        self.body = ''
        self.curl = curl
        self.curl.setopt(pycurl.WRITEFUNCTION, self.body_callback)
        self.curl.setopt(pycurl.HEADERFUNCTION, self.header_callback)

        
    def header_callback(self, data):
        self.headerstmp.append(data)


    def body_callback(self, data):
        self.body += data


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


    def finalize(self): 
        self.status = self.curl.getinfo(pycurl.RESPONSE_CODE)

        # construct haders
        firstline = 1
        self.dict = {}
        self.headers = hlist = []
        headerseen = ""
 
        for line in self.headerstmp:
            line = line.rstrip()
            firstline = 0
            if self.islast(line):
                # Note! No pushback here!  The delimiter line gets eaten.
                break
            elif headerseen and line and line[0] in ' \t':
                # XXX Not sure if continuation lines are handled properly
                # for http and/or for repeating headers
                # It's a continuation line.
                hlist.append(line)
                self.addcontinue(headerseen, line.strip())
                continue
            elif self.iscomment(line):
                # It's a comment.  Ignore it.
                continue
            headerseen = self.isheader(line)
            if headerseen:
                # It's a legal header line, save it.
                hlist.append(line)
                self.addheader(headerseen, line[len(headerseen)+1:].strip())
                continue

        del self.headerstmp
        self.addheader('X-LENZ-HTTP-Status', str(self.curl.getinfo(pycurl.HTTP_CODE)))
        self.addheader('X-LENZ-Effective-URL', self.curl.getinfo(pycurl.EFFECTIVE_URL))
        self.addheader('X-LENZ-Redirect-Count', str(self.curl.getinfo(pycurl.REDIRECT_COUNT)))

        self.type = self.curl.getinfo(pycurl.CONTENT_TYPE)
        
        #self.addheader('X-LENZ-TOTAL_TIME', str(self.curl.getinfo(pycurl.TOTAL_TIME)))
        #self.addheader('X-LENZ-NAMELOOKUP_TIME', str(self.curl.getinfo(pycurl.NAMELOOKUP_TIME)))
        #self.addheader('X-LENZ-CONNECT_TIME', str(self.curl.getinfo(pycurl.CONNECT_TIME)))
        #self.addheader('X-LENZ-SPEED_DOWNLOAD', str(self.curl.getinfo(pycurl.SPEED_DOWNLOAD)))
        

def get_curl_handle():
    c = pycurl.Curl() 
    c.setopt(pycurl.VERBOSE, config.http_debug)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(pycurl.USERAGENT, config.http_useragent)
    c.setopt(pycurl.ENCODING, 'identity')
    c.setopt(pycurl.COOKIEJAR, '.cookies.txt')
    c.setopt(pycurl.COOKIEFILE, '.cookies.txt')
    c.setopt(pycurl.HTTPHEADER, ['Accept: %s' % config.http_accept])
    c.setopt(pycurl.DNS_CACHE_TIMEOUT, 3600)
    c.setopt(pycurl.CONNECTTIMEOUT, config.http_timeout)
    c.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)
    return c

class MultiCurl:
    def __init__(self):
        self.m = pycurl.CurlMulti()
        self.handles = {}

    def add(self, handle):
        self.handles[handle] = True
        self.m.add_handle(handle)

    def loop(self):
        while 1:
            ret, num_handles = self.m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
            
        while num_handles:
            ret = self.m.select()
            if ret == -1:
                continue
            while 1:
                ret, num_handles = self.m.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break

eventloop = MultiCurl()


def request(page, url):
    servers.noteAccess(url)
    log.info('retriving %r' % url)
    (scheme, networklocation, path, parameters, query, fragment) = urlparse(url)
    host = networklocation.split(':')[0]

    c = get_curl_handle()
    d = Download(c)
    c.setopt(c.URL, url)

    eventloop.add(c)
    eventloop.loop()
    
    # try:
    #     c.perform()
    # except pycurl.error, msg:
    #    log.error("*** %s" % msg)
    #    return None    
        
    d.finalize()
    
    page.header = d
    page.data = d.body
    
    if d.status == 200:
        page.url = url
    elif d.status == 204:        # No Content
        return None
    elif d.status in [300,       # Multiple Choices
                      302,       # Found - not really sure how to handle this
                      ]:        
        # XXX this could be handled much smarter
        return None
    elif d.status in [400,
                      401,       # unauthorized
                      403,       # access denied
                      404,       # not fond
                      405,       # method no supported
                      410,       # Gone
                      414,       # Request URI Too Large
                      423,       # Locked
                      ]:
        return None
    elif d.status in [500,              # internal error
                      502,              # Bad Gateway
                      0,                # No Header was send 
                      ]:
        return None    
    else:
        # print vars(d)
        log.exception("unknown response code %r" % d.status)
        raise RuntimeError, "unknown response code %r" % d.status
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
        
