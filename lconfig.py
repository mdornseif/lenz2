import os, os.path
import sys
import logging

log = logging.getLogger('config')
log.setLevel(20)

class Config:
    def __init__(self):
        self.starturls = ['http://deepblack.lolitacoders.org:22222/',
                          'http://lolitacoders.org/',
                          'http://md.hudora.de/analog/',
                          'http://c0re.jp/c0de/coldcut/',
                          'http://c0re.23.nu/',
                          'http://koeln.ccc.de/~drt/analog/',
                          'http://koeln.ccc.de/~drt/',
                          'http://koeln.ccc.de/~drt/wiki.cgi?action=links&url=2',
                          'http://koeln.ccc.de/~drt/wiki.cgi?action=index',
                          'http://koeln.ccc.de/~drt/wiki.cgi?action=links'
                          ]
        self.excludelist = ['.*\?.+&.+',
                            r'/\?[NMSD]=[AD]$',
                            r'.*?sort=size$',
                            r'.*\.tar(\.gz)?$',
                            r'.*\.tgz$',
                            r'.*\.zip(\.gz)?$',
                            r'.*\.jpe?g(\.gz)?$',
                            r'.*\.gif(\.gz)?$',
                            r'.*\.png(\.gz)?$',
                            r'.*\.pl(\.gz)?$',
                            r'.*\.py(\.gz)?$',
                            r'.*\.c(\.gz)?$',
                            r'.*\.h(\.gz)?$',
                            r'.*\.o(\.gz)?$',
                            r'.*\.patch(\.gz)?$',
                            r'.*\.diff(\.gz)?$',
                            r'.*.ps(\.gz)?$',
                            r'.*.pdf(\.gz)?$',
                            r'.*.dvi(\.gz)?$']
        self.includelist = ['http://md.hudora.de/.*',
                            '.*ccc.*',
                            'http://c0re.jp/.*',
                            'http://.*koeln.ccc.de.*',
                            'http://.*koeln.ccc.de/~drt/.*',
                            'http://.*bewaff.net/.*',
                            'http://.*dorsch.org/.*',
                            'http://.*.23.nu/.*',
                            'http://.*olitacoders.org/.*',
                            'http://.*nerxs.com/.*',
                            'http://.*porz.org/.*']
        self.robotparser_debug = 0
	self.server_min_pause = 30
	self.user_agent = 'lenz2'
	self.user_agent_full = 'lenz2/0.2 ([31;40;1mlenz2[0m - http://c0re.jp/c0de/lenz2/bot.html)'
        self.archivedir = 'pages'
        self.archivegeneratorip = '213.221.113.91'

config = Config()

if os.path.exists(config.archivedir):
    if not os.path.isdir(config.archivedir):
        print "archivedir %r ist kein Verzeichnis" % config.archivedir
        sys.exit(1)
else:
    log.warn('creating archivedir %r' % config.archivedir)
    os.makedirs(config.archivedir)
