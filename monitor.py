import time
import lenzgopher
import frontier
import urlparse
from twisted.internet import tcp


concurrency = 1
connections = 0

def addConnection():
    global connections
    connections += 1
    # stop runaway errors
    assert connections <= 2000 

def delConnection():
    global connections
    connections -= 1
    assert connections >= 0 

def monitor():
    '''open new connenctions until we reach concurrency'''

    print "%s: monitor active" % time.localtime()

    while connections < concurrency:
        url = frontier.getURL()
        if url == None:
            # the frontier can't deliver new jobs at this time, so we do just nothing
            break
            
        (protocol, host, path, parameters, query, fragment) = urlparse.urlparse(url, 'gopher', 0)
        s = host.find(':')
        if s == -1:
            # this breaks on MacOS X because netinfo doesn't know gopher. urgs.
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
        # TODO: add timeout
        tcp.Client(host, port, lenzgopher.gopherRequestor(path))
        
