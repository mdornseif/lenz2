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
                    'http://news.google.de/',
                    'http://news.google.com/',
                    'http://www.bund.de/Service-Center/Veraeusserungen-.5651.htm',
                    'http://idw-online.de/public/',
                    'http://www.google.com/search?num=100&hl=en&lr=&ie=UTF-8&safe=off&as_qdr=all&q=+filetype%3Adoc+dienst&btnG=Search'
                    'http://www.altavista.com/web/results?dt=tmperiod&d2=0&filetype=msword&rc=dmn&swd=&nbq=50&pg=aq&aqmode=s&aqa=geheim&aqp=&aqo=&aqn=&kgs=0&kls=0',
                    'http://www.altavista.com/web/results?dt=tmperiod&d2=0&filetype=msword&rc=dmn&swd=&nbq=50&pg=aq&aqmode=s&aqa=vertraulich&aqp=&aqo=&aqn=&kgs=0&kls=0',
                    'http://www.altavista.com/web/results?dt=tmperiod&d2=0&filetype=msword&rc=dmn&swd=&nbq=50&pg=aq&aqmode=s&aqa=intern&aqp=&aqo=&aqn=&kgs=0&kls=0',
                    'http://www.altavista.com/web/results?dt=tmperiod&d2=0&filetype=xls&rc=dmn&swd=&nbq=50&pg=aq&aqmode=s&aqa=geheim&aqp=&aqo=&aqn=&kgs=0&kls=0',
                    'http://www.altavista.com/web/results?dt=tmperiod&d2=0&filetype=xls&rc=dmn&swd=&nbq=50&pg=aq&aqmode=s&aqa=vertraulich&aqp=&aqo=&aqn=&kgs=0&kls=0',
                    'http://www.altavista.com/web/results?dt=tmperiod&d2=0&filetype=xls&rc=dmn&swd=&nbq=50&pg=aq&aqmode=s&aqa=intern&aqp=&aqo=&aqn=&kgs=0&kls=0',
                    'http://www.alltheweb.com/search?advanced=1&cat=web&jsact=&_stype=norm&type=all&q=geheim&_b_query=&l=any&ics=utf-8&cs=utf-8&wf%5Bn%5D=3&wf%5B0%5D%5Br%5D=%2B&wf%5B0%5D%5Bq%5D=&wf%5B0%5D%5Bw%5D=&wf%5B1%5D%5Br%5D=%2B&wf%5B1%5D%5Bq%5D=&wf%5B1%5D%5Bw%5D=&wf%5B2%5D%5Br%5D=-&wf%5B2%5D%5Bq%5D=&wf%5B2%5D%5Bw%5D=&dincl=&dexcl=&geo=&doctype=msword&dfr%5Bd%5D=1&dfr%5Bm%5D=1&dfr%5By%5D=1980&dto%5Bd%5D=10&dto%5Bm%5D=7&dto%5By%5D=2004&hits=100&nooc=off',
                    'http://www.alltheweb.com/search?advanced=1&cat=web&jsact=&_stype=norm&type=all&q=vertrulich&_b_query=&l=any&ics=utf-8&cs=utf-8&wf%5Bn%5D=3&wf%5B0%5D%5Br%5D=%2B&wf%5B0%5D%5Bq%5D=&wf%5B0%5D%5Bw%5D=&wf%5B1%5D%5Br%5D=%2B&wf%5B1%5D%5Bq%5D=&wf%5B1%5D%5Bw%5D=&wf%5B2%5D%5Br%5D=-&wf%5B2%5D%5Bq%5D=&wf%5B2%5D%5Bw%5D=&dincl=&dexcl=&geo=&doctype=msword&dfr%5Bd%5D=1&dfr%5Bm%5D=1&dfr%5By%5D=1980&dto%5Bd%5D=10&dto%5Bm%5D=7&dto%5By%5D=2004&hits=100&nooc=off',
                    'http://www.diplomarbeit.de/website/kostenlos/uebersicht.php',
                    'http://www.diplom.de/welcome.html',
                    'http://www.diplomarbeiten24.de/',
                    'http://www.studeo.de/diplomarbeit/',
                    'http://www.referate.net/',
                    'http://www.fundus.org/',
                    'http://www.referate.heim.at/search.php',
                    'http://www.referate.de/p/startseite.htm',
                    'http://www.hausarbeiten.de/',
                    'http://de.dir.yahoo.com/Ausbildung_und_Beruf/Hochschulen/Hausarbeiten__Skripte_und_Klausuren/',
                    'http://www.unicum.de/grin/',
                    'http://www.uni-koeln.de/~ame45/hdbframe.htm',
                    'http://www.jurawelt.com/studenten/seminararbeiten/',
                    ]
for x in open('starturls.txt'):
    config.starturls.append(x.strip())
random.shuffle(config.starturls)

# where to save documents
config.documentdir = 'documents'

# where to save pages
config.pagedir = 'pages'

# the minimal amount of time between requests to the same server
config.minservergraceperiod = 20
config.averageservergraceperiod = 60

#
config.http_useragent = 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/125.2 (KHTML, like Gecko) Safari/125.8'
config.http_accept = '*/*'
config.http_debug = 2
config.http_timeout = 120

#
config.supportedprotocols = ['http', 'https']
