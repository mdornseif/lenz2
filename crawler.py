import time
import select
import crawlgopher
import asyncore
import frontier
import urlparse
import sys

concurrency = 2


def loop ():

    monitor()

    while asyncore.socket_map:
        asyncore.poll(20.0, asyncore.socket_map)
        monitor()


def monitor():
    '''open new connenctions until we reach concurrency'''

    while len(asyncore.socket_map) < concurrency:
        url = frontier.getURL()
        if url == None:
            break
            
        (protocol, host, path, parameters, query, fragment) = urlparse.urlparse(url, 'gopher', 0)
        s = host.find(':')
        if s == -1:
            port = socket.getservbyname(protocol, 'tcp')
            phost = host + ':' + str(port)
        else:
            port = int(host[s+1:])
            phost = host
            host = host[:s]

        if len(path) < 2:
            path = "/"
        else:
            path = path[2:] # Cuts initial slash and data type identifier

        print "adding", url, host, port, path
        s = crawlgopher.crawl(host, port, path)
        
    # work_in_progress/reaper.py
    # 'bring out your dead, <CLANG!>... bring out your dead!'
    now = int(time.time())
    for x in asyncore.socket_map.keys():
        s =  asyncore.socket_map[x]
        if hasattr(s, 'deadline'):
            if now  > s.deadline:
                print >>sys.stderr, 'reaping connection to', s.host
                s.close()
        


