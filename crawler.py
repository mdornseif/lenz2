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
    'gopher://w8n.koeln.ccc.de/1/uniprog']

sl = ["gopher://archive.msstate.edu", "gopher://gopher.nctr.fda.gov"]

for x in sl:
    frontier.add(x)


# use monitor() to fire up the number of connections we want
monitor()
# handle all the connection stuff
loop()

