#!/usr/bin/python

# $Id:$ 

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO) 

import httplib, socket, mimetools
from urlparse import urlparse
import pycurl
import servers

from config import config
from status import status

class HTTPResponse(mimetools.Message):
    """Handler for downloading data from URLs.

    Somewhat reesembling httplibs HTTPReply.
    """
    
    def __init__(self, curl, headers, body):
        self.status = curl.getinfo(pycurl.RESPONSE_CODE)
        self.type = curl.getinfo(pycurl.CONTENT_TYPE)
        self.url = curl.getinfo(pycurl.EFFECTIVE_URL)

        # construct haders
        firstline = 1
        self.dict = {}
        self.headers = hlist = []
        headerseen = ""
 
        for line in headers:
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

        self.addheader('X-LENZ-HTTP-Status', str(curl.getinfo(pycurl.HTTP_CODE)))
        self.addheader('X-LENZ-Effective-URL', curl.getinfo(pycurl.EFFECTIVE_URL))
        self.addheader('X-LENZ-Redirect-Count', str(curl.getinfo(pycurl.REDIRECT_COUNT)))

        status.curl_total_time.append(curl.getinfo(pycurl.TOTAL_TIME))
        status.curl_namelookup_time.append(curl.getinfo(pycurl.NAMELOOKUP_TIME))
        status.curl_connect_time.append(curl.getinfo(pycurl.NAMELOOKUP_TIME))
        status.curl_speed_download.append(curl.getinfo(pycurl.SPEED_DOWNLOAD))

        del headers
        self.body = body
        del body
        del curl
        
        
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

    def __repr__(self):
        v = vars(self)
        if 'body' in self.dict:
            v['body'] = v['body'][:30] + '...'
        return str(v)
        
class Curly:
    def __init__(self):
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.VERBOSE, config.http_debug)
        self.curl.setopt(pycurl.FOLLOWLOCATION, 1)
        self.curl.setopt(pycurl.MAXREDIRS, 5)
        self.curl.setopt(pycurl.USERAGENT, config.http_useragent)
        self.curl.setopt(pycurl.ENCODING, 'identity')
        self.curl.setopt(pycurl.COOKIEJAR, 'cookies.txt')
        self.curl.setopt(pycurl.COOKIEFILE, 'cookies.txt')
        self.curl.setopt(pycurl.HTTPHEADER, ['Accept: %s' % config.http_accept])
        self.curl.setopt(pycurl.DNS_CACHE_TIMEOUT, 3600)
        self.curl.setopt(pycurl.CONNECTTIMEOUT, config.http_timeout)
        self.curl.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)
        self.curl.setopt(pycurl.WRITEFUNCTION, self.body_callback)
        self.curl.setopt(pycurl.HEADERFUNCTION, self.header_callback)
        self.reinit()
        # beware - this creates a circular reference
        self.curl.curly = self

    def reinit(self):
        self.headerstmp = []
        self.body = ''
        self.done_callback = None
        
    def header_callback(self, data):
        self.headerstmp.append(data)

    def body_callback(self, data):
        self.body += data

    def setCallback(self, callback):
        self.done_callback = callback
        
    def setUrl(self, url):
        self.curl.setopt(pycurl.URL, url)

    def done(self):
        if self.done_callback:
            response = HTTPResponse(self.curl, self.headerstmp, self.body)
            del self.headerstmp
            del self.body
            self.done_callback(response)
        self.reinit()


class MultiCurl:
    def __init__(self):
        self.m = pycurl.CurlMulti()
        self.handles = {}
        self.freelist = []

        
    def addHandle(self, handle):
        self.handles[handle] = True
        self.m.add_handle(handle.curl)
        status.active_downloads += 1

    def getHandle(self):
        if len(self.freelist) > 0:
            handle = self.freelist.pop()
        else:
            handle = Curly()
        self.addHandle(handle)
        return handle


    def loop(self):
        # Run the internal curl state machine for the multi stack
        while 1:
            ret, num_handles = self.m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
            
        #while num_handles:
        if 1:
            ret = self.m.select()
            if ret != -1:
                while 1:
                    ret, num_handles = self.m.perform()
                    if ret != pycurl.E_CALL_MULTI_PERFORM:
                        break

        # Check for curl objects which have terminated, and add them to the freelist
        while 1:
            num_q, ok_list, err_list = self.m.info_read()
            for c in ok_list:
                self.m.remove_handle(c)
                status.active_downloads -= 1
                status.download_successes +=1
                log.debug("Success: %s" % c.getinfo(pycurl.EFFECTIVE_URL))
                c.curly.done()
                self.freelist.append(c.curly)
            for c, errno, errmsg in err_list:
                self.m.remove_handle(c)
                status.active_downloads -= 1
                status.download_failures +=1
                log.warn("Failed: %r %s" % (errno, errmsg))
                self.freelist.append(c.curly)
                c.curly.done()
            if num_q == 0:
                break
                
eventloop = MultiCurl()

loop = eventloop.loop

def fetch(page):
    servers.noteAccess(page.url)
    log.info('retriving %r' % page.url)
    c = eventloop.getHandle()
    c.setCallback(page.receivedFromNetwork)
    c.setUrl(page.url)
    eventloop.loop()