sl = ['gopher://w8n.koeln.ccc.de/', 'gopher://gopher.butler.edu',
"gopher://archive.msstate.edu", "gopher://athene.owl.de",
"gopher://bluefin.utmb.edu", "gopher://chrome.vortex.com",
"gopher://cyberwerks.com", "gopher://e-math.ams.org",
"gopher://eye.hooked.net", "gopher://ftp.std.com",
"gopher://gamma.sil.org", "gopher://gopher.nctr.fda.gov",
"gopher://gopher.nd.edu", "gopher://gopher1.un.org",
"gopher://leipzig.nct.de", "gopher://stockholm.ptloma.edu",
"gopher://vortex.com", "gopher://world.std.com",
'gopher://w8n.koeln.ccc.de/1/uniprog', 'gopher://gopher.butler.edu',
"gopher://aau.dk", "gopher://acad.udallas.edu",
"gopher://acc.msmc.edu", "gopher://acs2.byu.edu",
"gopher://admin.humberc.on.ca", "gopher://aida.heso.state.mn.us",
"gopher://aix1.uottawa.ca", "gopher://alpha1.csd.uwm.edu",
"gopher://apsu01.apsu.edu", "gopher://archive.msstate.edu",
"gopher://athene.owl.de", "gopher://atlantic.evsc.virginia.edu",
"gopher://aubranch.egwestate.andrews.edu",
"gopher://ayllu.rcp.net.pe", "gopher://babel.its.utas.edu.au",
"gopher://biosci.cbs.umn.edu", "gopher://bluefin.utmb.edu",
"gopher://ccins.camosun.bc.ca", "gopher://cdp.igc.apc.org",
"gopher://chiron.latrobe.edu.au", "gopher://chrome.vortex.com",
"gopher://cismserveur.univ-lyon1.fr", "gopher://cit1.citadel.edu",
"gopher://cix.org", "gopher://cloud.ccsf.cc.ca.us",
"gopher://conch-1.msen.com", "gopher://conch.msen.com",
"gopher://cruise.comms.unsw.edu.au", "gopher://cunyvm.cuny.edu",
"gopher://curry.edschool.virginia.edu",
"gopher://cx376187-c.crans1.ri.home.com", "gopher://cyberwerks.com",
"gopher://darwin.bu.edu", "gopher://dept.english.upenn.edu",
"gopher://dosfan.lib.uic.edu", "gopher://e-math.ams.org",
"gopher://eco.utexas.edu", "gopher://edcen.ehhs.cmich.edu",
"gopher://eole.ere.umontreal.ca", "gopher://erato.acnatsci.org",
"gopher://ero.ent.iastate.edu", "gopher://eye.hooked.net",
"gopher://feenix.metronet.com", "gopher://fohnix.metronet.com",
"gopher://folwer.acnatsci.org", "gopher://ftp.cc.duq.edu",
"gopher://ftp.cnd.org", "gopher://ftp.std.com",
"gopher://gamma.sil.org", "gopher://garcon.unicom.com",
"gopher://gaserver.ga.unc.edu", "gopher://gate.sinica.edu.tw",
"gopher://gbc.gbrownc.on.ca", "gopher://gds2.tc.umn.edu",
"gopher://gnd0.rmc.edu", "gopher://gopher.adp.wisc.edu",
"gopher://gopher.anc.org.za", "gopher://gopher.chem.uic.edu",
"gopher://gopher.firdi.org.tw", "gopher://gopher.nctr.fda.gov",
"gopher://gopher.nd.edu", "gopher://gopher1.un.org",
"gopher://gothic.lib.calpoly.edu", "gopher://gpu.utcc.utoronto.ca",
"gopher://greengenes.cit.cornell.edu",
"gopher://gutentag.cc.columbia.edu", "gopher://hawaii.uni-trier.de",
"gopher://hawk.undp.org", "gopher://hermes.ecn.purdue.edu",
"gopher://hoshi.cic.sfu.ca", "gopher://hubcap.clemson.edu",
"gopher://icineca.cineca.it", "gopher://inca.gate.net",
"gopher://info.ripn.net", "gopher://infoserver.bgsu.edu",
"gopher://inspire.ospi.wednet.edu", "gopher://iota.qmw.ac.uk",
"gopher://israel-info.gov.il", "gopher://itsa.ucsf.edu",
"gopher://jaguar.dacc.cc.il.us", "gopher://kimberly.807-city.on.ca",
"gopher://knot.queensu.ca", "gopher://leipzig.nct.de",
"gopher://lenti.med.umn.edu", "gopher://library.ucsc.edu",
"gopher://mach.vub.ac.be", "gopher://magpie.bio.indiana.edu",
"gopher://mailer.fsu.edu", "gopher://maine.maine.edu",
"gopher://mariposa.cc.uh.edu", "gopher://mde.merit.edu",
"gopher://merlin.rh.edu", "gopher://miamilink.lib.muohio.edu",
"gopher://minerva.acc.virginia.edu", "gopher://natasha.oswego.edu",
"gopher://nemesis.cs.berkeley.edu", "gopher://netlib2.cs.utk.edu",
"gopher://newalbion.com", "gopher://news.std.com",
"gopher://nic.merit.edu", "gopher://nickel.mv.net",
"gopher://nova.umuc.edu", "gopher://olymp.wu-wien.ac.at",
"gopher://omega.hanover.edu", "gopher://origin.lib.lsu.edu",
"gopher://panam3.panam.edu", "gopher://pcinfo.pc.maricopa.edu",
"gopher://pi.glockenspiel.complete.org", "gopher://picard.3k.com",
"gopher://picard.evms.edu", "gopher://power-house.ties.k12.mn.us",
"gopher://procrustes.biology.yale.edu",
"gopher://proteon.inet-serv.com", "gopher://purple.tmn.com",
"gopher://rail.bio.indiana.edu", "gopher://rf1.cuis.edu",
"gopher://rs7.loc.gov", "gopher://rsl-01.rsl.ox.ac.uk",
"gopher://rudi.ifs.hr", "gopher://rzubiz.unizh.ch",
"gopher://sanaga.itu.ch", "gopher://sdsumus.sdstate.edu",
"gopher://seds.lpl.arizona.edu", "gopher://semovm.semo.edu",
"gopher://server.uwindsor.ca", "gopher://server.vhdl.org",
"gopher://soochak.ncst.ernet.in", "gopher://sophia.smith.edu",
"gopher://spartan.ac.brocku.ca", "gopher://ssugopher.sonoma.edu",
"gopher://stockholm.ptloma.edu", "gopher://tang.qut.edu.au",
"gopher://taurus.cc.umb.edu", "gopher://text-fax.slu.edu",
"gopher://thunder.thunderstone.com", "gopher://tremaine.cc.uec.ac.jp",
"gopher://twsuvm.uc.twsu.edu", "gopher://ukcc.uky.edu",
"gopher://uniwa.uwa.edu.au", "gopher://uor.edu",
"gopher://utl1.library.utoronto.ca", "gopher://vaxd.sxu.edu",
"gopher://vetserv2.vetmed.vt.edu", "gopher://vm.biu.ac.il",
"gopher://vm.cc.latech.edu", "gopher://vortex.com",
"gopher://world.std.com", "gopher://wvnvm.wvnet.edu",
"gopher://www.circleintl.com", "gopher://www.shore.net",
"gopher://www.udel.edu", "gopher://www.utoledo.edu",
"gopher://www.well.com", "gopher://www1.williams.edu",
"gopher://www3.nsysu.edu.tw", "gopher://xavier.xu.edu",
"gopher://zenith.ngdc.noaa.gov" ]

sl = ["gopher://archive.msstate.edu", "gopher://gopher.nctr.fda.gov"]

for x in sl:
    frontier.add(x)


# use monitor() to fire up the number of connections we want
monitor()
# handle all the connection stuff
loop()

