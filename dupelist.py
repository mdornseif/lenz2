
import md5, struct, time
from bsddb3.db import *


class DupeList:

    def __init__(self, name="dupelist"):
        # this should be a singelton, should it?
        self.db = DB()
        self.db.set_cachesize(0, 10000000)   # 10 MB
        self.db.open('%s.db' % name, dbtype=DB_BTREE, flags=DB_CREATE)

    def seen(self, item):
        key = md5.new(item).digest()
        ret = self.db.get(key)
        if ret:
            return True
        else:
            self.db[key] = struct.pack('f', time.time())
            return False            

    def __len__(self):
        return self.db.stat()['ndata']

dupelist = DupeList()
