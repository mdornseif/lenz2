#!/usr/bin/python

# $Id$ 

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.WARN) 

import urlnorm
import servers
from config import config
import random

from dupelist import dupelist

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
            if not dupelist.seen(item):
                log.debug('adding %r' % item)
                self.append(item.strip())
            else:
                log.debug('dupe %r is not added' % item)
        else:
            log.info('unsupported scheme %r in  %r' % (scheme, item))
                                

    def get(self):
        if len(self) == 0:
            return None
        item = self.pop(0)
        tries = 1
        while not servers.mayAccess(item):
            log.debug('postproning %r' % item)
            self.append(item)
            tries += 1
            if tries > len(self):
                return None
            item = self.pop(0)
        return item

pageparsequeue = ProcessQueue()
documentfetchqueue = FetchQueue()

pagefetchqueue = FetchQueue()
random.shuffle(config.starturls)
pagefetchqueue.extend(config.starturls)
#for x in open('starturls.txt'):
#    pagefetchqueue.add(x.strip())

searchengines = ['http://www.google.com/search?as_q=%s&num=100&hl=en&ie=UTF-8&btnG=Google+Search&as_epq=&as_oq=&as_eq=&lr=&as_ft=i&as_filetype=doc&as_qdr=all&as_nlo=&as_nhi=&as_occt=any&as_dt=i&as_sitesearch=&safe=off',
                 'http://www.google.com/search?as_q=%s&num=100&hl=en&ie=UTF-8&btnG=Google+Search&as_epq=&as_oq=&as_eq=&lr=&as_ft=i&as_filetype=doc&as_qdr=all&as_nlo=&as_nhi=&as_occt=any&as_dt=i&as_sitesearch=&safe=off&start=100',
                 'http://www.google.com/search?as_q=%s&num=100&hl=en&ie=UTF-8&btnG=Google+Search&as_epq=&as_oq=&as_eq=&lr=&as_ft=i&as_filetype=ppt&as_qdr=all&as_nlo=&as_nhi=&as_occt=any&as_dt=i&as_sitesearch=&safe=off&start=200',
                 'http://www.google.com/search?as_q=%s&num=100&hl=en&ie=UTF-8&btnG=Google+Search&as_epq=&as_oq=&as_eq=&lr=&as_ft=i&as_filetype=doc&as_qdr=all&as_nlo=&as_nhi=&as_occt=any&as_dt=i&as_sitesearch=&safe=off&start=100',
                 'http://www.google.com/search?as_q=%s&num=100&hl=en&ie=UTF-8&btnG=Google+Search&as_epq=&as_oq=&as_eq=&lr=&as_ft=i&as_filetype=ppt&as_qdr=all&as_nlo=&as_nhi=&as_occt=any&as_dt=i&as_sitesearch=&safe=off&start=200',
                 'http://www.google.com/search?as_q=%s&num=100&hl=en&ie=UTF-8&btnG=Google+Search&as_epq=&as_oq=&as_eq=&lr=&as_ft=i&as_filetype=doc&as_qdr=all&as_nlo=&as_nhi=&as_occt=any&as_dt=i&as_sitesearch=&safe=off&start=300',
                 'http://www.google.com/search?as_q=%s&num=100&hl=en&ie=UTF-8&btnG=Google+Search&as_epq=&as_oq=&as_eq=&lr=&as_ft=i&as_filetype=ppt&as_qdr=all&as_nlo=&as_nhi=&as_occt=any&as_dt=i&as_sitesearch=&safe=off&start=400',
                 'http://www.google.com/search?as_q=%s&num=100&hl=en&ie=UTF-8&btnG=Google+Search&as_epq=&as_oq=&as_eq=&lr=&as_ft=i&as_filetype=doc&as_qdr=all&as_nlo=&as_nhi=&as_occt=any&as_dt=i&as_sitesearch=&safe=off&start=500',
                 'http://www.google.com/search?as_q=%s&num=100&hl=en&ie=UTF-8&btnG=Google+Search&as_epq=&as_oq=&as_eq=&lr=&as_ft=i&as_filetype=ppt&as_qdr=all&as_nlo=&as_nhi=&as_occt=any&as_dt=i&as_sitesearch=&safe=off&start=600',
                 'http://www.google.com/search?as_q=%s&num=100&hl=en&ie=UTF-8&btnG=Google+Search&as_epq=&as_oq=&as_eq=&lr=&as_ft=i&as_filetype=xls&as_qdr=all&as_nlo=&as_nhi=&as_occt=any&as_dt=i&as_sitesearch=&safe=off',
                 'http://www.altavista.com/web/results?pg=aq&aqmode=s&aqa=%s&aqp=&aqo=&aqn=&aqb=&kgs=0&kls=0&dt=tmperiod&d2=0&dfr%%5Bd%%5D=1&dfr%%5Bm%%5D=1&dfr%%5By%%5D=1980&dto%%5Bd%%5D=13&dto%%5Bm%%5D=7&dto%%5By%%5D=2004&filetype=msword&rc=dmn&swd=&lh=&nbq=150',
                 'http://www.altavista.com/web/results?pg=aq&aqmode=s&aqa=%s&aqp=&aqo=&aqn=&aqb=&kgs=0&kls=0&dt=tmperiod&d2=0&dfr%%5Bd%%5D=1&dfr%%5Bm%%5D=1&dfr%%5By%%5D=1980&dto%%5Bd%%5D=13&dto%%5Bm%%5D=7&dto%%5By%%5D=2004&filetype=ppt&rc=dmn&swd=&lh=&sc=on&nbq=150',
                 'http://www.altavista.com/web/results?pg=aq&aqmode=s&aqa=%s&aqp=&aqo=&aqn=&aqb=&kgs=0&kls=0&dt=tmperiod&d2=0&dfr%%5Bd%%5D=1&dfr%%5Bm%%5D=1&dfr%%5By%%5D=1980&dto%%5Bd%%5D=13&dto%%5Bm%%5D=7&dto%%5By%%5D=2004&filetype=xl&rc=dmn&swd=&lh=&sc=on&nbq=150',
                 'http://search.yahoo.com/search?_adv_prop=web&x=op&ei=UTF-8&prev_vm=p&va=%s&va_vt=any&vp=&vp_vt=any&vo=&vo_vt=any&ve=&ve_vt=any&vd=all&vst=0&vs=&vf=msword&vm=p&vc=&fl=0&n=100',
                 'http://search.yahoo.com/search?_adv_prop=web&x=op&ei=UTF-8&prev_vm=p&va=%s&va_vt=any&vp=&vp_vt=any&vo=&vo_vt=any&ve=&ve_vt=any&vd=all&vst=0&vs=&vf=ppt&vm=p&vc=&fl=0&n=100',
                 'http://search.yahoo.com/search?_adv_prop=web&x=op&ei=UTF-8&prev_vm=p&va=%s&va_vt=any&vp=&vp_vt=any&vo=&vo_vt=any&ve=&ve_vt=any&vd=all&vst=0&vs=&vf=xl&vm=p&vc=&fl=0&n=100'
                 ]

