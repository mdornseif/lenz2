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

from output.larbin import LarbinOutputSystem

documentoutput = LarbinOutputSystem(config.documentdir)
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
                print "*** docsave", len(self.body)
                documentoutput.save(self)
                pagefetchqueue.add(parenturl(self.url))
                
        elif self.status == 204:        # No Content
            return None
        elif self.status in [300,       # Multiple Choices
                             301,
                             302,       # Found - not really sure how to handle this
                             ]:        
            # XXX this could be handled much smarter
            return None
        elif self.status in [400,
                             401,       # unauthorized
                             403,       # access denied
                             404,       # not fond
                             405,       # method no supported
                             406,
                             408,
                             410,       # Gone
                             412,
                             414,       # Request URI Too Large
                             423,       # Locked
                             ]:
            return None
        elif self.status in [500,              # internal error
                             501,
                             502,              # Bad Gateway
                             503,
                             504,              # Origin Server Timeout
                             505,
                             506,
                             510,
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
    url = pagefetchqueue.get()
    if url:
        page = Page()
        page.url = url
        fetcher.fetch(page)
    return None


def fetch_a_document():
    url = documentfetchqueue.get()
    if url:
        page = Page()
        page.url = url
        fetcher.fetch(page)
    return None


def parse_a_page():
    if not pageparsequeue:
        return

    t = time.time()

    page = pageparsequeue.get()
    try:
        links = extractlinks.parseForUrlsInHtml(page.body, page.url)
    except Exception, msg:
        log.exception(msg)
        return None

    added = 0
    for link in links:
        if link not in dupelist and 'osdn.safaribooksonline.com' not in link:
            dummmy, ext = os.path.splitext(link)
            ext = ext.lower()
            if ext in config.documentsuffixes:
                    documentfetchqueue.add(link)
                    added += 1
            else:
                if ext not in config.nonpagesuffixes:
                    pagefetchqueue.add(link)
                    added += 1

    #log.debug('%d links (%d suitable for queue) in %.3fs extracted form %r' % (len(links), added, (time.time() - t), page.url))


    
def main():
    while len(pagefetchqueue) + len(pageparsequeue) + len(documentfetchqueue) > 0:

        if documentfetchqueue:
            print range(config.paralell_downloads - status.active_downloads - 2)
            for i in range(config.paralell_downloads - status.active_downloads - 2):
                fetch_a_document()
        
        log.info('dupe: %d, fetchqueue: %d, parsequeue: %d, docqueue: %d, active: %d, ok: %d, ko: %d' %(len(dupelist), len(pagefetchqueue), len(pageparsequeue), len(documentfetchqueue), status.active_downloads, status.download_successes, status.download_failures))
        t = time.time()
        fetcher.loop()
        print 'fetcher.loop(): %.3f' % (time.time() - t)

        print range(config.paralell_downloads - status.active_downloads)
        for i in range(config.paralell_downloads - status.active_downloads):
            fetch_a_page()
            parse_a_page()
                            
        log.info('dupe: %d, fetchqueue: %d, parsequeue: %d, docqueue: %d, active: %d, ok: %d, ko: %d' %(len(dupelist), len(pagefetchqueue), len(pageparsequeue), len(documentfetchqueue), status.active_downloads, status.download_successes, status.download_failures))
        t = time.time()
        fetcher.loop()
        print 'fetcher.loop(): %.3f' % (time.time() - t)
        log.info('dupe: %d, fetchqueue: %d, parsequeue: %d, docqueue: %d, active: %d, ok: %d, ko: %d' %(len(dupelist), len(pagefetchqueue), len(pageparsequeue), len(documentfetchqueue), status.active_downloads, status.download_successes, status.download_failures))
        t = time.time()
        parse_a_page()
        print 'parse_a_page(): %.3f' % (time.time() - t)
        log.info('dupe: %d, fetchqueue: %d, parsequeue: %d, docqueue: %d, active: %d, ok: %d, ko: %d' %(len(dupelist), len(pagefetchqueue), len(pageparsequeue), len(documentfetchqueue), status.active_downloads, status.download_successes, status.download_failures))
        t = time.time()
        fetcher.loop()
        print 'fetcher.loop(): %.3f' % (time.time() - t)
        log.info('dupe: %d, fetchqueue: %d, parsequeue: %d, docqueue: %d, active: %d, ok: %d, ko: %d' %(len(dupelist), len(pagefetchqueue), len(pageparsequeue), len(documentfetchqueue), status.active_downloads, status.download_successes, status.download_failures))
            

main()
