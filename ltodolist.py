# --drt@un.bewaff.net - http://c0re.jp/

"""This is where newly found URLs are stored. They will be passed
after deduping to the frontier"""

import re
import ldupecheck
from lconfig import config
import logging

log = logging.getLogger('todolist')
log.setLevel(20)

db = []

_ignored = 0

def getInfo():
    return ('todolist', ["todolist: %d URLs" % len(db),
                         "ignored: %d URLs" % _ignored ])

def init():
    global exclude_re
    global include_re
    
    for x in config.starturls:
        # insert in dupedb
        ldupecheck.checkIfOkAndAdd(x)
        # insert into our own db
        db.append(x)

    config.excludelist
    i = '(?i)(%s)'%'|'.join(config.includelist)
    e = '(?i)(%s)'%'|'.join(config.excludelist)
    include_re = re.compile(i, re.DOTALL)
    exclude_re = re.compile(e, re.DOTALL)
    log.info('include regex: %r' % i)
    log.info('exclude regex: %r' % e)


def add(url):
    global _ignored
    # check for robots.txt
    if exclude_re.search(url):
        _ignored += 1 
        log.debug('excluded %r', url)
        return 0
    if include_re.search(url):
        log.debug('adding %r', url)
        db.append(url)
        return 1
    else:
        _ignored += 1 
        log.debug('not included %r', url)
        return 0


def get():
    if len(db) > 0:
        return db.pop(0)
    else:
        return None

init()
