#!/usr/bin/python

'''A very simple gopherspace spider by drt.

It writes all typte, host, port, selector information it finds to stdout.

by drt - http://koeln.ccc.de/~drt/
'''

import Queue
import gopherlib
import time
import sys
import traceback
import signal
import cPickle

stop_spider = 0
restart_spider = 0

def handler(signum, frame):
    global stop_spider
    global restart_spider
    
    print 'Signal handler called with signal', signum
    stop_spider += 1
    if signum == signal.SIGALRM:
        restart_spider += 1
       
class selector:

    def __init__(self, sel, host = None, port = 70):
        self.host = host
        self.selector = sel
        self.port = port
        self.type = None
        self.last_visited = None
        self.size = None

    def __str__(self):
        return "[selector object host=%s, port=%s, selector=%s, type=%s, last_visited=%s size=%s]" % (repr(self.host), repr(self.port), repr(self.selector), repr(self.type), self.last_visited, self.size) 

    def __repr__(self):
        return self.__str__()

    def visited_now(self):
        self.last_visited = time.time()


class server:

    def __init__(self, host, port = 70):
        self.host = host
        self.port = port
        self.selectors = []
        self.last_visited = 0

    def __str__(self):
        return "[server object host=%s port=%s last_visited=%s %s]" % (repr(self.host), repr(self.port), repr(self.last_visited), self.selectors)
        
    def __repr__(self):
        return self.__str__()

    def add_selector(self, s, end = 0):
        assert isinstance(s, selector)
        if s.host == None:
            s.host = self.host
        if s.host != self.host:
            if s.host == None:
                s.host = self.host
                s.port = self.port
            else:
                raise AssertionError, 'selector host (%s) and server host (%s) differ' % (s.host, self.host)

        if end != 0:
            self.selectors.append(s)
        else:
            self.selectors.insert(0, s)

    def get_next_selector(self):
        if len(self.selectors) == 0:
            return None
        return self.selectors.pop(0)

    def get_selector(self, sel):
        for x in self.selectors:
            if x.selector == sel:
                self.selectors.remove(x)
                return x
        return None

    def visited_now(self):
        self.last_visited = time.time()

    def ensure_selector(self, sel):
        x = self.get_selector(sel)
        if x == None:
            x = selector(sel)
        self.add_selector(x)
        return x


class todo:

    def __init__(self):
        self.server_pause = 10
        self.servers = []

    def __str__(self):
        return repr(self.servers)

    def __repr__(self):
        self.__str__()
                                  
    def add_server(self, s, end = 0):
        assert isinstance(s, server)
        if end != 0:
            self.servers.append(s)
        else:
            self.servers.insert(0, s)

    def get_next_server(self):
        if len(self.servers) == 0:
            return None
        s = self.servers.pop(0)
        while s.last_visited + self.server_pause > time.time():
            time.sleep(1)
            print "sleeping ..."
            self.servers.append(s)
            s = self.servers.pop(0)
        return s

    def get_server(self, host, port = 70):
        for x in self.servers:
            if x.host == host and x.port == port:
                self.servers.remove(x)
                return x
        return None

    def ensure_server(self, host, port = 70):
        x = self.get_server(host, port)
        if x == None:
            x = server(host, port)
        self.add_server(x)
        return x


def spiderit(queue, blacklist):

    h = queue.get_next_server()
    while h and stop_spider == 0:
        s = h.get_next_selector()        
        if s:
            print >>sys.stderr, "-> %s:%s %s ... " % (s.host, s.port, s.selector),
            sys.stderr.flush()

            filelist = None
            try:
                filelist = gopherlib.get_directory(gopherlib.send_selector(s.selector, s.host, s.port))
            except:
                print >>sys.stderr, "failed"
                blacklist[host + ":" + port] = h

            if filelist == None:
                continue
            
            print >>sys.stderr, len(filelist)
            sys.stderr.flush()
                
            h.visited_now()
            s.visited_now()
            h.add_selector(s, -1)
            queue.add_server(h, -1)

            for x in filelist:
                (type, name, sel, host, port, foo) = x
                if type != 'i' and type != '3' and host != 'error.host':
                    print 'gopher://%s:%s/%s (%s)' % (host, port, sel, type)
                if type == '1':
                    if not blacklist.has_key(host + ':' + port): 
                        h = queue.ensure_server(host, port)
                        s = h.ensure_selector(sel)
                        s.type = type
                    
               
        h = queue.get_next_server()
        

