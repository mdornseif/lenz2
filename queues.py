#!/usr/bin/python

# $Id$ 

import urlnorm
import servers
from config import config


class DupeList(dict):
    def add(self, item):
        self[item] = True

dupelist = DupeList()


class ProcessQueue(list):
    def add(self, item):
        self.append(item)

    def get(self):
        return self.pop(0)

         
class FetchQueue(ProcessQueue):
    def normalize(self, item):
        normal = urlnorm.norms(item)
        # remove anchor-references
        normal = normal.split('#', 1)[0]
        # remove apache directory extravaganza [?[NDMS]=[AD]
        parm = normal.split('?', 1)[-1]
        if parm and len(parm) == 3 and parm[1] == '=' and parm[2] in 'AD' and parm[0] in 'NDMS':
            normal = normal[-4]
        return normal
    

    def add(self, item):
        global dupelist
        scheme = item.split(':')[0]
        if scheme in config.supportedprotocols:
            item = self.normalize(item)
            if item not in dupelist:
                self.append(item)
                dupelist.add(item)
            

    def get(self):
        item = self.pop(0)
        while not servers.mayAccess(item):
            self.append(item)
            item = self.pop(0)
        return item

pagefetchqueue = FetchQueue()
pagefetchqueue.extend(config.starturls)
pageparsequeue = ProcessQueue()
documentfetchqueue = FetchQueue()
