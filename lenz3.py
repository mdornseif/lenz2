#!/usr/bin/python

# $Id$ 


import logging
logging.basicConfig()

log = logging.getLogger()
log.setLevel(logging.DEBUG) #set verbosity to show all messages of severity >= DEBUG

import os, time
import urllib

import extractlinks
import servers
import fetcher

from config import config
from status import status
from queues import dupelist, pagefetchqueue, pageparsequeue, documentfetchqueue

from output.larbin import LarbinOutputSystem, LarbinLowMemOutputSystem

documentoutput = LarbinLowMemOutputSystem(config.documentdir)
pageoutput = LarbinOutputSystem(config.pagedir)

from pprint import pprint


class Page:
    def __init__(self):
        self.urls = []
        self.body = ''

    def __repr__(self):
        return repr(vars(self))

    def getData(self):
        return self.body

    def receivedFromNetwork(self, response):
        self.header = response
        self.status = response.status
        self.type = response
        self.body = response.body
        self.url = response.url
        del response.body
        self.processLoadedPage()

    def processLoadedPage(self):
        """To be called after page is received from the network."""
        if self.status == 200:
            # add to parse queue & save if needed
            dummy, ext = os.path.splitext(self.url)
            ext = ext.lower()
            if self.header.gettype() in config.pagemimetypes:
                pageoutput.save(self)
                pageparsequeue.add(self)
            elif ext in config.documentsuffixes or self.header.gettype() in config.documentmimetypes:
                print "*** docsave" 
                documentoutput.save(self)
                pagefetchqueue.add(parenturl(self.url))
        elif self.status == 204:        # No Content
            return None
        elif self.status in [300,       # Multiple Choices
                          302,       # Found - not really sure how to handle this
                          ]:        
            # XXX this could be handled much smarter
            return None
        elif self.status in [400,
                          401,       # unauthorized
                          403,       # access denied
                          404,       # not fond
                          405,       # method no supported
                          410,       # Gone
                          414,       # Request URI Too Large
                          423,       # Locked
                          ]:
            return None
        elif self.status in [500,              # internal error
                             502,              # Bad Gateway
                             503,
                             504,              # Origin Server Timeout
                             0,                # No Header was send 
                             ]:
            return None    
        else:
            print vars(self.header)
            log.exception("unknown response code %r" % self.status)
            raise RuntimeError, "unknown response code %r" % self.status


def parenturl(url):
    return '/'.join(url.split('/')[:-1]) + '/'

def fetch_a_page():
    page = Page()
    page.url = pagefetchqueue.get() 
    fetcher.fetch(page)
    return None


def fetch_a_document():
    page = Page()
    page.url = documentfetchqueue.get() 
    fetcher.fetch(page)
    return None


def parse_a_page():
    if not pageparsequeue:
        return
    
    page = pageparsequeue.get()
    try:
        links = extractlinks.parseForUrlsInHtml(page.getData(), page.url)
    except RuntimeError, msg:
        print "***", msg
        return None

    log.debug('%d links extracted form %r' % (len(links), page.url))
    for link in links:
        if link not in dupelist:
            dummmy, ext = os.path.splitext(link)
            ext = ext.lower()
            if ext in config.documentsuffixes:
                    documentfetchqueue.add(link)
            else:
                if ext not in config.nonpagesuffixes:
                    pagefetchqueue.add(link)

    
def main():
    while len(pagefetchqueue) + len(pageparsequeue) > 0:
        log.info('dupe: %d, fetchqueue: %d, parsequeue: %d, docqueue: %d, active: %d, ok: %d, ko: %d' %(len(dupelist), len(pagefetchqueue), len(pageparsequeue), len(documentfetchqueue), status.active_downloads, status.download_successes, status.download_failures))

        for i in range(config.paralell_downloads - status.active_downloads - 1):
            if documentfetchqueue:
                fetch_a_document()
            fetcher.loop()
            parse_a_page()

        if pagefetchqueue:
            fetch_a_page() 
        fetcher.loop()
        parse_a_page()
        fetcher.loop()
        parse_a_page()
        fetcher.loop()
            

main()
