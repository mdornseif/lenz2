from ARCive import ARCive
import os.path
import time
from lconfig import config

import logging

log = logging.getLogger('archivemanager')
log.setLevel(20)
arcname = os.path.join(config.archivedir, "%d.arc" % int(time.time()))
actarc = ARCive(arcname , 'w', "lenz2", config.archivegeneratorip)
log.info('creating new archive %r', arcname)
# actarc.close()

def store(resource):
    data = '\n'.join(map(lambda x: "%s: %s" % (x[0], x[1]),
                         resource.headers.items())) + '\n\n' + resource.body
    ct = resource.headers['Content-Type']
    # content-type can hace additional information like charset.
    x = ct.find(';')
    if x != -1:
        ct = ct[:x]
    actarc.writerawdoc(data, resource.url, ct)
