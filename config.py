#!/usr/bin/python

# $Id$ 

import random

class Config:
    pass

config = Config()

# file extensions which we will try to handle as documents
config.documentsuffixes = ['.doc', '.xls', '.ppt']
# mimetypes we will definitively handle as documents
config.documentmimetypes = ['application/msword', 'application/vnd.ms-excel',
                            'application/vnd.ms-powerpoint']

# file extensions we will never consider to be pages
config.nonpagesuffixes = ['.exe',
                          '.sit', '.rar', '.gz', '.tar', '.zip', 'dmg',
                          '.ico', '.gif', '.jpg', '.jpeg',
                          '.avi', '.mov', '.pdf', '.eps', '.ps',
                          '.c', '.h', '.txt', '.diff'
                          '.doc', '.xls', '.ppt',
                          '.torrent'
                          ]

# mime types which we will handle as pages
config.pagemimetypes = ['text/html',
                        'text/xml',
                        'application/xhtml+xml',
                        'application/xml',
                        ]

# urls where we start crawling
config.starturls = ['http://md.hudora.de/',
                    'http://blogs.23.nu/',
                    'http://www.bund.de/',
                    'http://www.bsi.de/',
                    'http://www.nrw.de/00_home/index.shtml',
                    'http://news.google.de/',
                    'http://news.google.com/',
                    'http://www.technorati.com/cosmos/breakingnews.html',
                    'http://blo.gs/',
                    ]

# where to save documents
config.documentdir = 'documents'

# where to save pages
config.pagedir = 'pages'

# the minimal amount of time between requests to the same server
config.minservergraceperiod = 20
config.averageservergraceperiod = 60

config.paralell_downloads = 30

#
config.http_useragent = 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/125.2 (KHTML, like Gecko) Safari/125.8'
config.http_accept = '*/*'
config.http_debug = 0
config.http_timeout = 60
#
config.supportedprotocols = ['http', 'https']