searchterms = ['institut', 'vorlesung', 'universitaet', 'universit&auml;t', 'diplom', 'thesis',
               'ausarbeitung', 'CfP', 'Conference', 'Paper', 'Award', 'Jounal', 'Proceedings',
               'hacker', 'XXX', 'bund',' bundes', 'minister', 'amt', 'dienst', 'dienstgebrauch',
               'geheim', 'vertraulich', 'land', 'landes', 'intern', 'memo', 'verschlussache',
               'pressefrei', 'transrapid', 'gazweiler', 'bilanz', 'abbau', 'presentation',
               'minutes', 'vorlesung', 'seminar', 'uebung', 'praktikum', 'referat', 'class',
               'hausaufgabe', 'homework', 'praktikum', 'dokument', 'dokumentation',
               'ausarbeitung', 'kosten', 'referate', 'download', 'folien', 'dias',
               'entwicklung', 'class', 'course', 'reference', 'abstract', 'need', 'bier',
               'lehrer', 'professor', 'assistent', 'brathering', 'daten', 'selten',
               'unbekannt', 'mahnung', 'filled', 'form', 'files', 'formular',
               'base', 'zins', 'land', 'zusammnefassung', 'conclusion', 'semester', 'term',
               'dezernat', 'amt', 'stelle', 'case', 'court', 'proof', 'word']
random.shuffle(searchengines)
random.shuffle(searchterms)
for engine in searchengines[:len(searchengines)/2]:
    for term in searchterms[:len(searchterms)/2]:
        pagefetchqueue.add(engine % term)
    
pagefetchqueue.extend(pagefetchqueue)
