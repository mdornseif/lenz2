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
from queues import dupelist, pagefetchqueue, pageparsequeue, documentfetchqueue

from output.larbin import LarbinOutputSystem, LarbinLowMemOutputSystem

documentoutput = LarbinLowMemOutputSystem(config.documentdir)
pageoutput = LarbinOutputSystem(config.pagedir)



class Page:
    def __init__(self):
        self.urls = []
        self.data = ''

    def __repr__(self):
        return repr(vars(self))

    def getData(self):
        if not self.data:
            self.data = self.read()
        return self.data

    def body_callback(self, buf):
        self.data = self.data + buf
                            

def fetch_a_page():
    page = Page()
    page.url = pagefetchqueue.get() 

    if not fetcher.fetch(page):
        return None

    dummy, ext = os.path.splitext(page.url)
    ext = ext.lower()
    if ext not in config.nonpagesuffixes:
        if page.header.gettype() in config.pagemimetypes:
            pageoutput.save(page)
            pageparsequeue.add(page)
            return page
    elif config.documentmimetypes in config.documentmimetypes:
        handle_a_document(page)
    return None


def handle_a_document(page):
    documentoutput.save(page) 

def fetch_a_document():
    page = Page
    page.url = documentfetchqueue.get() 
    print "-->", page.url
    if not fetcher.fetch(page):
        return None

    handle_a_document(page)
    return page


def parse_a_page():
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
        log.info('dupelist: %d, pagefetchqueue: %d, pageparsequeue: %d, documentfetchqueue: %d' %(len(dupelist), len(pagefetchqueue), len(pageparsequeue), len(documentfetchqueue)))
        if documentfetchqueue:
            fetch_a_document()
            time.sleep(1)
        if pagefetchqueue:
            fetch_a_page()
            time.sleep(1)
        if pageparsequeue:
            parse_a_page()
            time.sleep(1)
    

main()