def main():
    global stop_spider
    global restart_spider

    sl = ['gopher.butler.edu', "aau.dk", "acad.udallas.edu",
    "acc.msmc.edu", "acs2.byu.edu", "admin.humberc.on.ca",
    "aida.heso.state.mn.us", "aix1.uottawa.ca", "alpha1.csd.uwm.edu",
    "apsu01.apsu.edu", "archive.msstate.edu", "athene.owl.de",
    "atlantic.evsc.virginia.edu", "aubranch.egwestate.andrews.edu",
    "ayllu.rcp.net.pe", "babel.its.utas.edu.au", "biosci.cbs.umn.edu",
    "bluefin.utmb.edu", "ccins.camosun.bc.ca", "cdp.igc.apc.org",
    "chiron.latrobe.edu.au", "chrome.vortex.com",
    "cismserveur.univ-lyon1.fr", "cit1.citadel.edu", "cix.org",
    "cloud.ccsf.cc.ca.us", "conch-1.msen.com", "conch.msen.com",
    "cruise.comms.unsw.edu.au", "cunyvm.cuny.edu",
    "curry.edschool.virginia.edu", "cx376187-c.crans1.ri.home.com",
    "cyberwerks.com", "darwin.bu.edu", "dept.english.upenn.edu",
    "dosfan.lib.uic.edu", "e-math.ams.org", "eco.utexas.edu",
    "edcen.ehhs.cmich.edu", "eole.ere.umontreal.ca",
    "erato.acnatsci.org", "ero.ent.iastate.edu", "eye.hooked.net",
    "feenix.metronet.com", "fohnix.metronet.com",
    "folwer.acnatsci.org", "ftp.cc.duq.edu", "ftp.cnd.org",
    "ftp.std.com", "gamma.sil.org", "garcon.unicom.com",
    "gaserver.ga.unc.edu", "gate.sinica.edu.tw", "gbc.gbrownc.on.ca",
    "gds2.tc.umn.edu", "gnd0.rmc.edu", "gopher.adp.wisc.edu",
    "gopher.anc.org.za", "gopher.chem.uic.edu", "gopher.firdi.org.tw",
    "gopher.nctr.fda.gov", "gopher.nd.edu", "gopher1.un.org",
    "gothic.lib.calpoly.edu", "gpu.utcc.utoronto.ca",
    "greengenes.cit.cornell.edu", "gutentag.cc.columbia.edu",
    "hawaii.uni-trier.de", "hawk.undp.org", "hermes.ecn.purdue.edu",
    "hoshi.cic.sfu.ca", "hubcap.clemson.edu", "icineca.cineca.it",
    "inca.gate.net", "info.ripn.net", "infoserver.bgsu.edu",
    "inspire.ospi.wednet.edu", "iota.qmw.ac.uk", "israel-info.gov.il",
    "itsa.ucsf.edu", "jaguar.dacc.cc.il.us",
    "kimberly.807-city.on.ca", "knot.queensu.ca", "leipzig.nct.de",
    "lenti.med.umn.edu", "library.ucsc.edu", "mach.vub.ac.be",
    "magpie.bio.indiana.edu", "mailer.fsu.edu", "maine.maine.edu",
    "mariposa.cc.uh.edu", "mde.merit.edu", "merlin.rh.edu",
    "miamilink.lib.muohio.edu", "minerva.acc.virginia.edu",
    "natasha.oswego.edu", "nemesis.cs.berkeley.edu",
    "netlib2.cs.utk.edu", "newalbion.com", "news.std.com",
    "nic.merit.edu", "nickel.mv.net", "nova.umuc.edu",
    "olymp.wu-wien.ac.at", "omega.hanover.edu", "origin.lib.lsu.edu",
    "panam3.panam.edu", "pcinfo.pc.maricopa.edu",
    "pi.glockenspiel.complete.org", "picard.3k.com",
    "picard.evms.edu", "power-house.ties.k12.mn.us",
    "procrustes.biology.yale.edu", "proteon.inet-serv.com",
    "purple.tmn.com", "rail.bio.indiana.edu", "rf1.cuis.edu",
    "rs7.loc.gov", "rsl-01.rsl.ox.ac.uk", "rudi.ifs.hr",
    "rzubiz.unizh.ch", "sanaga.itu.ch", "sdsumus.sdstate.edu",
    "seds.lpl.arizona.edu", "semovm.semo.edu", "server.uwindsor.ca",
    "server.vhdl.org", "soochak.ncst.ernet.in", "sophia.smith.edu",
    "spartan.ac.brocku.ca", "ssugopher.sonoma.edu",
    "stockholm.ptloma.edu", "tang.qut.edu.au", "taurus.cc.umb.edu",
    "text-fax.slu.edu", "thunder.thunderstone.com",
    "tremaine.cc.uec.ac.jp", "twsuvm.uc.twsu.edu", "ukcc.uky.edu",
    "uniwa.uwa.edu.au", "uor.edu", "utl1.library.utoronto.ca",
    "vaxd.sxu.edu", "vetserv2.vetmed.vt.edu", "vm.biu.ac.il",
    "vm.cc.latech.edu", "vortex.com", "world.std.com",
    "wvnvm.wvnet.edu", "www.circleintl.com", "www.shore.net",
    "www.udel.edu", "www.utoledo.edu", "www.well.com",
    "www1.williams.edu", "www3.nsysu.edu.tw", "xavier.xu.edu",
    "zenith.ngdc.noaa.gov" ]


    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGQUIT, handler)
    signal.signal(signal.SIGALRM, handler)

    try:
        f = open("queue.pickle")
        queue = cPickle.load(f)
        f.close()
    except:
        print >>sys.stderr, "unpickling failed, using default queue"
        queue = todo()
        for x in sl:
            s = server(x)
            s.add_selector(selector(''))
            queue.add_server(s)

    try:
        f = open("blacklist.pickle")
        blacklist = cPickle.load(f)
        f.close()
    except:
        print >>sys.stderr, "unpickling failed, using empty blacklist"
        blacklist = {}



    while 1:
        spiderit(queue, blacklist)

        f = open('queue.pickle', 'w') 
        cPickle.dump(queue, f, 1)
        f.close()
        f = open('blacklist.pickle', 'w') 
        cPickle.dump(blacklist, f, 1)
        f.close()

        if restart_spider != 0:
            restart_spider = 0
            stop_spider = 0
        else:
            break
    
#    todo.put(('1/', 'w8n.koeln.ccc.de', 70))
#    todo.put(('1/', 'gopher.floodgap.com', 70))
#    todo.put(('1/', 'gopher.nct.de', 70))
#    spider(todo)

main()
