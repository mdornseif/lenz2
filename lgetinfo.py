# --drt@un.bewaff.net - http://c0re.jp/

import sys
import logging
from pprint import pprint

log = logging.getLogger('info')
log.setLevel(20)

info_modules = ['lserverbase', 'ltodolist', 'ldupecheck', 'lhttpclient', 'lfrontier']
#lgetinfo.py    lresource.py  
#    lserver.py    

for x in info_modules:
    __import__(x)

def collectInfo():
    ret = []
    for x in info_modules:
        log.debug('getting %r' % x)
        ret.append(sys.modules[x].getInfo())
    return ret

def dumpInfo():
    log.debug('dumping statistics')
    pprint(collectInfo())
    log.debug('dumping done')
